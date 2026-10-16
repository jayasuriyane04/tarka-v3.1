# Evaluation and supervised trial protocol

**Status:** Protocol, not results. Do not create example child participants or learning gains. Use `STATUS.md` for software checks and the results template for actual observations.

## Stage 1: authored content review

Before involving children, have an educator who did not author the content review all thirty lessons across the three age bands. Review every main/transfer question, choice, answer key, explanation and hint; do not sample only the first screen.

Check mathematical correctness, reading comprehension, ambiguity, answer uniqueness, cultural assumptions and whether the vocabulary suits the intended band. Confirm that a transfer item tests the concept in a genuinely different example. Record reviewer identity/role privately and retain dated issue notes without child data.

Proposed release threshold: every authored answer key and mapping is correct; no unresolved high-severity content or accessibility issue. This threshold is a target, not a measured result.

## Stage 2: software boundaries with synthetic profiles

Use adult-owned dummy profiles and synthetic answer histories. At minimum, check:

| Area | Acceptance evidence |
|---|---|
| Curriculum | Thirty original lessons, ten per age band; valid choices, keys, hints and transfer references |
| Grading | Incorrect choices never become correct because of a client flag or model response |
| Assistance | Hints/retries/transfer narration are recorded; first-attempt independent credit cannot be recovered by reloading |
| Session pacing | Selected duration (fifteen minutes by default) and sixty-second break enforced by the server across reloads/direct calls |
| Parent gate | Wrong PIN throttled; expiry and explicit locking work; another session cannot export/delete work |
| AI default | New household opts out; opt-out prevents inference even when operator has credentials |
| Model boundary | Invalid IDs, other-question IDs, extra prose, bad JSON and timeouts safely fall back to authored content |
| Data minimization | No nickname/PIN/cookies appear in model payloads or routine logs |
| Spending | Disabled/zero/exhausted budgets prevent calls; deleting work cannot reset reservations |
| Privacy actions | Export contains only promised work; deletion removes the documented records and retains only justified accounting data |
| Browser | Actual flows verified on desktop/narrow viewport; clear labels; keyboard focus/controls inspected |

Tests using a model double establish local handling, not real NVIDIA quality or service availability. Record doubles explicitly. Real-provider tests require separate adult opt-in, credentials and approved spend.

## Stage 3: optional real hint-selection evaluation

Using reviewed, synthetic contexts, compare selected hint IDs with an educator's acceptable-hint set. Measure valid allowed-ID rate, useful hint selection, fallback rate, latency and estimated cost. A valid ID can still be a poor teaching choice; schema success is not pedagogical success.

Run invalid-output and prompt-injection tests separately. The child UI must show only approved authored text even if the provider returns hostile or irrelevant prose. Log minimal metadata; do not store secret-bearing requests.

No real model result or quality percentage should be reported until measured. AI-free authored practice remains the baseline; optional hint selection must demonstrate a benefit to justify added complexity and external processing.

## Stage 4: small, appropriately arranged child trial

An adult-led prototype trial needs suitable adult permission, the child's willing agreement and any applicable institutional/setting review before recruitment. A household PIN does not establish these. An independent educator should have completed Stage 1 first.

Start with a small supervised usability pilot. Represent all three age bands if making claims about all three; otherwise report exactly which band was observed. Avoid collecting a full birth date or unnecessary identity information. Offer AI-off participation and separate choices for any screen/audio recording.

Keep each practice session within the app's fifteen-minute window. A suggested structure is:

1. **Adult/child explanation, before practice:** describe the study, voluntary participation, data use and ability to stop.
2. **Independent baseline, 2–3 minutes:** one reviewed item and a brief explanation in the child's own words, without revealing a future transfer answer.
3. **Tarka practice, 6–8 minutes:** observe an age-appropriate lesson, recording assistance and interface confusion. An adult remains available without coaching answers.
4. **Different transfer item, 2–3 minutes:** check application of the idea without a hint; record attempts and any adult help.
5. **Short feedback, 1–2 minutes:** ask what was clear, confusing or uncomfortable and what they would change.

Take the enforced break when it appears and stop sooner if the child wants to. Participation is not an exam and should not affect grades. Avoid collecting sensitive personal disclosures; Tarka is not designed to handle them.

## Reporting

Use [STUDY-RESULTS-TEMPLATE.md](STUDY-RESULTS-TEMPLATE.md). Record participant codes, coarse band, task IDs, AI setting, assistance, baseline/transfer evidence, technical interruptions and observations. Store permission records separately with restricted access.

Report sample size, task difficulty, selection bias, adult involvement and incomplete sessions. A small pilot is useful for finding usability problems; it cannot establish that the product causes durable learning gains or is suitable for every child in an age band. Do not substitute a scripted adult demo for child-study evidence.

## V3 voice evaluation

With synthetic profiles, test parent opt-in/off, unsupported browsers, no local English voice, delayed voice enumeration, remote voice exclusion, pause/resume/stop, cancellation on navigation/question changes/breaks/hidden tabs, stale response cancellation and narration endpoint errors. Verify that only visible/authorized content is spoken and that transfer support persists after reload. Automated voice adapters are test doubles; they do not establish audio quality.

On each intended real device, have an adult listen to all lesson examples and a sample of every maths notation. Record pronunciation, pace, transcript match, truncation and control latency. Include fractions, decimals, percentages, time notation and punctuation. Mark any unclear pronunciation for correction before child use. No audio recording of children is required. Compare reading with text alone and with speech as distinct supported conditions; do not infer learning gains from software tests.
