# V3 browser observations — 2026-10-16

Environment: Windows Codex in-app browser, built frontend and FastAPI at `http://127.0.0.1:8003`. The user started the normal PowerShell launcher. Synthetic adult-operated profile; no child participants or paid model calls.

| Scenario | Observed result |
|---|---|
| Setup | Age 6–8, device narration on, NVIDIA hints off; ten lesson cards displayed |
| New subtraction lesson | Wrong 11−4 answer received retry feedback; first hint delivered; revised answer received correct explanation |
| Transfer | Different seat-counting question; read-aloud requested before answer; correct answer labelled supported |
| Reload | Profile, completed lesson, explanation, consent and assistance evidence persisted |
| Voice | Local David, Mark and Zira enumerated; explicit Play produced transcript and started speech events; Pause/Resume/Stop worked; replay after paused Stop worked |
| Permission | Parent gate required PIN; turning voice off removed playback controls; turning it back on restored them |
| Parent record | Subtraction showed 5 attempts / 1 hint / 3 read-aloud requests and supported evidence |
| Export | Browser download completed; synthetic exported lesson had completed=true, transfer_independent=false and narration records for two questions |
| Reading | New vocabulary lesson used a fresh self-contained transfer passage, with the original story hidden; first correct unassisted transfer labelled independent |
| Older age band | Parent switched to ages 12–15; ten appropriate lesson cards appeared; new percentage lesson opened |
| Illustration | Percentage lesson showed one of four equal parts; Show/Hide labels displayed 1/4 |
| Voice choice | Zira and Gentle pace selected; speech entered playing/paused state with authored transcript |
| Break | Due break blocked learning; quiet-minute flow led to Ready to return, then lesson access resumed |
| Layout | Desktop and narrow layouts inspected; checked content widths matched viewport widths (1265 and 375 CSS pixels), without horizontal overflow |

Review fixes applied before the final checks: completed feedback restored from saved data; cancelled paused engine reset; late chunk events cannot undo Pause; voice card spans the narrow layout. Automated regression tests cover these logic fixes.

The listener stopped during one break check, producing a visible fetch error. User restart and reload restored the saved state; the break flow then passed. The cause of the stopped process was not established. The launcher must remain open.

Screenshots: `browser-independent-transfer.jpg`, `browser-voice-desktop.jpg`, `browser-voice-mobile.jpg`.

Limits: speech start/pause/resume events and UI state were observed, but no independent listening score is claimed. No real model call, mobile hardware, screen-reader audit, production database, deployment or educational outcome was verified. Unsupported/no-local-voice states are tested with doubles. Profile deletion is covered by API tests; no browser deletion was performed.
