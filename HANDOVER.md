# Tarka V3 handover

V3 directly copies V2 and preserves its learning/parent/provider features. It adds parent-controlled spoken teaching and twelve lessons, for thirty lessons and 120 questions across ages 6–15. V1 and V2 are unchanged. See STATUS.md for the final measured verification and remaining blockers.

Verified locally: **181 backend tests, 39 frontend tests, curriculum checks and production build pass**. Two complete new lessons were exercised in the browser: narrated maths transfer correctly recorded support; unassisted reading transfer recorded independent evidence. Reload persistence, parent controls/export, speech controls, older-age content, illustration labels and enforced breaks were checked. Screenshots and the detailed browser record are in `evaluation/reports`.

The existing browser test profile is **Demo Learner**, ages 12–15, with test PIN **482617**, voice on and AI off. These are synthetic local test values, not an account for a child. The clean archive excludes this profile and its database. `tarka-v3.zip` and `tarka-v3-package.json` are in the parent output folder.

## Start the application

From this `tarka-v3` folder in PowerShell run `./START-LOCAL.ps1`, then open **http://127.0.0.1:8003**. The launcher applies migrations and seeds the V3 database, then serves the built frontend. Keep the terminal open. It uses a project `.venv`, or the existing workspace `work/tarka-venv`. A fresh machine needs the dependency setup in README.md first.

## Review the new experience

Create an adult-owned dummy profile, enable device voice and leave optional NVIDIA hints off. Open a lesson, choose an installed English voice and pace, listen to the lesson, pause/resume/stop, then try a question and a delivered hint. The text remains available. If the browser exposes no local English voice, the app reports this and text practice still works.

Complete the practice items, listen to the different transfer question and answer correctly. The result must be supported, survive reload and appear with narration requests in the parent export. On another lesson, complete the transfer first try without hints/narration and confirm independent evidence. Test parent lock/settings, break controls and a reading transfer with its own passage.

## Accounts and remaining release work

Device voice needs no paid API or microphone. It is not NVIDIA-generated audio. Optional NVIDIA/Nebius hint selection still requires a server-side NEBIUS_API_KEY, an account-visible configured model, parent opt-in and an explicitly authorized spending ceiling. Preflight reads the catalog; live-check is separately gated and must use synthetic data. No paid calls have been authorized in this work.

PostgreSQL/Docker and public hosting require the environments described in docs/DEPLOYMENT.md. No site is published automatically. Record real audio quality, provider tests and deployment checks separately from automated test doubles. Educator review and supervised student testing remain pending; no learning gains or child participants are invented.

## Retained prototype limits

One learner per browser; 30-day session access without recovery; expired records need operator retention/deletion; parent PIN is not identity/consent verification; no complete school curriculum, open chat or microphone conversation. First-try transfer evidence is narrow and cannot prove mastery or absence of outside help.

The user records the video using docs/DEMO-STORYBOARD.md. V3 preserves original content, but this revised scope's hackathon eligibility must be rechecked before submission.
