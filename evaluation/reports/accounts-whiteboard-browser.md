# Account and whiteboard browser verification

Release record: 2026-10-21. Adult-operated synthetic software checks only; no children, learner study or learning-gain claim.

The verification server used `work/tarka-accounts-browser.db` at http://localhost:8004, separate from the usual http://127.0.0.1:8003 V3 profile and cookie host. Sandbox launches were initially unreachable and one stopped listener returned connection refused. The user-started verification server was reachable and supported the checks below. Keep its terminal open. No paid model call was made.

## Observed complete journey

- Header Create account changed the sign-in form to registration. Created the synthetic parent `qa_parent_1020_01`; setup created learner `Board Explorer`, ages 6–8, AI and voice off.
- Opened Make ten, then add. The optional board initially remained closed. Teach on the board returned three authored steps: 8+5, regroup into 10+3, total13. Next/Replay worked; counter quantities matched labels.
- Typed a private working note, drew a pointer stroke and used Undo. Changing from explanation to practice closed the board and cleared local working state.
- Checked the three practice answers, advanced to the different bead transfer. Its board offered only a scratchpad initially: earlier example absent and Teach disabled.
- Submitted wrong transfer answer12, received retry feedback, opened hint1, and displayed that delivered hint on the board. It showed “This story joins two groups” with authored-content attribution. No solution explanation appeared before the correct answer.
- Revised to14. Completed as Supported practice recorded. Reload returned the saved dashboard.
- Opened Account and signed out. Wrong password produced the generic username/password mismatch message. Correct sign-in restored Board Explorer and completed lesson.
- Parent PIN gate opened the saved overview: 1 lesson, 0 independent transfers, 4 questions, and row `5 / 1 / 0 / 2` (tries/hints/voice/board). Read-only synthetic database inspection confirmed completion=true, transfer_independent=false, two board requests and zero voice requests. No scratchpad text was present in the per-question stored support data.
- Count equal groups displayed the 0,2,4,6 number line and equal-group steps. Desktop and390px viewport setting (375px content) were inspected. Whiteboard/account controls fit without horizontal overflow. Browser error log was empty at the final check.

Checkbox automation once failed to set the setup acknowledgement via click; keyboard Space checked it and the journey continued. Two short browser-locator waits ended before password hashing completed; subsequent DOM inspection showed the expected error/success. These were automation timing observations, not fabricated failures or unexplained skipped tests.

## Evidence

- accounts-whiteboard-desktop.jpg: full desktop teaching view.
- accounts-whiteboard-mobile.jpg: narrow teaching view.
- accounts-mobile.jpg: narrow account controls.
- accounts-whiteboard-verification.json: aggregate evidence and remaining limits.

Password change, all-device revocation, cross-household denial, legacy PIN-claim migration, CSRF/origin, session expiry and deletion were checked by automated API tests. They were not all repeated in the browser. Existing legacy user profile was not claimed or deleted during these checks. No password-recovery or MFA service is implemented; live provider and production deployment remain unverified.
