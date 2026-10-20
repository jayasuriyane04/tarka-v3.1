# Tarka V3 handover — accounts and whiteboards

The V3 extension is implemented and verified locally. It preserves30 lessons/120 questions, voice teaching and parent controls, and adds authenticated parent accounts plus optional whiteboards for all15 maths lessons (45 authored steps). V1/V2 are unchanged.

## Run the normal application

From this folder in PowerShell, stop the old app with Ctrl+C and run `./START-LOCAL.ps1`. It applies the additive account migration and serves the built frontend at http://127.0.0.1:8003. Keep the terminal open. On a fresh machine, follow README.md to install locked dependencies and build first. Back up an existing deployed database before migration.

Choose Create account. A parent uses a made-up username, a15–128-character password and adult acknowledgement. If the current browser contains an older V3 learner, supply its existing parent PIN to keep that record. Sign-in on another browser restores account progress. One learner belongs to each account. Passwords and the six-digit parent PIN have separate roles. There is no forgotten-password/email recovery or MFA; save the password securely.

In a maths lesson select Open whiteboard → Teach on the board. Use Next/Previous/Replay. The tutor shows authored steps and diagrams; delivered NVIDIA-selected hints retain their source label when real inference is enabled. The scratchpad supports pen/eraser/undo/clear and typed working, held only in browser memory. The AI does not read or grade drawings. Transfer questions block old examples and preserve assistance records.

## Verification

Final source:247 backend tests (98 auth/API +149 regression),59 frontend tests, TypeScript/Vite build and original-content preservation pass. Browser signup, setup, wrong-password rejection, logout/login, saved progress, optional board navigation, drawing/undo, transfer restrictions, targeted hint board and supported completion were exercised. The parent view retained5 attempts,1 hint,0 voice requests and2 board requests for the completed synthetic lesson. Desktop/narrow layouts were checked. See STATUS.md and evaluation/reports/accounts-whiteboard-browser.md for evidence and limits.

Verification used http://localhost:8004 with a separate synthetic database in workspace work/. Its dummy account is qa_parent_1020_01, password `Local demo only autumn 2026!`, learner Board Explorer, PIN684291, AI/voice off. These public test values are not suitable real credentials. This test database is excluded from the distribution archive and does not alter the normal learner profile. Stop its terminal with Ctrl+C when no longer needed.

## Remaining external work

- Live NVIDIA/Nebius inference: enter NEBIUS_API_KEY locally, run preflight, authorize a spending ceiling, then perform the gated synthetic live check. Zero paid calls were made here.
- Production: validate PostgreSQL/container deployment and backups; configure HTTPS, secure cookies, strong secrets, exact origins and trusted-proxy/host limits. Use one app worker initially. No hosting was published.
- Independent security/accessibility/educator review and an appropriately arranged student study remain pending. API tests do not certify security or prove learning gains.

The clean archive is ../tarka-v3.zip; its checksum is ../tarka-v3-package.json. It includes source, built frontend, migrations, original content, tests, reports and instructions. Credentials, databases and installed dependencies are excluded. Account/whiteboard design details and API routes are in docs/ACCOUNTS-AND-WHITEBOARD.md. The user records the demo; no video was fabricated.
