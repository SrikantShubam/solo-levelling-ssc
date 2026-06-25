# Mimo Round 2 — Pattern System Inventory

## 1. Current Deterministic Pattern System

### Modules and Current Behavior

| Module | File | Lines | What It Does |
|--------|------|-------|--------------|
| `archetypes.py` | `src/ssc_study/archetypes.py` | 706 | 40+ keyword-based archetype classifiers across 5 SSC sections. Regex keyword matching assigns questions to archetypes (Number Systems, Algebra, Geometry, etc.). Provides `classify_question()`, `assign_archetypes()`, `ensure_default_archetypes()`, `get_weak_archetypes()`, `get_archetype_questions()`, `get_archetype_summary()`. |
| `cards.py` | `src/ssc_study/cards.py` | 665 | GK/GA fact card extraction via ordered regex extractors. Extracts who/what/which/when/where/how-many/superlative patterns from question text. Provides `extract_fact()`, `generate_fact_cards()`, `get_due_fact_cards()`, `get_fact_card_stats()`, `get_active_fact_cards()`, `get_expired_cards()`, `cbic_specific_accuracy()`, `needs_cbic_focus()`. |
| `queues.py` | `src/ssc_study/queues.py` | 320 | Four queue types: active (general non-holdout pool), sm2_review (due-for-review via scheduler), remediation (weak-archetype questions), boss_fight (50-79% accuracy band, timed practice). `QueueManager` class with `get_batch()`, `get_queue_sizes()`, `get_available_queues()`. Boss-fight blocked during notification audit. |
| `gates.py` | `src/ssc_study/gates.py` | 330 | Archetype unlock gates. `evaluate_probe()` routes archetypes: 80%+ → SM-2, 50-79% → boss fight, <50% with concept gap → remediation, <50% without concept gap → high-priority boss. `classify_probe_attempts()` for pure classification. `get_probe_candidates()` finds archetypes needing probing. `run_probe()` returns exactly 10 questions. `get_archetype_accuracy_by_tier()` and `get_tier2_readiness()` for shared Reasoning tier tracking. |
| `readiness.py` | `src/ssc_study/readiness.py` | 548 | Readiness dashboard aggregating 12+ conditions: foundation pulse accuracy, Tier-1/Tier-2 archetype mastery, module floors (Math, Reasoning, English, GA, CK), shared Reasoning Tier-2 readiness, CBIC card accuracy, mock performance/diversity, section floor, elimination skill, readiness trend. `compute_readiness()` returns `ReadinessReport` with pass/fail per condition. |
| `phase3.py` | `src/ssc_study/phase3.py` | 366 | Bounded deterministic Phase 3 orchestration loop. `plan_next_action()` chooses next action: probe → remediation → boss_fight → sm2_review → stop. `run_phase3_loop()` runs up to max_steps with archetype exclusion tracking. Actions are `Phase3Action` dataclasses with type, reason, question_count, question_ids, target_archetype. |
| `phase3_eval.py` | `src/ssc_study/phase3_eval.py` | 161 | Read-only predicted-vs-actual route comparison. `evaluate_phase3_predictions()` compares persisted pipeline prediction against recent actual outcomes. Uses latest non-holdout attempt window (10 attempts). Reports signal strength: insufficient (<5), weak (5-9), stable (10+). Read-only: does not mutate any tables. |

### Architecture Summary

The deterministic pattern system is a keyword/regex-based pipeline:

1. **Classification** (`archetypes.py`): Questions are classified into 40+ archetypes via keyword matching.
2. **Fact Extraction** (`cards.py`): GK/GA questions produce front/back memory cards via regex extractors.
3. **Queue Routing** (`queues.py`): Four queue types serve questions based on state (active, due, weak, partially-mastered).
4. **Gate Evaluation** (`gates.py`): Probe sessions route archetypes to SM-2, boss fights, remediation, or high-priority boss.
5. **Readiness Scoring** (`readiness.py`): 12+ conditions aggregated into a single ready/not-ready report.
6. **Orchestration** (`phase3.py`): Bounded loop chooses next diagnostic action deterministically.
7. **Evaluation** (`phase3_eval.py`): Read-only comparison of predicted vs actual routes.

## 2. Current Test Coverage

### Test Files

