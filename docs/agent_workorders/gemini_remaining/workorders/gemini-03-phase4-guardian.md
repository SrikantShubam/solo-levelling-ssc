# Gemini Workorder 03: Phase 4 Guardian Planner

## Role

Implementation worker for the Phase 4 main-grind planner.

## Objective

Implement the v1 Guardian planner described in:

- `docs/agent_workorders/gemini_remaining/specs/phase4-guardian-spec.md`

V1 is report-only. It recommends blocks, mocks, pulses, and audit mode, but does not create sessions or mutate queues.

## Allowed Files To Edit

You may create or modify only:

- `src/ssc_study/guardian.py`
- `src/ssc_study/cli.py`
- `tests/test_guardian.py`
- `tests/test_cli.py`
- `memory.md` only to append a short completion note after verification

If you need to touch another file, stop and report why.

## Required Files To Read

- `Plan.md`
- `README.md`
- `docs/agent_workorders/gemini_remaining/specs/phase4-guardian-spec.md`
- `src/ssc_study/config.py`
- `src/ssc_study/models.py`
- `src/ssc_study/db.py`
- `src/ssc_study/readiness.py`
- `src/ssc_study/audit.py`
- `src/ssc_study/reports.py`
- `src/ssc_study/cli.py`
- `tests/test_config.py`
- `tests/test_readiness.py`
- `tests/test_audit.py`
- `tests/test_cli.py`

## Required Tests

Add tests proving:

- default plan totals exactly 180 minutes.
- default plan includes SM-2, Tier-1 boss fights, Tier-2 module queue, GK/GA memory, English, and analysis blocks.
- Tier-1 floor shift changes boss fights to 25 minutes and Tier-2 to 70 minutes while preserving 180 total minutes.
- first Monday recommends foundation and CK pulses.
- pulse day replaces boss-fight blocks.
- mock day never removes SM-2.
- when pulse and mock collide, mock is recommended for the next grind day.
- active major notification audit removes new boss-fight advancement blocks and reports `notification_pause`.
- CLI renders the plan without changing counts in `sessions`, `attempts`, or queue-related tables.

## Implementation Constraints

- Use dataclasses for `GuardianPlan` and block rows.
- Accept `today` as an injectable date for deterministic tests.
- Keep database reads narrow.
- If evidence is missing, return warnings rather than inventing state.
- Do not create sessions.
- Do not update attempts.
- Do not mutate queues, readiness, archetypes, or audits.
- Do not add dependencies.

## Verification

Run:

```powershell
uv run pytest tests/test_guardian.py tests/test_audit.py tests/test_readiness.py tests/test_cli.py -q
uv run pytest -q
git diff -- src/ssc_study/guardian.py src/ssc_study/cli.py tests/test_guardian.py tests/test_cli.py memory.md
git status --short
```

Commit if tests pass:

```powershell
git add src/ssc_study/guardian.py src/ssc_study/cli.py tests/test_guardian.py tests/test_cli.py memory.md
git commit -m "feat: add guardian planning report"
```

## Final Response

Return:

- summary
- changed files
- exact verification results
- commit SHA if committed
- any deferred behavior

