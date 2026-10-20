"""Parent accounts: bounded scrypt, opaque sessions and durable atomic throttles.

No email address, identity verification, recovery service or child account is implied.
OWASP scrypt parameters: N=2**17, r=8, p=1 (128 MiB per operation).
"""
import hashlib
import hmac
import secrets
import threading
import time
import uuid
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from .config import settings
from .db import Account, AuthSession, AuthRateLimit, Family

COOKIE = 'tarka_v3_session'
_password_slot = threading.BoundedSemaphore(1)


def digest(value):
    return hmac.new(settings.session_secret.encode(), value.encode(), hashlib.sha256).hexdigest()


@contextmanager
def password_work():
    # Do not queue unlimited 128-MiB work or block the async event loop.
    if not _password_slot.acquire(blocking=False):
        raise HTTPException(503, 'Account service is busy. Please try again shortly.', headers={'Retry-After': '2'})
    try:
        yield
    finally:
        _password_slot.release()


def _derive(password, salt):
    return hashlib.scrypt(password.encode('utf-8'), salt=salt, n=131072, r=8, p=1,
                          dklen=32, maxmem=192 * 1024 * 1024)


def hash_password(password):
    with password_work():
        salt = secrets.token_bytes(16)
        return 'scrypt:131072:8:1:' + salt.hex() + ':' + _derive(password, salt).hex()


def verify_password(password, stored):
    # Nonexistent users do the same expensive work as real users.
    salt, expected, valid = bytes(16), bytes(32), False
    try:
        algorithm, n, r, p, salt_hex, value_hex = (stored or '').split(':')
        if (algorithm, n, r, p) == ('scrypt', '131072', '8', '1'):
            salt, expected = bytes.fromhex(salt_hex), bytes.fromhex(value_hex)
            valid = len(salt) == 16 and len(expected) == 32
    except (ValueError, TypeError):
        pass
    with password_work():
        actual = _derive(password, salt if valid else bytes(16))
    return secrets.compare_digest(actual, expected) and valid


