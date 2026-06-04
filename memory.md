## 2026-05-24 Extraction Stabilization

- P2 remains the active extraction pipeline; P1 is deprecated and only useful for historical/manual comparison.
- Root cause of many P2 batch failures was not pure OCR quality: Gemini quota errors were cached as page JSON with `questions: []`, then merged as if they were real empty pages.
- Extraction pages now carry `page_status`, `failure_type`, `provider`, `model`, `retryable`, `fallback_attempted`, and `fallback_used` metadata.
- Merge output now carries `structural_status` and `structural_failure_reasons`; `api_quota_or_rate_limit`, `model_refusal`, and JSON/schema failures are not treated as ordinary extraction misses.
- `ssc-corpus extract-pdf` now supports opt-in page fallback with `--allow-fallback --fallback-model <nim-model>`; fallback is never automatic.
- `ssc-corpus extract-pdf` now also supports provider selection, including NIM/OpenAI-compatible primary extraction.
- Added `ssc-corpus retry-failed-batch` and `ssc-corpus compare-phases` for patch reruns and phase reporting.
- Current NIM screening result: `meta/llama-4-maverick-17b-128e-instruct` is the strongest tested NIM model, but still too slow for broad full-PDF reruns; lighter NIM models collapsed on completeness.
- Generated investigation dossier: `reports/p2_failure_investigation_20260524.md` and `.json`.
