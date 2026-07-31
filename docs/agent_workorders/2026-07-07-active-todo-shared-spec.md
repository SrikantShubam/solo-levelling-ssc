# 2026-07-07 Active Todo Shared Spec

## Purpose

Convert today's checklist into parallel worker execution without losing project discipline.

This package is for:

- Grok: code-facing reconciliation, hardening triage, and targeted verification scope
- Gemini: UI-facing surfacing, reporting, and operator-facing review scope
- User: the real 2-hour Phase 1 baseline run

The baseline run itself is not worker-owned. It remains manual user validation.

## Project position

### Last landed changes

Latest landed `main` work completed the Phase 1 web bridge handoff:

- local baseline web flow
- Phase 1 result-page guidance
- frontend asset updates
- route and integration coverage

### Current local drift

The working tree now contains a substantial uncommitted hardening pass across:

- `src/ssc_corpus/*`
- `src/ssc_study/gates.py`
- `src/ssc_study/holdout.py`
- `src/ssc_study/models.py`
- `src/ssc_study/queues.py`
- `src/ssc_study/scheduler.py`
- multiple focused tests

### Overall project comparison

Per `README.md`, `Plan.md`, and `memory.md`, Phases 1-4 are broadly implemented.
That means today's worker goal is not new product invention. It is:

1. keep Phase 1 trustworthy before the user spends 2 hours on the baseline
2. reconcile current hardening work against the real Plan scope
3. tighten tests and operator-facing guidance
4. avoid speculative redesign

## User-owned work

The user owns the 2-hour baseline test block.

Workers must not claim the baseline has been completed unless they are explicitly given the user's actual run notes.

## Shared constraints

- Work in `C:\experiments\ssc`
- Follow `Plan.md`, `README.md`, `memory.md`, and the current source code
- Surgical changes only
- No React, deployment, auth, analytics, accounts, or schema redesign
- No unsupported product claims
- No answer leakage before submit
- Do not use smoke mode as proof of full baseline readiness
- Treat manual baseline validation as higher-priority truth than assumptions

## Shared goals

1. Make today's operator workflow clearer before and after the manual baseline
2. Keep the latest local hardening work aligned with the overall project plan
3. Strengthen verification around touched files and Phase 1 critical paths
4. Produce a reviewable, bounded output that Codex can integrate quickly

## Task split

### Grok owns

- reconcile the current local hardening scope with `Plan.md`
- identify which local changes are baseline-critical vs general hardening
- tighten backend/test-side verification for touched corpus/study areas
- propose or implement only minimal fixes required by failing or missing tests

### Gemini owns

- turn today's active checklist into a clearer operator-facing execution surface
- improve docs or small local UI/status surfaces only if they help the user's baseline workflow
- make the latest project state easier to read after the user's baseline run
- keep all messaging honest about advisory vs implemented behavior

## Non-goals

- running the user's 200-question baseline for them
- inventing new Phase 5+ product ideas
- broad refactors of scheduler, study loop, or corpus architecture
- changing schema unless explicitly required and proven
- adding remote services or frontend build tooling

## Acceptance criteria

Worker output is acceptable only if all are true:

1. It stays inside the assigned scope.
2. It cites `Plan.md`, repo code, or test evidence for behavioral claims.
3. It distinguishes implemented behavior from operator guidance.
4. It preserves current Phase 1 baseline constraints.
5. It includes focused verification commands and exact results.
6. It does not silently widen scope into unrelated cleanup.

## Required test cases

These are the minimum cases workers should preserve or extend.

### Phase 1 critical path

- full baseline path remains separate from smoke mode
- no correct answers leak before submit
- duplicate submit remains safe/idempotent if already covered
- result-page guidance still reflects current `Plan.md` thresholds

### Hardening reconciliation

- touched corpus/study modules still pass their focused tests
- holdout, queue, scheduler, extraction, and CLI behavior stay within existing contracts
- read-only/reporting paths do not invent new mutation behavior

### Operator-facing clarity

- user-facing guidance clearly marks manual steps vs implemented automation
- unavailable state is explicit instead of implied success

## Example findings

Good finding examples:

- "`scheduler.py` changed readiness routing, but no test proves it still matches the `Plan.md` exclusion rule below 55%."
- "`cli.py` now touches more error paths; add a focused regression instead of widening Phase 1 web tests."
- "`app.js` copy implies a workflow can start from web, but the repo only supports CLI follow-up today."

Bad finding examples:

- "The app should probably become multi-user."
- "Maybe redesign the whole dashboard."
- "Everything looks fine" without test evidence.

## Required deliverable shape

Every worker report must include:

- scope handled
- assumptions made
- files changed
- tests added or updated
- exact commands run
- exact results
- remaining limitations
- specific items that Codex should review before merge

