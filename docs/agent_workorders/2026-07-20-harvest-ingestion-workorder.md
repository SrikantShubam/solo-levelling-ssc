# 2026-07-20 Harvest Corpus Ingestion — With Mandatory Answer-Leak Audit

You are working in `C:\experiments\ssc`. Read this entire file before writing
any code. A safety backup of `data/study.db` already exists at
`data/backups/study-pre-harvest-ingest-*.db` — do not delete it.

## Background

This session already did (all in `docs/agent_workorders/2026-07-17-*` and
`2026-07-18/19-*`): remapped/masked the original 2,355-question corpus's
answer-leaking images (7 known sources in `ANSWER_LEAKING_SOURCES` in
`src/ssc_study/corpus_assets.py`), fixed passage linking, verified answers,
corrected modality tags, and activated a 48-archetype atlas
(`archetypes`/`questions.archetype_id`, built by
`scripts/build_atlas_stage1.py`, rerunnable/idempotent).

Separately, 64 new SSC CGL PDFs were extracted (not yet imported into
`data/study.db`) into `pipeline_output/harvest_batch/<pdf_stem>/`, each with
a `merged_questions_global_order.json`. Total 4,527 pages processed via
OpenRouter `qwen/qwen3-vl-32b-instruct`, cost ~$2.38, all 64 PDFs completed
successfully. This workorder ingests that harvest into the live corpus.

## CRITICAL — read before doing anything else

The harvest's extraction merge pipeline (shared code, same as the original
corpus) already populates real per-question crops, `question_modality`,
`evidence_status`, `visual_required`, `table_required` — this is NOT the
degenerate "shared whole-page image" case Wave 1b fixed for
`2020_tier2_kdcampus_answer_key`/`2024_tier1_appx_answer_key`. Per-question
crops here are genuinely 1:1 (verified: 92 distinct crop files for 98
questions in one sampled PDF).

**However**: many of these harvest PDFs are answer-key/response-sheet
sourced, same as the original corpus's leak problem, and their per-question
crops **visibly show the marked correct answer** (green check, red X,
status box) because none of these new PDF names are registered in
`ANSWER_LEAKING_SOURCES` yet, so the existing masking pipeline never ran
against them. **Confirmed by direct visual inspection**: the crop for
`2023_tier1_prepp_2023-07-14_shift1` question 1
(`pipeline_output/harvest_batch/2023_tier1_prepp_2023-07-14_shift1/assets/question_crops/2023_tier1_prepp_2023-07-14_shift1_p01_q001_question.png`)
shows a full green checkmark next to the correct option and red X's next to
wrong ones, plus a status box — i.e., this is currently a raw, unmasked
answer leak that would reach students pre-submit if imported as-is.

The harvest manifest (`manifest.csv`, pulled from
`manstein@192.168.1.14:~/ssc-pdf-harvest/` earlier, check if still present
locally or re-fetch) has a rough `has_answer_key` column (yes/no/unknown)
from web-scraping heuristics — **do not trust this column alone**. Every
extracted question's `notes` field (in
`pipeline_output/harvest_batch/<pdf>/merged_questions_global_order.json`)
often explicitly describes what the model saw, e.g. "Option 2 is marked
with a green check, indicating it is correct" — this is real evidence,
scan it.

## Required work, in order

### Step 1 — Systematic leak-source audit (do this FIRST, before import)

For every one of the 64 harvested PDFs, determine whether it is an
answer-leaking source by inspecting the actual extracted content (`notes`,
`manual_review_reasons`, `evidence_reasons`, `raw_gemini_record` fields in
`merged_questions_global_order.json` — check what's actually populated) for
language indicating a visible marked/checked/highlighted correct-answer
indicator on the page. A PDF counts as leaking if **any** of its questions
show this evidence. Cross-reference against the manifest's `has_answer_key`
column but resolve every disagreement by trusting the extracted evidence,
not the manifest. Produce and report a clear list: which of the 64 PDFs are
leaking, which are clean, and your confidence/method for each.

### Step 2 — Register and mask

Add every confirmed-leaking new PDF name to `ANSWER_LEAKING_SOURCES` in
`src/ssc_study/corpus_assets.py`. Then import the corpus (Step 3 below)
before masking, since masking operates on DB rows — or import first with
these sources pre-registered so the existing gate (`_has_unmaskable_answer_leak`
in `baseline_web.py`) correctly excludes their crops from being servable
until masked. Either order is fine as long as no leaking-source crop is ever
reachable via `_question_asset_urls` before masking completes. Then run
`remap_question_assets`/`mask_answer_leaking_crop` (existing functions,
already proven in Wave 1/1b — reuse, do not rewrite) against the newly
imported rows from these sources. Since these are genuine per-question
crops (not shared pages), masking should work cleanly like the
`2021_tier1_sscportal_shift1_response_sheet` case did — but still apply the
same safety check Wave 1b/2c used
(`masked_crop_preserves_question_content`-style: reject and exclude rather
than serve a masked crop that lost too much content or still shows the
leak). Manually open and describe at least 8 masked crops across at least 4
different newly-registered leaking sources to confirm the checkmark/status
box is gone and question content is intact.

### Step 3 — Import

Run `ssc-study import --pipeline-root pipeline_output/harvest_batch
--db-path data/study.db` (check exact flag names against `ssc-study import
--help` — use them as documented). This assigns a fresh, independent
holdout split (~25% per section) within the new batch only, using
`INSERT OR REPLACE INTO questions` keyed by `question_id`.

**Mandatory collision check**: before import, record the current row count
and a hash/set of all existing `question_id`s in `data/study.db`. After
import, verify:
- Every pre-existing question_id's row is byte-identical to before (no
  silent overwrite from a colliding new question_id). If any collision is
  found, stop and report it — do not paper over it.
