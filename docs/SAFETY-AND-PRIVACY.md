# Safety and privacy design record

**Status:** Prototype design and release checklist. This document is not certification, legal advice or evidence that every check below has passed. Record observed checks in `STATUS.md` and a dated release record.

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
| Opaque household/session identifiers | Keep one browser household's work separate | Cookies must be protected; session ownership checked server-side |
| PIN verification data | Gate parent actions locally | Store only a suitable salted verifier, never plaintext; never send to a model |
| Selected answers, attempts and assistance | Grade and represent progress honestly | Parent export/delete should cover the documented work |
| Session/break timestamps | Enforce pacing across reloads | Do not trust a child-supplied clock or elapsed duration |
| AI opt-in | Record the household's optional-inference choice | Setup also requires adult self-attestation, but this is not verified identity or legal consent |
| Provider usage and reserved budget | Bound spending and audit operations | Deletion cannot reset the budget; remove unnecessary child links |
| Infrastructure logs and backups | Operate and recover the service | Operator must define access and retention; not covered automatically by UI deletion |

## Provider boundary

With AI off, lesson practice and hints should require no model request. With it on, disclose that structured learning context can be processed by Nebius. Keep a machine-tested allowlist of transmitted fields. Do not send the nickname, household PIN, cookies, exact age/birth date or unrestricted history.

The model is a selector, not a source of new child-facing prose. Reject a hint ID that is missing, wrong-typed, outside the current question or accompanied by disallowed fields. Rendering should use the authored local text after validation; silently displaying a model explanation defeats this boundary.

Turning AI off prevents subsequent eligible requests; it does not undo previous processing. Check the applicable model/service terms, data-handling options and retention before a trial. Do not claim data remains entirely on-device or that providers retain nothing without evidence.

## Parent gate

The six-digit PIN is a local household convenience. It must have a salted verifier, attempt throttling, short-lived parent authorization, ownership checks and CSRF protections. Never store it in browser local storage or return it from an export. A child can still obtain an adult's PIN or use an unlocked parent session; the interface should allow the adult to close that session explicitly.

An acknowledgement checkbox is self-attestation. It is not age verification, guardianship verification or a legal-consent mechanism. Before any public or school deployment, the operator must determine the permissions, safeguards, notices and review appropriate to that deployment. This prototype makes no COPPA, GDPR, DPDP or other regulatory compliance claim.

## Delete and export semantics

Current session limit: access expires 30 days after session creation and cannot be recovered after expiry or cookie loss. Expiry does **not** automatically delete the old database rows. In-app export/deletion then becomes unavailable for that old session. Resolve this account/retention limitation or establish a specific operator-managed process before collecting real child data. No automatic cleanup or permanent record storage is promised.

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
