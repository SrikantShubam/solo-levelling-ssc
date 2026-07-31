# Phase 3 Orchestrator Design

## Goal

Add a deterministic Phase 3 orchestration loop that can run diagnostic work without constant user steering. The loop should choose the next diagnostic action, execute the smallest valid step, record the outcome, and produce a reviewable report.

## Why

The repo already has the core primitives for Phase 3:

- archetype probe selection and routing in `src/ssc_study/gates.py`
- structured question queues in `src/ssc_study/queues.py`
- interactive session execution in `src/ssc_study/quiz.py`
- skip-list lifecycle in `src/ssc_study/skips.py`

What is missing is the control layer that turns those primitives into a repeatable operating loop.

## Scope

This design adds:

- a new `phase3.py` orchestration module
- deterministic next-step planning for diagnostic work
- loop execution with bounded iterations
- structured reporting for every loop run
- CLI entrypoint to run and inspect the loop

This design does not add:

- LLM-based arbitration
- background scheduling
- automatic long-running daemons
- major schema rewrites beyond the minimum needed for auditable loop reports

## Operating Model

The orchestrator owns one bounded run.

Each iteration does:

1. inspect current study state
2. pick the highest-priority next action
3. execute exactly one action
4. record the result
5. stop when there is no eligible work, the iteration cap is reached, or a blocker appears

## Prioritized Action Order

The first version will prioritize:

1. `probe`
   - choose an unlocked candidate from `get_probe_candidates()`
   - prepare a 10-question probe batch
2. `remediation`
   - if remediation inventory exists, assign a remediation batch
3. `boss_fight`
   - if boss-fight inventory exists, assign a boss-fight batch
4. `sm2_review`
   - if due review exists, assign an SM-2 batch
5. `stop`
   - no eligible work remains

This order is deliberate: Phase 3 should first create diagnoses, then exploit them.

## Execution Modes

The orchestrator supports two modes:

- `plan`
  - compute the next actions without launching interactive quiz sessions
  - useful for tests and dry runs
- `run`
  - create concrete session plans for the next actions
  - still bounded and deterministic

The first implementation will keep `run` non-interactive from the orchestrator perspective:

- it prepares the session payload
- it does not auto-answer questions
- the actual quiz interaction remains in `QuizSession`

## Public API

`src/ssc_study/phase3.py`

- `Phase3Action`
  - typed record for one loop action
- `Phase3RunReport`
  - typed report for one orchestrator run
- `plan_next_action(db, *, tier=None, section=None) -> Phase3Action`
- `run_phase3_loop(db, *, max_steps=5, tier=None, section=None, dry_run=False) -> Phase3RunReport`

## Reporting

Each action report should include:

- action type
- reason selected
- target archetype if applicable
- expected question count
- resulting route or queue assignment if applicable
- stop reason for terminal actions

The final run report should include:

- total actions executed
- action list in order
- whether the loop completed normally
- stop reason

## CLI

Add a new command:

`ssc-study phase3`

Initial options:

- `--max-steps`
- `--dry-run`
- `--tier`
- `--section`
- `--db-path`

CLI behavior:

- print the chosen action sequence
- print stop reason
- print concise counts only, not raw question payloads

## Testing Strategy

Test the orchestrator as pure decision logic first.

Required behavior:

- chooses `probe` before queue work when probe candidates exist
- chooses `remediation` when no probe candidates exist and remediation inventory exists
- chooses `boss_fight` before `sm2_review` when boss-fight inventory exists
- stops cleanly with `no_eligible_work`
- respects `max_steps`
- dry-run mode does not mutate session tables
- CLI returns success and prints the action summary

## Risks

### Risk: orchestration duplicates existing queue logic

Mitigation:
- the orchestrator only decides which primitive to invoke
- queue/gate ownership stays in existing modules

### Risk: interactive quiz flow is too tightly coupled

Mitigation:
- first version returns prepared work and only lightly integrates with CLI
- avoid deep changes to `QuizSession`

### Risk: action priority is arguable

Mitigation:
- keep priority explicit and localized in one selector function
- make later tuning cheap

## Acceptance

The feature is good enough when:

- one CLI command can produce a bounded Phase 3 action run
- the action order is deterministic and test-covered
- the run report explains why each step happened
- the code can evolve later to add model-assisted arbitration without rewriting the loop
