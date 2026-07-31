# DeepSeek Round 2 Workorder

## Role

Contract-test and test-spec reviewer with strict merge-quality gates.

## Assigned Branch

Branch:
- `codex/phase3b-deepseek-tests`

Worktree:
- `C:\experiments\ssc\ds`

## Objective

Redo the pattern-intelligence contract package with stronger test discipline.

Round one surfaced useful API ideas, but the pytest artifact was not merge-quality. This round must distinguish:
- `spec-quality`: useful contract notes that still need orchestrator rewrite
- `merge-quality`: tests or docs that can be copied into main with minimal edits

## Allowed Files To Edit

You may create or modify only:
- `docs/agent_workorders/deepseek-round2-pattern-contract.md`
- optional: `tests/test_pattern_intelligence_contract.py`

If you touch the test file, it must satisfy the contract-shape rules in the canonical docs.

## Required Files To Read

- `Plan.md`
- `README.md`
- `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md`
- `C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-test-cases.md`
- `C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md`
- `C:\experiments\ssc\docs\superpowers\specs\2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `C:\experiments\ssc\tests\test_phase3.py`
- `C:\experiments\ssc\tests\test_phase3_eval.py`
- `C:\experiments\ssc\src\ssc_study\phase3.py`
- `C:\experiments\ssc\src\ssc_study\phase3_eval.py`

## Deliverable

Write `docs/agent_workorders/deepseek-round2-pattern-contract.md` with:

1. `Round One Failures To Correct`
- top-level missing-module import failure
- tautological assertion patterns
- overconstrained API or module-shape assumptions

2. `Canonical Contract`
- exam-pattern behaviors
- user-error behaviors
- priority-combiner behaviors
- Phase 3 boundary behaviors

3. `Spec-Quality Vs Merge-Quality`
- label each proposed test or test group

4. `If Updating Pytest`
- explain why each edited test is collection-safe
- explain why each failure mode is meaningful

## Test Rules

If you edit `tests/test_pattern_intelligence_contract.py`, you must not:
- fail collection through top-level import of a missing module
- use `or True`, tautological assertions, or placeholder checks
- hardcode a single future module path unless the canonical spec fixes it
- assume dataclass fields beyond the canonical spec

Preferred strategy:
- docs-only if you cannot produce merge-quality tests
- otherwise, a collection-safe contract file that clearly marks pre-implementation expectations

## Verification

Run:

```powershell
if (Test-Path tests/test_pattern_intelligence_contract.py) { uv run pytest tests/test_pattern_intelligence_contract.py -q --tb=short }
git status --short
git add docs/agent_workorders/deepseek-round2-pattern-contract.md tests/test_pattern_intelligence_contract.py
git commit -m "test: refine pattern intelligence contract round2"
git push -u origin codex/phase3b-deepseek-tests
```

Return:
- status
- changed files
- whether the output is `spec-quality` or `merge-quality`
- exact verification result
- exact remaining production API assumptions
- commit SHA
- push status, or exact push failure
