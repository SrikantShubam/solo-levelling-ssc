# Work Order: 2026-07-07 Grok Hardening And Reconciliation

## Objective

Own the code-facing half of today's active todo.

Focus on the current uncommitted hardening pass and determine what is required before the user spends 2 hours on the manual baseline. Keep the work test-driven and surgical.

## Read first

- `Plan.md`
- `README.md`
- `memory.md`
- `errors.md`
- `checklist.md`
- `docs/agent_workorders/2026-07-07-active-todo-shared-spec.md`
- `src/ssc_corpus/acquisition.py`
- `src/ssc_corpus/ai_review.py`
- `src/ssc_corpus/cli.py`
- `src/ssc_corpus/crops.py`
- `src/ssc_corpus/extraction.py`
- `src/ssc_corpus/pdf_layout.py`
- `src/ssc_study/gates.py`
- `src/ssc_study/holdout.py`
- `src/ssc_study/models.py`
- `src/ssc_study/queues.py`
- `src/ssc_study/scheduler.py`
- touched tests under `tests/`

## Scope

You own:

1. classifying the current local diff into:
   - baseline-critical
   - general hardening
   - optional cleanup that should not block today
2. closing any small, test-proven gap that threatens baseline trust
3. tightening focused tests in touched backend areas
4. reporting what should be merged together vs split later

You do not own:

- the user's manual baseline run
- a new frontend redesign
- broad refactors unrelated to the touched files

## Constraints

- test-first for behavior changes
- preserve existing CLI and Phase 1 web behavior unless a test proves a bug
- no schema changes unless absolutely required and defended
- no speculative cleanup
- prefer narrow fixes over abstraction

## Required tasks

1. Review the local diff and classify each changed file into one of the three buckets.
2. Cross-check the changed behavior against `Plan.md` and `README.md`.
3. Identify any missing focused regression in the touched backend/test areas.
4. Add the smallest missing tests needed for baseline confidence.
5. Fix only concrete issues exposed by those tests or by direct code/test mismatch.
6. Report whether the current hardening set should land as:
   - one cohesive commit
   - two commits (`baseline-critical` and `general hardening`)
   - more than two only if clearly justified

## Required test cases

Cover the smallest relevant set from below:

- holdout behavior still matches documented exclusions
- queue/scheduler changes do not contradict current readiness or routing rules
- extraction/pdf-layout/resource handling still fails safely
- CLI changes return stable operator-facing errors
- touched DB/quiz/audit behavior remains contract-safe where covered by existing tests

## Example acceptable outputs

- add one focused scheduler regression because a changed threshold now lacks a test
- add one extraction recovery test because the code now self-heals corrupt cached page JSON
- recommend splitting the diff into `phase1-safety` and `corpus-hardening` because they verify differently

## Example unacceptable outputs

- rewriting the scheduling model without a failing test
- introducing new product scope because "it might help later"
- claiming the manual baseline is validated without the user's run evidence

## Verification commands

Run the smallest relevant commands you actually use. Prefer targeted verification before full suite.

Candidate commands:

```powershell
uv run pytest tests/test_db.py tests/test_holdout.py tests/test_quiz.py tests/test_queues.py -q
uv run pytest tests/test_extraction.py tests/test_crops_utils.py tests/test_http_download.py tests/test_native_pipeline_compare.py -q
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```

Run `uv run pytest -q` only if your final changed set justifies it.

## Deliverable report

Include:

- diff buckets with file examples
- bugs found
- tests added or changed
- exact commands run
- exact results
- merge recommendation for the current diff
- residual risk before the user's baseline block

