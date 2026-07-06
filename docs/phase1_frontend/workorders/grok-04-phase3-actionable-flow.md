# Work Order: Grok 04 - Phase 3 Actionable Web Contract

## Objective

Build the smallest backend bridge from baseline results to Phase 3 diagnostic action. This should turn the existing recommendation layer into a structured, testable contract.

## Read first

- `Plan.md`
- `grok_critic.md`
- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `src/ssc_study/baseline_web.py`
- `src/ssc_study/web.py`
- `src/ssc_study/phase3.py`
- `src/ssc_study/gates.py`
- `tests/test_baseline_web.py`
- `tests/test_web.py`

## Constraints

- No new framework.
- No auth, deployment, accounts, analytics, or broad dashboard work.
- No DB schema change unless absolutely required and explained.
- Preserve existing CLI behavior.
- Do not derive Phase 3 guidance from smoke mode.
- Do not mutate DB state in a "next action" endpoint unless explicitly named and tested.

## Tasks

1. Add or refine a backend route for Phase 3 next action, preferably:
   - `GET /api/phase3/next-action`
   - optional `section` query parameter
2. Reuse `plan_next_action()` from `phase3.py`.
3. Return a stable JSON schema with action type, reason, target archetype, question count, CLI fallback command, and whether a web session can be started.
4. If you add a web start action, keep it tiny and fully tested.
5. Ensure baseline result next steps can reference the same backend contract without duplicating logic.
6. Add route and service tests.

## Acceptance criteria

- Route returns a stable schema.
- Optional section filtering works.
- Stop/no-work state is explicit.
- Baseline smoke behavior remains isolated from Phase 3.
- Existing Phase 1 tests pass.
- Full suite passes.

## Deliverable report

Include:

- summary of backend capability reused
- routes added or changed
- tests added
- exact commands and results
- remaining limitations
