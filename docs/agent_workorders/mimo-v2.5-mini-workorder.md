# Mimo v2.5 Mini Workorder

## Role

Cheap inventory and documentation worker.

## Assigned Branch

Branch:
- `codex/phase3b-mimo-inventory`

Worktree:
- `C:\experiments\ssc\mm`

## Objective

Create a compact inventory of current phase drift and pattern/archetype-related code and tests.

This is documentation only.

## Allowed Files To Edit

You may create or modify only:
- `docs/agent_workorders/mimo-pattern-system-inventory.md`

## Files To Read

Required:
- `Plan.md`
- `README.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `src/ssc_study/archetypes.py`
- `src/ssc_study/cards.py`
- `src/ssc_study/queues.py`
- `src/ssc_study/gates.py`
- `tests/test_archetypes.py`
- `tests/test_cards.py`
- `tests/test_queues.py`
- `tests/test_gates.py`

## Deliverable

Write `docs/agent_workorders/mimo-pattern-system-inventory.md` with:
- current phase drift between `Plan.md`, README, docs, and code
- current modules that already classify or use patterns
- current tests covering those modules
- places where pattern logic is keyword/rule-based
- places where user-performance diagnostics begin
- gaps relevant to Phase 2c exam-pattern intelligence
- gaps relevant to Phase 3 user-error intelligence

## Boundaries

Do not:
- modify source code
- modify tests
- add dependencies
- change README or Plan
- touch generated data

## Verification

Run:

```powershell
git diff -- docs/agent_workorders/mimo-pattern-system-inventory.md
git status --short
git add docs/agent_workorders/mimo-pattern-system-inventory.md
git commit -m "docs: inventory pattern system"
git push -u origin codex/phase3b-mimo-inventory
```

Return:
- status
- file changed
- top ten inventory findings
- any missing context
- commit SHA
- push status, or exact push failure
