# Phase 3 Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic autonomous Phase 3 orchestration loop with a CLI entrypoint and test coverage.

**Architecture:** Add a dedicated `phase3.py` module that inspects existing gate and queue primitives, chooses the next diagnostic action, and returns a bounded run report. Keep session execution and queue logic in their current modules; the orchestrator only coordinates them.

**Tech Stack:** Python, SQLite, pytest, click/rich CLI.

---

### Task 1: Add orchestrator tests

**Files:**
- Create: `tests/test_phase3.py`
- Modify: `tests/test_cli.py`
- Test: `tests/test_phase3.py`, `tests/test_cli.py`

- [ ] **Step 1: Write failing orchestrator tests**

- [ ] **Step 2: Run the focused Phase 3 tests to verify they fail**

Run: `uv run pytest tests/test_phase3.py -q`
Expected: FAIL because `ssc_study.phase3` does not exist yet.

- [ ] **Step 3: Write failing CLI surface test**

- [ ] **Step 4: Run the CLI-focused test to verify it fails**

Run: `uv run pytest tests/test_cli.py -q`
Expected: FAIL because the `phase3` command does not exist yet.

### Task 2: Implement the orchestrator module

**Files:**
- Create: `src/ssc_study/phase3.py`
- Modify: `src/ssc_study/models.py`
- Test: `tests/test_phase3.py`

- [ ] **Step 1: Add result dataclasses for Phase 3 actions and runs**

- [ ] **Step 2: Implement deterministic next-action selection**

- [ ] **Step 3: Implement bounded loop execution with dry-run support**

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_phase3.py -q`
Expected: PASS

### Task 3: Integrate the CLI command

**Files:**
- Modify: `src/ssc_study/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Add `phase3` command and options**

- [ ] **Step 2: Print a concise action summary and stop reason**

- [ ] **Step 3: Run CLI-focused tests**

Run: `uv run pytest tests/test_cli.py -q`
Expected: PASS

### Task 4: Verify broader compatibility

**Files:**
- Modify: `memory.md`
- Test: `tests/test_phase3.py`, `tests/test_cli.py`, `tests/test_gates.py`, `tests/test_queues.py`, `tests/test_quiz.py`

- [ ] **Step 1: Run the targeted regression set**

Run: `uv run pytest tests/test_phase3.py tests/test_cli.py tests/test_gates.py tests/test_queues.py tests/test_quiz.py -q`
Expected: PASS

- [ ] **Step 2: Record the implementation result in `memory.md`**

- [ ] **Step 3: Commit or hand off with evidence**

