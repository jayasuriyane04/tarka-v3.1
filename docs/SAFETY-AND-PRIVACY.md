# Safety and privacy design record

**Status:** Prototype design and release checklist. This document is not certification, legal advice or evidence that every check below has passed. Record observed checks in [STATUS.md](../STATUS.md) and a dated release record. See [accounts and whiteboard details](ACCOUNTS-AND-WHITEBOARD.md) for the latest feature boundaries.

UNICEF's *Guidance on AI and children, version 3.0* emphasizes children's safety, data protection, fairness, transparency, accountability, development and meaningful inclusion. Tarka uses those principles as design prompts; UNICEF has not reviewed or endorsed Tarka. The mapping below is our implementation approach, not a UNICEF compliance assessment. [Official guidance](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children)

## Design choices and residual limits

| Goal | Concrete prototype control | What remains to establish |
|---|---|---|
| Limit generated-content exposure | AI selects a current-question hint ID; only authored text is shown | Independent review of every authored hint and tests for invalid/extra model output |
| Keep humans responsible | Adult setup and parent controls; no perfect-teacher or companion claims | Appropriate adult permission and supervision for the actual setting |
| Minimize child data | Nickname and coarse age band; no birth date, school, photos or open chat | Inspect requests/logs and verify deployment/provider retention |
| Make choices understandable | Optional AI starts off; explain its limited role; authored practice works without AI | Check that children and adults understand the labels |
| Support manageable practice | Server-enforced break and ability to stop earlier | Observe usability and avoid presenting timing as health advice |
| Avoid overstating learning | Track assistance and independent transfer evidence separately | Educator review and appropriately designed exploratory testing |
| Provide practical control | Parent-gated export and deletion of documented child work | Verify ownership, completeness, backup handling and retained usage metadata |
| Consider inclusion | Three age bands and plain prepared tasks | Review reading demands, disability access, cultural assumptions and differences within each band |

## Intended data inventory

Confirm the exact fields against the implemented database and endpoints before releasing a trial.

| Data | Why it exists | Disclosure/control requirement |
|---|---|---|
| Nickname and age band | Label the learner and choose authored content | Use a non-identifying nickname; do not infer full identity |
| Parent username and salted password verifier | Authenticate the parent account and restore its one learner across devices | No email required; never store/export plaintext passwords or send credentials to a model |
| Opaque household/session identifiers | Keep each account or unlinked profile's work separate | HttpOnly cookies, Secure in production; ownership and revocation checked server-side |
| PIN verification data | Gate parent actions locally | Store only a suitable salted verifier, never plaintext; never send to a model |
| Selected answers, attempts and assistance | Grade and represent progress honestly | Parent export/delete should cover the documented work |
| Narration and whiteboard request metadata | Distinguish requested support from independent transfer | Separate voice/board counts; neither proves the learner listened or understood |
| Drawing strokes | Optional scratch space beside the maths explanation | Browser memory only; not transmitted, saved, graded or sent to a model |
| Session/break timestamps | Enforce pacing across reloads | Do not trust a child-supplied clock or elapsed duration |
| AI opt-in | Record the household's optional-inference choice | Setup also requires adult self-attestation, but this is not verified identity or legal consent |
| Provider usage and reserved budget | Bound spending and audit operations | Deletion cannot reset the budget; remove unnecessary child links |
| Infrastructure logs and backups | Operate and recover the service | Operator must define access and retention; not covered automatically by UI deletion |

## Provider boundary

With AI off, lesson practice and hints require no model request. With it on, disclose that structured learning context can be processed by Nebius. Keep a machine-tested allowlist of transmitted fields. Do not send account usernames/passwords, the nickname, household PIN, cookies, drawings, exact age/birth date or unrestricted history.

The model is a selector, not a source of new child-facing prose. Reject a hint ID that is missing, wrong-typed, outside the current question or accompanied by disallowed fields. Rendering should use the authored local text after validation; silently displaying a model explanation defeats this boundary.

Turning AI off prevents subsequent eligible requests; it does not undo previous processing. Check the applicable model/service terms, data-handling options and retention before a trial. Do not claim data remains entirely on-device or that providers retain nothing without evidence.

## Parent gate

Parent sign-in uses a username and password of 15–128 characters. Passwords have random salts and scrypt verifiers; raw passwords are not persisted. Opaque session tokens are stored server-side as keyed hashes and sent in HttpOnly, SameSite cookies, with Secure required in production. State changes require session-bound CSRF protection and permitted origins. Authentication attempts use durable rate-limit reservations. Account creation/login rotate the session; password change revokes other sessions and replaces the current one. Sign-out and sign-out everywhere revoke the applicable sessions.

Authenticated access lasts at most seven days, with a 24-hour idle limit measured from server requests. Expiry requires sign-in again but does not remove the account's saved records. There is one learner per account. No email verification, self-service password reset, MFA, verified parental identity or account recovery guarantee is implemented.

The separate six-digit PIN is a household convenience gate within that signed-in session. It has a salted verifier, attempt throttling, short-lived parent authorization, ownership checks and CSRF protections. It is not stored in browser local storage or returned from an export. A child can still obtain an adult's PIN or use an unlocked parent session; the adult can explicitly lock parent controls. The PIN cannot reset the account password. Use the documented single application worker until progression/parent-gate concurrency protections are reviewed for multiple workers.

