# Accounts and optional maths boards

Extension dated 2026-10-19. See STATUS.md for measured verification; implementation is not an independent security audit or a claim of educational effectiveness.

## Parent account

Create account uses a made-up parent username (3–32 ASCII letters, digits or underscores, case-insensitive) and a password of 15–128 characters. A parent/caregiver confirms they are setting up the account. No email, email verification, external identity provider or paid account service is required. One account owns one learner profile. Sign in from another browser restores the same profile and progress.

Passwords use salted scrypt (N=131072, r=8, p=1, 32-byte result, 16-byte salt). Each hash requires about 128 MiB and only one password operation per application process runs at once; overload returns a retryable 503 instead of queuing expensive work. Credentials are never returned by validation errors, included in exports or sent to the model.

The browser holds an opaque random HttpOnly, SameSite=Strict cookie, not a JWT or password in localStorage. The database holds an HMAC digest of the session token. Login, registration and password change rotate the cookie and CSRF value. Sessions expire after seven days absolutely or 24 hours without API activity; the UI's active polling counts as activity. Sign-out revokes the current session; sign-out on all devices and password change revoke other sessions. Account records remain until deletion. Password changes require the old password. There is no forgotten-password recovery, email reset, MFA or account import in this MVP. Save the password in a password manager.

POST requests require the session CSRF token and reject origins outside the configured allowlist. Owned-session lookup controls all lesson and parent data. Parent capabilities are short-lived and tied to the current session. Account deletion requires the current password as well as the parent PIN gate, and deletes the account, all sessions, learner records and household-linked usage. The global operator spend ledger remains.

Persistent atomic database counters limit expensive account work by peer, username and global budget. They are separate from ordinary lesson request limits. The client IP comes from the ASGI request peer: configure only trusted proxy IPs; never blindly trust forwarded headers. Run one application worker initially because learning progress updates still use process-local serialization.

## Keep an older V3 profile

Migration 0003 adds account, session and rate-limit tables; it does not rewrite existing lesson or learner records. An unexpired older browser-only profile can continue to learn, or choose Create account and supply its existing six-digit parent PIN to link the saved record. After linking, the old cookie cannot reopen it. Signing into a different account switches records; it does not merge the older profile. There is no automatic recovery of an expired or lost legacy cookie. Back up the database before migrating a real deployment.

## Maths teaching board

Every one of the fifteen maths lessons has three authored steps (45 total) based on its existing worked example. Choose Open whiteboard, then Teach on the board; Previous step, Next step and Replay steps control the explanation. The board can also show a hint already delivered or feedback after the server has checked an answer.

The model's permitted role remains selecting an authored hint through the existing opt-in/budget gates. A board displaying such a hint is labelled NVIDIA-selected; otherwise it explicitly says authored content with no live AI generation. Opening the board does not make a new model call. It never renders provider-generated HTML, SVG or arbitrary diagram commands. Structured schemas bound counters, fraction bars, number lines and schematic rectangles. React renders teaching text safely.

During a fresh transfer question, earlier worked-example boards are unavailable. Only already delivered hints or checked feedback can appear. Opening the empty scratchpad does not count as help; requesting teaching steps before an answer records support. Help already used is not cleared by closing the board or reloading. Replaying post-answer feedback does not remove previously earned evidence. Parent progress/export separates board requests from voice requests, while shared assistance flags protect transfer scoring.

The scratchpad provides pen, eraser, undo, clear and a keyboard working box. It is private in browser memory: drawings/typed notes are not saved, sent to the server or read by the model. It clears when closed, when the question/context changes or on reload. Drawing is bounded to 120 strokes with at most 1000 points each. Rectangles are labelled schematics rather than scale drawings. Manual step controls do not imply real-time handwriting recognition, adaptive free-form tutoring or generated voice.

## API and data additions

| Endpoint | Role |
|---|---|
| POST /api/auth/register | Create account; optional existing_pin claims an older owned profile |
| POST /api/auth/login | Verify username/password and issue a rotated owned session |
| POST /api/auth/logout | Revoke this session and return a blank guest bootstrap |
| POST /api/auth/logout-all | Revoke all account sessions and return a blank guest bootstrap |
| POST /api/auth/password | Verify current_password and change to new_password |
| POST /api/whiteboard | Authorize lesson/hint/feedback content for the current maths question |

Auth endpoints return the full bootstrap, including authenticated/username/legacy_profile and rotated CSRF when appropriate. The board returns a validated title, source, question ID and at most six typed steps. Bootstrap does not contain password/PIN verifiers or session token digests. Migration 0003 is additive. Board counts and assistance reuse the existing per-question JSON record, preserving older voice counts.

## Before deployment

Set APP_ENV=production, PostgreSQL, a random SESSION_SECRET, COOKIE_SECURE=true and exact HTTPS ALLOWED_ORIGINS. Add host-level TLS/rate limits, trusted-proxy settings and backup/retention procedures. The development cookie is deliberately not Secure on localhost HTTP. Do not expose the development configuration publicly. Exercise the release in actual PostgreSQL and target browsers; neither an offline migration compile nor SQLite tests establishes that production environment works.

Design references: [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), and [authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html). These informed the design; they do not certify this implementation.
