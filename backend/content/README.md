# Tarka v3 foundation curriculum

This collection contains **30 original lessons and 120 questions**, authored for this prototype. The original 18 V2 lesson objects are preserved exactly and 12 new lessons are appended. Each age band (6–8, 9–11 and 12–15) has five maths and five reading lessons. Every lesson has three practice questions followed by one different transfer question. Age bands organise foundation practice; they are not ability diagnoses, formal age-level assessments or claims of alignment with a national curriculum.

| Band | Maths | Reading |
|---|---|---|
| 6–8 | Making ten, equal groups, halves and quarters; **new:** subtraction within 20, tens and ones | Story details, sequence, actions as evidence; **new:** vocabulary in context, pronoun references |
| 9–11 | Equivalent fractions, perimeter, one-step equations; **new:** decimal addition, elapsed time | Recorded facts, causes and inference, main ideas; **new:** comparing accounts, instructions and conditions |
| 12–15 | Ratios, fraction arithmetic, two-step equations; **new:** percentages of amounts, arithmetic mean | Claims and evidence, observation versus interpretation, survey scope; **new:** figurative language, counterexamples and qualifiers |

All fifteen practice passages and all fifteen shorter reading transfer texts are original. Younger passages are short; hints invite another look or another step. Encouragement is neutral and noncompetitive. There are no rankings, ability labels or pressure to maintain a streak. A hint-supported answer should be recorded as assisted. A correct multiple-choice transfer answer is evidence for that question only, not proof of broad mastery.

## Data contract

`lessons.json` is a list. Each lesson contains:

- `id`, `title`, `subject` (`maths` or `reading`), `age_band` (`6-8`, `9-11`, `12-15`), `skill`, `summary`, `explanation`, `encouragement`.
- `worked_example`: `{prompt, explanation}`.
- `passage`: original practice text, present on reading lessons.
- `visual`: `{kind, caption, ...}`. Counters add `groups` (integer counts); fractions add `numerator` and `denominator`; number lines add `start`, `end`, `step`; reading adds `focus`.
- `questions`: four objects with `id`, `kind` (`practice` or `transfer`), `prompt`, exactly four `options`, zero-based `answer_index`, `explanation` and exactly three progressive `hints`.

Reading questions also contain `evidence`, a source quotation. **Every reading transfer’s new text is embedded in its own `prompt`, starting `Read: ...`; there is no separate question-level passage field.** The public API allowlist `{id, prompt, options, kind}` therefore contains the full new text. During practice, the lesson-level `passage` must also be shown.

Maths questions contain private `check` metadata for validation. Its operations are `add`, `subtract`, `multiply`, `fraction`, `equation`, `ratio` and `mean`. Decimal operands are strings to avoid floating-point rounding. Mean metadata contains the actual values and includes zero values when counting. The validator uses exact rational arithmetic and checks that exactly one answer option is numerically correct. These checks are developer data, not child-facing explanations or model instructions.

Do not send `answer_index`, `check`, the answer explanation or future-question answer keys in an unsolved question’s public payload. Keep answer grading in the backend. Evidence and explanations may be used as authored feedback when appropriate.

## Reproduction and verification

From the v3 project root:

```powershell
python evaluation/author_lessons.py
python evaluation/validate_curriculum.py
python -m pytest backend/tests/test_curriculum.py -q
```

`author_lessons.py` is the auditable source of this authored collection and overwrites only the v3 lesson JSON when explicitly run. Its V2 definitions remain unchanged; V3 definitions follow them. `validate_curriculum.py` performs no network calls and writes `evaluation/reports/curriculum-validation.json`.

Validation checks all 60 maths answers using separate arithmetic metadata, all 60 reading evidence quotations, fifteen self-contained reading transfers, lesson distribution, option uniqueness, hint counts, schema and correct-answer position balance. All four answer positions occur thirty times. A parity test compares the first eighteen objects with `../tarka-v2/backend/content/lessons.json` when that sibling checkout is available; it explicitly skips in a standalone V3 distribution. New skills are checked for uniqueness and separation from the retained skills.

These checks do not prove the wording is optimally age-appropriate or that reading inferences are pedagogically valid. No independent teacher review or child learning study has been completed; obtain those reviews before claiming educational efficacy. Spoken teaching reads these authored explanations, questions and available hints; it must not introduce hidden answer metadata into unsolved-question narration.
