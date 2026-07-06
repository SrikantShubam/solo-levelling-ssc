# Work Order: Grok 01 Backend Contract

## Objective

Create the backend contract for the Phase 1 local web MVP without changing the existing CLI behavior.

## Scope

Implement or propose the smallest backend layer needed for:

- Preflight readiness.
- Smoke exam start.
- Full baseline start.
- Exam submit.
- Result lookup.

## Files to inspect first

- `src/ssc_study/quiz.py`
- `src/ssc_study/db.py`
- `src/ssc_study/models.py`
- `src/ssc_study/cli.py`
- `tests/test_quiz.py`
- `tests/conftest.py`

## Required behavior

- Full mode must reuse the existing `foundation_pulse` requirements.
- Full mode must return exactly 200 questions.
- Smoke mode must return exactly 5 questions: 2 Quant/DI, 1 Reasoning, 1 English, 1 GK/GA.
- No route may expose `correct_option_label` before submit.
- All served and submitted questions must be non-holdout.
- Submit must compute correctness server-side.
- Submit must persist attempts only once per `exam_id`.
- Smoke mode must not be recorded as a real `foundation_pulse` session.
- Existing CLI quiz behavior must remain unchanged.

## Recommended implementation shape

Prefer a small new backend module rather than putting business logic directly into route handlers.

Suggested functions:

```text
get_baseline_preflight(db) -> dict
start_baseline_exam(db, mode) -> dict
submit_baseline_exam(db, payload) -> dict
get_baseline_result(db, session_id) -> dict
```

Route handlers should call these functions and translate domain errors into HTTP responses.

## Persistence rules

- Full mode session type: `foundation_pulse`.
- Smoke mode session type: `analysis`.
- Use `sessions.notes` to store an idempotency marker:
  - `phase1_web_full:<exam_id>`
  - `phase1_web_smoke:<exam_id>`
- On duplicate submit, return the existing result for that marker.
- Do not add a new table for v1 unless impossible to avoid.

## Tests to add

- Preflight ready and underfilled cases.
- Smoke start exact split.
- Full start exact split.
- Start responses do not include correct answers.
- Submit persists one session and expected attempts.
- Duplicate submit does not duplicate attempts.
- Holdout submit is rejected.
- Unknown question submit is rejected.

## Verification commands

Run at minimum:

```text
uv run pytest tests/test_quiz.py -q
uv run pytest tests/test_db.py tests/test_quiz.py -q
```

If route tests are added in a new file, run that file directly too.

## Output required

Report:

- Source files changed.
- Tests added.
- Exact commands and results.
- Any unresolved risk.

