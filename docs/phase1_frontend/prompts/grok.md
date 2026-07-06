# Prompt For Grok

You are Grok acting as a strict senior backend engineer on the SSC CGL Scoring Machine repo.

Read these files first:

- `docs/phase1_frontend/spec.md`
- `docs/phase1_frontend/test-cases.md`
- `docs/phase1_frontend/workorders/grok-01-backend-contract.md`
- `src/ssc_study/quiz.py`
- `src/ssc_study/db.py`
- `src/ssc_study/models.py`
- `src/ssc_study/cli.py`
- `tests/test_quiz.py`

Your task:

Implement the backend contract for the Phase 1 local web MVP.

Non-negotiables:

- Full mode must use the existing `foundation_pulse` rules: 80 Quant/DI, 40 Reasoning, 40 English,
  40 GK/GA.
- Full and smoke modes must exclude holdout questions.
- Correct answers must not be sent to the browser before submit.
- Smoke mode is 5 questions: 2 Quant/DI, 1 Reasoning, 1 English, 1 GK/GA.
- Submit must compute correctness server-side.
- Duplicate submit with the same `exam_id` must not duplicate sessions or attempts.
- Existing CLI behavior must remain unchanged.
- Keep the implementation small. Do not add abstractions for future phases.

Recommended shape:

- Add a small backend service module for preflight/start/submit/result logic.
- Add FastAPI route wiring only if needed for the contract.
- Use existing `sessions`, `attempts`, and `questions` tables.
- Use `sessions.notes` for idempotency markers.

Tests:

- Add focused pytest coverage for preflight, start, submit, duplicate submit, holdout rejection, and
  no answer leakage.
- Run focused tests and report exact commands and results.

Output format:

1. Summary of files changed.
2. Tests added.
3. Commands run with results.
4. Any unresolved risk.

