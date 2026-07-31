- Files changed
  - `src/ssc_study/corpus_assets.py`
  - `tests/test_baseline_web.py`
  - `data/study.db`
  - Regenerated/deleted generated `question_crops_masked` outputs under the seven answer-leaking sources.

- Migration/script added and exact command to run it
  - Reused existing script: `scripts/remap_baseline_assets.py`
  - Command run: `uv run python scripts/remap_baseline_assets.py --db data/study.db`
  - Final run output:
    - `rows_seen=2355`
    - `rows_remapped=0`
    - `missing_asset_rows=0`
    - `masked_rows=564`
    - `unmaskable_answer_leak_rows=0`
  - Note: the earlier timed-out run had already updated the DB; the final run verified/regenerated masks from that state.

- Counts
  - Shared/whole-page only:
    - `2020_tier2_kdcampus_answer_key`: 191 rows excluded, 0 masked files remain.
    - `2024_tier1_appx_answer_key`: 38 rows excluded, 0 masked files remain.
  - Per-question only:
    - `2021_tier1_sscportal_shift1_response_sheet`: 100 masked rows.
    - `2024_tier1_sscportal_sep09_shift1_response_sheet`: 100 masked rows.
  - Mixed per-question plus shared/whole-page:
    - `2024_tier2_sscportal_jan18_response_sheet`: 136 masked, 14 excluded.
    - `2024_tier2_sscportal_jan19_response_sheet`: 96 masked, 4 excluded.
    - `2024_tier2_sscportal_jan20_response_sheet`: 132 masked, 18 excluded.
  - Previously masked rows now excluded instead: 265 DB rows have `question_crop_path = NULL`.
  - Preflight `quality_exclusions`: `unmaskable_answer_leak=166`, `passage_dependent=44`, `answer_integrity_failure=8`, `unverified_answer=155`, `mojibake=7`, `duplicate_content=39`, `invalid_options=3`.
  - Corrupted shared masked DB refs: `0`.

- Tests added
  - Added regression coverage for two question rows sharing one `page_images/page_02.png` crop path with marker-like pixels.
  - The test verifies no masked file is produced, both DB rows are nulled, and both rows are counted as `unmaskable_answer_leak`.

- Exact verification commands and exact results
  - `uv run pytest tests/test_baseline_web.py::TestAnswerLeakMasking::test_remap_question_assets_excludes_shared_page_images_without_masking -q`
    - First failed before fix: `assert 2 == 0` for `stats.masked_rows`.
  - `uv run pytest tests/test_baseline_web.py::TestAnswerLeakMasking -q`
    - `6 passed in 1.97s`
  - `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
    - `133 passed in 6.60s`
  - `uv run pytest -q`
    - `409 passed, 2 warnings in 116.08s (0:01:56)`

- Residual risk or follow-ups for Wave 2
  - Shared whole-page assets are now excluded rather than corrupted. Wave 2 still needs real per-question re-cropping/bounding boxes for excluded answer-key/page-image sources.
  - Visual checks performed:
    - Opened KD Campus `page_02.png`: full page with RC passage plus questions 10-20, no answer annotation; masked output is gone and DB rows are excluded.
    - Opened Appx `page_01.png`: multi-question whole page, not a question crop; masked output is gone and DB rows are excluded.
    - Opened regenerated 2021 SSCPortal per-question masked crop: only question content remains above the answer/status annotation.

