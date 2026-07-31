# Phase 2c And Phase 3 Pattern Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build read-only exam-pattern and user-error pattern intelligence reports with clear phase boundaries.

**Architecture:** Add documentation and tests first, then implement small report modules only after worker review. Exam-pattern analysis reads corpus questions only; user-error analysis reads recent non-holdout attempts. A later priority combiner joins the two reports without mutating runtime state.

**Tech Stack:** Python, SQLite, pytest, existing `ssc_study` DB/models/CLI patterns.

---

## Task 1: Lock Phase Taxonomy

Files:
- Modify: `README.md`
- Modify: `docs/agent_workorders/phase3-scope-breakdown.md`
- Test: documentation review only

Steps:
- [ ] Update the README phase table so Phase 1 means Foundation Gate, not PDF acquisition.
- [ ] Add Phase 2c as Exam Pattern Intelligence.
- [ ] Keep Phase 3 as Diagnostic Grinding / User Diagnostic Intelligence.
- [ ] Mark Phase 4 as Main Grind and mock cadence consumer.
- [ ] Verify no doc claims model pattern output mutates runtime state.

## Task 2: Add Test Contract

Files:
- Create: `tests/test_pattern_intelligence_contract.py`

Steps:
- [ ] Add tests for exam-pattern read-only behavior.
- [ ] Add tests for holdout exclusion in exam-pattern analysis.
- [ ] Add tests for section/archetype/tier/year distribution output.
- [ ] Add tests for user-error latest-window behavior.
- [ ] Add tests for holdout-linked attempt exclusion.
- [ ] Add tests proving Phase 3 action planning does not consume pattern reports.

## Task 3: Implement Read-Only Exam Pattern Report

Files:
- Create: `src/ssc_study/patterns_exam.py`
- Test: `tests/test_pattern_intelligence_contract.py`

Steps:
- [ ] Add dataclasses for exam pattern rows and report summaries.
- [ ] Query non-holdout questions only.
- [ ] Compute section, tier, year, and archetype distributions.
- [ ] Generate an advisory mock blueprint.
- [ ] Add signal strength based on evidence count.
- [ ] Keep the function pure/read-only.

## Task 4: Implement Read-Only User Error Pattern Report

Files:
- Create: `src/ssc_study/patterns_user.py`
- Test: `tests/test_pattern_intelligence_contract.py`

Steps:
- [ ] Add dataclasses for user pattern rows and report summaries.
- [ ] Query latest non-holdout attempts only.
- [ ] Detect repeated wrong archetypes and concept tags.
- [ ] Detect timing-pressure candidates separately from accuracy weakness.
- [ ] Include source attempt IDs and question IDs.
- [ ] Keep the function pure/read-only.

## Task 5: Implement Advisory Priority Combiner

Files:
- Create: `src/ssc_study/patterns_priority.py`
- Test: `tests/test_pattern_intelligence_contract.py`

Steps:
- [ ] Combine exam importance and user weakness with confidence.
- [ ] Downweight weak/insufficient signals.
- [ ] Return advisory priorities only.
- [ ] Do not update queues, gates, readiness, or sessions.

## Task 6: Add CLI Reports

Files:
- Modify: `src/ssc_study/cli.py`
- Test: `tests/test_cli.py`

Steps:
- [ ] Add `ssc-study patterns exam`.
- [ ] Add `ssc-study patterns user`.
- [ ] Add `ssc-study patterns priority`.
- [ ] Print counts, signal strength, and evidence IDs.
- [ ] Add CLI read-only tests.

## Verification

Run:

```powershell
uv run pytest tests/test_pattern_intelligence_contract.py tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py -q
uv run pytest -q
```

Expected:
- Pattern-intelligence tests pass.
- Existing Phase 3 tests still pass.
- Full suite remains green.