An acknowledgement checkbox is self-attestation. It is not age verification, guardianship verification or a legal-consent mechanism. Before any public or school deployment, the operator must determine the permissions, safeguards, notices and review appropriate to that deployment. This prototype makes no COPPA, GDPR, DPDP or other regulatory compliance claim.

## Delete and export semantics

Linked account records return after sign-in even if the session expires or its cookie is cleared. Existing unlinked V3 profiles retain their original 30-day cookie lifetime until an adult claims them through registration with the existing parent PIN. After that old cookie expires or is lost, no self-service claim/import route exists. Expiry does **not** delete database rows. Operators must define retention and deletion of inaccessible legacy records, expired sessions and backups; no automatic cleanup or permanent record storage is promised.

For a linked account, the parent-gated delete action requires the current account password and explicit confirmation, then removes the account, its sessions, learner profile, learning records and family-linked usage rows. An unlinked profile requires its parent authorization and confirmation. Export contains documented profile/learning data, not password/PIN verifiers or authentication secrets. Private drawings are never part of the server record and are not included in export.

- Specify which profile, responses, hint/assistance records and progress are included in export and deletion.
- Verify parent authorization and household ownership for both actions.
- Never export the PIN verifier, API keys, session/CSRF tokens or another household's data.
- Preserve aggregate spending reservations so deletion cannot authorize additional spend.
- Remove unnecessary child identifiers from retained operational records; document any retained metadata.
- Explain that backups, downloaded exports, provider records and web-server logs require separate handling.
- Set a retention period and deletion process before collecting real trial data; no automatic expiry should be assumed unless implemented and tested.

## Release checks

- [ ] Independent educator reviews all thirty lessons, answer keys, hints and transfer items.
- [ ] AI-off requests make no inference call, including attempts to call hint endpoints directly.
- [ ] Invalid model outputs cannot reach the child as prose or select another question's content.
- [ ] Answers and progress come from server-owned keys and attempt history.
- [ ] Hint/retry assistance cannot be bypassed to claim first-attempt independence.
- [ ] Parent PIN is hashed, throttled, never exported and never included in provider requests.
- [ ] Account password verifiers and opaque session tokens are protected; failed login messages do not disclose password validity or secret request fields.
- [ ] Login, password change, logout and logout-all have the documented session rotation/revocation behavior.
- [ ] Legacy PIN claim preserves progress and invalidates the old bearer cookie.
- [ ] Parent authorization expires; sensitive actions check ownership and CSRF.
- [ ] Session and break rules persist across reloads and direct API calls.
- [ ] Export/delete behavior matches the explanation shown to adults.
- [ ] Budget reservations survive deleting child work.
- [ ] Keyboard, screen-reader and age-appropriate readability checks are recorded.
- [ ] No analytics/advertising or third-party content has been introduced without a new review.
- [ ] Real provider access, deployment settings and logs are reviewed before an AI-enabled trial.

Software tests can verify specific boundaries. They cannot establish that a child-facing product is perfectly safe or pedagogically effective.

## V3 voice boundary

Speech is off until a parent enables it. The server returns only allowed authored segments, after ownership, CSRF, age-band, question-state and break checks. There is no free-text narration endpoint and no microphone recording. The browser restricts playback to English voices marked localService and does not offer remote voices. Operating-system voice implementation and pronunciation still require review on the actual deployment devices.

The database records narration segment requests and their assistance status per question, not an audio file or a claim that the child listened. These records are included in parent export and removed with the learning record. Narration of a transfer prompt counts as support and cannot be cleared by reloading or toggling the parent setting. No extra paid service is called by narration.

- [ ] Check local voice availability, pronunciation, pause/stop and transcript accuracy on each supported browser/device.
- [ ] Verify speech never starts automatically or continues after navigation, a break or a parent lock/settings change.
- [ ] Verify narrated transfer questions remain marked supported after reload and export.

## Maths whiteboard boundary

The fifteen maths worked examples contain forty-five authored teaching steps. `POST /api/whiteboard` accepts a lesson ID and an allowed segment, not arbitrary text, markup, coordinates or model-generated board instructions. The server validates ownership, age band, question state and break rules before returning bounded steps/diagrams. Worked examples are unavailable during transfer; hint boards require an already-delivered hint, and feedback boards require a checked answer.

Optional NVIDIA hint selection can supply the approved hint already recorded by the existing hint flow. Opening the board makes no additional inference call and never introduces new free-form model text. The backend records board assistance before returning content, using a separate count from narration and a shared assistance flag for transfer scoring. This records requested support, not attention or educational benefit. Private drawing strokes stay in browser memory and have no server submission/interpretation endpoint.

- [ ] Educator review covers all authored board steps, diagram labels and arithmetic.
- [ ] Transfer restrictions and assistance survive direct API calls, reload and switching between voice and board.
- [ ] Drawing remains local and is bounded; keyboard users can read and navigate the teaching steps without drawing.
- [ ] Stale board responses cannot appear for another learner, question or session.
