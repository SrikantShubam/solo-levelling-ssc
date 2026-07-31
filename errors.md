## 2026-05-24 P2 Empty-Page Failure

- Symptom: Several PDFs in `extraction_reruns/p2_all_pdfs_20260524` showed `0` or very low question counts.
- Root cause: Page-level Gemini failures, especially `ResourceExhausted: 429`, were persisted as empty page JSON and then merged as valid extraction output.
- Fix: classify page failures explicitly, preserve failure metadata through merge, set `INFRA_FAILURE`/`QUARANTINE` instead of generic `FAIL`, and add a fallback hook for failed pages.
- Verification: `python -m pytest -q` passed with `43 passed`.

## 2026-05-24 Controlled Fallback Pilot Failure

- Symptom: Controlled rerun of `2019_tier1_prepp_shift1.pdf` with `--allow-fallback` extracted only 13/100 questions.
- Root cause: Gemini primary hit quota after early pages; NIM fallback model `microsoft/phi-4-multimodal-instruct` returned HTTP 400 `DEGRADED function cannot be invoked` for failed pages.
- Fix: fallback failures are now classified as `fallback_provider_unavailable` instead of keeping `failure_type: null`.
- Verification: `python -m pytest -q` passed with `43 passed`.

## 2026-05-25 NIM-First Screening Outcome

- Symptom: NIM-first full-PDF retry remained non-viable even after adding native NIM-primary extraction.
- Evidence:
  - `mistralai/mistral-medium-3.5-128b` timed out on early full-PDF pilot pages and scored poorly on sampled-page comparison.
  - `meta/llama-4-maverick-17b-128e-instruct` was the best sampled NIM model but still only reached 0.50 correct-answer accuracy on the 2023 sample pages.
  - lighter NIM vision candidates returned effectively zero usable extraction on the sampled pages.
- Consequence: do not do broad full-PDF NIM reruns yet; move to targeted failed-page repair instead.
- Verification: `python -m pytest -q` passed with `44 passed`.

## 2026-07-11 Manual Baseline Web Readiness Failure

- Symptom: A real 200-question baseline/mock run exposed repeated questions, mojibake text, non-rendering image/visual questions, and skipped questions caused by missing learner knowledge.
- Root cause: Phase 1 web baseline preflight/start treated raw non-holdout section counts as readiness. It did not require a web-safe unique pool, so duplicate normalized content, mojibake rows, invalid options, and visual/table questions unsupported by the web renderer could enter the baseline.
- Fix: `src/ssc_study/baseline_web.py` now builds baseline starts and preflight readiness from web-safe unique candidates only, reports raw counts and quality exclusions, rejects dirty/underfilled pools, and keeps answer leakage behavior unchanged.
- Verification: `uv run pytest tests/test_baseline_web.py -q` passed with `29 passed`; `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q` passed with `108 passed`.

## 2026-07-11 Baseline Cannot Clear Selected Answer

- Symptom: During the web baseline exam, once an option was selected there was no UI path to leave that question unattempted again.
- Root cause: The frontend state and backend submit path already supported `user_answer: null`, but the exam UI only provided option selection and navigation controls; it never deleted `state.answers[question_id]`.
- Fix: Added a `Clear Response` control to the question footer and a JS handler that deletes the current answer, saves the draft, and refreshes the question/nav state.
- Verification: `uv run pytest tests/test_phase1_frontend.py::TestStatic::test_exam_ui_can_clear_an_answer_back_to_unattempted -q` passed.

## 2026-07-13 Smoke Baseline Incomplete Stem

- Symptom: Smoke baseline served `2024_tier1_appx_answer_key_q29`, whose stem began mid-sentence: `pair does not belong to that group? ... (23/09/2024 SHIFT-3)`.
- Root cause: The web-safe gate checked option count/labels, mojibake, duplicates, and missing assets, but did not reject orphaned continuation stems or blank option text. Answer-key appendix rows can contain partial fragments while still having four option labels.
- Fix: `baseline_web.py` now rejects lower-case continuation stems as `incomplete_stem` and treats blank option text as `invalid_options`. The row remains in the DB for later repair/backfill but cannot enter the web baseline pool.
- Verification: targeted regression tests passed with `4 passed`; web/db slice passed with `129 passed`; full suite passed with `395 passed, 2 warnings`.

Follow-up correction: the first incomplete-stem heuristic was too broad because it treated any row whose first alphabetic character was lowercase as incomplete. That falsely excluded valid stems beginning with currency, formulas, blanks, or symbols. The detector is now narrowed to known continuation prefixes only, and the three true split rows (`q8`, `q22`, `q29` in `2024_tier1_appx_answer_key`) were reconstructed from adjacent DB/source PDF evidence. Full suite verification after repair: `396 passed, 2 warnings`.
