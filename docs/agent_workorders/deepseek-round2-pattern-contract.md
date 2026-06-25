# DeepSeek Round 2 — Pattern Intelligence Contract

## 1. Round One Failures To Correct

### 1.1 Top-Level Missing-Module Import Failure (Critical)

**File:** `tests/test_pattern_intelligence_contract.py` (round one)

```python
from ssc_study.pattern_intelligence import (
    ExamPatternReport,
    PatternPriorityReport,
    UserPatternReport,
    analyze_exam_patterns,
    analyze_user_error_patterns,
    combine_pattern_priorities,
)
```

The module `ssc_study.pattern_intelligence` does not exist. This top-level `import` statement causes the entire test module to **fail at collection time** — pytest cannot load any test. This is the single highest-priority failure to fix because it blocks all downstream CI checks.

**Fix:** Replace all top-level production imports with guarded per-test imports using `pytest.importorskip("ssc_study.pattern_intelligence")` inside each test function body. The module collects successfully, skips only at call time, and communicates exactly which missing module blocks execution.

### 1.2 Tautological Assertion Pattern

**File:** `tests/test_pattern_intelligence_contract.py` (round one, line ~211)

```python
assert result.priority_items[0].confidence < result.priority_items[0].confidence or True
```

The `or True` suffix makes this assertion pass unconditionally — it is logically equivalent to `assert True`. This provides zero signal and hides the fact that the confidence comparison was never verified.

**Fix:** Replace with a concrete comparison against an expected confidence value. If the comparison depends on implementation details not yet fixed, skip the assertion rather than papering over it.

### 1.3 Overconstrained API And Module-Shape Assumptions

Round one hardcoded:
- Exact module path `ssc_study.pattern_intelligence`
- Exact dataclass names `ExamPatternReport`, `UserPatternReport`, `PatternPriorityReport`
- Exact field names (`evidence_question_ids`, `evidence_attempt_ids`, `timing_weakness`, `accuracy_weakness`, `priority_items`, `confidence`, `priority_score`, etc.)
- Exact function signatures with parameter names like `latest_window`, `archetype_ids`

None of these are fixed by the canonical spec. The design doc (`2026-06-25-phase2c-phase3-pattern-intelligence-design.md`) defines expected future APIs only as sketches. The pattern-intelligence-test-cases.md defines *behaviors* not *APIs*.

**Fix:** Write behavior-contract tests that depend on function-level import of the *module* (not specific names), then use attribute access via `getattr` or the module object itself. Avoid hardcoding field names that are absent from the canonical spec.

---

## 2. Canonical Contract

Contracts are organized by the four behavior groups from the canonical test-case doc (`pattern-intelligence-test-cases.md`). Each contract cites the source document.

### 2.1 Exam-Pattern Behaviors

| # | Contract | Source Test Case | Current Status |
|---|----------|-----------------|---------------|
| E1 | `analyze_exam_patterns` is read-only: snapshot `questions`, `archetypes`, `attempts`, `sessions`, `sm2_state`, `fact_cards` before and after; assert unchanged | `test_exam_patterns_are_read_only` | `spec-quality` — no impl exists |
| E2 | Holdout questions are excluded from evidence: seed same archetype with holdout + non-holdout; only non-holdout IDs appear in evidence | `test_exam_patterns_exclude_holdout_questions` | `spec-quality` — no impl exists |
| E3 | Report includes section, tier, year, archetype distribution counts | `test_exam_patterns_report_distribution_counts` | `spec-quality` — no impl exists |
| E4 | Signal strength maps: 0-4 evidence → `insufficient`, 5-9 → `weak`, 10+ → `stable` | `test_exam_patterns_report_signal_strength` | `spec-quality` — no impl exists |
| E5 | Mock blueprint is advisory only: no session created, no queue state changed | `test_mock_blueprint_is_advisory_only` | `spec-quality` — no impl exists |

**Detailed Contract (E2):**
```
Given: archetype A with question H (is_holdout=1) and question N (is_holdout=0)
When:  analyze_exam_patterns runs
Then:  H is absent from evidence IDs, N is present
Rationale: Sealed holdout data must not leak into corpus-level pattern analysis.
```

