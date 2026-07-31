# DeepSeek v4 Flash Workorder

## Role

Test-first implementation worker for bounded Phase 3b scaffolding.

## Assigned Branch

Branch:
- `codex/phase3b-deepseek-tests`

Worktree:
- `C:\experiments\ssc\ds`

## Objective

Draft the test contract for Phase 2c exam-pattern intelligence and Phase 3 user-error intelligence.

This is tests/spec only. Do not implement production code.

## Allowed Files To Edit

You may create or modify only:
- preferred: `docs/agent_workorders/deepseek-pattern-test-spec.md`
- optional if safe: `tests/test_pattern_intelligence_contract.py`

## Files To Read

Required:
- `Plan.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-test-cases.md`
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `tests/test_phase3.py` if present
- `tests/test_phase3_eval.py` if present
- `src/ssc_study/archetypes.py`
- `src/ssc_study/phase3.py` if present
- `src/ssc_study/phase3_eval.py` if present

If Phase 3 files are missing in your worktree, record that as a context gap. Do not invent duplicate modules.

## Desired Test Coverage

Write tests or a test-spec report that specify, but do not implement, these behaviors:
- exam-pattern analysis is read-only
- exam-pattern analysis excludes holdout questions
- exam-pattern analysis reports section, archetype, tier, year, evidence IDs, and signal strength
- advisory mock blueprints do not create sessions or mutate queues
- user-error analysis is read-only
- user-error analysis excludes holdout-linked attempts
- user-error analysis uses latest attempt windows
- user-error analysis separates timing weakness from accuracy weakness
- priority combiner downweights low-confidence signals
- runtime Phase 3 action planning does not consume pattern reports

## Boundaries

Do not:
- modify production files
- modify existing tests except to import shared fixtures if absolutely necessary
- change DB schema
- create migrations
- add dependencies
- touch corpus outputs

## Verification

Run the narrow test command:

```powershell
if (Test-Path tests/test_pattern_intelligence_contract.py) { uv run pytest tests/test_pattern_intelligence_contract.py -q }
git status --short
git add docs/agent_workorders/deepseek-pattern-test-spec.md tests/test_pattern_intelligence_contract.py
git commit -m "test: specify pattern intelligence contract"
git push -u origin codex/phase3b-deepseek-tests
```

Expected result:
- fail because production code does not exist yet, or documentation-only if you wrote only the test spec.

Return:
- status
- changed files
- test command and result
- exact missing production API implied by the tests
- commit SHA
- push status, or exact push failure
