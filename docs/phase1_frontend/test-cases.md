# Phase 1 Frontend MVP Test Cases

## Acceptance tests

1. Local server starts with `ssc-study web --db-path <test-db> --host 127.0.0.1 --port 8765`.
2. Landing page renders database readiness and section counts.
3. Smoke exam starts with exactly 5 non-holdout questions.
4. User can answer, navigate, submit, and see a result.
5. Full exam starts with exactly 200 non-holdout questions when the database is eligible.
6. Full exam section split is exactly 80 Quant/DI, 40 Reasoning, 40 English, 40 GK/GA.
7. Underfilled full baseline fails before creating a session.
8. Existing CLI quiz tests still pass.

## Backend unit tests

- Preflight returns required counts and available counts.
- Preflight marks `full_ready=false` when any full section is short.
- Preflight marks `smoke_ready=false` when any smoke section is short.
- Full selector rejects any count other than 200.
- Full selector excludes holdout questions.
- Smoke selector excludes holdout questions.
- Submit rejects holdout question IDs.
- Submit rejects unknown question IDs.
- Submit rejects wrong full section distribution.
- Submit treats missing answers as skipped.
- Submit computes correctness server-side.
- Submit creates exactly one session row.
- Submit creates exactly one attempt per question.
- Duplicate submit with the same `exam_id` returns the existing result and does not create new attempts.

## Route tests

- `GET /` returns HTTP 200 and contains the smoke and full baseline controls.
- `GET /api/baseline/preflight` returns HTTP 200 with `required`, `available`, `missing`,
  `full_ready`, and `smoke_ready`.
- `POST /api/baseline/start` with `{"mode":"smoke"}` returns 5 questions and no correct labels.
- `POST /api/baseline/start` with `{"mode":"full"}` returns 200 questions and no correct labels.
- `POST /api/baseline/start` with invalid mode returns HTTP 400.
- `POST /api/baseline/submit` returns score and section breakdown.
- `GET /api/baseline/result/{session_id}` returns the persisted score.
- `GET /api/baseline/result/{bad_id}` returns HTTP 404.

## Frontend smoke tests

Use the smallest practical browser-level check. If Playwright is not already available, do not add a
heavy browser test dependency in v1; use route and HTML tests instead.

Required smoke checks:

- Landing HTML includes the app shell, start buttons, and readiness text.
- Static JS file is served.
- Static CSS file is served.
- Smoke start response can be rendered by the frontend.
- Submit confirmation includes unanswered count.
- Result screen can render the backend result payload.

## Regression tests to protect existing behavior

- `uv run pytest tests/test_quiz.py -q`
- `uv run pytest tests/test_db.py tests/test_quiz.py tests/test_readiness.py -q`
- `uv run pytest -q` before final merge if runtime allows.

## Test data fixture requirements

Create helpers that can seed:

- Full eligible database: 80+ Quant/DI, 40+ Reasoning, 40+ English, 40+ GK/GA non-holdout questions.
- Smoke eligible database: 2+ Quant/DI, 1+ Reasoning, 1+ English, 1+ GK/GA non-holdout questions.
- Underfilled database: one section below requirement.
- Holdout trap database: enough non-holdout questions plus extra holdout questions that must never appear.

## Failure evidence expected from agents

Each model must report:

- Commands run.
- Tests added.
- Tests passed or failed.
- Any unverified area.
- Any source files changed.

