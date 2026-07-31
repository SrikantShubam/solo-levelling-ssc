Files changed: `src/ssc_study/modality_recrop.py`, `scripts/repair_modalities_and_recrop.py`, `tests/test_crops_utils.py`, `data/study.db`.

Scripts added and exact commands to run them: `uv run python scripts/repair_modalities_and_recrop.py --db data/study.db`.

Counts: modality corrections made: `table_di -> text_only: 91`, `math_formula -> text_only: 176`, `dice -> text_only: 28`, `graph_chart -> text_only: 52`, `visual_options -> text_only: 13`. Total: `360`.

Counts: recropped/masked/still-excluded per source: `2020_tier2_kdcampus_answer_key`: `0` retained recropped/masked, `191` still excluded. `2024_tier1_appx_answer_key`: `0` retained recropped/masked, `38` still excluded. Final script exclusion reasons: `numbered_boundary_not_found: 189`, `masked_crop_too_small: 38`, `answer_marker_not_found: 2`. DB has `0` unmasked crop refs for both target sources.

Tests added: focused tests for English modality false positives, explicit question-number anchor parsing, non-leading number rejection, and stem-only masked crop rejection.

Exact verification commands and results: `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py tests/test_crops_utils.py -q` -> `145 passed in 9.53s`. `uv run pytest -q` -> `421 passed, 7 warnings in 142.32s (0:02:22)`.

Residual risk: the existing shared masking heuristic is not reliable for these two PDFs’ generated crop format. Visual self-review found generated crops either lost options or cut too aggressively, so the script correctly leaves all 229 target rows excluded rather than serving unsafe or incomplete images. Manual 5-per-source masked-crop confirmation could not be completed because no generated crop survived the content-preservation gate.

