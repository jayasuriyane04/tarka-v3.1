"""Real password hashes and durable database sessions; no external identity service."""
import json
import secrets
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func, delete

from app import auth, main
from app.db import Account, AuthSession, AuthRateLimit, Family, LearningRecord
from test_api import database, client, SETUP, setup, post, unlock

PASSWORD = 'a safe test passphrase 2026'
NEW_PASSWORD = 'another safe test passphrase 2026'


def refresh(client):
    boot = client.get('/api/bootstrap').json()
    client.headers['X-CSRF-Token'] = boot['session']['csrf_token']
    return boot


def register(client, username='parent_one', **extra):
    result = post(client, 'auth/register', username=username, password=PASSWORD, adult_confirmed=True, **extra)
    assert result.status_code == 200, result.text
    client.headers['X-CSRF-Token'] = result.json()['session']['csrf_token']
    return result.json()


def login(client, username='parent_one', password=PASSWORD):
    refresh(client)
    result = post(client, 'auth/login', username=username, password=password)
    assert result.status_code == 200, result.text
    client.headers['X-CSRF-Token'] = result.json()['session']['csrf_token']
    return result.json()


def legacy(client, database):
    """Create the exact pre-account database/cookie shape, never a new guest bypass."""
    raw = secrets.token_urlsafe(32)
    with database() as db:
        family = Family(id=str(uuid.uuid4()), token_hash=main.digest(raw), csrf=secrets.token_hex(32),
                        pin_hash=main.hash_pin(SETUP['pin']), nickname='Old learner')
        db.add(family)
        db.flush()
        db.add(LearningRecord(id=family.id + ':m68-01', family_id=family.id, lesson_id='m68-01',
                             answers={'p1': [{'choice': 0, 'correct': True}]}, hints={}, narrations={}))
        db.commit()
        family_id = family.id
    client.cookies.clear()
    client.cookies.set(main.COOKIE, raw)
    refresh(client)
    return family_id, raw


def test_registration_requires_adult_and_new_setup_requires_account(client):
    assert post(client, 'setup', **SETUP).status_code == 401
    assert post(client, 'auth/register', username='parent', password=PASSWORD, adult_confirmed=False).status_code == 422
    old_cookie = client.cookies.get(main.COOKIE)
    old_csrf = client.headers['X-CSRF-Token']
    boot = register(client, 'Parent_One')
    assert boot['auth'] == {'authenticated': True, 'username': 'parent_one', 'legacy_profile': False}
    assert old_cookie != client.cookies.get(main.COOKIE)
    assert old_csrf != boot['session']['csrf_token']
    assert post(client, 'setup', **SETUP).status_code == 200
    with TestClient(main.app) as stolen:
        stolen.cookies.set(main.COOKIE, old_cookie)
        assert stolen.get('/api/lessons/m68-01').status_code == 401


def test_password_storage_and_session_tokens_are_not_plaintext(client, database):
    register(client)
    with database() as db:
        account = db.scalar(select(Account))
        assert account.password_hash.startswith('scrypt:131072:8:1:')
        assert PASSWORD not in account.password_hash
        assert auth.verify_password(PASSWORD, account.password_hash)
        assert not auth.verify_password(PASSWORD + 'x', account.password_hash)
        assert db.get(AuthSession, client.cookies.get(main.COOKIE)) is None
        assert db.get(AuthSession, auth.digest(client.cookies.get(main.COOKIE))) is not None
    boot = refresh(client)
    assert PASSWORD not in json.dumps(boot)
    assert 'password_hash' not in json.dumps(boot)


def test_login_restores_old_family_and_progress_after_family_age_limit(client, database):
    registered = register(client)
    setup(client)
    post(client, 'hints', lesson_id='m68-01')
    with database() as db:
        db.get(Family, registered['session']['id']).created_at = time.time() - 90 * 86400
        db.commit()
    with TestClient(main.app) as second:
        result = login(second, 'PARENT_ONE')
        assert result['session']['id'] == registered['session']['id']
        assert result['profile']['nickname'] == SETUP['nickname']
        assert second.get('/api/lessons/m68-01').json()['state']['assistance_level'] == 1


def test_login_errors_are_generic_and_do_not_change_session(client):
    register(client)
    original_cookie = client.cookies.get(main.COOKIE)
    missing = post(client, 'auth/login', username='not_existing', password=PASSWORD)
    wrong = post(client, 'auth/login', username='parent_one', password='incorrect password')
    assert missing.status_code == wrong.status_code == 401
    assert missing.json() == wrong.json()
    assert client.cookies.get(main.COOKIE) == original_cookie


