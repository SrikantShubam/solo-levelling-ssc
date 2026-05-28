# NIM-First Retry And Phase Comparison Report

Date: 2026-05-25

## Summary

This report compares `P1 | P2 | P2 patch1 | patch2` using the actual artifacts in the workspace and the NIM-first retry work completed in this session.

Current result:

- `P1` and `P2` historical results are available.
- `P2 patch1` corpus-wide rerun results are available.
- `patch2` code is implemented for NIM-first extraction and failed-batch retry, but a full failed-set rerun was not completed in this session because the NIM models that were tested did not meet both latency and extraction-quality requirements.

The NIM-first conclusion from the current evidence is simple:

- `meta/llama-4-maverick-17b-128e-instruct` is the best NIM candidate tested so far.
- It is still too slow for a broad full-PDF failed-batch rerun in the current setup.
- Smaller/faster NIM candidates collapsed on completeness.

## Phase Definitions

| Label | Artifact Basis | Carrier | QC Layer | Key Limitation |
|---|---|---|---|---|
| `P1` | Historical native P1 comparison outputs | Gemini page-image extraction | none beyond raw shape checks | raw LLM answers only; no deterministic evidence |
| `P2` | `extraction_batch/tier1_gemini` | Gemini page-image extraction | precision layer, crops, HSV evidence, canonical review | structurally good on original Tier-1 batch, but still Gemini-dependent |
| `P2 patch1` | `extraction_reruns/p2_all_pdfs_20260524` | Gemini page-image extraction | same precision layer | quota/schema/refusal failures mixed into low/zero-question outputs |
| `patch2` | code added in this session | provider-selectable primary carrier, including NIM-first | same precision layer plus structural failure metadata | no broad NIM model passed both speed and quality gates yet |

## Architecture Changes By Phase

| Phase | What Changed |
|---|---|
| `P1 -> P2` | Added deterministic green-answer evidence, question/option crops, modality flags, canonical answer arbitration, and review gating. |
| `P2 -> P2 patch1` | Broadened rerun scope from original Tier-1 batch to corpus-wide rerun, but still relied on Gemini as the primary carrier. |
| `P2 patch1 -> patch2` | Added page-level `page_status`, `failure_type`, `provider`, `model`, `retryable`, `fallback_attempted`, `fallback_used`, merged `structural_status`, NIM/OpenAI-compatible primary extraction support, `retry-failed-batch`, and phase-comparison/reporting helpers. |

Implemented files:

- `src/ssc_corpus/extraction.py`
- `src/ssc_corpus/cli.py`
- `src/ssc_corpus/batch_retry.py`
- `src/ssc_corpus/reporting_compare.py`
- `src/ssc_corpus/extraction_investigation.py`

## Results Comparison

### Corpus-Level Outcome

| Phase | Scope | Result |
|---|---|---|
| `P1` | historical Tier-1 native comparison artifacts only | available only for 2019 and isolated 2021 comparison outputs |
| `P2` | original Tier-1 precision batch | 6/6 PDFs structurally complete |
| `P2 patch1` | 19-PDF corpus rerun | 7 usable-with-review, 9 rerun-needed, 2 fallback-needed, 1 quarantine |
| `patch2` | NIM-first retry | tooling complete, model screening complete, no full failed-set batch completed |

### Representative Side-By-Side: 2019 Tier-1

Source PDF: `2019_tier1_prepp_shift1.pdf`

| Phase | Questions | QC / Coverage | Notes |
|---|---:|---|---|
| `P1` | 100 | raw LLM answer coverage `100/100` | from `pipeline_1_vs_2_comparison.md` |
| `P2` | 100 | canonical auto-answer coverage `98/100`; 2 blocked for manual review | precision layer reduced false certainty |
| `P2 patch1` | 100 | `BLOCKED` | structurally complete, but from the pre-stabilization corpus-wide rerun |
| `patch2` | not rerun with NIM-first | n/a | no 2019 NIM-first rerun artifact exists yet |

### Representative Side-By-Side: 2023 Tier-1

Source PDF: `2023_tier1_prepp_shift1.pdf`

| Phase | Questions | QC / Coverage | Notes |
|---|---:|---|---|
| `P1` | 100 | `PASS_WITH_MANUAL_REVIEW` | original historical batch output |
| `P2` | 100 | `BLOCKED` with `23` blocking reviews | precision layer accepted less automatically than P1 |
| `P2 patch1` | 0 | `FAIL` | primary failure type `api_quota_or_rate_limit` |
| `patch2` | no merged PDF output | pilot incomplete | NIM-first pilot with `mistralai/mistral-medium-3.5-128b` timed out after only 3 page JSON files |

## NIM-First Screening Results

Reference sample:

- PDF: `2023_tier1_prepp_shift1.pdf`
- Pages: `1, 5, 17, 28`
- Reference output: historical merged questions from original Tier-1 batch

### Stronger NIM Candidates

| Model | Correct Acc | Chosen Acc | Option Shape | Text Similarity | Outcome |
|---|---:|---:|---:|---:|---|
| `mistralai/mistral-medium-3.5-128b` | 0.12 | 0.50 | 0.50 | 0.50 | too weak and too slow |
| `meta/llama-4-maverick-17b-128e-instruct` | 0.50 | 1.00 | 1.00 | 0.99 | best current NIM candidate, but still not high-confidence enough for batch promotion |
| `google/gemma-3n-e4b-it` | 0.12 | 0.50 | 0.12 | 0.35 | not viable |

Source: `extraction_trials/model_comparison_2023_nim_primary_candidates/model_comparison_report.md`

### Lighter NIM Candidates

| Model | Correct Acc | Chosen Acc | Option Shape | Text Similarity | Outcome |
|---|---:|---:|---:|---:|---|
| `meta/llama-3.2-11b-vision-instruct` | 0.00 | 0.00 | 0.00 | 0.00 | unusable |
| `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | 0.00 | 0.00 | 0.00 | 0.00 | unusable |

Source: `extraction_trials/model_comparison_2023_nim_light_candidates/model_comparison_report.md`

## NIM-First Pilot

Pilot attempted:

- PDF: `2023_tier1_prepp_shift1.pdf`
- Primary model: `mistralai/mistral-medium-3.5-128b`
- Output folder: `extraction_reruns/nim_primary_pilot_20260524/2023_tier1_prepp_shift1`

Observed result:

- page 1: `provider_timeout`
- page 2: `provider_timeout`
- page 3: extracted successfully
- command timed out before a merged PDF result could be produced

This means `patch2` is currently a tooling and screening milestone, not yet a promoted corpus rerun.

## Practical Conclusion

The request to rerun the failed set with NIM first is only partially satisfied today:

- completed: NIM-first extraction path
- completed: failed-batch retry command
- completed: phase-comparison tooling
- completed: NIM model screening and one real NIM-first full-PDF pilot
- not completed: full failed-set `patch2` rerun

The reason is not missing code anymore. The blocker is model viability:

- the only NIM candidate that preserved option shape and chosen-answer quality well enough was `meta/llama-4-maverick-17b-128e-instruct`
- that model is still too slow and not accurate enough on correct-answer extraction to justify a broad failed-batch rerun without further routing or prompt work

## Recommended Next Step

Use `meta/llama-4-maverick-17b-128e-instruct` only for targeted page repair, not whole-PDF reruns.

The next engineering move should be:

1. add targeted failed-page repair instead of full-PDF NIM rerun
2. route only pages marked `api_quota_or_rate_limit` or `provider_timeout`
3. merge repaired pages back into `P2 patch1` runs
4. regenerate the phase comparison after patched-page repair, not after another full-PDF retry