def throttle(db, request, action, username=None, family_id=None):
    """Atomic fixed windows, surviving restart and concurrent app workers.

    Trust the socket peer only; do not accept arbitrary X-Forwarded-For.
    Reverse proxies must configure trusted proxy headers at the ASGI server.
    """
    now = time.time()
    host = request.client.host if request.client else 'local'
    # Stop blocked peers before they consume the global expensive-work allowance.
    scopes = [('peer:' + host, 20, 600), ('global', 120, 60)]
    if username:
        scopes.append(('username:' + username.lower(), 8, 600))
    if family_id:
        scopes.append(('claim:' + family_id, 5, 600))
    dialect = db.bind.dialect.name
    if dialect == 'sqlite':
        from sqlalchemy.dialects.sqlite import insert
    elif dialect == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        raise HTTPException(503, 'This database does not support account protection.')
    limited = False
    db.execute(delete(AuthRateLimit).where(AuthRateLimit.expires_at < now))
    for scope, ceiling, seconds in scopes:
        start = int(now // seconds) * seconds
        key = digest(scope) + ':' + str(start)
        statement = insert(AuthRateLimit).values(key=key, count=1, expires_at=start + seconds)
        count = db.scalar(statement.on_conflict_do_update(index_elements=['key'],
                         set_={'count': AuthRateLimit.count + 1}).returning(AuthRateLimit.count))
        limited |= count > ceiling
        if limited:
            break  # A blocked peer cannot fill storage with arbitrary usernames.
    db.commit()  # Failed passwords still consume their reserved attempt.
    if limited:
        raise HTTPException(429, 'Too many account attempts. Wait ten minutes before trying again.', headers={'Retry-After': '600'})


def reserve_pin_attempt(db, family_id):
    """Reserve one of five PIN failures atomically before running the hash.

    Successful proofs refund the reservation; concurrent workers cannot race
    a count-then-insert check. Claiming a legacy profile shares this same limit.
    """
    now = time.time()
    start = int(now // 600) * 600
    key = digest('pin:' + family_id) + ':' + str(start)
    if db.bind.dialect.name == 'sqlite':
        from sqlalchemy.dialects.sqlite import insert
    else:
        from sqlalchemy.dialects.postgresql import insert
    statement = insert(AuthRateLimit).values(key=key, count=1, expires_at=start + 600)
    count = db.scalar(statement.on_conflict_do_update(index_elements=['key'],
                     set_={'count': AuthRateLimit.count + 1}).returning(AuthRateLimit.count))
    db.commit()
    if count > 5:
        raise HTTPException(429, 'Too many PIN attempts. Wait ten minutes before trying again.', headers={'Retry-After': '600'})
    return key


def refund_pin_attempt(db, key):
    db.execute(update(AuthRateLimit).where(AuthRateLimit.key == key, AuthRateLimit.count > 0)
               .values(count=AuthRateLimit.count - 1))
    db.commit()


def active_session(family):
    return getattr(family, '_active_session', None)


def account_for(db, family):
    session = active_session(family)
    return db.get(Account, session.account_id) if session and session.account_id else None


def csrf_for(family):
    session = active_session(family)
    return session.csrf if session else family.csrf


def parent_scope(family):
    return active_session(family) or family


def identify(db, request):
    raw = request.cookies.get(COOKIE, '')
    if not raw or len(raw) > 128:
        return None
    now = time.time()
    session = db.get(AuthSession, digest(raw))
    if session:
        if session.revoked or session.expires_at <= now or session.last_seen_at <= now - settings.auth_idle_seconds:
            return None
        family = db.get(Family, session.family_id)
        if not family:
            return None
        owner = db.scalar(select(Account).where(Account.family_id == family.id))
        if owner and (session.account_id != owner.id or session.credential_version != owner.credential_version):
            return None
        if session.account_id and not owner:
            return None
        if now - session.last_seen_at > 60:
            session.last_seen_at = now
            db.commit()
        family._active_session = session
        return family
    # V2/V3 cookie-only profiles survive migration. Once claimed, the old
    # family token must never authenticate the account or its learning records.
    family = db.scalar(select(Family).where(Family.token_hash == digest(raw)))
    if (not family or family.created_at <= now - 30 * 86400
            or db.scalar(select(Account.id).where(Account.family_id == family.id))):
        return None
    family._active_session = None
    return family


def revoke_current(db, family):
    session = active_session(family)
    if session:
        session.revoked = True
        session.parent_hash, session.parent_expires = '', 0
    family.parent_hash, family.parent_expires = '', 0
    # Invalidate the legacy fallback on every authentication boundary.
    family.token_hash = digest(secrets.token_urlsafe(32))


def issue_session(db, family, response, account=None):
    now = time.time()
    raw = secrets.token_urlsafe(32)
    lifetime = settings.auth_session_seconds if account else settings.auth_idle_seconds
    session = AuthSession(token_hash=digest(raw), family_id=family.id,
                          account_id=account.id if account else None,
                          credential_version=account.credential_version if account else 0,
                          csrf=secrets.token_hex(32), created_at=now, last_seen_at=now,
                          expires_at=now + lifetime, revoked=False)
    db.add(session)
    family._active_session = session
    db.commit()
    response.set_cookie(COOKIE, raw, httponly=True, secure=settings.cookie_secure,
                        samesite='strict', max_age=lifetime, path='/')
    return family


def new_guest(db, response):
    family = Family(id=str(uuid.uuid4()), token_hash=digest(secrets.token_urlsafe(32)), csrf=secrets.token_hex(32))
    db.add(family)
    db.flush()
    return issue_session(db, family, response)


def revoke_all(db, account):
    db.execute(update(AuthSession).where(AuthSession.account_id == account.id).values(revoked=True, parent_hash='', parent_expires=0))


def require_account(db, family):
    account = account_for(db, family)
    if not account:
        raise HTTPException(401, 'A parent or caregiver needs to sign in first.')
    return account
