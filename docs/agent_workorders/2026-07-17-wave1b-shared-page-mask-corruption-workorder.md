# 2026-07-17 Wave 1b: Fix Shared-Page-Image Masking Corruption

You are working in `C:\experiments\ssc`. This is a corrective follow-up to
`docs/agent_workorders/2026-07-17-wave1-baseline-corpus-safety-workorder.md`,
which you (or another worker) already implemented. Read that file and
`src/ssc_study/corpus_assets.py` fully before changing anything.

## Confirmed bug

`2020_tier2_kdcampus_answer_key` (and possibly other answer-leaking sources)
store only whole-page images under `page_images/page_NN.png` — there are no
per-question crop files for this source. Multiple distinct `question_id`
rows (verified: 11 rows, `q10` through `q20`) share the **identical**
`question_crop_path` pointing at the same page image.

`mask_answer_leaking_crop` in `src/ssc_study/corpus_assets.py` runs its
pixel-color heuristic (`_find_answer_marker_y`) against these shared page
images as if they were single-question crops, then crops and overwrites one
masked file per unique source path. This is destructive for two reasons:

1. Cropping a page based on wherever the heuristic finds a marker discards
   content for every other question that shares that same page image —
   verified: `page_02.png` for this source has no real answer-key
   annotation on it at all (the heuristic false-triggered, likely on the
   diagonal "KD Campus" watermark), yet the masked output kept only 29% of
   the page height, deleting an entire reading-comprehension passage plus
   9 questions' worth of content that legitimately belonged on that page.
2. I independently measured all 30 masked pages in this source: kept height
   ranges from 14% to 81% of the original. This is systemic across the
   whole source, not an isolated case.

There is no bounding-box data in `page_json/page_NN.json` for this source
(checked `page_02.json` — text only, no coordinates), so there is no cheap
way to make the crop question-specific. Do not attempt to infer per-question
regions from text layout heuristics for this workorder — that is Wave 2
scope (real per-question re-cropping from source PDFs).

## Required fix

1. **Detect shared/whole-page crop assets before masking.** In
   `remap_question_assets` (or a helper in `corpus_assets.py`), before
   calling `mask_answer_leaking_crop`, check whether the resolved crop path
   is referenced by more than one `question_id` in the corpus (or, more
   robustly: check whether the crop file lives directly under a
   `page_images/` directory rather than a `question_crops/`-style
   per-question directory — inspect the actual directory naming convention
   used across `pipeline_output/p2_gemini/*/`. Prefer whichever signal is
   unambiguous; if both are cheaply available, require both to agree before
   treating an asset as safely maskable).
2. **Never mask a shared/whole-page asset.** For any answer-leaking-source
   question whose resolved crop is a shared/whole-page image, do not run the
   pixel heuristic and do not produce a masked file. Treat it the same as
   `answer_marker_not_found` / `image_unreadable` today: exclude the
   question from the web-safe pool with the existing `unmaskable_answer_leak`
   reason (do not invent a new reason unless the existing one doesn't fit —
   if it doesn't cleanly fit, propose a narrowly-scoped new reason like
   `shared_page_asset_unmaskable` and wire it through
   `_web_baseline_rejection_reason` in `baseline_web.py` the same way the
   existing reasons are wired).
3. **Revert/regenerate the already-corrupted masked outputs.** Delete the
   currently-generated masked files under
   `pipeline_output/p2_gemini/2020_tier2_kdcampus_answer_key/question_crops_masked/`
   (and check the other 6 answer-leaking sources for the same shared-page
   pattern — verify each one directly, do not assume only kdcampus is
   affected) and re-run the remap/mask script so the DB reflects correct
   exclusions instead of corrupted masked paths.
4. **Do not touch the masking logic for genuine per-question crops.** The
   `2021_tier1_sscportal_shift1_response_sheet` source (and any other source
   confirmed to have true per-question crop files, one file per question)
   should keep working exactly as already verified in Wave 1 — only add the
   shared-page guard, don't change behavior for the case that already works.

## Verification required before reporting done

- For every one of the 7 `ANSWER_LEAKING_SOURCES`, confirm whether its crop
  assets are per-question or shared/whole-page, and report which is which.
- Confirm zero masked output files remain for any source where masking was
  incorrectly applied to a shared page image.
- Confirm the DB no longer points any question at a corrupted masked file;
  affected rows must show up in `quality_exclusions` instead.
- Re-run `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
  and `uv run pytest -q`, paste exact results.
- Add a regression test that would have caught this: e.g. a fixture with two
  question rows sharing one crop path, asserting neither gets masked and
  both are excluded (or excluded consistently), not silently corrupted.
- Manually open (describe what you see) at least 2 before/after image pairs
  from the previously-corrupted source to confirm no corruption remains and
  no answer leak was reintroduced.

## Report format

Same as the Wave 1 workorder: files changed, counts (which sources were
shared-page vs per-question, how many previously-masked rows are now
excluded instead), tests added, exact verification commands and results,
residual risk for Wave 2.
