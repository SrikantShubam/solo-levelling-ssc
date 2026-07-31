**Files changed**

[src/ssc_study/baseline_web.py](C:/experiments/ssc/src/ssc_study/baseline_web.py)  
[src/ssc_study/answer_verification.py](C:/experiments/ssc/src/ssc_study/answer_verification.py)  
[src/ssc_study/question_assets.py](C:/experiments/ssc/src/ssc_study/question_assets.py)  
[src/ssc_study/web.py](C:/experiments/ssc/src/ssc_study/web.py)  
[src/ssc_study/db.py](C:/experiments/ssc/src/ssc_study/db.py)  
[src/ssc_study/static/app.js](C:/experiments/ssc/src/ssc_study/static/app.js)  
[tests/test_answer_verification.py](C:/experiments/ssc/tests/test_answer_verification.py)  
[tests/test_baseline_web.py](C:/experiments/ssc/tests/test_baseline_web.py)  
[tests/test_web.py](C:/experiments/ssc/tests/test_web.py)  
[tests/test_phase1_frontend.py](C:/experiments/ssc/tests/test_phase1_frontend.py)  
[scripts/repair_wave3a_mojibake.py](C:/experiments/ssc/scripts/repair_wave3a_mojibake.py)

**Scripts/migrations added with exact commands**

Added migration `17` in [src/ssc_study/db.py](C:/experiments/ssc/src/ssc_study/db.py) for `_app_secrets`. It auto-applies on next `Database(...)` open; no manual migration command is needed.

Added and ran:
```powershell
python scripts/repair_wave3a_mojibake.py
python scripts/reverify_baseline_answers.py
```

**Per-task counts**

Task 1  
Web-safe pool before/after:
- `Quant/DI`: `313 -> 331`
- `Reasoning`: `228 -> 274`
- `English`: `585 -> 631`
- `GK/GA`: `259 -> 331`

Rows recovered by the Task 1 leak-rule change:
- `183`

Leaking-source `page` asset URLs pre-submit:
- `0`

Task 2  
`unverified_answer` in the two target answer-key sources before/after:
- `2020_tier2_kdcampus_answer_key`: `0 -> 0`
- `2024_tier1_appx_answer_key`: `0 -> 0`

Task 3  
Added marks-based scoring to result payload and UI:
- overall and per-section now include `correct`, `wrong`, `skipped`, `percent`, `marks_earned`, `marks_max`
- thresholds remain percent-based and unchanged

Task 4  
Exam token restart proof:
- persisted token secret in DB `_app_secrets`
- verified by test that issues a token, closes DB, reloads `ssc_study.baseline_web`, reopens DB, and successfully submits with the original token

Task 5  
Backup proof:
- full-mode submit now creates `data/backups/study-YYYYMMDD-HHMMSS.db`
- pruning keeps newest `20`
- verified by test that pre-creates `25` backups, runs full submit, then asserts only `20` remain and a fresh backup exists

Task 6  
Mojibake repaired/remaining:
- repaired: `7`
- remaining in the wave3a set: `0`

Per-row Task 6 outcome:
- `2024_tier1_prepp_shift1_q47`: repaired
- `2024_tier1_prepp_shift1_q60`: repaired
- `2024_tier1_prepp_shift1_q61`: repaired
- `2024_tier1_prepp_shift1_q62`: repaired
- `2024_tier1_prepp_shift1_q64`: repaired
- `2024_tier1_prepp_shift1_q70`: repaired
- `2024_tier1_prepp_shift1_q89`: repaired

**Tests added**

Added regression coverage for:
- text-only leaking-source rows with null crop remaining eligible
- leaking-source page URLs never being emitted
- leaking-source page asset endpoint blocking direct `/page` access
- numeric parenthesized answer-key parsing like `1. (2)`
- worked-solution parsing like `Q8 ... Option C`
- marks/wrong/skipped result payload behavior
- token survival across DB reopen plus fresh module import
- backup creation and pruning
- frontend marks/result breakdown rendering

**Exact verification commands and results**

```powershell
git diff --check
```
Result:
- unrelated pre-existing issue reported: `src/ssc_study/scheduler.py:275: new blank line at EOF`

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```
Result:
- `144 passed in 10.83s`

```powershell
uv run pytest -q
```
Result:
- `429 passed, 7 warnings in 53.96s`

Additional focused self-review run:
```powershell
uv run pytest tests/test_answer_verification.py tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```
Result:
- `148 passed, 5 warnings in 8.41s`

**Residual risk**

- `git diff --check` still reports an unrelated pre-existing EOF whitespace issue in `src/ssc_study/scheduler.py`; I did not touch that file.
- `python scripts/reverify_baseline_answers.py` emitted MuPDF `ExtGState 'GS2'` parse warnings from staged PDFs but completed; no rows changed in the two target sources because they were already fully verified in `data/study.db`.
- Full-suite warnings remain the existing PyMuPDF/Google deprecation warnings; no new functional failures remain.