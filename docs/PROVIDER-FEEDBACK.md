# Provider and device observations — 2026-10-16

These are implementation observations, not feedback submitted to a provider.

## NVIDIA through Nebius Token Factory

The server has a configurable model/endpoint, validates a structured hint identifier, bounds requests/retries and reserves estimated cost against the operator ceiling. The model selects authored guidance; it does not grade or speak. Mocked provider boundary tests pass.

The local preflight passed application configuration and reported missing `NEBIUS_API_KEY`. Zero inference requests were made. Account model availability, actual structured-output behavior, latency, token accounting, cost and selection quality remain unverified. Do not call these mocked results an NVIDIA benchmark. No Super comparison or model routing was added.

After the operator supplies a local key and explicitly authorizes spending, record the account-visible model, synthetic live-check result, request/response usage, time to response, selected card quality and any fallback. Keep credentials and child data out of feedback. Inspect account-specific retention and service terms before a child trial.

## Device speech

The Windows in-app browser exposed Microsoft David, Mark and Zira as local English voices. A real narration request produced a visible transcript, and browser speech events reached playing, paused, resumed and stopped states. Replaying after a paused stop was checked. This verifies software controls, not independently heard pronunciation or educational quality.

Review caught two lifecycle issues: cancelled speech could retain the engine's paused flag, and a late chunk event could undo a pause. Both were fixed with regression tests. Narrow layouts now give the voice panel its own full row. Completed feedback remains available after reload and can be narrated.

No voice recordings, microphone permissions, external TTS requests or paid voice calls are used. Browser-reported `localService` is the selection boundary; the operating system controls the installed voice implementation. Human listening tests for fractions, percentages, decimals and each target device remain pending.
