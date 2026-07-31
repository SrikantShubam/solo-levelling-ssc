# 2026-07-17 Wave 2c: Modality Reclassification + Real Per-Question Recropping

You are working in `C:\experiments\ssc`. Read this file fully before
changing anything. This is Wave 2 work, running after Wave 2a (passages)
and Wave 2b (answer verification) have already landed — read
`docs/agent_workorders/2026-07-17-wave1-baseline-corpus-safety-workorder.md`,
its `wave1b` follow-up, `2026-07-17-wave2a-passage-groups-workorder.md`, and
`2026-07-17-wave2b-answer-verification-workorder.md` for context on what
already exists before you start.

## Context

Two problems, handled together because both need the source PDFs:

**1. Modality misclassification.** The original diagnosis found English
questions (grammar-error-spotting, jumbled-sentence-order) mislabeled with
`question_modality = 'math_formula'`. Since `math_formula` is treated as a
safe web-text modality (`_WEB_TEXT_MODALITIES` in `baseline_web.py`), this
pollutes what gets served and means the modality field can't be trusted for
filtering.

**2. Two sources have no per-question crops at all.** `2020_tier2_kdcampus_answer_key`
(191 rows) and `2024_tier1_appx_answer_key` (38 rows) only ever had whole
shared page images (`page_images/page_NN.png`, multiple questions per page).
Wave 1b confirmed masking these page-level images is destructive (it
corrupted content shared across ~10 questions per page) and correctly
excludes all 229 rows rather than serving broken/leaking images. Source PDFs
for both are available at
`answer_key_candidates_staging/2020_tier2_kdcampus_answer_key.pdf` and
`answer_key_candidates_staging/2024_tier1_appx_answer_key.pdf` — use them to
produce real per-question crops.

## Required reading before changing anything

- `src/ssc_corpus/crops.py`, `src/ssc_corpus/pdf_layout.py`,
  `src/ssc_corpus/extraction.py` — this repo already has a crop-generation
  pipeline used for every other source; use it, don't build a parallel one
- `src/ssc_study/corpus_assets.py` (`ANSWER_LEAKING_SOURCES`,
  `mask_answer_leaking_crop`, `remap_question_assets`)
- `src/ssc_study/baseline_web.py` (`_question_needs_visual_asset`,
  `_has_unmaskable_answer_leak`, `_web_baseline_rejection_reason`)
- `tests/test_crops_utils.py`, `tests/test_baseline_web.py`

## Scope

### Modality reclassification (all 2,355 rows)

Re-audit `question_modality` against the actual question content (crop
image where available, else question text) for every row, not just the two
whole-page sources. Fix misclassified rows — the known case is English
questions tagged `math_formula`; look for the same pattern in other
sections. Write this as a rerunnable script, same convention as
`scripts/remap_baseline_assets.py`.

### Real per-question recropping for the two whole-page sources

Using the existing crop pipeline (`src/ssc_corpus/crops.py` and friends)
against the source PDFs in `answer_key_candidates_staging/`, generate real
per-question crop images for `2020_tier2_kdcampus_answer_key` and
`2024_tier1_appx_answer_key`, matched to existing `question_id`/
`source_page`/`global_question_number` rows — do not re-run full corpus
extraction, only crop generation keyed to already-known question boundaries.

Both sources are in `ANSWER_LEAKING_SOURCES` (they carry the same
check/cross answer annotations as the other response-sheet sources). Any
newly generated per-question crop for these two sources **must** go through
the existing `mask_answer_leaking_crop` pipeline before
`question_crop_path` is set to it — never point a question at an unmasked
crop from these sources. Verify each masked result the same way Wave 1
verified the response-sheet source: confirm the answer annotation is gone
and the question content is preserved, for a sample of at least 5 per
source.

If a reliable per-question boundary cannot be determined for some rows
(e.g. ambiguous page layout), leave those specific rows excluded — do not
guess boundaries. Report exactly which rows and why.

## Out of scope

- Passage linking (Wave 2a, already done)
- Answer verification / `evidence_status` changes (Wave 2b, already done)
- Any change to the masking heuristic itself (`_find_answer_marker_y`) —
  reuse it as-is; if it fails on these two sources' actual crop format, report
  that as a blocker rather than modifying the shared masking function without
  re-verifying the other five sources it already works for

## Verification required before reporting done

- Run `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py tests/test_crops_utils.py -q`
  and `uv run pytest -q`, paste exact results.
- Report exact counts: modality corrections made (by from/to modality pair),
  rows successfully recropped and masked per source, rows still excluded
  and why.
- Manually confirm at least 5 masked crops per newly-cropped source by
  describing what you see (question content preserved, no answer leak).

## Report format

Files changed, scripts added and exact commands to run them, counts
(modality corrections, rows recropped/masked/still-excluded per source),
tests added, exact verification commands and results, residual risk.