@pytest.mark.parametrize('route,payload', [
    ('auth/register', {'username': 'new_parent', 'password': PASSWORD, 'adult_confirmed': True}),
    ('auth/login', {'username': 'parent_one', 'password': PASSWORD}),
    ('auth/logout', {}), ('auth/logout-all', {}),
    ('auth/password', {'current_password': PASSWORD, 'new_password': NEW_PASSWORD}),
])
def test_every_auth_mutation_rejects_bad_csrf_and_origin(client, route, payload):
    assert client.post('/api/' + route, json=payload, headers={'X-CSRF-Token': 'wrong'}).status_code == 403
    assert client.post('/api/' + route, json=payload, headers={'Origin': 'https://attacker.invalid'}).status_code == 403


def test_logout_revokes_cookie_and_parent_access(client):
    register(client)
    setup(client)
    parent = unlock(client)
    old_cookie, old_csrf = client.cookies.get(main.COOKIE), client.headers['X-CSRF-Token']
    response = post(client, 'auth/logout')
    assert response.status_code == 200
    assert response.json()['auth']['authenticated'] is False
    assert response.json()['profile'] is None
    with TestClient(main.app) as replay:
        replay.cookies.set(main.COOKIE, old_cookie)
        replay.headers.update({'X-CSRF-Token': old_csrf, 'X-Parent-Token': parent})
        assert replay.get('/api/parent/export').status_code == 401
        assert replay.post('/api/answer', json={'lesson_id': 'm68-01', 'choice': 0}).status_code == 401


def test_parent_unlock_token_is_bound_to_authenticated_session(client):
    register(client)
    setup(client)
    token = unlock(client)
    with TestClient(main.app) as second:
        login(second)
        second.headers['X-Parent-Token'] = token
        assert second.get('/api/parent/export').status_code == 403
        unlock(second)
        assert second.get('/api/parent/export').status_code == 200
    assert client.get('/api/parent/export').status_code == 200


def test_logout_all_revokes_other_devices(client):
    register(client)
    setup(client)
    with TestClient(main.app) as second:
        login(second)
        assert second.get('/api/lessons/m68-01').status_code == 200
        response = post(client, 'auth/logout-all')
        assert not response.json()['auth']['authenticated']
        assert second.get('/api/lessons/m68-01').status_code == 401


def test_password_change_requires_old_password_revokes_others_and_rotates_current(client):
    register(client)
    setup(client)
    unlock(client)
    old_cookie, old_csrf = client.cookies.get(main.COOKIE), client.headers['X-CSRF-Token']
    with TestClient(main.app) as second:
        login(second)
        assert post(client, 'auth/password', current_password='incorrect password', new_password=NEW_PASSWORD).status_code == 401
        changed = post(client, 'auth/password', current_password=PASSWORD, new_password=NEW_PASSWORD)
        assert changed.status_code == 200, changed.text
        assert changed.json()['auth']['authenticated']
        assert client.cookies.get(main.COOKIE) != old_cookie
        assert changed.json()['session']['csrf_token'] != old_csrf
        assert client.get('/api/parent/export').status_code == 403
        assert second.get('/api/lessons/m68-01').status_code == 401
        refresh(second)
        assert post(second, 'auth/login', username='parent_one', password=PASSWORD).status_code == 401
        assert login(second, password=NEW_PASSWORD)['auth']['authenticated']


@pytest.mark.parametrize('field', ['expires_at', 'last_seen_at'])
def test_absolute_and_idle_session_expiry(client, database, field):
    register(client)
    setup(client)
    with database() as db:
        session = db.get(AuthSession, auth.digest(client.cookies.get(main.COOKIE)))
        setattr(session, field, time.time() - 8 * 86400)
        db.commit()
    assert client.get('/api/lessons/m68-01').status_code == 401
    assert login(client)['auth']['authenticated']


def test_legacy_profile_claim_preserves_records_and_revokes_old_cookie(client, database):
    family_id, old_cookie = legacy(client, database)
    assert refresh(client)['auth']['legacy_profile']
    assert client.get('/api/lessons/m68-01').status_code == 200
    assert post(client, 'auth/register', username='parent_one', password=PASSWORD, adult_confirmed=True).status_code == 403
    assert post(client, 'auth/register', username='parent_one', password=PASSWORD, adult_confirmed=True, existing_pin='999999').status_code == 403
    boot = register(client, existing_pin=SETUP['pin'])
    assert boot['session']['id'] == family_id
    assert not boot['auth']['legacy_profile']
    with database() as db:
        assert db.get(LearningRecord, family_id + ':m68-01').answers
    with TestClient(main.app) as replay:
        replay.cookies.set(main.COOKIE, old_cookie)
        assert replay.get('/api/lessons/m68-01').status_code == 401


def test_legacy_claim_pin_throttling_cannot_be_reset_with_new_username(client, database):
    legacy(client, database)
    for index in range(5):
        response = post(client, 'auth/register', username=f'parent_{index}', password=PASSWORD,
                        adult_confirmed=True, existing_pin='999999')
        assert response.status_code == 403
    assert post(client, 'auth/register', username='final_parent', password=PASSWORD,
                adult_confirmed=True, existing_pin=SETUP['pin']).status_code == 429


