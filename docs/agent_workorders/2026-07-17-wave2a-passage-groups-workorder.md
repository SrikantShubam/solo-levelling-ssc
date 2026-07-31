# 2026-07-17 Wave 2a: Passage/RC Group Support

You are working in `C:\experiments\ssc`. Read this file fully before changing
anything. This is Wave 2 work, building on the already-landed Wave 1 baseline
safety pass (`docs/agent_workorders/2026-07-17-wave1-baseline-corpus-safety-workorder.md`
and the `...wave1b-...` follow-up) — read both for context on what already
exists (`src/ssc_study/corpus_assets.py`, the web-safe gate in
`src/ssc_study/baseline_web.py`, `scripts/remap_baseline_assets.py`).

## Context

The original 2-hour manual baseline run showed comprehension/cloze questions
served with no passage — a stem like "Select the most appropriate option to
fill in blank number 1." with nothing to fill in. Wave 1 added a narrow
regex-based exclusion (`_looks_passage_dependent` in `baseline_web.py`,
reason `passage_dependent`) so these ~44 rows are currently excluded from
the web-safe pool rather than served broken. That is a stopgap, not a fix.

There is no `passages` table and no `passage_id` column today — the schema
has no concept of a passage. Source PDFs for every corpus PDF are available
at `answer_key_candidates_staging/<pdf_name>.pdf` — use these to recover the
real passage text; do not guess or fabricate passage content.

## Required reading before changing anything

- `src/ssc_study/models.py`, `src/ssc_study/db.py` (schema/migration
  conventions — find how prior migrations were added and follow the same
  pattern)
- `src/ssc_study/baseline_web.py` (`_looks_passage_dependent`,
  `_PASSAGE_DEPENDENT_PATTERNS`, `_web_baseline_rejection_reason`)
- `src/ssc_corpus/extraction.py`, `src/ssc_corpus/pdf_layout.py` (existing
  PDF text/page extraction conventions — reuse them rather than inventing a
  new extraction path)
- `tests/test_baseline_web.py`
- `memory.md` / `errors.md` — search "2026-07-13 Smoke Baseline Incomplete
  Stem" for the followup note about over-broad heuristics; apply the same
  caution here (don't build a passage-detector broader than the evidence
  supports)

## Scope

1. **Schema**: add a `passages` table (at minimum: `passage_id`,
   `pdf_name`, `source_page`, `passage_text`, `created_at`) and a nullable
   `questions.passage_id` foreign key, via a migration following this repo's
   existing migration convention in `db.py`.
2. **Recovery**: for every question currently excluded as `passage_dependent`
   (44 rows today; also re-scan more broadly — the original full diagnosis
   found 110+ rows matching looser passage/cloze phrasing such as "based on
   the passage", "in the given passage", "fill in blank" — re-derive the
   real set from first principles against the corpus, don't just take the
   Wave 1 count as the ceiling), locate the passage on the source PDF page
   (via `pdf_name` + `source_page`) and extract the actual passage text.
   Group all questions sharing one passage under the same `passage_id`.
3. **Gate update**: once a question has a resolved `passage_id` with real
   `passage_text`, it must no longer be excluded as `passage_dependent`.
   Questions whose passage cannot be confidently recovered stay excluded —
   do not link a `passage_id` you are not confident is correct.
4. **Serving**: extend `_question_to_client` (or equivalent) to include the
   linked passage text, and update the frontend (`landing.html`/`app.js`) to
   render the passage above the question stem when present. Keep this
   minimal — a labeled block above the stem is sufficient, no new interaction
   patterns needed.

## Out of scope

- Do not touch answer verification (`evidence_status`, `correct_option_*`)
  — that is Wave 2b, a separate workorder running after this one.
- Do not touch modality reclassification or the two whole-page-only sources
  (`2020_tier2_kdcampus_answer_key`, `2024_tier1_appx_answer_key`) — that is
  Wave 2c.
- Do not change the answer-leak masking policy or `corpus_assets.py`.

## Landmine to avoid

Multiple questions can legitimately share one passage (a 10-blank cloze has
10 questions, one passage). Do not create a duplicate passage row per
question — dedupe by `(pdf_name, source_page)` or by normalized passage text
before inserting.

## Verification required before reporting done

- Run `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
  and `uv run pytest -q`, paste exact results.
- Report exact counts: passages created, questions linked, questions still
  excluded as `passage_dependent` and why (source PDF passage not
  confidently locatable — name the specific rows).
- Manually confirm at least 2 linked passages render correctly by describing
  what you see (passage text present, matches source PDF, no truncation).

## Report format

Files changed, migration added, counts (passages created / questions linked
/ questions still excluded), tests added, exact verification commands and
results, residual risk for later waves.
