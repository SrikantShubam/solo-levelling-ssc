# Gemini Remaining Work Handoff

This package is the canonical handoff for Gemini workers that cannot use MCP.

Start here, then execute one workorder at a time. Do not combine workorders unless the user explicitly asks for a combined pass.

## Current Project Status

Source of truth order:

1. `Plan.md`
2. `README.md`
3. `memory.md`
4. `docs/agent_workorders/phase3-scope-breakdown.md`
5. Current code and tests

Known status:

- Phase 2 corpus extraction is accepted for build-on use.
- Phase 2b study runtime is approved in the later README implementation review and reinforced by `memory.md`.
- Phase 3 deterministic orchestration and read-only evaluation exist.
- Phase 2c exam-pattern intelligence is specified but not implemented as a production module.
- Phase 4 Guardian/main-grind scheduling is still upcoming.
- README has documentation drift: earlier Phase 2b critic text says missing items that later sections and current code say are complete.

## Files In This Handoff

- `docs/agent_workorders/gemini_remaining/remaining-work-register.md`
- `docs/agent_workorders/gemini_remaining/specs/phase2c-pattern-intelligence-spec.md`
- `docs/agent_workorders/gemini_remaining/specs/phase4-guardian-spec.md`
- `docs/agent_workorders/gemini_remaining/specs/docs-consistency-spec.md`
- `docs/agent_workorders/gemini_remaining/workorders/gemini-01-remaining-audit.md`
- `docs/agent_workorders/gemini_remaining/workorders/gemini-02-phase2c-pattern-intelligence.md`
- `docs/agent_workorders/gemini_remaining/workorders/gemini-03-phase4-guardian.md`
- `docs/agent_workorders/gemini_remaining/workorders/gemini-04-docs-consistency.md`
- `docs/agent_workorders/gemini_remaining/codex-review-and-validation-plan.md`

## Recommended Execution Order

1. Run `gemini-01-remaining-audit.md`.
2. If the audit confirms no newer implementation exists, run `gemini-02-phase2c-pattern-intelligence.md`.
3. Run `gemini-03-phase4-guardian.md` after Phase 2c is either implemented or explicitly deferred.
4. Run `gemini-04-docs-consistency.md` after implementation work, so docs describe the resulting state.
5. Return Gemini's final response, changed files, test output, and commit SHA to Codex for review using `codex-review-and-validation-plan.md`.

## Global Rules For Gemini

- Do not edit `.env`, `.env.example`, credentials, generated caches, corpus data, or extraction outputs.
- Do not use network access.
- Do not add model/API dependencies.
- Do not delete tests.
- Do not rename public functions unless the workorder explicitly allows it.
- Do not let advisory pattern intelligence mutate queues, gates, readiness, attempts, sessions, archetypes, SM-2, or mock generation in v1.
- Keep changes surgical and consistent with existing `ssc_study` patterns.
- Add or update tests before implementation where the workorder asks for code.
- Run the exact verification commands in the workorder.

## Expected Gemini Final Response

Gemini must return:

- Workorder completed.
- Files changed.
- Test commands run and exact result.
- Commit SHA if committed.
- Any blocked item with the exact reason.
- Any behavior intentionally deferred.

