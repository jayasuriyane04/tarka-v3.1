# Tarka Family v3 — Devpost draft

**Draft only; not submitted.** This child-focused V3 directly copies V2, adds voice teaching and twelve lessons, and lives separately from the unchanged Tarka DSA v1 project. Hackathon eligibility, current track requirements and submission rules have not been rechecked for v3. Confirm them before choosing a submission category or publishing this text.

## One-line description

A parent-guided maths and reading practice prototype that records help honestly and gives optional AI a tightly limited teaching role.

## Inspiration

At-home practice should help a learner think through an idea and give caregivers a useful picture of the help involved. Tarka Family explores that experience through small, prepared lessons, gentle retry feedback and a different question that tests transfer of the idea.

## What it does

Tarka Family contains thirty original lessons and one hundred and twenty multiple-choice questions: five maths lessons and five reading lessons for each of the 6–8, 9–11 and 12–15 age bands. Each lesson includes a worked example, a concept illustration, three practice questions, progressive authored hints and a separate transfer question.

The server grades answers against authored keys and saves attempts and requested help. Supported completion stays separate from a first-attempt transfer answer with no recorded hint or read-aloud support. This is a narrow practice indicator, not a mastery score or evidence that no outside help occurred.

A caregiver chooses a nickname, broad age band and session duration. A six-digit household PIN gates settings, progress, export and deletion. Sessions include server-enforced breaks. The prototype has no open child chat, file uploads, advertisements or public rankings. The PIN is a convenience gate, not adult identity verification or a legal-consent system.

## How we built it

V3 reuses the core project's React/TypeScript frontend approach, FastAPI backend, validated request schemas, session ownership controls, migrations and budgeted provider boundary. PostgreSQL is the deployment target; SQLite supports local preview. V3 has its own folder, configuration, database and cookie namespace. It does not use v1's code editor or code-execution service.

The optional provider integration targets NVIDIA Nemotron through Nebius Token Factory. Its configured starting model is `nvidia/Nemotron-3_5-Lightning`; account availability and live behavior still require verification. A caregiver must opt in, and the operator must separately configure credentials and an authorized spending ceiling.

The model receives limited structured lesson context and selects an allowed authored hint ID. The server validates the response and renders the corresponding prepared card. Unrestricted model prose never becomes the child's teaching text. Invalid responses or provider failures use a labelled authored fallback. The model cannot grade answers, bypass a break or award learning progress.

## What we learned while building

Correctness, feedback and evidence of learning need different controls. A schema can constrain a model response without proving that the selected hint is pedagogically useful. Likewise, completing a question after hints should not become a claim of independent understanding. These distinctions shaped the server-owned learning loop and the parent view.

## Verification and current limits

Use STATUS.md and evaluation/reports for dated V3 software results. V2 results do not establish V3 verification. Provider tests use doubles; device speech tests may use a fake speech adapter. Audible quality, live NVIDIA inference and production deployment must each be measured separately. No child study or educational effectiveness is claimed.

The browser household has a fixed 30-day session lifetime without account recovery; expiry does not delete stored records. Independent curriculum/accessibility review, appropriate permissions for any child trial and a deployment-specific retention process remain necessary.

## Next steps

The local browser journey has been checked with synthetic data; see STATUS.md for its limits. Next verify the account-visible model and a budgeted synthetic inference run; test PostgreSQL deployment; independently review every lesson; then conduct an appropriately arranged supervised usability pilot using the prepared protocol. Measure hint usefulness, failure rate, latency and cost before claiming the optional model improves the experience.

## Attribution

NVIDIA supplies the model family targeted by the optional inference integration; Nebius Token Factory is the intended hosted inference service. Live use must be demonstrated before presenting that integration as verified. Tarka's original code and lesson content use Apache License 2.0; dependencies and hosted models retain their own terms. NVIDIA and Nebius do not endorse Tarka.

**Before publishing:** recheck hackathon rules, replace pending verification statements only with actual evidence, add the real repository/deployment/video links, and distinguish this v3 scope from any v1 submission.

## Spoken teaching and attribution

A separate parent opt-in enables explicit read-aloud actions. The server authorizes lesson/question/hint/feedback segments and records assistance; the browser speaks them with an installed English voice reported as local. Pause, resume, stop and visible text keep the learner in control. Narrated transfers are marked supported. Device speech is not NVIDIA-generated audio, and no hosted TTS service is claimed. NVIDIA's role remains optional hint selection through Nebius Token Factory.
