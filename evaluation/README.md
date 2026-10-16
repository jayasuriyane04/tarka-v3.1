# Reproduce the checks

Run these using the environment installed from `backend/requirements.lock.txt`:

```text
cd backend
python -m pytest -q --junitxml=../evaluation/reports/backend-tests.xml
cd ..
python evaluation/validate_curriculum.py
python evaluation/verify_v2_baseline.py
cd frontend
npm ci
npm test -- --reporter=json --outputFile=../evaluation/reports/frontend-tests.json
npm run build
```

The backend suite runs real application handlers against isolated test databases with synthetic profiles. Provider HTTP responses are mocked. Each of the 30 lessons is exercised through wrong answer, hint, revision and different transfer; separate tests distinguish assisted/revised from first-try unassisted transfer.

Curriculum validation checks exact-arithmetic metadata, valid/unique choices, reading evidence quotations, transfer passage availability and distribution. It does not prove vocabulary suitability or semantic correctness of every reading explanation. Tests using authored answer metadata are not an independent pedagogical assessment.

Frontend tests verify renderer output and API-client boundaries. They do not drive a real browser or validate screen-reader behavior. Record browser observations separately following `HANDOVER.md` and `docs/EVALUATION.md`.

Reports are dated software observations, not NVIDIA quality benchmarks. Live model selection usefulness, latency, invoice cost, educator review and child learning outcomes are unmeasured. A real comparison should score selected cards against independently reviewed acceptable-card sets; keep those evaluation labels outside runtime model messages. Use `app.manage preflight` and the budget-gated synthetic `live-check` only under the documented account/spending conditions.

V3 adds narration authorization/migration/assistance tests and speech-controller tests with a fake browser adapter. These do not measure real audible voice quality. V2-BASELINE.json records copied source hashes; verify V2 remains unchanged when packaging.
