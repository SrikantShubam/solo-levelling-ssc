# Phase 3 Anti-Overfit Evaluation Design

## Goal

Complete the Phase 3 evaluation slice by making prediction-vs-actual audit results trustworthy without making the runtime orchestrator smarter.

## Why

Phase 3 already has two separate pieces:

- `src/ssc_study/phase3.py` chooses bounded diagnostic actions.
- `src/ssc_study/phase3_eval.py` compares persisted route predictions against observed outcomes.

The risk is self-confirming evaluation. If evaluation reads sealed/holdout evidence, stale historical attempts, or feeds results back into runtime state, the system can look accurate because it graded itself on contaminated data.

## Evaluation Contract

The evaluator is read-only.

It may inspect:

- `archetypes`
- `questions`
- `attempts`
- `sessions`
- `sm2_state`

It must not update:

- queues
- readiness gates
- archetype route state
- SM-2 state
- attempts or sessions
- runtime loop policy

Runtime Phase 3 orchestration must not consume evaluator output. Evaluation exists for external audit and reporting only.

## Actual Route Derivation

Actual route derivation uses only recent, non-holdout attempts for questions attached to the archetype being compared.

Rules:

- Ignore every attempt where the linked question has `is_holdout = 1`.
- Use only the latest attempt window.
- The current window is the latest 10 non-holdout attempts by `attempt_id`.
- Reorder the selected window chronologically before classification.
- Classify the window with the same pure gate classifier used by runtime gate evaluation.

Holdout questions are reserved for sealed validation. They must not participate in Phase 3 route explanation.

## Signal Strength

Every comparison reports how much evidence supports the actual route.

Signal values:

- `insufficient`: fewer than 5 actual non-holdout attempts.
- `weak`: 5 to 9 actual non-holdout attempts.
- `stable`: 10 actual non-holdout attempts in the latest window.

Sparse data must stay visibly sparse. The evaluator should not pretend that 5 attempts are as meaningful as a full 10-attempt probe window.

## Public Behavior

Existing comparison fields remain available:

- `predicted_route`
- `actual_route`
- `matches`
- `reason`

The evaluator adds:

- `actual_attempt_count`
- `actual_accuracy`
- `signal_strength`

CLI output should show signal strength and attempt count per archetype comparison. This is display-only and must not add options that mutate runtime state.

## Anti-Overfitting Coverage

The tests should cover:

- read-only evaluation snapshots
- holdout exclusion from actual route derivation
- latest-window behavior over all historical attempts
- route-boundary parity with the gate classifier
- high-priority boss classification without concept-gap leakage
- signal strength reporting
- probe eligibility requiring enough non-holdout questions
- plan invariance to question ID and insertion order
- no repeated archetype within one bounded Phase 3 run

## Out Of Scope

This slice does not add:

- model-assisted arbitration
- Phase 4 daily scheduling
- feedback loops from evaluation into orchestration
- sealed holdout scoring
- new database tables
- new CLI mutation flags

## Acceptance

The slice is complete when:

- evaluator output is read-only and independently test-covered
- actual-route derivation ignores holdout attempts
- actual-route derivation uses the latest 10 non-holdout attempts
- CLI displays evidence strength
- full test verification passes
