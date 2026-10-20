"""Tarka Family: deterministic practice, protected parent controls, narrow AI hints."""
import asyncio
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import hashlib
import hmac
import math
import secrets
import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, delete, func, update
from sqlalchemy.exc import IntegrityError
from .config import ROOT, settings
from .db import SessionLocal, Family, Lesson, LearningRecord, Usage, Budget, Account, AuthSession
from .schemas import SetupIn, UnlockIn, ProfileIn, LessonIn, AnswerIn, DeleteIn, NarrationIn, NarrationOut, RegisterIn, LoginIn, PasswordIn
from .providers import ProviderUnavailable, cards_for, select_hint
from . import auth

COOKIE = 'tarka_v3_session'
_locks = {}
_anonymous = defaultdict(deque)


@asynccontextmanager
async def lifespan(app):
    settings.validate_deployment()
    yield


app = FastAPI(title='Tarka Family Voice API', version='0.3.0', lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    # Pydantic's default errors include the offending input, which may contain
    # passwords, PINs or a malformed JSON request body. Never echo those values.
    return JSONResponse({'detail': [{'loc': item['loc'], 'type': item['type'],
                                    'msg': 'Invalid value. Check this field.'}
                                   for item in error.errors()]}, status_code=422)


@app.middleware('http')
async def protect_http(request, call_next):
    if request.method == 'POST':
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 16384:
                return JSONResponse({'detail': 'This request is too large.'}, status_code=413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if request.url.path.startswith('/api'):
        response.headers['Cache-Control'] = 'no-store'
    if settings.app_env == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response


def digest(value):
    return hmac.new(settings.session_secret.encode(), value.encode(), hashlib.sha256).hexdigest()


def hash_pin(pin):
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', pin.encode(), bytes.fromhex(salt), 210000).hex()
    return salt + ':' + hashed


def check_pin(pin, stored):
    if ':' not in stored:
        return False
    salt, expected = stored.split(':', 1)
    actual = hashlib.pbkdf2_hmac('sha256', pin.encode(), bytes.fromhex(salt), 210000).hex()
    return secrets.compare_digest(expected, actual)


def identify(db, request):
    return auth.identify(db, request)


def limit_anonymous(request):
    key = request.client.host if request.client else 'local'
    cutoff = time.monotonic() - 60
    if len(_anonymous) > 5000:
        for old in list(_anonymous):
            if not _anonymous[old] or _anonymous[old][-1] < cutoff:
                del _anonymous[old]
    queue = _anonymous[key]
    while queue and queue[0] < cutoff:
        queue.popleft()
    if len(queue) >= 60:
        raise HTTPException(429, 'Please wait a little, then try again.')
    queue.append(time.monotonic())


async def context(request: Request):
    with SessionLocal() as db:
        family = identify(db, request)
        if family is None:
            raise HTTPException(401, 'Please reload to open your learning space.')
        if request.method == 'POST':
            origin = request.headers.get('origin')
            if origin and origin not in {value.strip() for value in settings.allowed_origins.split(',')}:
                raise HTTPException(403, 'This website is not allowed to change your learning space.')
            if not secrets.compare_digest(request.headers.get('x-csrf-token', ''), auth.csrf_for(family)):
                raise HTTPException(403, 'Please reload to refresh your session.')
        if request.method == 'POST' or request.url.path.startswith('/api/lessons/'):
            # Reading a lesson may create its record/start the timer, so serialize it too.
            lock = _locks.setdefault(family.id, asyncio.Lock())
            if lock.locked():
                raise HTTPException(409, 'One moment—your previous step is still saving.')
            try:
                async with lock:
                    if request.method == 'POST':
                        count = db.scalar(select(func.count()).select_from(Usage).where(Usage.family_id == family.id, Usage.provider == 'request', Usage.created_at > time.time() - 60))
                        if count >= 40:
                            raise HTTPException(429, 'Please take a short pause before trying again.')
                        db.add(Usage(id=str(uuid.uuid4()), family_id=family.id, provider='request', status=request.url.path.rsplit('/', 1)[-1][:30]))
                        db.commit()
                    yield db, family
            finally:
                _locks.pop(family.id, None)
        else:
            yield db, family


def setup_required(family):
    if not family.pin_hash:
        raise HTTPException(409, 'Ask a parent or caregiver to set up your learning space first.')


def parent_required(request, family):
    setup_required(family)
    token = request.headers.get('x-parent-token', '')
    scope = auth.parent_scope(family)
    if not token or len(token) > 128 or scope.parent_expires <= time.time() or not secrets.compare_digest(digest(token), scope.parent_hash):
        raise HTTPException(403, 'Unlock the parent space to make this change.')


def profile(family):
    return {key: getattr(family, key) for key in ['nickname', 'age_band', 'ai_enabled', 'voice_enabled', 'session_minutes']} if family.pin_hash else None


def break_state(family):
    moment = time.time()
    active = family.break_until > 0
    elapsed = bool(family.started_at and moment - family.started_at >= family.session_minutes * 60)
    remaining = max(0, math.ceil(family.break_until - moment)) if active else 0
    return {'due': active or elapsed, 'seconds_remaining': remaining, 'minutes': family.session_minutes,
            'session_seconds_remaining': max(0, math.ceil(family.session_minutes * 60 - (moment - family.started_at))) if family.started_at else family.session_minutes * 60,
            'started': active}


def ready_to_learn(db, family):
    setup_required(family)
    if break_state(family)['due']:
        raise HTTPException(423, 'Time for a little break. Stretch, look away from the screen, then come back.')
    if not family.started_at:
        family.started_at = time.time()
        db.commit()


def lesson_data(db, family, lesson_id):
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.data['age_band'] != family.age_band:
        raise HTTPException(404, 'This lesson is not in your current learning collection.')
    return lesson.data


def record_for(db, family, lesson_id):
    key = family.id + ':' + lesson_id
    record = db.get(LearningRecord, key)
    if record is None:
        record = LearningRecord(id=key, family_id=family.id, lesson_id=lesson_id, position=0, answers={}, hints={}, narrations={}, completed=False, transfer_independent=False)
        db.add(record)
        db.flush()
    return record


def collection(db, family):
    lessons = sorted([row.data for row in db.scalars(select(Lesson)) if row.data['age_band'] == family.age_band], key=lambda row: row['id'])
    records = {row.lesson_id: row for row in db.scalars(select(LearningRecord).where(LearningRecord.family_id == family.id))}
    summaries = []
    for lesson in lessons:
        record = records.get(lesson['id'])
        summaries.append({**{key: lesson[key] for key in ['id', 'title', 'subject', 'age_band', 'skill', 'summary']},
                          'completed': bool(record and record.completed), 'transfer_independent': bool(record and record.transfer_independent)})
    relevant = [records[x['id']] for x in lessons if x['id'] in records]
    progress = {'completed_lessons': sum(row.completed for row in relevant), 'independent_transfers': sum(row.transfer_independent for row in relevant),
                'practised_questions': sum(bool(attempts) for row in relevant for attempts in row.answers.values()), 'total_lessons': len(lessons),
                'by_subject': [{'subject': subject, 'completed': sum(row['completed'] for row in summaries if row['subject'] == subject),
                                'independent': sum(row['transfer_independent'] for row in summaries if row['subject'] == subject),
                                'total': sum(row['subject'] == subject for row in summaries)} for subject in ['maths', 'reading']]}
    return summaries, progress


def bootstrap_data(db, family):
    lessons, progress = collection(db, family) if family.pin_hash else ([], {'completed_lessons': 0, 'independent_transfers': 0, 'practised_questions': 0, 'total_lessons': 0, 'by_subject': []})
    account = auth.account_for(db, family)
    return {'session': {'id': family.id, 'csrf_token': auth.csrf_for(family), 'setup_complete': bool(family.pin_hash)},
            'auth': {'authenticated': account is not None, 'username': account.username if account else None,
                     'legacy_profile': bool(family.pin_hash and not account)},
            'profile': profile(family), 'lessons': lessons, 'progress': progress, 'break': break_state(family),
            'mode': {'ai': 'nebius_ready' if family.ai_enabled and settings.nebius_api_key and settings.enable_paid_operations else 'lesson',
                     'paid_enabled': settings.enable_paid_operations}}


def feedback_for(question, attempts):
    if not attempts:
        return None
    correct = attempts[-1]['correct']
    return {'correct': correct, 'message': 'That fits. Let’s see why.' if correct else 'Let’s look at it another way. You can try again or ask for a hint.',
            'explanation': question['explanation'] if correct else None, 'evidence': question.get('evidence') if correct else None}


def public_lesson(db, family, lesson, record):
    position = record.position
    question = lesson['questions'][position] if position < len(lesson['questions']) else None
    attempts = record.answers.get(question['id'], []) if question else []
    hints = record.hints.get(question['id'], []) if question else []
    narration = record.narrations.get(question['id'], {}) if question else {}
    feedback_question = question or (lesson['questions'][-1] if record.completed else None)
    feedback_attempts = record.answers.get(feedback_question['id'], []) if feedback_question else []
    public = {key: lesson.get(key) for key in ['id', 'title', 'subject', 'age_band', 'skill', 'summary', 'explanation', 'worked_example', 'passage', 'visual']}
    return {**public, 'total_questions': len(lesson['questions']), 'index': position,
            'question': {key: question[key] for key in ['id', 'prompt', 'options', 'kind']} if question else None,
            'state': {'tries': len(attempts), 'assistance_level': len(hints), 'answered': bool(attempts and attempts[-1]['correct']),
                      'narration_requests': narration.get('requests', 0),
                      'voice_assisted': narration.get('voice_assistance', narration.get('assistance', False) if not narration.get('whiteboard_assistance') else False),
                      'whiteboard_requests': narration.get('whiteboard_requests', 0),
                      'whiteboard_assisted': narration.get('whiteboard_assistance', False),
                      'last_choice': attempts[-1]['choice'] if attempts else None, 'completed': record.completed, 'transfer_independent': record.transfer_independent},
            'hints': hints, 'last_feedback': feedback_for(feedback_question, feedback_attempts) if feedback_question else None}


@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '0.3.0', 'product': 'Tarka Family Voice'}


@app.get('/api/bootstrap')
def bootstrap(request: Request, response: Response):
    limit_anonymous(request)
    with SessionLocal() as db:
        family = identify(db, request)
        if family is None:
            family = auth.new_guest(db, response)
        return bootstrap_data(db, family)


@app.post('/api/auth/register')
def register(body: RegisterIn, request: Request, response: Response, ctx=Depends(context)):
    db, family = ctx
    if auth.account_for(db, family):
        raise HTTPException(409, 'Sign out before creating another parent account.')
    username = body.username.lower()
    auth.throttle(db, request, 'register', username)
    if family.pin_hash:
        reservation = auth.reserve_pin_attempt(db, family.id)
        if not body.existing_pin or not check_pin(body.existing_pin, family.pin_hash):
            raise HTTPException(403, 'Enter the existing parent PIN to protect this saved profile.')
        auth.refund_pin_attempt(db, reservation)
    stored = auth.hash_password(body.password)
    if db.scalar(select(Account.id).where(Account.username == username)):
        raise HTTPException(409, 'Could not create this account. Choose another username or sign in.')
    account = Account(id=str(uuid.uuid4()), family_id=family.id, username=username,
                      password_hash=stored, credential_version=1)
    db.add(account)
    auth.revoke_current(db, family)
    try:
        db.flush()
        auth.issue_session(db, family, response, account)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Could not create this account. Choose another username or sign in.')
    return bootstrap_data(db, family)


@app.post('/api/auth/login')
def login(body: LoginIn, request: Request, response: Response, ctx=Depends(context)):
    db, current = ctx
    username = body.username.lower()
    auth.throttle(db, request, 'login', username)
    account = db.scalar(select(Account).where(Account.username == username))
    if not auth.verify_password(body.password, account.password_hash if account else None):
        raise HTTPException(401, 'The username or password did not match.')
    family = db.get(Family, account.family_id)
    if not family:
        raise HTTPException(401, 'The username or password did not match.')
    auth.revoke_current(db, current)
    auth.issue_session(db, family, response, account)
    return bootstrap_data(db, family)


@app.post('/api/auth/logout')
def logout(response: Response, ctx=Depends(context)):
    db, family = ctx
    auth.revoke_current(db, family)
    return bootstrap_data(db, auth.new_guest(db, response))


@app.post('/api/auth/logout-all')
def logout_all(response: Response, ctx=Depends(context)):
    db, family = ctx
    account = auth.require_account(db, family)
    # In-flight logins authenticated against the previous version are invalid too.
    db.execute(update(Account).where(Account.id == account.id)
               .values(credential_version=Account.credential_version + 1))
    auth.revoke_all(db, account)
    auth.revoke_current(db, family)
    return bootstrap_data(db, auth.new_guest(db, response))


@app.post('/api/auth/password')
def change_password(body: PasswordIn, request: Request, response: Response, ctx=Depends(context)):
    db, family = ctx
    account = auth.require_account(db, family)
    auth.throttle(db, request, 'password', account.username)
    if not auth.verify_password(body.current_password, account.password_hash):
        raise HTTPException(401, 'The current password did not match.')
    new_hash = auth.hash_password(body.new_password)
    # Compare-and-update also closes concurrent password-change races across workers.
    changed = db.execute(update(Account).where(Account.id == account.id,
                         Account.credential_version == account.credential_version,
                         Account.password_hash == account.password_hash)
                         .values(password_hash=new_hash, credential_version=Account.credential_version + 1))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Your account changed in another session. Sign in again.')
    db.refresh(account)
    auth.revoke_all(db, account)
    auth.revoke_current(db, family)
    auth.issue_session(db, family, response, account)
    return bootstrap_data(db, family)


@app.post('/api/setup')
def setup(body: SetupIn, ctx=Depends(context)):
    db, family = ctx
    if family.pin_hash:
        raise HTTPException(409, 'Your learning space is already set up. Use the parent settings.')
    auth.require_account(db, family)
    family.pin_hash = hash_pin(body.pin)
    for key in ['nickname', 'age_band', 'ai_enabled', 'voice_enabled', 'session_minutes']:
        setattr(family, key, getattr(body, key))
    db.commit()
    return bootstrap_data(db, family)


@app.get('/api/lessons/{lesson_id}')
def get_lesson(lesson_id: str, ctx=Depends(context)):
    db, family = ctx
    ready_to_learn(db, family)
    lesson = lesson_data(db, family, lesson_id)
    record = record_for(db, family, lesson_id)
    db.commit()
    return public_lesson(db, family, lesson, record)


@app.post('/api/answer')
def answer(body: AnswerIn, ctx=Depends(context)):
    db, family = ctx
    ready_to_learn(db, family)
    lesson = lesson_data(db, family, body.lesson_id)
    record = record_for(db, family, body.lesson_id)
    if record.completed:
        raise HTTPException(409, 'You finished this lesson. Choose another to practise a new idea.')
    question = lesson['questions'][record.position]
    attempts = record.answers.get(question['id'], [])
    if attempts and attempts[-1]['correct']:
        raise HTTPException(409, 'This question is checked. Move to the next one.')
    correct = body.choice == question['answer_index']
    attempts = [*attempts, {'choice': body.choice, 'correct': correct}]
    record.answers = {**record.answers, question['id']: attempts}
    if question['kind'] == 'transfer' and correct:
        record.transfer_independent = (len(attempts) == 1 and not record.hints.get(question['id'])
                                       and not record.narrations.get(question['id'], {}).get('assistance'))
        record.completed = True
        record.position = len(lesson['questions'])
    db.commit()
    return {**feedback_for(question, attempts), 'can_continue': correct and not record.completed,
            'lesson': public_lesson(db, family, lesson, record), 'progress': collection(db, family)[1]}


@app.post('/api/continue')
def continue_lesson(body: LessonIn, ctx=Depends(context)):
    db, family = ctx
    ready_to_learn(db, family)
    lesson = lesson_data(db, family, body.lesson_id)
    record = record_for(db, family, body.lesson_id)
    if record.completed:
        return public_lesson(db, family, lesson, record)
    question = lesson['questions'][record.position]
    attempts = record.answers.get(question['id'], [])
    if not attempts or not attempts[-1]['correct']:
        raise HTTPException(409, 'Finish this question before moving on.')
    record.position += 1
    db.commit()
    return public_lesson(db, family, lesson, record)


@app.post('/api/hints')
async def hint(body: LessonIn, ctx=Depends(context)):
    db, family = ctx
    ready_to_learn(db, family)
    lesson = lesson_data(db, family, body.lesson_id)
    record = record_for(db, family, body.lesson_id)
    if record.completed:
        raise HTTPException(409, 'This lesson is finished. Try a new lesson.')
    question = lesson['questions'][record.position]
    attempts = record.answers.get(question['id'], [])
    if attempts and attempts[-1]['correct']:
        raise HTTPException(409, 'You have checked this question. Try the next one.')
    hints = record.hints.get(question['id'], [])
    if len(hints) >= 3:
        return {**hints[-1], 'lesson': public_lesson(db, family, lesson, record)}
    level, selected, source, notice = len(hints) + 1, 'step_hint', 'lesson', None
    if family.ai_enabled and settings.enable_paid_operations and settings.nebius_api_key:
        try:
            selected = await select_hint(db, family, lesson, question, level, attempts)
            source = 'nebius'
        except ProviderUnavailable as error:
            notice = str(error)
    hint_data = {'level': level, 'message': cards_for(lesson, question, level)[selected], 'source': source}
    if notice:
        hint_data['provider_notice'] = notice
    record.hints = {**record.hints, question['id']: [*hints, hint_data]}
    db.commit()
    return {**hint_data, 'lesson': public_lesson(db, family, lesson, record)}


@app.post('/api/narration', response_model=NarrationOut)
def narration(body: NarrationIn, ctx=Depends(context)):
    """Authorize only visible lesson material; never accept arbitrary speech text."""
    db, family = ctx
    ready_to_learn(db, family)
    if not family.voice_enabled:
        raise HTTPException(403, 'Ask a parent or caregiver to turn on spoken teaching in the parent space.')
    lesson = lesson_data(db, family, body.lesson_id)
    record = record_for(db, family, body.lesson_id)
    if body.segment != 'hint' and body.hint_level is not None:
        raise HTTPException(422, 'A hint level is only used when reading a delivered hint.')
    if record.completed and body.segment != 'feedback':
        raise HTTPException(409, 'This lesson is finished. You can listen to its checked feedback.')
    question = lesson['questions'][-1] if record.completed else lesson['questions'][record.position]
    attempts = record.answers.get(question['id'], [])
    answered = bool(attempts and attempts[-1]['correct'])
    source = 'lesson'
    if body.segment == 'lesson':
        if question['kind'] == 'transfer':
            raise HTTPException(409, 'Try this new challenge with its own question. Earlier examples are closed during transfer.')
        example = lesson['worked_example']
        parts = [lesson['explanation'], lesson.get('passage'), 'Worked example.', example['prompt'], example['explanation']]
        label = 'Lesson explanation and worked example'
    elif body.segment == 'question':
        parts = [question['prompt'], *[f'Option {index + 1}. {option}' for index, option in enumerate(question['options'])]]
        label = 'Current question and choices'
    elif body.segment == 'hint':
        hints = record.hints.get(question['id'], [])
        chosen = next((item for item in hints if item['level'] == body.hint_level), None)
        if chosen is None:
            raise HTTPException(409, 'Open that hint first, then choose to listen to it.')
        parts = [chosen['message']]
        source = chosen['source']
        label = f'Hint {chosen["level"]}'
    else:
        checked = feedback_for(question, attempts)
        if checked is None:
            raise HTTPException(409, 'Check an answer first to hear its feedback.')
        parts = [checked['message'], checked['explanation'], checked['evidence']]
        label = 'Checked answer feedback'
    result = NarrationOut(text='\n\n'.join(part for part in parts if part), label=label,
                          source=source, question_id=question['id'])
    previous = record.narrations.get(question['id'], {})
    segments = dict(previous.get('segments', {}))
    segments[body.segment] = segments.get(body.segment, 0) + 1
    # Save before delivering text: a failed browser playback still counts as a
    # request for help. Never revoke an already-earned correct transfer result.
    record.narrations = {**record.narrations, question['id']: {**previous,
        'requests': previous.get('requests', 0) + 1,
        'assistance': bool(previous.get('assistance') or (not answered and body.segment in {'lesson', 'question', 'hint'})),
        'voice_assistance': bool(previous.get('voice_assistance', previous.get('assistance', False) if not previous.get('whiteboard_assistance') else False)
                                 or (not answered and body.segment in {'lesson', 'question', 'hint'})),
        'segments': segments, 'last_requested_at': time.time(),
    }}
    db.commit()
    return result


@app.post('/api/break/start')
def start_break(ctx=Depends(context)):
    db, family = ctx
    setup_required(family)
    if not family.break_until:
        family.break_until = time.time() + settings.break_seconds
        db.commit()
    return break_state(family)


@app.post('/api/break/finish')
def finish_break(ctx=Depends(context)):
    db, family = ctx
    setup_required(family)
    if not family.break_until or family.break_until > time.time():
        raise HTTPException(409, 'Your short break is still running. Come back when the timer is ready.')
    family.break_until, family.started_at = 0, time.time()
    db.commit()
    return break_state(family)


@app.post('/api/parent/unlock')
def unlock(body: UnlockIn, ctx=Depends(context)):
    db, family = ctx
    setup_required(family)
    reservation = auth.reserve_pin_attempt(db, family.id)
    if not check_pin(body.pin, family.pin_hash):
        db.add(Usage(id=str(uuid.uuid4()), family_id=family.id, provider='security', status='pin_failed'))
        db.commit()
        raise HTTPException(403, 'That PIN did not match.')
    auth.refund_pin_attempt(db, reservation)
    token = secrets.token_urlsafe(32)
    scope = auth.parent_scope(family)
    scope.parent_hash, scope.parent_expires = digest(token), time.time() + settings.parent_token_seconds
    db.commit()
    return {'parent_token': token, 'expires_in': settings.parent_token_seconds}


@app.get('/api/parent/overview')
def parent_overview(request: Request, ctx=Depends(context)):
    db, family = ctx
    parent_required(request, family)
    summaries, progress = collection(db, family)
    records = {row.lesson_id: row for row in db.scalars(select(LearningRecord).where(LearningRecord.family_id == family.id))}
    for item in summaries:
        record = records.get(item['id'])
        item['attempts'] = sum(len(value) for value in record.answers.values()) if record else 0
        item['hints_used'] = sum(len(value) for value in record.hints.values()) if record else 0
        item['narration_requests'] = sum(value.get('requests', 0) for value in record.narrations.values()) if record else 0
        item['whiteboard_requests'] = sum(value.get('whiteboard_requests', 0) for value in record.narrations.values()) if record else 0
    budget = db.get(Budget, 1)
    return {'profile': profile(family), 'progress': progress, 'lessons': summaries,
            'usage': {'reserved_usd': budget.reserved_usd if budget else 0, 'budget_usd': settings.paid_budget_usd,
                      'ai_requests': db.scalar(select(func.count()).select_from(Usage).where(Usage.family_id == family.id, Usage.provider == 'nebius')),
                      'ai_available': bool(settings.nebius_api_key and settings.enable_paid_operations)}}


@app.post('/api/parent/lock')
def lock_parent(request: Request, ctx=Depends(context)):
    db, family = ctx
    parent_required(request, family)
    scope = auth.parent_scope(family)
    scope.parent_hash, scope.parent_expires = '', 0
    db.commit()
    return {'locked': True}


@app.post('/api/parent/settings')
def change_settings(body: ProfileIn, request: Request, ctx=Depends(context)):
    db, family = ctx
    parent_required(request, family)
    for key in ['nickname', 'age_band', 'ai_enabled', 'voice_enabled', 'session_minutes']:
        setattr(family, key, getattr(body, key))
    db.commit()
    return bootstrap_data(db, family)


@app.get('/api/parent/export')
def export_progress(request: Request, ctx=Depends(context)):
    db, family = ctx
    parent_required(request, family)
    records = db.scalars(select(LearningRecord).where(LearningRecord.family_id == family.id)).all()
    return {'product': 'Tarka Family Voice v3', 'exported_at': time.time(), 'profile': profile(family),
            'lessons': [{'lesson_id': row.lesson_id, 'position': row.position, 'completed': row.completed,
                         'transfer_independent': row.transfer_independent, 'answers': row.answers, 'hints': row.hints,
                         'narrations': row.narrations} for row in records]}


@app.post('/api/parent/delete-profile')
def delete_profile(body: DeleteIn, request: Request, response: Response, ctx=Depends(context)):
    db, family = ctx
    parent_required(request, family)
    account = auth.account_for(db, family)
    if account:
        auth.throttle(db, request, 'delete', account.username)
        if not body.current_password or not auth.verify_password(body.current_password, account.password_hash):
            raise HTTPException(401, 'Enter your current password to delete this account and profile.')
        db.delete(account)
    db.execute(delete(AuthSession).where(AuthSession.family_id == family.id))
    db.execute(delete(LearningRecord).where(LearningRecord.family_id == family.id))
    db.execute(delete(Usage).where(Usage.family_id == family.id))
    db.delete(family)
    # The global spend reservation remains so deletion cannot reset the ceiling.
    db.commit()
    response.delete_cookie(COOKIE, path='/', httponly=True, secure=settings.cookie_secure, samesite='strict')
    return {'deleted': True}


from .whiteboard import register_whiteboard
register_whiteboard(app, context=context, ready_to_learn=ready_to_learn, lesson_data=lesson_data,
                    record_for=record_for, feedback_for=feedback_for)


dist = ROOT / 'frontend/dist'
if (dist / 'assets').exists():
    app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')


@app.get('/')
def index():
    return FileResponse(dist / 'index.html') if (dist / 'index.html').exists() else JSONResponse({'detail': 'Build the frontend to open Tarka Family.'}, status_code=503)


@app.get('/favicon.svg')
def favicon():
    return FileResponse(dist / 'favicon.svg' if (dist / 'favicon.svg').exists() else ROOT / 'frontend/public/favicon.svg')
