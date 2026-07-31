# Gemini Round 2 Workorder

## Role

Taxonomy and boundary reviewer with explicit correction duties.

## Assigned Branch

Branch:
- `codex/phase3b-gemini-scope`

Worktree:
- `C:\experiments\ssc\gm`

## Objective

Redo the phase taxonomy review with stronger claim discipline.

This is documentation only. Do not implement code or tests.

Your round-one output was useful, but one claim overstated the absence of tier-specific reasoning support. This round must explicitly separate:
- fully confirmed claims
- partially confirmed claims
- branch-stale or unsupported claims

## Allowed Files To Edit

You may create or modify only:
- `docs/agent_workorders/gemini-round2-phase-taxonomy-review.md`

## Required Files To Read

- `Plan.md`
- `README.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md`
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `C:\experiments\ssc\src\ssc_study\gates.py`
- `C:\experiments\ssc\src\ssc_study\readiness.py`
- `C:\experiments\ssc\src\ssc_study\phase3_eval.py`
- `C:\experiments\ssc\tests\test_phase3.py`
- `C:\experiments\ssc\tests\test_phase3_eval.py`

You may also inspect your local worktree copies, but when local and canonical-main differ, prefer the canonical-main path and call out the drift.

## Deliverable

Write `docs/agent_workorders/gemini-round2-phase-taxonomy-review.md` with these sections:

1. `Confirmed`
- Facts that are clearly supported by code or plan.

2. `Partially Confirmed`
- Claims that are directionally right but need narrower wording.

3. `Unsupported Or Branch-Stale`
- Claims that should not be repeated as repo truth.

4. `Final Taxonomy`
- Exact breakdown of Phase 2c exam patterns vs Phase 3 user-error patterns.

5. `Overfitting And Independence Risks`
- Holdout leakage
- self-confirming loops
- sparse-evidence inflation

6. `Promotion Gates`
- what must be true before pattern output can affect runtime

## Hard Rules

Do not:
- use `file:///` links
- say tier-specific reasoning support is fully absent
- claim runtime currently consumes pattern reports
- modify code or tests
- use network

## Verification

Run:

```powershell
git diff -- docs/agent_workorders/gemini-round2-phase-taxonomy-review.md
git status --short
git add docs/agent_workorders/gemini-round2-phase-taxonomy-review.md
git commit -m "docs: refine phase taxonomy review round2"
git push -u origin codex/phase3b-gemini-scope
```

Return:
- status
- changed file
- three corrected claims from round one
- five strongest final conclusions
- commit SHA
- push status, or exact push failure
