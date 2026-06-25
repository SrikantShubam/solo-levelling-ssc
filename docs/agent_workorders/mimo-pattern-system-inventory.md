# Pattern System Inventory

## 1. Phase Drift

| Document | Phase 2 | Phase 2c | Phase 3 | Phase 3b |
|----------|---------|----------|---------|----------|
| Plan.md | Corpus, holdout, atlas, shared archetypes, fact cards | Not mentioned | Diagnostic grinding: probe, infer failure, route | Not mentioned |
| README.md | ✅ complete | Not listed | 🔜 upcoming | Not listed |
| phase3-scope-breakdown.md | Paper-level pattern recognition belongs here | Recommended: model-based paper pattern discovery | User-error diagnostics against existing atlas | Read-only extension first; do not mutate queues/gates |
| Current code | Keyword/rule-based archetypes, fact cards, queues, gates | Nothing implemented | phase3.py (orchestration), phase3_eval.py (read-only eval) | Guardrails written, no code yet |

**Drift summary:** Plan.md puts pattern mining in Phase 2/3. README marks Phase 2b done, Phase 3 upcoming. phase3-scope-breakdown recommends Phase 2c for exam patterns, Phase 3b for user-error augmentation. Current code has no model-based pattern discovery at all.

## 2. Modules That Classify or Use Patterns

| Module | Pattern role | Key functions |
|--------|-------------|---------------|
| `archetypes.py` | Static keyword/rule-based archetype classifier | `classify_question()`, `assign_archetypes()`, `ensure_default_archetypes()`, `get_weak_archetypes()` |
| `cards.py` | Regex-based fact extraction from GK/GA questions | `extract_fact()`, `generate_fact_cards()`, `get_active_fact_cards()`, `cbic_specific_accuracy()`, `needs_cbic_focus()` |
| `queues.py` | Uses archetype accuracy to route questions | `QueueManager.get_batch()` with active, sm2_review, remediation, boss_fight queues |
| `gates.py` | Routes archetypes based on probe accuracy | `evaluate_probe()`, `classify_probe_attempts()`, `get_tier2_readiness()` |
| `phase3.py` | Deterministic orchestration loop for diagnostics | `plan_next_action()`, `run_phase3_loop()` |
| `phase3_eval.py` | Read-only comparison of predicted vs actual routes | `evaluate_phase3_predictions()` |

## 3. Tests Covering Those Modules

| Test file | Module | Coverage |
|-----------|--------|----------|
| `test_archetypes.py` | `archetypes.py` | Keyword classification, ensure defaults, assign, weak detection, summary, questions |
| `test_cards.py` | `cards.py` | Fact extraction (capital, who, when, where, superlative), generation, due cards, stats, expired exclusion, CBIC accuracy |
| `test_queues.py` | `queues.py` | Active/SM-2/boss_fight batches, holdout exclusion, tier/section filters, audit pause blocking |
| `test_gates.py` | `gates.py` | Probe evaluation (4 routes), probe candidates, probe requirements, tier accuracy, tier-2 readiness |

**Note:** `phase3.py` and `phase3_eval.py` have no dedicated test files found in `tests/`.

## 4. Keyword/Rule-Based Pattern Logic

All pattern classification in the codebase is keyword/rule-based:

| Location | Mechanism |
|----------|-----------|
| `archetypes.py:37-389` | 40+ `ARCHETYPE_DEFS` with compiled regex keyword sets per archetype |
| `archetypes.py:402-426` | `classify_question()` counts regex matches per section, picks highest |
| `cards.py:37-284` | 8 ordered regex extractors (`_capital_fact`, `_who_fact`, `_when_fact`, etc.) |
| `cards.py:274-284` | First-match-wins extractor priority list |
| `gates.py:305-329` | `_detect_concept_gap()` counts same-tag wrong answers (>50% = gap) |

No LLM, embedding, or statistical clustering is used for pattern classification.

## 5. User-Performance Diagnostics Entry Points

| Location | What it does |
|----------|-------------|
| `gates.py:114-135` | `classify_probe_attempts()` — routes by accuracy thresholds (80%+, 50-79%, <50%) |
| `gates.py:305-329` | `_detect_concept_gap()` — heuristic: same concept_tag on >50% of wrong answers |
| `phase3.py:47-87` | `plan_next_action()` — chooses probe, remediation, boss_fight, or sm2_review |
| `phase3.py:90-135` | `run_phase3_loop()` — bounded loop executing up to `max_steps` actions |
| `phase3_eval.py:37-112` | `evaluate_phase3_predictions()` — compares persisted prediction vs recent actuals |
| `cards.py:613-653` | `needs_cbic_focus()` — detects CBIC readiness gap vs aggregate GA |

**Entry point gap:** `_detect_concept_gap()` is purely heuristic. No model-based failure-cause inference exists.

## 6. Gaps Relevant to Phase 2c (Exam-Pattern Intelligence)

| Gap | Evidence |
|-----|----------|
| No model-based paper pattern discovery engine | phase3-scope-breakdown.md: "Not currently done: A model-based paper pattern discovery engine" |
| No learned pattern registry | No code or schema for discovered patterns |
| No confidence-calibrated pattern hypotheses | No confidence/scoring on discovered patterns |
| No holdout-based evaluation of discovered patterns | phase3-scope-breakdown.md recommends this before promotion |
| Atlas normalization incomplete | README caveat 2: "Normalize atlas to 160-240 archetypes is not complete" |
| Archetypes are static definitions | `ARCHETYPE_DEFS` is hardcoded; no mechanism to discover new archetypes from data |
| No cross-year pattern trend analysis | No code analyzes how archetype frequency or difficulty shifts across 2019-2024 |

## 7. Gaps Relevant to Phase 3 (User-Error Intelligence)

| Gap | Evidence |
|-----|----------|
| Concept gap detection is heuristic only | `gates.py:305-329` — tag-counting heuristic, no model |
| No failure cause taxonomy | Only `concept_gap: bool` exists; no structured failure categories |
| No model-based arbitration | Plan.md mentions "after local Qwen exists, arbitration can be batched" — not implemented |
| No student label richness | `attempts.student_label` exists in schema but `_detect_concept_gap` only uses `is_correct` and `concept_tag` |
| phase3.py and phase3_eval.py have no tests | No `test_phase3.py` or `test_phase3_eval.py` found |
| eval output doesn't feed back | phase3_eval.py is read-only by design; no mechanism to adjust queues/gates from eval results |
| No time-pressure vs concept-gap discrimination | `_detect_concept_gap` checks concept_tag but ignores `time_spent_seconds` |

## 8. Summary

**What exists:** 40+ keyword archetypes, 8 fact-card extractors, 4 queue types, probe-based routing, deterministic Phase 3 orchestration, read-only evaluation, tier-specific accuracy tracking, expired-card exclusion, CBIC-specific readiness.

**What's missing:** Model-based pattern discovery (Phase 2c), model-assisted failure diagnosis (Phase 3), pattern registry, holdout-validated pattern promotion, phase3 tests, and any mechanism for eval output to influence scheduling.
