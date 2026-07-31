# Mimo Round 2 Workorder

## Role

Low-cost inventory worker with explicit fact-check correction duties.

## Assigned Branch

Branch:
- `codex/phase3b-mimo-inventory`

Worktree:
- `C:\experiments\ssc\mm`

## Objective

Redo the pattern-system inventory with stronger verification against canonical-main files.

Round one was useful but included a false repo-wide claim about missing Phase 3 tests. This round must correct stale-branch errors instead of repeating them.

## Allowed Files To Edit

You may create or modify only:
- `docs/agent_workorders/mimo-round2-pattern-system-inventory.md`

## Required Files To Read

- `Plan.md`
- `README.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md`
- `C:\experiments\ssc\src\ssc_study\archetypes.py`
- `C:\experiments\ssc\src\ssc_study\cards.py`
- `C:\experiments\ssc\src\ssc_study\queues.py`
- `C:\experiments\ssc\src\ssc_study\gates.py`
- `C:\experiments\ssc\src\ssc_study\readiness.py`
- `C:\experiments\ssc\src\ssc_study\phase3.py`
- `C:\experiments\ssc\src\ssc_study\phase3_eval.py`
- `C:\experiments\ssc\tests\test_archetypes.py`
- `C:\experiments\ssc\tests\test_cards.py`
- `C:\experiments\ssc\tests\test_queues.py`
- `C:\experiments\ssc\tests\test_gates.py`
- `C:\experiments\ssc\tests\test_phase3.py`
- `C:\experiments\ssc\tests\test_phase3_eval.py`

## Deliverable

Write `docs/agent_workorders/mimo-round2-pattern-system-inventory.md` with:

1. `Current Deterministic Pattern System`
- modules and what each currently does

2. `Current Test Coverage`
- exact test files, including Phase 3 and Phase 3 eval coverage

3. `Current Gaps`
- missing model-based paper pattern discovery
- missing model-assisted failure taxonomy
- missing pattern registry
- missing runtime consumption of pattern reports by design

4. `Round One Corrections`
- list the stale or inaccurate claims from the previous inventory and correct them

5. `Cheap But High-Value Next Checks`
- what a small worker can verify next without touching production code

## Hard Rules

Do not:
- claim a file or test is missing without checking the canonical main path
- modify code or tests
- change docs outside the allowed file
- use network

## Verification

Run:

```powershell
git diff -- docs/agent_workorders/mimo-round2-pattern-system-inventory.md
git status --short
git add docs/agent_workorders/mimo-round2-pattern-system-inventory.md
git commit -m "docs: refine pattern system inventory round2"
git push -u origin codex/phase3b-mimo-inventory
```

Return:
- status
- changed file
- top ten findings
- three corrected claims from round one
- commit SHA
- push status, or exact push failure
