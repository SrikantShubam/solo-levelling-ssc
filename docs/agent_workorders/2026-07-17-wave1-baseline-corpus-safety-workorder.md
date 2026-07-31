# 2026-07-17 Wave 1: Baseline Corpus Safety Workorder

You are working in `C:\experiments\ssc`. Read this file fully before changing anything.

## Context

A manual 2-hour, 200-question baseline exam run exposed four corpus-quality
failures that reach the web baseline UI: broken image rendering, unrendered
math, wrong answers, and half-assed comprehension questions. Root-cause
diagnosis (already done, do not redo it) found:

1. Every `question_crop_path` / `page_asset_path` in `data/study.db` points to
   `extraction_reruns\p2_all_pdfs_20260524\...`, a directory that no longer
   exists. The real assets live under `pipeline_output\p2_gemini\...` (or, for
   sources not in that tree, under `deprecated\...`). All ~2,355 image
   references currently 404.
2. The web-safe question gate (`_build_web_safe_question_pool` and
   `_is_web_safe` in `src/ssc_study/baseline_web.py`) does not exclude:
   - rows with `evidence_status IN ('PASS_LLM_ONLY', 'BLOCKED')` (134 + 67
     rows respectively) — these have no verified answer-key evidence.
   - rows where `correct_option_label` is not present among the parsed
     `options_json` labels (2 rows), or where `correct_option_text` disagrees
     with the option text at that label (11 rows) — answer-key integrity
     failures.
   - passage/cloze-dependent orphan stems whose entire question text assumes
     a passage or numbered blank that isn't stored anywhere (~110+ rows,
     e.g. stems like "Select the most appropriate option to fill in blank
     number 1." with no attached passage). Building real passage support is
     Wave 2 scope — for now these must be excluded from the web-safe pool,
     the same way `incomplete_stem` rows are already excluded.
3. **Answer-leakage risk in crop images**: crops sourced from response-sheet /
   answer-key PDFs (pdf_name contains `response_sheet` or `answer_key`:
   `2020_tier2_kdcampus_answer_key`, `2021_tier1_sscportal_shift1_response_sheet`,
   `2024_tier1_appx_answer_key`, `2024_tier1_sscportal_sep09_shift1_response_sheet`,
   `2024_tier2_sscportal_jan18_response_sheet`,
   `2024_tier2_sscportal_jan19_response_sheet`,
   `2024_tier2_sscportal_jan20_response_sheet`) visually mark the correct
   option with a check/cross overlay baked into the image. Confirmed by
   direct visual inspection of
   `pipeline_output\p2_gemini\2021_tier1_sscportal_shift1_response_sheet\assets\question_crops\2021_tier1_sscportal_shift1_response_sheet_p01_q003_question.png`
   — it shows a green check next to the correct option and red X's on the
   others, plus a "Chosen Option" footer. Serving this crop pre-submit is an
   answer leak.

## Decision made (do not re-litigate)

Policy for item 3: **mask, don't exclude.** For the seven response-sheet /
answer-key sources listed above, do not serve the raw stored crop pre-submit.
Instead:

- Detect answer-leaking sources by `pdf_name` membership in the list above
  (call this set `ANSWER_LEAKING_SOURCES`, defined once, not scattered).
- Produce masked crop variants that crop out (do not blur — crop away
  entirely) any image content at or below the first answer-annotation marker
  row for that page. The reliable structural signal in these sources is the
  row starting with `Ans` (as seen in the sample above) — the mask must cut
  the image strictly above that row's y-coordinate, keeping the question
  stem, any embedded figure/table, and the option list, but never the
  check/cross overlay or the "Question ID / Status / Chosen Option" footer
  box.
- Store masked variants alongside originals (do not overwrite raw crops —
  they remain useful ground truth for Wave 2 answer verification) and point
  `question_crop_path`/serving logic at the masked variant for these sources
  only. Non-leaking sources are unaffected and continue serving their
  existing (already answer-free) crops once repointed to their real location.
- If a given response-sheet page's crop cannot be reliably masked (e.g. the
  answer marker row cannot be located with confidence), exclude that question
  from the web-safe pool rather than risk serving a leaking image. Log which
  question_ids were excluded this way and why, in your report.

## Required reading before changing anything

- `src/ssc_study/baseline_web.py` (full file — the gate, pool builder, and
  asset URL logic all live here)