**Detailed Contract (E4):**
```
Given: groups of 3, 7, and 12 non-holdout questions in separate archetypes
When:  analyze_exam_patterns runs for each group
Then:  signal_strength is "insufficient" for 3, "weak" for 7, "stable" for 12
Rationale: Sparse evidence must be visibly sparse (anti-overfitting rule).
```

### 2.2 User-Error Behaviors

| # | Contract | Source Test Case | Current Status |
|---|----------|-----------------|---------------|
| U1 | `analyze_user_error_patterns` is read-only: same snapshot as E1 | `test_user_patterns_are_read_only` | `spec-quality` — no impl exists |
| U2 | Holdout-linked attempts excluded: attempt on holdout question does not contribute to evidence | `test_user_patterns_exclude_holdout_attempts` | `spec-quality` — no impl exists |
| U3 | Uses latest attempt window, not all-history: older and newer weakness patterns; report follows the latest | `test_user_patterns_use_latest_window` | `spec-quality` — no impl exists |
| U4 | Detects repeated wrong archetype: seed repeated wrong attempts in one archetype; report returns that archetype with attempt IDs | `test_user_patterns_detect_repeated_wrong_archetype` | `spec-quality` — no impl exists |
| U5 | Detects repeated concept gap: seed repeated wrong attempts sharing `concept_tag`; report marks concept-cluster weakness | `test_user_patterns_detect_repeated_concept_gap` | `spec-quality` — no impl exists |
| U6 | Timing separated from accuracy: correct but slow attempts and wrong but fast attempts produce separate weakness signals | `test_user_patterns_separate_timing_from_accuracy` | `spec-quality` — no impl exists |
| U7 | Signal strength: same 0-4/5-9/10+ thresholds as exam patterns | `test_user_patterns_report_signal_strength` | `spec-quality` — no impl exists |

**Detailed Contract (U3):**
```
Given: archetype A — older 10 attempts show weakness in Algebra,
       newer 5 attempts show weakness in Ratios
When:  analyze_user_error_patterns runs (default latest_window=50)
Then:  the report's primary archetype weakness is Ratios (the latest window)
Rationale: User's current state matters more than historical state.
```

**Detailed Contract (U6):**
```
Given: attempts — (correct, time=300s), (correct, time=310s), (wrong, time=15s)
When:  analyze_user_error_patterns runs
Then:  the report surfaces a timing weakness (slow on corrects)
       separately from accuracy weakness (the wrong answer)
Rationale: Slow mastery and wrong answers have different remedies.
```

### 2.3 Priority-Combiner Behaviors

| # | Contract | Source Test Case | Current Status |
|---|----------|-----------------|---------------|
| P1 | High exam weight + high user weakness outranks low+high and high+low | `test_priority_combiner_prefers_high_exam_weight_and_high_user_weakness` | `spec-quality` — no impl exists |
| P2 | Weak-confidence patterns outranked by stable-confidence (otherwise equal) | `test_priority_combiner_downweights_low_confidence` | `spec-quality` — no impl exists |
| P3 | Combiner is advisory-only: no DB object required or mutated | `test_priority_combiner_is_advisory_only` | `spec-quality` — no impl exists |

**Note:** These contracts do not depend on a database — they combine two in-memory report objects. This means they can be tested without DB fixtures.

**Formula (from design doc):**
```python
priority = exam_importance * user_weakness * confidence
```

### 2.4 Phase 3 Boundary Behaviors

| # | Contract | Source Test Case | Current Status |
|---|----------|-----------------|---------------|
| B1 | `plan_next_action` does not consume pattern reports: action selection unchanged from existing deterministic Phase 3 rules | `test_phase3_planner_does_not_consume_pattern_reports` | `merge-quality` — existing `test_phase3.py` already proves `plan_next_action` is deterministic and does not reference pattern analysis |
| B2 | Contract test module collects without missing-module failure in pre-implementation state | `test_contract_tests_collect_without_missing_module_failure` | `merge-quality` — verified by running pytest collection on the test file |
| B3 | Future pattern CLI commands are read-only: DB snapshot unchanged after running each command; output includes evidence count + signal strength | `test_pattern_cli_commands_are_read_only` | `spec-quality` — no CLI exists yet |

