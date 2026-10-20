# Tarka v3

**Small steps in maths and reading, with parent accounts, optional spoken teaching and maths whiteboards.** This separate prototype is for supported practice across ages 6–15. It contains thirty original lessons, ten for each broad age band: 6–8, 9–11 and 12–15. It directly copies and extends V2 in `../tarka-v2`; both V2 and the DSA application in `../tarka` remain unchanged. The original 18 lesson objects are preserved and 12 new lessons added.

An adult creates a username/password account, then sets up one learner with a nickname, age band and six-digit household PIN. Account sign-in restores saved progress on another device. The separate PIN protects parent controls within a signed-in learning space; neither the account nor the PIN verifies identity, age, guardianship or legally sufficient consent.

Children answer authored multiple-choice questions. The server grades against authored answers. They can request prepared hints, try a separate transfer question and see assistance-aware progress. A first-attempt independent result is kept separate from work completed after hints, retries, transfer narration or whiteboard support. Assistance requests are recorded conservatively before content is delivered; they are not proof that the learner listened or studied it.

## AI has a narrow role

AI starts **off** for every household. If an adult opts in, the operator has enabled paid operations, and the account/budget are ready, NVIDIA Nemotron through Nebius Token Factory can select an allowed authored hint ID. The app validates that ID and displays the original authored text. It does not display free-form model prose to the child.

Without AI access, authored lessons and deterministic grading remain available. There is no child free-text chat, uploading, web browsing or code execution. No Judge0 account is needed for v3.

These constraints reduce exposure to generated content. They do not make the prototype a perfect teacher, establish educational effectiveness or certify child-safety/privacy compliance. Original lesson content still needs independent review before use with children.

## Optional spoken teaching

Enable **Device voice** during adult setup or in the protected parent settings. Then choose an installed English voice and pace in a lesson and press a listen button. Tarka can read the lesson, current question, a hint already requested, or available feedback. Pause, resume and stop are available; playback never starts automatically. Text and a visible transcript remain available.

The first version uses the browser's Web Speech API with voices reported as local (`localService=true`). If the browser exposes no suitable local voice, the app explains that speech is unavailable and the full text journey still works. Device/browser voice quality varies; install an English speech voice through your operating system if needed. No microphone or voice recording is used.

**Device speech is not NVIDIA-generated audio.** Optional NVIDIA inference selects a permitted authored hint; a device voice may then read that text. No hosted TTS provider or voice API key is required, and narration makes no paid inference call. A parent can allow speech while leaving NVIDIA hints off.

Narration is authorized by the server and cannot read unrequested hints, unseen answer keys, or the practice example during transfer. Listening to a transfer question is recorded as support, not independent transfer. This conservative accounting does not measure whether the child actually heard or understood it.

## Run locally

For this prepared workspace, run `./START-LOCAL.ps1` from the V3 folder and open **http://127.0.0.1:8003**. Keep that terminal open. The launcher uses the built frontend and applies V3 migrations/seed data. Follow the installation steps below on a fresh machine; build the frontend with `npm run build` before using the launcher.

