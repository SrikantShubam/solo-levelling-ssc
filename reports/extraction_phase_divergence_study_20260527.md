# Extraction Phase Divergence Study — 2026-05-27 Update

## On Track (Convergent With Plan)

| Plan Requirement | Current Status | Evidence |
|---|---|---|
| Precision layer that routes uncertain answers to review | Implemented in P2 — green-answer evidence, canonical arbitration, review gating | `extraction.py`, QC reports show `PASS_WITH_MANUAL_REVIEW` / `BLOCKED` routing |
| Visual/math/table questions retain reviewable assets | Page images, crops, HSV evidence preserved in every batch run | `assets/` per extraction run |
| Multi-provider extraction path (not just Gemini) | `patch2` code added: NIM/OpenAI-compatible primary + fallback support | `extraction.py` — `ssc-corpus extract-pdf --provider` |
| Structural failure classification | Pages carry `page_status`, `failure_type`, `provider`, `model`, `retryable`, `fallback_*` metadata | `memory.md`, merged JSON schema |
| Phase comparison tooling | `ssc-corpus compare-phases` and `reporting_compare.py` exist | `cli.py`, `reporting_compare.py` |
| Failed-batch retry command | `ssc-corpus retry-failed-batch` implemented | `batch_retry.py`, `cli.py` |

## Diverged (Off Plan)

| Plan Expectation | Reality | Gap |
|---|---|---|
| Precision-over-recall at answer level | 9/19 PDFs had <10 questions extracted; 6 had 0. The loss is at document level, not answer level. | *Document-level structural stability* was not planned for |
| Gemini as sole carrier is sufficient | 9 PDFs failed primarily from quota exhaustion (`api_quota_or_rate_limit`) — an infra failure masked as extraction failure | *Provider diversity* is needed, not just precision — but NIM alternatives are too slow or too inaccurate |
| One-pass corpus-wide extraction is feasible | Source heterogeneity is much worse than expected: response sheets, coaching PDFs, answer keys, notices all need different handling | *Document-class triage* must precede extraction |
| Output suitable for ground-truth corpus freeze | Only 4/9 Tier-1 PDFs had full 100-question extraction; 4 accepted artifacts in corpus dossier | *Corpus freeze is premature* — extraction is still iterative |
| Model refusal is budget-limited | `2020_tier2_kdcampus_answer_key.pdf` blocked by copyright refusal — orthogonal to cost | *Content policy* is a real operational constraint not addressed in plan |
| SQLite database with `questions`, `archetypes`, etc. | No `.sqlite` or `.db` file exists anywhere in the workspace | *Data is still in JSON/MD files* — the planned database layer hasn't started |
| Extraction flows into atlas/clustering | Clustering, archetype normalization, holdout reservation not started | *Atlas phase is blocked* by extraction instability |
| 160–240 archetypes normalized | No archetype work begun | *Archetype phase has zero progress* |

## What Was Added That Wasn't In The Plan

| Unplanned Work | Justification |
|---|---|
| Full 19-PDF corpus-wide rerun (`p2_all_pdfs_20260524`) | Uncovered the document-class heterogeneity problem |
| P2 failure investigation + dossier | Diagnosed empty-page root cause |
| NIM model screening (7 models across 3 trials) | Sought provider diversity; found none production-ready |
| Document-class classification (response_sheet, coaching, tier2_section, answer_key, notice) | Emerged as necessary from failure analysis |
| Controlled fallback pilot + stabilization | Tested fallback path; found fallback model also failed |
| Gemini day3 retries (standard + failed-file subset) | Partial recovery — 2023 tier1 went from 0→100 questions; 5/6 Tier-2 pdfs still at 0 |
| `memory.md` and `errors.md` tracking | Needed for cross-session continuity on complex infra debugging |

## Current Extraction Coverage (After All Retries)

| Bucket | Count | Detail |
|---|---|---|
| Structurally complete (100/100) | 4 Tier-1 PDFs | 2019, 2020, 2021 (response sheet), 2022 — all `BLOCKED` with review items |
| Recovered by day3 retry (0→100) | 1 PDF | 2023_tier1_prepp_shift1 — `BLOCKED` |
| Still at 0 or near-0 questions | 6 PDFs | All Tier-2 sheets + 2024_tier1_sscportal_sep09 — still `FAIL` |
| Usable-with-review but incomplete | 2 Tier-2 section booklets | 2019 (200q), 2021 (200q) — `BLOCKED` |
| Quarantine/refusal | 2 PDFs | 2020_tier2_answer key (refusal), 2024_tier1_appx_answer_key (non-question) |
| Partial extraction (<100) | 4 PDFs | 2021_tier1 (91q), 2022_tier2 (81q), 2024_tier2 (7q), 2024_tier2_jan20 (9q) |

## Bottom Line

**The extraction phase is ~40% done against the original plan.**

The precision-and-review pipeline (P2) works correctly on well-behaved PDFs — that part is on track. But the plan assumed all PDFs would be well-behaved, which turned out wrong. The plan's extraction phase had no:
- document-class triage
- per-class extraction benchmarks
- provider diversity contingency
- corpus acceptance gate

These are now the real prerequisites before the plan's downstream steps (SQLite, atlas, clustering) can start. The recommended next step per the prior divergence study — build a document-class triage layer and per-class extraction benchmarks — has not yet been executed. The bottleneck has shifted from *answer precision* to *document routing and infra resilience*.
