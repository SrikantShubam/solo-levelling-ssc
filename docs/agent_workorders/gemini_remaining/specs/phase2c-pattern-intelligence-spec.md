# Phase 2c Pattern Intelligence Spec

## Goal

Build read-only exam-pattern intelligence that summarizes what the non-holdout corpus contains and produces advisory mock blueprints. The output may inform human review and future mock planning, but it must not mutate runtime state in v1.

## Source Files To Inspect

- `Plan.md`
- `README.md`
- `docs/agent_workorders/phase3-scope-breakdown.md`
- `docs/superpowers/specs/2026-06-25-phase2c-phase3-pattern-intelligence-design.md`
- `docs/superpowers/plans/2026-06-25-phase2c-phase3-pattern-intelligence.md`
- `src/ssc_study/db.py`
- `src/ssc_study/models.py`
- `src/ssc_study/archetypes.py`
- `src/ssc_study/phase3_eval.py`
- `src/ssc_study/cli.py`
- Existing tests around DB, CLI, Phase 3, queues, gates, and readiness

## Required Behavior

Add read-only analysis APIs:

```python
analyze_exam_patterns(db, *, tier=None, years=None, exclude_holdout=True) -> ExamPatternReport
combine_pattern_priorities(exam_report, user_report=None) -> PatternPriorityReport
```

Required report fields:

- total non-holdout question count
- filters applied
- section distribution
- tier distribution
- year distribution when source metadata supports it
- archetype distribution
- source question IDs for every reported pattern row
- signal strength: `insufficient`, `weak`, or `stable`
- advisory mock blueprint by section and archetype

Signal strength:

- `insufficient`: fewer than 30 eligible questions or fewer than 3 archetypes
- `weak`: at least 30 eligible questions but fewer than 100, or fewer than 10 archetypes
- `stable`: at least 100 eligible questions and at least 10 archetypes

The advisory mock blueprint must:

- derive only from non-holdout questions
- include section allocation and top archetype allocations
- include source question IDs used as evidence
- be labelled advisory
- not create a session, mock, attempt, queue item, archetype update, or readiness update

CLI:

```text
ssc-study patterns exam
ssc-study patterns priority
```

CLI output must include:

- eligible count
- signal strength
- section distribution
- top archetypes
- advisory disclaimer

## Explicit Non-Goals

- Do not use LLMs.
- Do not call Gemini, OpenAI, Qwen, DeepSeek, or any network API.
- Do not use holdout questions for pattern generation.
- Do not change extraction outputs.
- Do not create mocks or sessions.
- Do not modify Phase 3 orchestration to consume this output.
- Do not mutate readiness.

## Acceptance Tests

Tests must prove:

- holdout questions are excluded by default
- read-only analysis does not mutate core tables
- section/tier/archetype distributions are deterministic
- signal strength thresholds are visible
- advisory blueprint includes evidence question IDs
- CLI prints the key evidence and advisory status
- Phase 3 orchestration remains independent from pattern reports

## Verification

Run:

```powershell
uv run pytest tests/test_pattern_intelligence_contract.py tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py -q
uv run pytest -q
```

