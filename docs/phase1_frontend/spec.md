# Phase 1 Frontend MVP Spec

## Goal

Build the smallest local web frontend that lets the user take the Phase 1 foundation baseline exam.

Success means:

- A local web server starts from the existing `ssc-study` CLI.
- The landing page shows whether the real 200-question baseline can be started.
- The user can take a short smoke exam from the same UI.
- The user can take the full 200-question `foundation_pulse` baseline when the database is eligible.
- Submitting an exam persists attempts and shows a result summary.

## Current backend facts

- Existing command: `ssc-study quiz --session-type foundation_pulse --count 200`.
- Existing selector: `src/ssc_study/quiz.py::_load_foundation_pulse`.
- Required full split:
  - Quant/DI: 80
  - Reasoning: 40
  - English: 40
  - GK/GA: 40
- The existing selector excludes `is_holdout = 1`.
- Existing `attempts` and `sessions` tables are enough for MVP persistence.

## Recommended architecture

- Add a local web command to `ssc-study`, for example:

```text
ssc-study web --db-path ~/.ssc_study/study.db --host 127.0.0.1 --port 8765
```

- Use FastAPI for HTTP routes.
- Use Jinja templates plus static CSS/JS.
- Keep browser state in `localStorage` until submit.
- Persist to SQLite only on submit.
- Check current FastAPI/Jinja docs with Context7 before implementation.

## Routes and behavior

### `GET /`

Render the landing page.

Must show:

- Database path.
- Eligible non-holdout question counts by section.
- Full baseline readiness.
- Smoke test start button.
- Full baseline start button, disabled if underfilled.

### `GET /api/baseline/preflight`

Return current readiness.

Response shape:

```json
{
  "full_ready": true,
  "required": {"Quant/DI": 80, "Reasoning": 40, "English": 40, "GK/GA": 40},
  "available": {"Quant/DI": 120, "Reasoning": 70, "English": 65, "GK/GA": 60},
  "missing": {},
  "smoke_ready": true
}
```

If underfilled, `full_ready` must be false and `missing` must explain the shortage per section.

### `POST /api/baseline/start`

Request:

```json
{"mode": "smoke"}
```

or:

```json
{"mode": "full"}
```

Behavior:

- `mode=full` returns exactly 200 questions with the foundation split.
- `mode=smoke` returns 5 questions using this fixed split: 2 Quant/DI, 1 Reasoning, 1 English,
  1 GK/GA.
- Neither mode may include holdout questions.
- Correct answer labels must not be included in the response.
- The response includes a client-side `exam_id` UUID used for localStorage and submit idempotency.

Response shape:

```json
{
  "exam_id": "uuid",
  "mode": "smoke",
  "question_count": 5,
  "questions": [
    {
      "question_id": "q1",
      "index": 1,
      "section": "Quant/DI",
      "tier": "tier1",
      "question_text": "Question text",
      "options": [
        {"label": "1", "text": "A"},
        {"label": "2", "text": "B"},
        {"label": "3", "text": "C"},
        {"label": "4", "text": "D"}
      ]
    }
  ]
}
```

### `POST /api/baseline/submit`

Request shape:

```json
{
  "exam_id": "uuid",
  "mode": "smoke",
  "started_at": "2026-07-06T10:00:00Z",
  "ended_at": "2026-07-06T10:05:00Z",
  "answers": [
    {
      "question_id": "q1",
      "user_answer": "1",
      "time_spent_seconds": 42,
      "marked_for_review": false
    }
  ]
}
```

Behavior:

- Validate that every submitted question exists and is non-holdout.
- Validate mode-specific counts and section distribution.
- Create one `sessions` row.
- Use `session_type='foundation_pulse'` for full mode.
- Use `session_type='analysis'` for smoke mode with a note prefix like `phase1_web_smoke:<exam_id>`.
- Insert one attempt per submitted question.
- Treat unanswered questions as skipped: `user_answer=null`, `is_correct=0`, `student_label='skipped'`.
- Compute correctness server-side from the database.
- Update session `question_count`, `correct_count`, and `ended_at`.
- If the same `exam_id` is submitted again, return the existing result instead of duplicating attempts.

Response shape:

```json
{
  "session_id": 123,
  "mode": "smoke",
  "question_count": 5,
  "correct_count": 3,
  "accuracy": 0.6,
  "by_section": {
    "Quant/DI": {"total": 2, "correct": 1},
    "Reasoning": {"total": 1, "correct": 1},
    "English": {"total": 1, "correct": 0},
    "GK/GA": {"total": 1, "correct": 1}
  }
}
```

### `GET /api/baseline/result/{session_id}`

Return the persisted result for a completed smoke or full Phase 1 web session.

## UI requirements

- The UI must feel like an exam console, not a landing page.
- Desktop-first layout with mobile-safe fallback.
- Main exam screen:
  - Question text and options.
  - Section/tier metadata.
  - Previous and next navigation.
  - Question number grid.
  - Answered/unanswered/marked states.
  - Timer showing elapsed time.
  - Submit confirmation with unanswered count.
- Persist in-progress answers in `localStorage` by `exam_id`.
- On reload, restore answers for the active exam.
- Never show correct answers before submit.
- Result screen shows total score and section breakdown.

## Non-goals

- No accounts or login.
- No hosted deployment.
- No React, Next.js, Vue, or build pipeline.
- No full analytics dashboard.
- No changes to Phase 2, Phase 3, or Guardian behavior.
- No sealed-holdout usage.

## Edge cases

- Empty database: landing page explains import is required.
- Underfilled full baseline: full start button disabled and missing counts shown.
- Underfilled smoke mode: smoke start disabled and missing counts shown.
- Invalid mode: HTTP 400.
- Holdout question in submit payload: HTTP 400.
- Unknown question in submit payload: HTTP 400.
- Duplicate submit: return existing session result.
- Browser refresh during exam: local draft restores.
- Browser storage cleared: user must start again.

