# Gemini Workorder 01: Remaining Scope Audit

## Role

Evidence-first auditor.

## Objective

Confirm the actual remaining work before implementation. The output must distinguish current repo gaps from documentation drift.

## Allowed Files To Edit

Create only:

- `docs/agent_workorders/gemini_remaining/remaining-audit-report.md`

## Required Files To Read

- `Plan.md`
- `README.md`
- `memory.md`
- `checklist.md`
- `docs/agent_workorders/phase3-scope-breakdown.md`
- `docs/agent_workorders/gemini_remaining/remaining-work-register.md`
- `docs/agent_workorders/gemini_remaining/specs/phase2c-pattern-intelligence-spec.md`
- `docs/agent_workorders/gemini_remaining/specs/phase4-guardian-spec.md`
- `src/ssc_study/cli.py`
- `src/ssc_study/readiness.py`
- `src/ssc_study/phase3.py`
- `src/ssc_study/phase3_eval.py`
- any `src/ssc_study/*pattern*` or `src/ssc_study/*guardian*` files if they exist
- related tests if matching modules exist

## Report Sections

Write these sections:

1. `Confirmed Implemented`
2. `Confirmed Remaining`
3. `Documentation Drift`
4. `Implementation Risk`
5. `Recommended Workorder Order`
6. `Evidence`

Every claim must cite file paths and line numbers.

## Commands

Use these commands or equivalent PowerShell commands:

```powershell
git status --short
rg -n "patterns|guardian|phase4|Phase 4|mock cadence|daily|180|pulse|external_mocks|calibrated|readiness" src tests README.md Plan.md docs
rg -n "Phase 2b is MVP-complete|Missing for full Phase 2b approval|Current Verdict|Phase 2c|Phase 3b" README.md docs memory.md
```

## Hard Rules

- Do not implement code.
- Do not modify tests.
- Do not rewrite README.
- Do not infer missing code from docs alone; inspect source.
- If a file is absent, report absence as evidence.

## Verification

Run:

```powershell
git diff -- docs/agent_workorders/gemini_remaining/remaining-audit-report.md
git status --short
```

Optional commit:

```powershell
git add docs/agent_workorders/gemini_remaining/remaining-audit-report.md
git commit -m "docs: audit remaining SSC work"
```

## Final Response

Return:

- audit verdict
- confirmed remaining items
- changed file
- commands run and result
- commit SHA if committed
- blockers

