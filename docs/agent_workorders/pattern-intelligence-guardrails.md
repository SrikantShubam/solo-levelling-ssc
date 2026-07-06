# Pattern Intelligence Guardrails

## Scope Boundaries

- Phase 2c owns exam-paper pattern intelligence.
- Phase 3 owns user-error diagnostic intelligence over attempts.
- `Phase 3b` is optional naming for a read-only advisory extension inside the broader Phase 3 area. It is not a separate runtime scheduler.
- Phase 4 consumes validated signals for scheduling and mock cadence.

## Read-Only First

The first implementation must not mutate:
- `questions`
- `archetypes`
- `attempts`
- `sessions`
- `sm2_state`
- `fact_cards`
- `notification_audits`
- queues
- readiness state

## Holdout Rules

- Holdout questions cannot generate exam patterns.
- Attempts linked to holdout questions cannot generate user-error patterns.
- Holdout can only validate later promoted pattern behavior.

## Model Output Rules

Every model-generated pattern must include:
- pattern name
- pattern type: `exam_pattern` or `user_error`
- section
- tier if applicable
- evidence question IDs or attempt IDs
- confidence/signal strength
- reason text
- counterexample notes when available

Pattern reports must also say whether they are:
- `spec-quality`: useful analysis or a contract draft
- `merge-quality`: safe to promote into canonical docs/tests after orchestrator review

Patterns without evidence IDs are not actionable.

## Promotion Rules

No pattern may affect mocks, queues, gates, readiness, archetypes, or SM-2 until it has:
- minimum evidence count
- non-holdout validation
- signal strength of `stable`
- explicit review approval
- regression tests proving no holdout leakage

## Worker Rules

Workers must:
- stay inside assigned files
- cite `Plan.md`, README, or code evidence
- report missing files as context gaps
- avoid schema changes
- avoid dependency changes
- avoid generated data changes

Workers must not:
- directly edit runtime scheduling
- make Phase 3 consume pattern reports
- change mock generation behavior
- rename existing phases without updating source-of-truth docs
- state that a file or test is missing unless they checked both the local worktree and the canonical main path when instructed
