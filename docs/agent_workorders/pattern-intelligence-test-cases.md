# Pattern Intelligence Test Cases

## Contract Shape Rules

- Contract tests must collect successfully even before production implementation exists.
- If production APIs are not implemented yet, prefer:
  - spec-only documentation, or
  - tests that fail at call time after guarded import/feature checks
- Do not force a red test through top-level import failure of a missing module.
- Do not use tautological assertions.
- Do not lock the implementation to a single module name unless the canonical spec already does so.
- Prefer behavior contracts over dataclass-shape micromanagement.

## Exam Pattern Intelligence

- `test_exam_patterns_are_read_only`
  - Snapshot `questions`, `archetypes`, `attempts`, `sessions`, `sm2_state`, and `fact_cards`.
  - Run exam-pattern analysis.
  - Assert snapshot unchanged.

- `test_exam_patterns_exclude_holdout_questions`
  - Seed same archetype with non-holdout and holdout questions.
  - Run exam-pattern analysis.
  - Assert only non-holdout question IDs appear in evidence.

- `test_exam_patterns_report_distribution_counts`
  - Seed multiple sections, tiers, years, and archetypes.
  - Assert report includes correct section, tier, year, and archetype counts.

- `test_exam_patterns_report_signal_strength`
  - Seed 0-4, 5-9, and 10+ evidence groups.
  - Assert signal strength is `insufficient`, `weak`, and `stable`.

- `test_mock_blueprint_is_advisory_only`
  - Run exam-pattern analysis.
  - Assert no session is created and no queue state changes.

## User Error Pattern Intelligence

- `test_user_patterns_are_read_only`
  - Snapshot core tables.
  - Run user-error analysis.
  - Assert snapshot unchanged.

- `test_user_patterns_exclude_holdout_attempts`
  - Seed attempts linked to holdout and non-holdout questions.
  - Assert only non-holdout attempts contribute to patterns.

- `test_user_patterns_use_latest_window`
  - Seed older attempts showing one weakness and newer attempts showing another.
  - Assert report follows the latest window.

- `test_user_patterns_detect_repeated_wrong_archetype`
  - Seed repeated wrong attempts in one archetype.
  - Assert report returns that archetype with evidence attempt IDs.

- `test_user_patterns_detect_repeated_concept_gap`
  - Seed repeated wrong attempts with the same `concept_tag`.
  - Assert report marks concept-cluster weakness.

- `test_user_patterns_separate_timing_from_accuracy`
  - Seed correct but slow attempts and wrong but fast attempts.
  - Assert timing weakness is separate from accuracy weakness.

- `test_user_patterns_report_signal_strength`
  - Seed 0-4, 5-9, and 10+ attempts.
  - Assert signal strength is `insufficient`, `weak`, and `stable`.

## Priority Combiner

- `test_priority_combiner_prefers_high_exam_weight_and_high_user_weakness`
  - Combine synthetic exam and user reports.
  - Assert high/high outranks low/high and high/low.

- `test_priority_combiner_downweights_low_confidence`
  - Compare stable and weak signals with otherwise equal scores.
  - Assert weak signal ranks lower.

- `test_priority_combiner_is_advisory_only`
  - Run combiner.
  - Assert no DB object is required or mutated.

## Phase Boundary

- `test_phase3_planner_does_not_consume_pattern_reports`
  - Seed pattern reports or monkeypatch pattern functions if they exist.
  - Run `plan_next_action`.
  - Assert action selection is unchanged from existing deterministic Phase 3 rules.

- `test_contract_tests_collect_without_missing_module_failure`
  - Import the contract-test module in a pre-implementation state.
  - Assert collection succeeds even if the feature is absent.

- `test_pattern_cli_commands_are_read_only`
  - Run each future CLI command against a seeded DB.
  - Assert DB snapshot unchanged and output includes evidence count plus signal strength.
