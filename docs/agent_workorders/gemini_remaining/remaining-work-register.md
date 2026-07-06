# Remaining Work Register

This register defines the remaining repo work after Phase 2b approval and Phase 3 orchestrator/evaluator hardening.

## R1: Remaining-Scope Audit

Status: required before implementation.

Purpose:
- Confirm the current working tree has not already implemented any item listed below.
- Produce file/line evidence for each confirmed gap.
- Separate actual gaps from README drift.

Output:
- `docs/agent_workorders/gemini_remaining/remaining-audit-report.md`

Gemini workorder:
- `docs/agent_workorders/gemini_remaining/workorders/gemini-01-remaining-audit.md`

## R2: Phase 2c Exam-Pattern Intelligence

Status: completed.

Purpose:
- Add read-only corpus pattern analysis over non-holdout questions.
- Report section, tier, year, and archetype distributions.
- Produce advisory mock blueprints without creating mocks or sessions.
- Add an advisory priority combiner that can join exam importance with existing user diagnostic signals without runtime coupling.

Non-goals:
- No LLM pattern mining.
- No mutation of queues, gates, readiness, attempts, sessions, archetypes, SM-2, or mock generation.
- No holdout usage for pattern generation.

Spec:
- `docs/agent_workorders/gemini_remaining/specs/phase2c-pattern-intelligence-spec.md`

Gemini workorder:
- `docs/agent_workorders/gemini_remaining/workorders/gemini-02-phase2c-pattern-intelligence.md`

## R3: Phase 4 Guardian Main-Grind Scheduler

Status: planner v1 completed.

Purpose:
- Add a deterministic daily plan generator for the 180-minute main grind.
- Encode mock cadence, monthly pulses, notification-audit pause behavior, and the Tier-1 floor based Tier-2 shift.
- Keep v1 as a planner/report layer, not an automatic quiz/session executor.

Non-goals:
- No full UI.
- No automatic mock/session creation in v1.
- No background daemon, notifications, or calendar integration.
- Full Phase 4 execution remains out of scope until sessions, mock execution, and queue mutation are explicitly promoted.

Spec:
- `docs/agent_workorders/gemini_remaining/specs/phase4-guardian-spec.md`

Gemini workorder:
- `docs/agent_workorders/gemini_remaining/workorders/gemini-03-phase4-guardian.md`

## R4: Documentation Consistency

Status: completed.

Purpose:
- Resolve README drift between early Phase 2b critic text and later approved implementation review.
- Make phase names consistent with `Plan.md` and `phase3-scope-breakdown.md`.
- Add links from README to the current Phase 2c and Phase 4 specs/workorders.

Spec:
- `docs/agent_workorders/gemini_remaining/specs/docs-consistency-spec.md`

Gemini workorder:
- `docs/agent_workorders/gemini_remaining/workorders/gemini-04-docs-consistency.md`

## R5: Codex Review And Validation

Status: performed after Gemini returns work.

Purpose:
- Review Gemini's diff for scope control, test quality, runtime safety, and phase-boundary violations.
- Add missing regression tests if Gemini's tests are weak.
- Run focused and full verification before accepting work.

Review plan:
- `docs/agent_workorders/gemini_remaining/codex-review-and-validation-plan.md`
