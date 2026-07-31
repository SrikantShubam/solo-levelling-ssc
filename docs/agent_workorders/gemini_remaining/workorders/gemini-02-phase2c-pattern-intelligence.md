# Gemini Workorder 02: Phase 2c Pattern Intelligence

## Role

Implementation worker for read-only exam-pattern intelligence.

## Objective

Implement the v1 Phase 2c pattern-intelligence report described in:

- `docs/agent_workorders/gemini_remaining/specs/phase2c-pattern-intelligence-spec.md`

Start with tests, then implement the smallest production surface that passes them.

## Allowed Files To Edit

You may create or modify only:

- `src/ssc_study/patterns_exam.py`
- `src/ssc_study/patterns_priority.py`
- `src/ssc_study/cli.py`
- `tests/test_pattern_intelligence_contract.py`
- `tests/test_cli.py`
- `memory.md` only to append a short completion note after verification

If you need to touch another file, stop and report why.

## Required Files To Read

- `Plan.md`
- `README.md`
- `docs/agent_workorders/gemini_remaining/specs/phase2c-pattern-intelligence-spec.md`
- `docs/superpowers/specs/2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `src/ssc_study/db.py`
- `src/ssc_study/models.py`
- `src/ssc_study/archetypes.py`
- `src/ssc_study/phase3.py`
- `src/ssc_study/phase3_eval.py`
- `src/ssc_study/cli.py`
- `tests/test_phase3.py`
- `tests/test_phase3_eval.py`
- `tests/test_cli.py`

## Required Tests

Add tests proving:

- `analyze_exam_patterns` excludes holdout questions by default.
- the analyzer does not change row counts in `questions`, `attempts`, `sessions`, `archetypes`, or `sm2_state`.
- distributions include section, tier, year when available, and archetype.
- each pattern row exposes source question IDs.
- signal strength follows the spec thresholds.
- advisory mock blueprint is labelled advisory and does not create a session.
- `ssc-study patterns exam` renders eligible count, signal strength, and top archetypes.
- Phase 3 action planning does not import or consume pattern reports.

## Implementation Constraints

- Use existing DB helpers and row conventions.
- Prefer dataclasses in the new modules.
- Keep all functions deterministic.
- Default to `exclude_holdout=True`.
- Do not add LLM calls.
- Do not add dependencies.
- Do not mutate runtime tables.
- Do not modify Phase 3 behavior.

## Verification

Run:

```powershell
uv run pytest tests/test_pattern_intelligence_contract.py tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py -q
uv run pytest -q
git diff -- src/ssc_study/patterns_exam.py src/ssc_study/patterns_priority.py src/ssc_study/cli.py tests/test_pattern_intelligence_contract.py tests/test_cli.py memory.md
git status --short
```

Commit if tests pass:

```powershell
git add src/ssc_study/patterns_exam.py src/ssc_study/patterns_priority.py src/ssc_study/cli.py tests/test_pattern_intelligence_contract.py tests/test_cli.py memory.md
git commit -m "feat: add read-only pattern intelligence"
```

## Final Response

Return:

- summary
- changed files
- exact verification results
- commit SHA if committed
- any deferred behavior