- New row count = old row count + newly inserted rows (not fewer, which
  would indicate accidental overwrites).

### Step 4 — Modality/evidence sanity spot-check

Spot-check ~15-20 rows across different harvested PDFs and sections for
`question_modality`/`visual_required`/`table_required`/`evidence_status`
correctness (same category of bug found in the original corpus: e.g.
English questions mislabeled as `math_formula`). If you find a systematic
pattern of misclassification (not just isolated noise), reuse
`classify_question_for_web_modality` from
`src/ssc_study/modality_recrop.py` (already built in Wave 2c) to correct it
for the new rows — do not build a new classifier. If spot-checks look
clean, say so and move on; do not manufacture work.

### Step 5 — Atlas backfill

Re-run `scripts/build_atlas_stage1.py` against the updated `data/study.db`
so newly imported non-holdout rows get `archetype_id` assigned via the
existing 48-archetype rule set. This script is already idempotent/rerunnable
— verify it only touches new rows plus any stale rule-matches, not holdout
rows (same guarantee it already has for the original corpus).

### Step 6 — Final measurement (this is what gets reported to the user)

Run `get_baseline_preflight(db)` from `src/ssc_study/baseline_web.py`
**before Step 3 and after Step 5**, and report the full before/after
comparison: `raw_available` per section, `available` (web-safe) per section,
and `quality_exclusions` breakdown, plus the net new servable question count
this ingestion added. This number — new genuinely web-safe questions gained
— is the headline answer the user is waiting for.

## Explicit constraints

- Do not touch or modify existing Wave 1/1b/2a/2b/2c/3a source files beyond
  what's needed to call their existing functions (e.g. registering new
  sources in `ANSWER_LEAKING_SOURCES`, calling
  `classify_question_for_web_modality` if Step 4 finds real issues). Do not
  rewrite the masking heuristic, the gate logic, or the atlas rules.
- Do not delete the pre-ingestion backup at
  `data/backups/study-pre-harvest-ingest-*.db`.
- If Step 1's audit or Step 2's masking turns up something you're not
  confident about (e.g. a source where masking looks unreliable, similar to
  the kdcampus/appx shared-page case), exclude conservatively rather than
  guess — same standard as every prior wave this session.
- This deals with real money already spent and a real corpus already in
  use (410+ recorded attempts, active SM-2 state) — do not do anything that
  could corrupt `attempts`, `sessions`, or `sm2_state` tables. Import only
  touches `questions`, `passages` (if any harvest rows are passage-linked —
  check, but this is not expected to be common), and `archetypes`/
  `archetype_id` assignment.

## Verification required before reporting done

- Step 1's full leak-source classification list (leaking vs clean, all 64).
- Step 2's masking results: counts masked/excluded per newly-registered
  source, plus the manual crop descriptions.
- Step 3's collision-safety proof (exact before/after counts, zero
  overwritten pre-existing rows).
- Step 4's spot-check findings and any correction applied.
- Step 5's atlas backfill counts.
- Step 6's full before/after preflight comparison.
- Run `uv run pytest -q`, paste exact results.
- Confirm `attempts`/`sessions`/`sm2_state` row counts are unchanged from
  before this workorder started.

## Report format

Leak-source audit list, masking counts + manual verification, import
collision-safety proof, modality spot-check outcome, atlas backfill counts,
full before/after preflight numbers (this is the headline deliverable), test
suite results, and any residual risk.
