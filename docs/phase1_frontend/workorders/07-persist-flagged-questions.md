# Workorder 07: Persist Flagged Baseline Questions

## Goal

Persist every `marked_for_review` question from the web baseline so uncomfortable or doubtful questions can be reviewed after submit.

## Why This Blocks Another 200Q Attempt

The browser currently sends `marked_for_review`, but the backend discards it. If the user flags questions during a two-hour baseline, that signal is lost after submit. A manual baseline should produce a review queue, not just a score.

## Files

- Modify: `src/ssc_study/db.py`
- Modify: `src/ssc_study/models.py`
- Modify: `src/ssc_study/baseline_web.py`
- Modify: `src/ssc_study/reports.py` or add a focused query helper if cleaner
- Test: `tests/test_baseline_web.py`
- Test: `tests/test_phase1_frontend.py`

## Data Model Decision

Prefer adding a boolean column to `attempts`:

- `marked_for_review INTEGER NOT NULL DEFAULT 0`

Reason: this is an attempt-level signal from a specific session, not an intrinsic property of the question. A separate `attempt_flags` table is more flexible, but unnecessary unless multiple flag types are needed immediately.

## Implementation Steps

- [x] Add a DB migration that adds `attempts.marked_for_review INTEGER NOT NULL DEFAULT 0`.
- [x] Extend `Attempt` with `marked_for_review: bool = False`.
- [x] In `submit_baseline_exam()`, read `marked_for_review` from each submitted answer.
- [x] Persist it in `_persist_attempt_with_sm2()` or the attempt insert path.
- [ ] Add a query helper or report path to fetch flagged questions by `session_id`.
- [x] Keep skipped questions and marked questions independent: a question may be skipped and marked.

## Required Tests

- [x] Submitting a marked baseline answer stores `marked_for_review = 1`.
- [ ] Submitting an unmarked answer stores `marked_for_review = 0`.
- [x] Marked + skipped persists both `student_label = 'skipped'` and `marked_for_review = 1`.
- [ ] Duplicate submit remains idempotent and does not duplicate flagged attempts.
- [ ] Result or helper query can recover flagged question IDs for a session.

## Acceptance Criteria

- `marked_for_review` survives page submit and can be queried after the exam.
- No answer leakage is introduced.
- Full relevant tests pass:
  - `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
  - `uv run pytest -q`