| Test File | Lines | What It Covers |
|-----------|-------|----------------|
| `tests/test_archetypes.py` | 160 | `classify_question()` keyword matching (Algebra, Blood Relations, Geography, unmatched, options text). `ensure_default_archetypes()` creation and idempotency. `assign_archetypes()` DB updates. `get_weak_archetypes()` empty state. `get_archetype_summary()` stats. `get_archetype_questions()` empty state. Archetype definition uniqueness and keyword presence. |
| `tests/test_cards.py` | 176 | `extract_fact()` for capital, who-discovered, when-established, where-is, superlative, non-GK/GA, unmatched. `generate_fact_cards()` integration, persistence, idempotency. `get_due_fact_cards()` empty and due states. `get_fact_card_stats()` zero and counted states. Expired card exclusion and queryability. CBIC accuracy and focus checks. |
| `tests/test_queues.py` | 77 | `QueueManager.get_batch()` for active, sm2, unknown type. `get_queue_sizes()` structure. `get_available_queues()` listing. Active queue excludes holdout. Tier and section filters. Boss-fight blocked during notification audit. |
| `tests/test_gates.py` | 110 | `evaluate_probe()` routing: high accuracy → SM-2, medium → boss fight, low with concept gap → remediation, low without concept gap → high-priority boss. `get_probe_candidates()` requires archetypes in DB. `run_probe()` requires enough questions. `get_archetype_accuracy_by_tier()` zero state. `get_tier2_readiness()` not-ready state. |
| `tests/test_phase3.py` | 271 | `plan_next_action()` prefers probe candidates, uses remediation when no probe, prefers boss_fight before sm2, stops when no eligible work, skips probe when count below probe size, invariant to question ID order. `run_phase3_loop()` respects max_steps, dry_run does not create sessions, does not repeat archetype across steps. |
| `tests/test_phase3_eval.py` | 451 | `evaluate_phase3_predictions()` reports match for boss_fight, reports mismatch against recent actuals, marks probe without actual outcome, is read-only (snapshot unchanged), ignores holdout attempts, uses latest attempt window not all historical, route boundaries match gate classifier, reports high_priority_boss without concept gap, reports signal strength (stable/weak/insufficient). |

### Phase 3 Coverage Specifics

- **`test_phase3.py`**: 8 tests covering `plan_next_action()` and `run_phase3_loop()`. Tests probe preference, remediation fallback, boss_fight priority, stop condition, threshold behavior, invariance, max_steps, dry_run, and no-archetype-repeat.
- **`test_phase3_eval.py`**: 10 tests covering `evaluate_phase3_predictions()`. Tests match/mismatch, probe without outcome, read-only guarantee, holdout exclusion, latest window, route boundaries, high_priority_boss, and signal strength levels.

## 3. Current Gaps

### Missing Model-Based Paper Pattern Discovery

- No LLM or model-based engine discovers exam-paper patterns (section mix, archetype frequency, tier/year distribution).
- Current archetype classification is purely keyword/regex-based (`archetypes.py`).
- `Plan.md` mentions "After local Qwen exists, arbitration can be batched to the model" for failure cause inference, but this is not implemented.
- No model generates blueprint-level mock guidance from corpus analysis.

### Missing Model-Assisted Failure Taxonomy

- Current failure classification in `gates.py` uses rule-based concept gap detection (`_detect_concept_gap()`): checks if >50% of wrong answers share the same concept_tag.
- No model arbitrates failure causes (student label + rule inference + manual arbitration per Plan.md).
- `phase3_eval.py` compares predicted vs actual routes but does not classify *why* failures occurred.

### Missing Pattern Registry

- No centralized registry stores discovered patterns with confidence, evidence, and promotion status.
- Archetypes are defined in `ARCHETYPE_DEFS` list in `archetypes.py` — a static code constant, not a runtime registry.
- No pattern lifecycle tracking (discovery → validation → promotion → regression test).

### Missing Runtime Consumption of Pattern Reports by Design

- `phase3.py` orchestrates diagnostic actions but does not consume pattern reports.
- `phase3_eval.py` evaluates routes but does not feed results back into pattern discovery.
- No runtime path exists for model-discovered patterns to influence queues, gates, readiness, or mock generation.
- `pattern-intelligence-guardrails.md` explicitly requires read-only-first implementation, but no advisory layer exists yet.

