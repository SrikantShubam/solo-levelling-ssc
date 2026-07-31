# 2026-07-17 Wave 3b: Post-Submit Review Screen + Question Reporting

You are working in `C:\experiments\ssc`. Read this file fully before
changing anything. Waves 1 through 3a are already landed and verified —
read the `2026-07-17-wave*` workorders in this directory for the gate
architecture (`src/ssc_study/baseline_web.py`), asset/masking rules
(`src/ssc_study/corpus_assets.py`), frontend patterns
(`src/ssc_study/static/app.js`, `templates/landing.html`), and web routes
(`src/ssc_study/web.py`).

## Task 1: Post-submit per-question review screen

Today the result page shows section scores, marks, and tier guidance, but
the learner cannot see which questions they got wrong or what the correct
answers were — the highest-learning-value moment of a mock is missing.

Add a review view reachable from the scored result page:

- For each question in the submitted exam, show: index, section, the
  question text (with passage above it when linked, same as the exam view),
  the options, the learner's answer, the correct answer, correctness /
  skipped status, and time spent.
- **Answer data must only ever flow after submit.** The pre-submit
  no-answer-leak contract is sacred: correct answers may only be fetched
  through a result/review endpoint that verifies the session is already
  persisted (submitted). Never add correct-answer data to the start payload
  or any pre-submit endpoint. Follow the existing `get_baseline_result`
  session-based pattern; extend it or add a sibling
  `get_baseline_review(db, session_id)` that returns per-question detail
  by joining the session's attempts to questions.
- **Post-submit, the answer-leak masking rule inverts.** For questions from
  `ANSWER_LEAKING_SOURCES`, the RAW UNMASKED crop (green tick / red cross)
  is a ready-made visual explanation and is safe to display in the review
  screen only. Serve it via a review-only asset route that validates the
  session is submitted and owns that question. Do not reuse the pre-submit
  asset route for this, and do not let the review asset route serve
  unmasked crops for question_ids outside a submitted session.
- Keep UI consistent with the existing premium cockpit style (reuse
  existing CSS tokens/cards; a simple list with per-question cards and a
  wrong-only filter toggle is enough).

## Task 2: "Report this question" button

- New `question_reports` table via the standard `db.py` migration
  convention: report_id, question_id, session_id (nullable), reason (short
  free text), created_at.
- A small "Report question" control on each question card in BOTH the exam
  view (pre-submit) and the review view (post-submit), posting to a new
  endpoint. Pre-submit reports must not include or return any answer data.
- A `ssc-study reports` CLI subcommand (follow `cli.py` conventions)
  listing open reports with question_id, pdf_name, reason, created_at, so
  reported questions can be triaged in later corpus-repair waves.
- Rate-limit is unnecessary (local single-user app), but reject empty
  reason strings and cap reason length sensibly.

## Out of scope

- Pacing/quadrant analytics
- Archetype/atlas work
- Any change to eligibility gates or masking policy
- Any change to scoring/thresholds

## Verification required before reporting done

- `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q` and full `uv run pytest -q`, paste exact results.
- Add tests proving: review endpoint refuses unsubmitted/unknown sessions;
  review payload contains correct answers only for the session's own
  questions; pre-submit endpoints still contain zero answer data (extend
  the existing no-leak tests to cover the new routes); unmasked-crop review
  route refuses questions not in the submitted session; report endpoint
  persists and CLI lists it.
- Manually describe one full flow: submit a smoke exam in a test, fetch the
  review, confirm a wrong answer shows learner-vs-correct labels.

## Report format

Files changed, migration added, tests added, exact verification commands
and results, residual risk.
