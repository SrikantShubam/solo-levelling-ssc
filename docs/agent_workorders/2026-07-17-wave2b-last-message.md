Files changed:
- `src/ssc_study/answer_verification.py`
- `scripts/reverify_baseline_answers.py`
- `tests/test_answer_verification.py`
- `data/study.db` updated by the script

Script added and exact command:
`uv run python scripts/reverify_baseline_answers.py --db data/study.db`

Counts:
- Before: `unverified_answer=155`, `answer_integrity_failure=8`
- Resolved: `22` total
- Resolved from crop/answer-key visual ground truth sources: `6`
- Resolved from staging answer-key PDFs: `16`
- After: `unverified_answer=133`, `answer_integrity_failure=8`
- Still excluded: `141` target rows remain unresolved because no row-level ground truth was recoverable from the available staged/visual evidence.
- Overall current exclusion counts after the update: `unmaskable_answer_leak=189`, `unverified_answer=133`, `answer_integrity_failure=8`, `mojibake=7`, `invalid_options=3`

Manual confirmations:
- `81616113313`: staged `2020_tier1_prepp_shift1.pdf` Q17 showed green option `4. XVVU`; DB set label `4`, text `XVVU`, status `PASS_WITH_EVIDENCE`.
- `26433083436`: staged `2021_tier2_prepp_english.pdf` Q11 showed green option `2. discovered`; DB set label `2`, text `discovered`.
- `2024_tier1_appx_answer_key_q8`: staged answer-key table showed Q8 = `C`; DB mapped that to label `3`, text `135 : 17`.
- Spot check: `2024_tier2_sscportal_jan20_response_sheet.pdf` Q1 showed green option `3. 1330`.

Tests added:
- `tests/test_answer_verification.py` covers green-span answer extraction from a real staged PDF and DB promotion from row-level answer-key evidence.

Exact verification commands and results:
- `uv run pytest tests/test_answer_verification.py -q` -> `2 passed, 5 warnings`
- `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q` -> `138 passed in 3.86s`
- `uv run pytest -q` -> `417 passed, 7 warnings in 39.12s`

Residual risk for later waves:
- The 8 integrity failures are still excluded because the available row-level evidence did not confirm which field is correct.
- Some newly verified response-sheet rows remain learner-unsafe due to `unmaskable_answer_leak`; answer correctness is fixed, but serving safety is still governed by Wave 1/1b masking rules.
- The verifier uses deterministic PDF color spans / answer-key tables from staged source PDFs, not model reasoning. Rows without that evidence remain excluded.