---

## 3. Spec-Quality vs Merge-Quality Labels

### Merge-Quality Items

These are ready for the main branch with minimal edits:

| Item | Reason |
|------|--------|
| Contract document (this file) | Defines exact expected behaviors, cites canonical sources, is documentation-only with no runtime risk |
| B1: Phase 3 planner boundary | Already proven by existing `test_phase3.py`. No new test needed — the existing test suite proves `plan_next_action` ignores pattern reports |
| B2: Collection-safe module | The guarded-import pattern (`pytest.importorskip` inside each test body) ensures the module collects cleanly even before any implementation exists |

### Spec-Quality Items

These are useful contract definitions that need orchestrator rewrite before merging:

| Item | Reason |
|------|--------|
| E1-E5: All exam-pattern tests | Production module does not exist. Test logic is correct per spec, but the exact API surface (`analyze_exam_patterns` signature, return type fields) cannot be finalized until an orchestrator or implementer locks the interface. The per-test `pytest.importorskip` pattern makes them safe to merge now, but the assertions inside should be reviewed once the API is stabilized. |
| U1-U7: All user-error tests | Same rationale as exam-pattern tests. The report field names (`repeated_archetypes`, `timing_weakness`, `accuracy_weakness`, etc.) are spec sketches, not finalized contracts. |
| P1-P3: All priority-combiner tests | Combiner formula is advisory-only in v1. The direction is correct; exact weighting may change. |
| B3: CLI read-only commands | No CLI implementation exists. Test cannot be validated. |

### Merge-Quality Test File Strategy

If updating `tests/test_pattern_intelligence_contract.py`:

1. **Guard every production import** with `pytest.importorskip("ssc_study.pattern_intelligence")` inside each test function — never at module level.
2. **Do not assume specific field names** beyond what is provably in the canonical spec. For return-value inspection, use `getattr()` with defaults and document which fields are speculative.
3. **No tautological assertions** — every `assert` must compare against a known value or condition, never against itself with `or True`.
4. **Use existing fixtures** (`in_memory_db` for raw connections, `study_db`/`seeded_db` for `Database` objects) from `conftest.py`. Do not create new fixture factories unless absolutely necessary.

---

## 4. Assumptions About Future Production API

The test file assumes these will exist in `ssc_study/pattern_intelligence.py` (per `2026-06-25-phase2c-phase3-pattern-intelligence-design.md`):

| Assumption | Source | Risk |
|-----------|--------|------|
| Module `ssc_study.pattern_intelligence` | Design doc "Public Interfaces" | Low — explicitly named |
| `analyze_exam_patterns(db, *, ...)` function | Design doc | Low — explicitly named |
| `analyze_user_error_patterns(db, *, ...)` function | Design doc | Low — explicitly named |
| `combine_pattern_priorities(exam_report, user_report)` function | Design doc | Low — explicitly named |
| Report types are dataclasses or similar attribute-bearing objects | Assumed by behavior tests | Medium — could be dicts or NamedTuples; tests use attribute access |
| CLI commands under `ssc-study patterns` | Design doc | Low — explicitly named, but `spec-quality` |

**The test file rounds assertions through the module reference** (e.g., `result = pi.analyze_exam_patterns(db)`) rather than importing specific names. This makes it resilient to naming changes within the module.

---

## 5. Verification

```powershell
# Verify the test file collects successfully (no ImportError at collection time)
if (Test-Path tests/test_pattern_intelligence_contract.py) {
    uv run pytest tests/test_pattern_intelligence_contract.py --collect-only -q
}

# Verify existing Phase 3 tests are unaffected
uv run pytest tests/test_phase3.py tests/test_phase3_eval.py -q --tb=short
```

Expected result for the contract file before implementation:
- Collection: **pass** (no ImportError)
- Tests: **all skipped** (because `pytest.importorskip` fires when the pattern_intelligence module is absent)