def test_login_rate_limit_survives_new_browser_and_in_memory_reset(client, database, monkeypatch):
    # Focus on the durable reservation without spending a scrypt call per failure.
    calls = []
    monkeypatch.setattr(auth, 'verify_password', lambda *args: calls.append(args) or False)
    for _ in range(8):
        assert post(client, 'auth/login', username='target_parent', password=PASSWORD).status_code == 401
    assert len(calls) == 8
    main._anonymous.clear()
    main._locks.clear()
    with TestClient(main.app) as second:
        refresh(second)
        assert post(second, 'auth/login', username='TARGET_PARENT', password=PASSWORD).status_code == 429
    assert len(calls) == 8
    with database() as db:
        assert db.scalar(select(func.count()).select_from(AuthRateLimit)) >= 3


def test_expensive_password_work_has_nonblocking_concurrency_limit():
    with auth.password_work():
        with pytest.raises(main.HTTPException) as error:
            auth.hash_password(PASSWORD)
        assert error.value.status_code == 503


@pytest.mark.parametrize('payload', [
    {'username': 'valid', 'password': 'SHORT_SECRET', 'adult_confirmed': True},
    {'username': 'valid', 'password': ['SENSITIVE_PASSWORD'], 'adult_confirmed': True},
    {'username': 'bad space', 'password': PASSWORD, 'adult_confirmed': True},
    {'username': 'valid', 'password': PASSWORD, 'adult_confirmed': True, 'existing_pin': 'PIN_SECRET'},
])
def test_validation_errors_do_not_echo_credential_inputs(client, payload):
    response = post(client, 'auth/register', **payload)
    assert response.status_code == 422
    for secret in ['SHORT_SECRET', 'SENSITIVE_PASSWORD', 'PIN_SECRET', PASSWORD]:
        assert secret not in response.text
    assert 'input' not in response.text


def test_malformed_json_does_not_echo_password(client):
    response = client.post('/api/auth/login', content='{"password":"SENSITIVE_PASSWORD",', headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert 'SENSITIVE_PASSWORD' not in response.text


def test_duplicate_usernames_are_case_insensitive(client):
    register(client)
    with TestClient(main.app) as other:
        refresh(other)
        response = post(other, 'auth/register', username='PARENT_ONE', password=PASSWORD, adult_confirmed=True)
        assert response.status_code == 409


def test_account_deletion_requires_password_and_revokes_other_sessions(client, database):
    boot = register(client)
    setup(client)
    unlock(client)
    with TestClient(main.app) as second:
        login(second)
        assert post(client, 'parent/delete-profile', confirm=True).status_code == 401
        assert post(client, 'parent/delete-profile', confirm=True, current_password='wrong password').status_code == 401
        assert post(client, 'parent/delete-profile', confirm=True, current_password=PASSWORD).status_code == 200
        assert second.get('/api/lessons/m68-01').status_code == 401
    with database() as db:
        assert db.get(Family, boot['session']['id']) is None
        assert db.scalar(select(Account).where(Account.username == 'parent_one')) is None


def test_account_cannot_access_another_family_progress(client):
    owner = register(client)
    setup(client)
    post(client, 'hints', lesson_id='m68-01')
    with TestClient(main.app) as other:
        refresh(other)
        stranger = register(other, 'different_parent')
        setup(other)
        assert stranger['session']['id'] != owner['session']['id']
        assert other.get('/api/lessons/m68-01').json()['state']['assistance_level'] == 0


def test_blocked_peer_does_not_exhaust_global_hash_budget(database):
    blocked = SimpleNamespace(client=SimpleNamespace(host='peer-one'))
    allowed = SimpleNamespace(client=SimpleNamespace(host='peer-two'))
    with database() as db:
        for _ in range(20):
            auth.throttle(db, blocked, 'login')
        for _ in range(5):
            with pytest.raises(main.HTTPException) as error:
                auth.throttle(db, blocked, 'login')
            assert error.value.status_code == 429
        global_before = db.scalar(select(func.sum(AuthRateLimit.count)).where(AuthRateLimit.key.like(auth.digest('global') + ':%')))
        assert global_before == 20
        auth.throttle(db, allowed, 'login')
        assert db.scalar(select(func.sum(AuthRateLimit.count)).where(AuthRateLimit.key.like(auth.digest('global') + ':%'))) == 21


def test_pin_limit_reservations_are_atomic_across_independent_sessions(database):
    def reserve(_):
        with database() as db:
            try:
                auth.reserve_pin_attempt(db, 'same-family')
                return True
            except main.HTTPException as error:
                assert error.status_code == 429
                return False
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(reserve, range(12))) == 5


def test_successful_pin_proofs_refund_reservation(database):
    with database() as db:
        for _ in range(10):
            key = auth.reserve_pin_attempt(db, 'family')
            auth.refund_pin_attempt(db, key)
        assert db.get(AuthRateLimit, key).count == 0