- `src/ssc_study/question_assets.py` (asset path validation)
- `src/ssc_study/db.py` (connection/migration conventions — see how prior
  migrations were added, e.g. migration 14 mentioned in `memory.md`)
- `tests/test_baseline_web.py`
- `memory.md` (search "2026-07-11 Baseline Web-Safe Pool Hardening" and
  "2026-07-13 Smoke Baseline Incomplete Stem" for the existing exclusion
  pattern you are extending)
- `errors.md` (same two entries, for symptom-to-fix history)

## Scope — do exactly these four things

### 1. Asset path remap

Write a one-time DB migration (or repair script under `scripts/` if that is
the existing convention — check first) that, for every question row, resolves
the correct current asset path by `pdf_name` and rewrites
`question_crop_path` / `page_asset_path` to point at the real file under
`pipeline_output\p2_gemini\<pdf_name>\...` when it exists there, else under
the matching `deprecated\...` tree. Verify with `os.path.exists` before
writing — do not write a path you have not confirmed exists on disk. Report
how many rows were remapped, how many still resolve to no file (these must be
excluded from the web-safe pool, not silently served), and add this as a
tracked exclusion reason (e.g. `missing_asset`) alongside existing reasons
like `incomplete_stem`.

Add serve-time validation too: `_question_asset_urls` (or wherever assets are
turned into URLs) should not hand out a URL for a path that doesn't resolve
on disk at serve time — defense in depth in case of future path drift.

### 2. Web-safe gate extension

Extend the existing exclusion logic (same shape as `incomplete_stem` /
`invalid_options` / mojibake checks already there) to also exclude:

- `evidence_status IN ('PASS_LLM_ONLY', 'BLOCKED')` → reason `unverified_answer`
- `correct_option_label` not in parsed option labels, or
  `correct_option_text` mismatched with the option text at that label →
  reason `answer_integrity_failure`
- passage/cloze-orphan stems → reason `passage_dependent` (build a targeted
  detector; do not reuse the overly broad first attempt at `incomplete_stem`
  that the team already had to walk back — read that follow-up note in
  `errors.md` before writing a heuristic, and keep it narrow and evidenced,
  not a blanket lowercase-first-letter or short-stem rule)

`get_baseline_preflight` already reports `quality_exclusions` as a dict —
extend it with these new reason keys rather than inventing a new reporting
shape.

### 3. Answer-leaking source masking

Implement the masking policy above. This will likely need a small image
utility (Pillow is a reasonable dependency if not already present — check
`pyproject.toml` first) that locates the answer-marker row and crops above
it. Test it against real sample crops from at least two of the seven listed
sources before trusting it at scale, and handle the "can't locate marker
confidently" case by excluding (reason `unmaskable_answer_leak`) rather than
guessing.

### 4. Tests

Add regression coverage for all of the above:
- asset path remap resolves to real files (or is excluded, never silently
  broken)
- each new exclusion reason is independently testable
- masking removes the answer-marker region for a sample leaking image and
  preserves the question/option region
- preflight/start still refuse to serve any excluded row

## Explicitly out of scope for Wave 1

- Building real passage/RC group support (Wave 2)
- Answer re-verification pass beyond the label/text integrity check above
  (Wave 2)
- Modality reclassification (Wave 2)
- Math rendering (KaTeX/MathJax) — Wave 1 relies on masked/remapped crop
  images being the authoritative visual, not on rendering LaTeX from text
- Any Phase 3 / Guardian / readiness scoring changes

If you find scope drift or a blocker that requires Wave 2 decisions to
proceed, stop and report it — do not expand scope to cover it yourself.

## Verification required before reporting done

- Run `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
  and paste the exact result.
- Run `uv run pytest -q` (full suite) and paste the exact result.
- Manually confirm at least 3 remapped asset paths resolve to real files on
  disk.
- Manually confirm at least 1 masked image from a response-sheet source no
  longer contains the answer marker (describe what you visually verified).

## Report format

- Files changed
- Migration/script added and exact command to run it
- Counts: rows remapped, rows still `missing_asset`, rows newly excluded per
  reason (`unverified_answer`, `answer_integrity_failure`,
  `passage_dependent`, `unmaskable_answer_leak`)
- Tests added
- Exact verification commands and exact results
- Residual risk or follow-ups for Wave 2
