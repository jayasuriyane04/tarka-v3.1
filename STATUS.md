# Tarka V3 status — 2026-10-21

## Accounts and whiteboard extension

Implemented and browser-verified in the separate V3 folder. V1/V2 work is preserved. Parent username/password accounts now own learner records; Create account, Sign in, sign-out, all-device sign-out and password change are wired to backend routes. Salted scrypt, opaque revocable sessions, CSRF/origin protections, per-session parent capabilities, durable login/PIN attempt limits and credential-safe validation are included. Legacy V3 progress can be linked with its existing PIN. Migration0003 is additive.

All fifteen maths lessons now offer optional whiteboards with45 authored steps, validated counters/fractions/number-lines/rectangles, manual step navigation and private drawing/typing. The board can show delivered NVIDIA-selected authored hints when configured; it does not generate unrestricted lessons or make a new paid call. Transfer blocks old examples. Separate board counts and shared assistance flags keep supported work distinct from independent transfer.

## Final extension verification

| Check | Measured result |
|---|---|
| Backend final source | **247 passed** across98 authentication/API tests and149 remaining regression/content/migration/provider/whiteboard tests; zero failures |
| Frontend | **59 passed** across7 files |
| TypeScript / production build | Passed;39 modules |
| Preservation | V2's58 source hashes unchanged; all18 original lesson objects retained |
| SQLite migration / PostgreSQL SQL | Migration/legacy preservation tests and PostgreSQL SQL compilation pass; live PostgreSQL unverified |
| Actual browser | Signup→setup→maths board→attempts→hint board→supported transfer→reload→sign-out→wrong-password rejection→sign-in→saved parent progress passed |
| Layout | Desktop and375px content width checked; no horizontal overflow in inspected board/account views |
| Paid integrations | Zero live inference calls; missing key and authorized ceiling remain external blockers |

Reports: [verification record](evaluation/reports/accounts-whiteboard-verification.json), [browser evidence](evaluation/reports/accounts-whiteboard-browser.md), and dated test XML/screenshots in the same directory. The earlier244-test run passed too; final split runs cover the latest247 collected tests after the throttle/revocation fixes. One existing Starlette/HTTPX deprecation warning remains; it did not fail tests.

## Start and remaining steps

Restart `./START-LOCAL.ps1` in the V3 folder to apply migration0003 and load the built update at http://127.0.0.1:8003. Existing unlinked learners choose Create account and their existing PIN to keep progress. The verification app at http://localhost:8004 uses a separate synthetic database, not the usual V3 learner records. See [HANDOVER.md](HANDOVER.md).

No email password recovery, MFA or identity verification is implemented. Public operation still needs tested PostgreSQL/container/HTTPS hosting, secret configuration, retention/backups and independent review. Live Nebius requires a server-side key, account model check, parent opt-in and an explicitly authorized spending ceiling. No public deployment, real-child trial or educational/security certification is claimed.

## Previous voice release — historical 2026-10-16 evidence

The V3 local application is implemented and browser-verified. It is a separate copy of V2, with optional device narration and twelve additional lessons. V2 remains unchanged: all 58 source hashes match the baseline, and the original 18 lesson objects are exactly preserved.

## Completed

- Thirty maths/reading lessons and 120 questions, with ten lessons per age band (6–8, 9–11, 12–15). Each has a worked example, three practice questions, three progressive hints per question, and a different transfer question.
- Retained V2 setup, parent PIN, age filtering, deterministic checks, hints/revisions, transfer evidence, persistence, export/deletion, enforced breaks, constrained optional NVIDIA hint selection and spending controls.
- Added a separate parent voice opt-in, local English voice/pace selection, explicit play/pause/resume/stop, visible transcripts and unavailable/error fallbacks. No microphone or hosted TTS.
- Added server-authorized narration, persisted narration requests, assistance-aware transfer scoring and migration 0002. Transfer narration counts as support even if playback later fails.
- Isolated V3 database/cookie/ports (8003 built app; 5175 development), sample configuration, deployment files and documentation.
- Fixed completed feedback disappearing after reload, replay after paused Stop, pause handling at chunk boundaries and cramped narrow-screen voice layout.

## Measured verification

| Check | Result |
|---|---|
| Backend | **181 passed**, 19.36 s; one Starlette TestClient/HTTPX deprecation warning |
| Frontend | **39 passed**, including voice lifecycle, rendering and API-client boundaries |
| TypeScript / production build | Passed; Vite built 34 modules |
| Curriculum validator | 30 lessons / 120 questions; 60 exact-arithmetic key checks and 60 reading evidence-source checks; 15 self-contained reading transfers |
| Original preservation | 58/58 source hashes unchanged; original 18 lesson objects preserved; 12 additions |
| Migrations | Local SQLite upgrade/seed passed; upgrade from original schema with existing progress tested; PostgreSQL SQL compilation tested |
| Actual browser | Windows in-app browser at `http://127.0.0.1:8003`; synthetic adult-operated profile only |
| Live provider preflight | Configuration passed; model access blocked by missing `NEBIUS_API_KEY`; **zero inference calls** |

Browser checks completed: setup with voice on/AI off; new subtraction lesson through wrong answer, hint, revision and narrated transfer; supported evidence and explanation retained after reload; independent new vocabulary transfer with a different passage; parent PIN/lock, consent revocation and re-enabling, data export; 12–15 collection and percentage illustration labels; mandatory break and return; local voice/pace choice, play/pause/resume/stop and transcript. Export recorded the narrated transfer as assisted. Device voices enumerated as Microsoft David, Mark and Zira. Desktop and narrow (375 CSS-pixel content width) layouts were inspected; no horizontal overflow in the checked views.

The server initially could not be reached when launched inside the sandbox. The user's normal PowerShell launch resolved this. Later the listener stopped; the app showed a fetch error, and restart/reload restored the persisted profile and break state. No database reset was needed. Keep the launcher terminal open.

Reports and screenshots are in `evaluation/reports`. These are synthetic software checks, not a child study. Browser speech state/events were observed; audible pronunciation, comprehension and educational effectiveness have not been independently assessed. Unsupported speech scenarios and security boundaries are covered by automated tests, not every physical browser/device.

## Remaining external checks

1. Set `NEBIUS_API_KEY` in the V3 root `.env`, run the read-only preflight against the account catalog, and explicitly authorize a spending ceiling before `live-check`. Live quality/latency/cost, Super comparison and model routing remain unmeasured/unimplemented.
2. Install/use Docker and PostgreSQL to validate the provided deployment recipe, then supply hosting access and a publishing destination. No public deployment was made.
3. Conduct human listening and accessibility checks, independent educator review and any appropriately arranged supervised student trial. No participants, learning gains or compliance certification are claimed.
4. Recheck the revised V3 scope against current hackathon requirements before submitting. The user records the video from the supplied storyboard.

## Resume / handover

Run `./START-LOCAL.ps1` from this folder and keep it open. See `HANDOVER.md`. The browser has a **synthetic Demo Learner** profile, currently ages 12–15, voice enabled and AI disabled. Its local test PIN is `482617`; it is not a production credential. The test profile/database and downloaded export are excluded from the distribution archive.

Clean package: `../tarka-v3.zip`; checksum/inventory: `../tarka-v3-package.json`. Source, locked dependencies, built frontend, original content, tests/reports, screenshots and deployment instructions are included; installed packages, local credentials and databases are excluded.
