# Gemini Workorder 04: Documentation Consistency

## Role

Documentation cleanup worker.

## Objective

Update docs so the project status is clear after the implementation work. Use:

- `docs/agent_workorders/gemini_remaining/specs/docs-consistency-spec.md`

## Allowed Files To Edit

You may modify only:

- `README.md`
- `docs/agent_workorders/phase3-scope-breakdown.md`
- `docs/agent_workorders/pattern-intelligence-guardrails.md`
- `docs/agent_workorders/gemini_remaining/remaining-work-register.md`
- `memory.md` only to append a short completion note after verification

If you need to touch another file, stop and report why.

## Required Files To Read

- `README.md`
- `Plan.md`
- `memory.md`
- `docs/agent_workorders/phase3-scope-breakdown.md`
- `docs/agent_workorders/pattern-intelligence-guardrails.md`
- `docs/agent_workorders/gemini_remaining/specs/docs-consistency-spec.md`
- `docs/agent_workorders/gemini_remaining/remaining-work-register.md`

## Required Changes

- Add a current-status note near the README Phase 2b critic explaining that it is historical and later sections supersede it.
- Update the README phase table to include Phase 2c.
- Keep Phase 4 marked upcoming unless `src/ssc_study/guardian.py` and tests exist and pass.
- Make Phase 3 wording match `phase3-scope-breakdown.md`.
- Remove or qualify any claim that model-generated pattern output currently mutates runtime state.
- Keep the documentation concise.

## Verification

Run:

```powershell
rg -n "Phase 2b is MVP-complete|Missing for full Phase 2b approval|Current Verdict|Phase 2c|Phase 3b|Phase 4|runtime.*pattern|mutate" README.md docs
git diff -- README.md docs/agent_workorders/phase3-scope-breakdown.md docs/agent_workorders/pattern-intelligence-guardrails.md docs/agent_workorders/gemini_remaining/remaining-work-register.md memory.md
git status --short
```

Commit if the diff is correct:

```powershell
git add README.md docs/agent_workorders/phase3-scope-breakdown.md docs/agent_workorders/pattern-intelligence-guardrails.md docs/agent_workorders/gemini_remaining/remaining-work-register.md memory.md
git commit -m "docs: clarify remaining SSC phases"
```

## Final Response

Return:

- summary
- changed files
- exact verification results
- commit SHA if committed
- any remaining ambiguous doc claim

