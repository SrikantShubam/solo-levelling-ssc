# Gemini 3.5 Flash High Workorder

## Role

Broad-scope scout and design reviewer.

## Assigned Branch

Branch:
- `codex/phase3b-gemini-scope`

Worktree:
- `C:\experiments\ssc\gm`

## Objective

Review and refine the corrected phase taxonomy and pattern-intelligence design.

This is an investigation and design task only. Do not implement production code.

## Allowed Files To Edit

You may create or modify only:
- `docs/agent_workorders/gemini-phase-taxonomy-review.md`

## Files To Read

Required:
- `Plan.md`
- `README.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `src/ssc_study/archetypes.py`
- `src/ssc_study/phase3.py` if present
- `src/ssc_study/phase3_eval.py` if present
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-17-phase3-orchestrator-design.md` if present
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-25-phase3-anti-overfit-completion-design.md` if present

If a file is missing in your worktree, record it as a context gap.

## Deliverable

Write `docs/agent_workorders/gemini-phase-taxonomy-review.md` with:
- whether Phase 2c is the correct home for exam-paper pattern intelligence
- whether Phase 3 is the correct home for user-error pattern intelligence
- exact phase drift between `Plan.md`, README, docs, and code
- exact evidence from `Plan.md` and current code
- a minimal read-only design critique
- risks of overfitting or self-confirming evaluation
- forbidden integration points
- recommended promotion gates before patterns affect mocks, queues, readiness, or archetypes

## Boundaries

Do not:
- modify source code
- modify tests
- add dependencies
- change schemas
- run LLM calls
- use network

## Verification

Run:

```powershell
git diff -- docs/agent_workorders/gemini-phase-taxonomy-review.md
git status --short
git add docs/agent_workorders/gemini-phase-taxonomy-review.md
git commit -m "docs: review phase taxonomy and pattern scope"
git push -u origin codex/phase3b-gemini-scope
```

Return:
- status
- file changed
- five strongest conclusions
- any missing context
- commit SHA
- push status, or exact push failure
