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
