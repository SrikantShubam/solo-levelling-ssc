# Documentation Consistency Spec

## Goal

Make project documentation reflect the current implementation state without overstating unfinished Phase 2c or Phase 4 work.

## Required Behavior

Update README and coordination docs so they consistently state:

- Phase 2 corpus is accepted for build-on use.
- Phase 2b is approved as implemented, based on the later implementation review and current tests.
- The earlier Phase 2b critic is historical and should not be read as current status.
- Phase 2c means exam-pattern intelligence over the corpus.
- Phase 3 means user diagnostic grinding over attempts and archetypes.
- Phase 3b is optional shorthand for read-only advisory work, not a separate runtime scheduler.
- Phase 4 means Guardian/main-grind planner and mock cadence.

Do not remove historical notes unless they are actively misleading. Prefer adding a short "current status" note above older critic sections.

## Required Files To Inspect

- `README.md`
- `Plan.md`
- `memory.md`
- `docs/agent_workorders/phase3-scope-breakdown.md`
- `docs/agent_workorders/pattern-intelligence-guardrails.md`
- `docs/superpowers/specs/2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `docs/agent_workorders/gemini_remaining/remaining-work-register.md`

## Acceptance Checks

- README phase table includes Phase 2c and describes Phase 4 as upcoming.
- README has an explicit current-status note near the Phase 2b critic.
- No doc says Phase 2b is still missing all 12 approval items without historical context.
- No doc says model-discovered pattern output currently mutates runtime state.
- No doc claims Phase 4 is implemented unless code and tests prove it.

## Verification

Run:

```powershell
rg -n "Phase 2b is MVP-complete|Missing for full Phase 2b approval|Phase 2c|Phase 3b|Phase 4|runtime.*pattern|mutate" README.md docs
git diff -- README.md docs/agent_workorders docs/superpowers
```