## 4. Round One Corrections

### Correction 1: "phase3.py and phase3_eval.py have no dedicated test files"

**Round-1 claim**: Phase 3 orchestrator and evaluation modules lack test coverage.

**Correction**: Both `tests/test_phase3.py` (271 lines, 8 tests) and `tests/test_phase3_eval.py` (451 lines, 10 tests) exist on canonical main. Tests cover probe preference, remediation fallback, boss_fight priority, stop conditions, max_steps, dry_run, read-only guarantee, holdout exclusion, route boundary matching, and signal strength reporting.

**Evidence**: `C:\experiments\ssc\tests\test_phase3.py` and `C:\experiments\ssc\tests\test_phase3_eval.py` on canonical main.

### Correction 2: "Phase 3 is 🔜 upcoming"

**Round-1 claim**: Phase 3 is entirely future work.

**Correction**: Phase 3 orchestrator (`phase3.py`, 366 lines) and Phase 3 evaluation (`phase3_eval.py`, 161 lines) already exist on canonical main. `plan_next_action()` and `run_phase3_loop()` provide bounded deterministic orchestration. `evaluate_phase3_predictions()` provides read-only predicted-vs-actual comparison. What remains is model-based pattern discovery (Phase 2c) and optional advisory layer (Phase 3b).

**Evidence**: `C:\experiments\ssc\src\ssc_study\phase3.py:47` (`plan_next_action`), `C:\experiments\ssc\src\ssc_study\phase3_eval.py:37` (`evaluate_phase3_predictions`).

### Correction 3: "readiness.py is missing or incomplete"

**Round-1 claim**: Readiness dashboard is not implemented.

**Correction**: `readiness.py` exists at 548 lines on canonical main with `compute_readiness()` aggregating 12+ conditions: foundation pulse, Tier-1/Tier-2 archetype mastery, module floors (Math, Reasoning, English, GA, CK), shared Reasoning Tier-2 readiness, CBIC card accuracy, mock performance/diversity, section floor, elimination skill, and readiness trend.

**Evidence**: `C:\experiments\ssc\src\ssc_study\readiness.py:44` (`compute_readiness`), 12 individual check functions.

## 5. Cheap But High-Value Next Checks

### Check 1: Verify All 6 Test Files Collect on Canonical Main

Run `uv run pytest tests/test_archetypes.py tests/test_cards.py tests/test_queues.py tests/test_gates.py tests/test_phase3.py tests/test_phase3_eval.py -q` on canonical main to confirm all tests collect and pass.

### Check 2: Verify Test Count Matches README Claim

README claims 218 tests pass. Run `uv run pytest -q --tb=no` on canonical main and compare count.

### Check 3: Check Phase 3 Eval Read-Only Guarantee

Inspect `phase3_eval.py` for any write operations (INSERT, UPDATE, DELETE) to confirm it is truly read-only. The snapshot test (`test_phase3_eval_is_read_only`) should catch regressions.

### Check 4: Check Holdout Exclusion in Phase 3 Eval

Verify `phase3_eval.py` filters holdout attempts via `q.is_holdout = 0` in `_recent_attempts_for_archetype()`. Confirm `test_phase3_eval_ignores_holdout_attempts_when_deriving_actual_route` catches regressions.

### Check 5: Check Concept Gap Detection Thresholds

Verify `_detect_concept_gap()` in `gates.py` uses >50% threshold for same-tag wrong answers. Confirm this matches Plan.md intent and is tested in `test_low_accuracy_with_concept_gap`.

### Check 6: Check Boss-Fight Audit Pause Enforcement

Verify `QueueManager._boss_fight_batch()` calls `is_audit_paused()` and raises `RuntimeError`. Confirm `test_boss_fight_blocked_during_major_notification_audit` catches regressions.

### Check 7: Check Shared Reasoning Tier-2 Readiness Logic

Verify `get_tier2_readiness()` in `gates.py` requires 5+ Tier-2 attempts AND 80%+ Tier-2 accuracy. Confirm this matches Plan.md Tier-2 readiness requirement.

### Check 8: Verify No Runtime Consumption of Pattern Reports

Confirm `phase3.py` does not import or call any pattern report module. This is a design boundary per `pattern-intelligence-guardrails.md`.
