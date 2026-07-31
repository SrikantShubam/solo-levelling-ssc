# 2026-07-20 Harvest Answer-Verification Recovery

You are working in `C:\experiments\ssc`. A safety backup of `data/study.db`
already exists at `data/backups/study-pre-harvest-verification-*.db` — do
not delete it.

## Background and the actual problem

The harvest ingestion (`docs/agent_workorders/2026-07-20-harvest-ingestion-corrected-workorder.md`,
already landed) imported 6,180 of 12,521 extracted harvest questions;
6,341 were filtered by the shared loader's `practice_ready` gate
(`src/ssc_study/loader.py`). A breakdown of *why* (sampled 15 of 64
harvest files, 3,654 not-practice-ready rows):
- `correct_option_unresolved_or_conflict`: 3,323 (91% of sampled reasons)
- `malformed_options`: 1,385
- `low_confidence`: 1,220
- `math_parse_lossy`: 125

Separately, of the 6,180 already-imported rows, 5,070 have
`evidence_status = 'PASS_LLM_ONLY'` (unverified) and only 1,110 have
`PASS_WITH_EVIDENCE`.

**The key fact making this recoverable**: every one of these 64 harvest
PDFs is already registered in `ANSWER_LEAKING_SOURCES` in
`src/ssc_study/corpus_assets.py` — meaning every one of them is confirmed
to visually show which option is marked correct (green check/red X). The
`correct_option_unresolved_or_conflict` and `PASS_LLM_ONLY` states aren't
evidence the underlying questions are bad — they're evidence that nothing
**independently verified** what the vision model read off the page.

`src/ssc_study/answer_verification.py` (built and proven in Wave 2b earlier
this session — read it fully) already solves exactly this: it reads the
PDF's actual vector text color data via `fitz` (not the vision model's
interpretation) to deterministically find which option is marked green,
completely independent of what the extraction pipeline guessed. This was
already verified to work correctly (independently cross-checked against
raw PDF byte data in this session's history). Reuse this exact mechanism —
do not build a new one, do not use an LLM for this, it must stay
deterministic and evidence-based like the rest of this session's work.

## Task

### Part A — Recover already-imported `PASS_LLM_ONLY` rows (5,070 rows)

For every harvest question currently `evidence_status = 'PASS_LLM_ONLY'` in
`data/study.db`, run `extract_green_answer_labels` (and
`extract_letter_answer_key_labels` as fallback, same as
`answer_verification.py` already does) against its source PDF
(`answer_key_candidates_staging/<pdf_name>.pdf` if present, else the
harvested PDF at `data/harvest_pdfs/<pdf_name>.pdf`) keyed by
`global_question_number`. Where the deterministic extractor confirms a
label:
- If it matches the currently stored `correct_option_label`: promote
  `evidence_status` to `PASS_WITH_EVIDENCE` (or whatever status
  `answer_verification.py` already uses for this — reuse its exact
  constant, don't invent a new one).
- If it disagrees with the currently stored label: correct
  `correct_option_label`/`correct_option_text` to match the deterministic
  evidence (the PDF's own color data is ground truth here, same principle
  Wave 2b already established) and set the same verified evidence status.
- If no deterministic evidence can be found for that question, leave it as
  `PASS_LLM_ONLY` — do not guess.

### Part B — Recover unimported `correct_option_unresolved_or_conflict` rows

For every harvest question that was filtered out of import specifically
for `blocking_review_reasons` containing `correct_option_unresolved_or_conflict`
(re-scan the source `merged_questions_global_order.json` files under
`pipeline_output/harvest_batch/` to find these — they were never imported,
so they're not in the DB yet), run the same deterministic extractor. Where
it resolves a confident label:
- Set `canonical_correct_option_label` (and `correct_option_text`) in that
  question's record to the deterministically-verified value, mark
  `practice_ready = true`, and clear the resolved blocking reason (leave
  other blocking reasons alone if any remain — a row should only become
  practice_ready if ALL blocking reasons are resolved, not just this one).
- Where no deterministic evidence resolves the conflict, leave it
  unpromoted/excluded — do not guess, do not force it through.
- Do not touch rows blocked for `malformed_options`, `low_confidence`, or
  `math_parse_lossy` — those aren't answer-verification problems, leave
  them out of scope for this workorder.
- After updating the JSON files, re-run `ssc-study import --pipeline-root
  pipeline_output/harvest_batch --db-path data/study.db` to pick up the
  newly-qualified rows (the loader is hash-based and idempotent, this
  should only add the newly-qualified rows, not duplicate anything already
  imported — verify this is actually true, don't assume).

### Mandatory safety checks (same standard as every prior wave)

- Before touching anything, snapshot: total `questions` count, per-pdf
  question_id sets for a handful of already-imported harvest PDFs,
  protected table counts (`attempts`, `sessions`, `sm2_state`).
- After Part A and Part B, re-verify: zero collisions with pre-existing
  non-harvest corpus IDs, zero duplicate IDs within harvest, protected
  tables unchanged, no previously-imported harvest row's `question_id`
  changed (updates should be `UPDATE ... WHERE question_id = ?`, never
  delete-and-reinsert with a different ID).
- Run `get_baseline_preflight()` before this workorder's changes and after,
  report the full before/after comparison — this is the headline number.

## Verification required before reporting done

- Exact counts: how many of the 5,070 `PASS_LLM_ONLY` rows got promoted to
  verified evidence (and how many of those also had their stored answer
  corrected because it disagreed with the deterministic evidence — report
  this separately and clearly, it matters).
- Exact counts: how many previously-unimported
  `correct_option_unresolved_or_conflict` rows got resolved and newly
  imported.
- Full before/after `get_baseline_preflight()` — headline: new total
  web-safe question count and the delta from this workorder specifically.
- Manually describe at least 5 promoted/corrected rows: show the PDF
  source, the deterministically-extracted label, and what was stored
  before vs after.
- Protected-table and collision-safety proof (exact counts).
- `uv run pytest -q` results.

## Report format

Snapshot before, Part A results (promoted count, corrected count,
unresolved-remaining count), Part B results (newly-qualified count,
still-excluded count with reasons), collision/protected-table safety proof,
manual verification samples, full before/after preflight numbers (headline
deliverable), test suite results, residual risk.
