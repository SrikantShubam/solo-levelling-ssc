# Codex Review Plan For Phase 1 Frontend MVP

## Review stance

Act as a strict senior engineer. The goal is not to praise agent work; the goal is to prevent a
broken Phase 1 baseline UI from shipping.

## Diff audit

Check:

- Only Phase 1 frontend MVP files changed.
- Existing CLI behavior was not broken.
- No unrelated refactors.
- No broad formatting churn.
- No new production dependencies beyond the chosen minimal web stack.
- No database migration unless explicitly justified.

## Backend audit

Verify:

- Full baseline uses the existing foundation pulse split.
- Full baseline returns exactly 200 questions.
- Smoke mode returns exactly 5 questions with 2/1/1/1 split.
- All queries exclude `is_holdout = 1`.
- Start payloads do not include correct answers.
- Submit computes correctness from DB rows.
- Submit validates unknown, holdout, duplicate, and malformed question IDs.
- Duplicate submit does not create extra sessions or attempts.
- Smoke sessions are distinguishable from full baseline sessions.

## Frontend audit

Verify:

- Landing page exposes readiness, missing counts, smoke start, and full start.
- Full start is disabled when backend preflight says underfilled.
- Exam UI supports answer selection, navigation, direct question jump, and submit confirmation.
- Draft state persists in localStorage by `exam_id`.
- Refresh restores draft answers.
- Correct answers are not present in HTML, JS bootstrap payload, or API start response.
- Result view renders total score and section breakdown.
- UI remains usable on a narrow viewport.

## Test audit

Required tests:

- Preflight ready and underfilled.
- Smoke start exact split.
- Full start exact split.
- No answer leakage in start responses.
- Holdout exclusion.
- Submit persistence.
- Duplicate submit idempotency.
- Result lookup.
- Landing/static route smoke.
- Existing `tests/test_quiz.py`.

If any of these are missing, add the smallest focused test before approving.

## Verification sequence

Run focused checks first:

```text
uv run pytest tests/test_quiz.py -q
```

Run new Phase 1 tests:

```text
uv run pytest tests/test_phase1_frontend*.py -q
```

Run related regression tests:

```text
uv run pytest tests/test_db.py tests/test_quiz.py tests/test_readiness.py -q
```

Run full suite if runtime allows:

```text
uv run pytest -q
```

## Ship criteria

Ship only if:

- Required tests pass.
- Full and smoke modes are both usable.
- Correct answers are protected until submit.
- Holdout questions are protected.
- Duplicate submit is safe.
- Existing CLI behavior still passes tests.

## No-ship criteria

Do not ship if:

- Full baseline can include holdout questions.
- Correct answers leak before submit.
- Full baseline distribution is not exact.
- Smoke mode is missing.
- Submit can duplicate attempts.
- UI uses hardcoded/fake questions.
- Existing CLI tests fail.

