# Work Order: DeepSeekV4 03 Tests And Edge Cases

## Objective

Validate the Phase 1 frontend MVP like a strict reviewer. Add tests that catch data leaks,
incorrect persistence, broken smoke mode, and false readiness.

## Files to inspect first

- `docs/phase1_frontend/spec.md`
- `src/ssc_study/quiz.py`
- `src/ssc_study/db.py`
- Any new web/backend files from Grok or Gemini.
- Any new route/static/template tests.

## Required test coverage

- Full readiness true only when every required section has enough non-holdout questions.
- Full readiness false when any section is short.
- Smoke readiness true only when 2/1/1/1 split can be met.
- Full start returns exactly 200 questions.
- Smoke start returns exactly 5 questions.
- Returned question payloads never include `correct_option_label` or `correct_option_text`.
- Holdout questions never appear in start responses.
- Submit rejects holdout question IDs.
- Submit rejects unknown question IDs.
- Submit rejects wrong full section distribution.
- Submit computes correctness from DB, not client input.
- Duplicate submit with same `exam_id` does not create duplicate attempts.
- Smoke sessions are not recorded as `foundation_pulse`.
- Existing `ssc-study quiz` behavior remains covered.

## Adversarial cases

Add tests for these if the implementation makes them possible:

- Client sends duplicate question IDs in one submit.
- Client sends invalid answer label.
- Client omits `answers` for some served questions.
- Client sends negative or impossible time values.
- Client submits full mode with only smoke count.
- Client tries to include a holdout question mixed with valid non-holdout questions.

## Constraints

- Do not rewrite the implementation unless a test exposes a real defect.
- Do not add broad integration frameworks unless already present.
- Prefer small pytest route/unit tests over heavy browser infrastructure.
- Keep fixtures local to the tests unless they are broadly useful.

## Verification commands

Run focused tests first:

```text
uv run pytest tests/test_quiz.py -q
```

Then run any new web/frontend test file directly:

```text
uv run pytest tests/test_phase1_frontend*.py -q
```

Before handoff, run:

```text
uv run pytest tests/test_db.py tests/test_quiz.py tests/test_readiness.py -q
```

If runtime allows, run:

```text
uv run pytest -q
```

## Output required

Report:

- Tests added.
- Bugs found.
- Bugs fixed, if any.
- Exact commands and results.
- Any remaining untested behavior.