Install Python 3.11+ and Node.js 20.19+ or 22+. From **this v3 project directory** in PowerShell:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
Set-Location backend
..\.venv\Scripts\python.exe -m app.manage upgrade
..\.venv\Scripts\python.exe -m app.manage seed
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8003
```

In a second terminal, from this project directory:

```powershell
Set-Location frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5175`. Use that hostname consistently. V3 uses separate ports, cookies and database names from V1 and V2. Keep the versions in separate folders and do not reuse their databases. SQLite is a local preview convenience; deployment uses PostgreSQL.

## Parent controls and privacy

- Select **Create account** and choose a parent username plus a 15–128-character password. There is one learner per account. No email address is required.
- Choose a non-identifying nickname and broad age band; a birth date or school name is unnecessary.
- Keep both the account password and household PIN private. Passwords use salted scrypt verifiers; opaque session cookies are HttpOnly and are Secure in production.
- Use **Account** to change the password, sign out on this device, or sign out on all devices. Changing the password revokes other sessions.
- Turn optional AI hint selection on or off in parent controls. Declining AI does not prevent authored practice.
- Export learning records through the parent gate. For a linked account, deletion removes the account and its learner/profile history and requires the current account password as well as parent authorization. Downloaded copies and backups need separate handling.
- Sessions default to fifteen minutes of practice; a parent can choose ten or twenty minutes. The default enforced break is sixty seconds before resuming. This is a product pacing rule, not a medical recommendation.

Deleting child work does not reset the operator's budget ledger. See [the parent guide](docs/PARENT-GUIDE.md) and [privacy boundaries](docs/SAFETY-AND-PRIVACY.md) for what the prototype does and does not promise.

Authenticated sessions expire after seven days at most, or after 24 hours without a server request. Signing in again restores account records; cookie expiry does not delete progress. Existing unlinked V3 profiles retain their original 30-day access limit until claimed through **Create account** with their existing parent PIN. Claim before that cookie expires or is cleared. There is no self-service password reset, email recovery, MFA or import feature. Save the password securely; the PIN cannot reset it. The operator must still define record/session retention and backups.

## Optional maths whiteboard

Every maths lesson has an optional tutor board: **15 worked examples with 45 authored teaching steps**, including bounded diagrams and equations. Open it deliberately, move through the steps, or display a hint already requested or checked answer feedback. A private drawing space supports pen, eraser, undo and clear; drawings stay in browser memory, are not uploaded or interpreted by AI, and are not saved after leaving/reloading.

The board uses approved authored content, not new free-form model instructions. When enabled and available, NVIDIA can select the existing allowed hint that the board then displays. Opening a board makes no new model call. Earlier worked examples are unavailable during a transfer question; permitted support is recorded separately from voice requests and prevents an assisted transfer from being counted as independent. Authored text remains available without the board.

## Enable optional Nebius access

Enter credentials in the local root `.env` file, never in chat or frontend code. From `backend`, run `python -m app.manage preflight` using the project environment to check the configured model against your account's available models; this reads the catalog without generating a response. Before any paid call, obtain an explicit spending ceiling and set `ENABLE_PAID_OPERATIONS=true` and `PAID_BUDGET_USD` to that ceiling. Household AI opt-in remains a separate requirement.

See [deployment instructions](docs/DEPLOYMENT.md) for account checks, PostgreSQL, HTTPS and the release checklist. No paid calls, public deployment or child study are implied by this repository.

## Verify the prototype

From `backend`, using the activated environment:

```text
python -m pytest
```

From `frontend`:

```text
npm test
npm run build
```

Use [STATUS.md](STATUS.md) for the checks actually performed and remaining blockers, and [account and whiteboard notes](docs/ACCOUNTS-AND-WHITEBOARD.md) for the latest feature boundaries. API tests and successful builds do not substitute for browser inspection, live provider checks, educator review or a carefully arranged child study.

## Documentation

- [Parent guide](docs/PARENT-GUIDE.md)
- [Accounts and whiteboard](docs/ACCOUNTS-AND-WHITEBOARD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Safety and privacy design](docs/SAFETY-AND-PRIVACY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Evaluation and child-study protocol](docs/EVALUATION.md)
- [Study results template](docs/STUDY-RESULTS-TEMPLATE.md)
- [Dependency and license inventory](docs/DEPENDENCIES.md)
- [Demo storyboard](docs/DEMO-STORYBOARD.md)
- [Provider and voice observations](docs/PROVIDER-FEEDBACK.md)
- [Devpost draft](docs/DEVPOST-DRAFT.md)

Original v3 code and lessons use [Apache License 2.0](LICENSE). Third-party dependencies and hosted models retain their own terms. NVIDIA, Nebius and UNICEF do not endorse this prototype.
