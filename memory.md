## 2026-05-24 Extraction Stabilization

- P2 remains the active extraction pipeline; P1 is deprecated and only useful for historical/manual comparison.
- Root cause of many P2 batch failures was not pure OCR quality: Gemini quota errors were cached as page JSON with `questions: []`, then merged as if they were real empty pages.
- Extraction pages now carry `page_status`, `failure_type`, `provider`, `model`, `retryable`, `fallback_attempted`, and `fallback_used` metadata.
- Merge output now carries `structural_status` and `structural_failure_reasons`; `api_quota_or_rate_limit`, `model_refusal`, and JSON/schema failures are not treated as ordinary extraction misses.
- `ssc-corpus extract-pdf` now supports opt-in page fallback with `--allow-fallback --fallback-model <nim-model>`; fallback is never automatic.
- `ssc-corpus extract-pdf` now also supports provider selection, including NIM/OpenAI-compatible primary extraction.
- Added `ssc-corpus retry-failed-batch` and `ssc-corpus compare-phases` for patch reruns and phase reporting.
- Current NIM screening result: `meta/llama-4-maverick-17b-128e-instruct` is the strongest tested NIM model, but still too slow for broad full-PDF reruns; lighter NIM models collapsed on completeness.
- Generated investigation dossier: `reports/p2_failure_investigation_20260524.md` and `.json`.

## 2026-06-05 Phase 2b Audit Follow-Up

- Audited Phase 2b against `Plan.md` and README critic/test spec.
- Confirmed prior gaps around notification pause, migration safety, and sealed-holdout session typing; current code now observes `PAUSED` notification audits, blocks boss-fight queue loading during a major audit, migrates v13 DBs to accept `sealed_mock`, and records sealed-holdout sessions as `sealed_mock`.
- Added regression coverage for observable notification pause, boss-fight pause enforcement, migration 14 preserving existing `attempts.session_id` FKs, sealed-holdout session typing, and native pipeline comparison without historical fixture directories.
- Full suite verification: `uv run pytest -q` passed with `218 passed`, with warnings only for Python 3.10/google API support and deprecated `google.generativeai`.

## 2026-06-17 Phase 3 Orchestrator

- Added deterministic Phase 3 orchestration in `src/ssc_study/phase3.py`.
- The loop now selects bounded next actions in priority order: `probe -> remediation -> boss_fight -> sm2_review -> stop`.
- Added CLI entrypoint `ssc-study phase3` with `--max-steps`, `--dry-run`, `--tier`, and `--section`.
- Added regression coverage in `tests/test_phase3.py` and `tests/test_cli.py`.
- Verification: `uv run pytest tests/test_phase3.py tests/test_cli.py tests/test_gates.py tests/test_queues.py tests/test_quiz.py -q` passed with `39 passed`; `uv run pytest -q` passed with `225 passed` and the existing Google/Python warnings only.

## 2026-06-17 Phase 3 Evaluation

- Added Phase 3 prediction-vs-actual comparison in `src/ssc_study/phase3_eval.py`.
- Evaluation compares the pipeline's persisted route prediction for each archetype against the route implied by the latest actual attempts.
- Added pure probe classification helper in `src/ssc_study/gates.py` so route comparison uses the same thresholds as runtime gate evaluation without mutating DB state.
- Added CLI entrypoint `ssc-study phase3-eval` with optional `--archetype-id` filtering and `--limit`.
- Verification: `uv run pytest tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py tests/test_gates.py tests/test_queues.py tests/test_quiz.py -q` passed with `43 passed`; `uv run pytest -q` passed with `229 passed` and the same existing two warnings.

## 2026-06-25 Phase 3 Anti-Overfit Completion

- Added evaluation contract spec at `docs/superpowers/specs/2026-06-25-phase3-anti-overfit-completion-design.md`.
- Hardened `src/ssc_study/phase3_eval.py` without coupling it to runtime orchestration.
- Phase 3 evaluation is now explicitly read-only, derives actual routes from the latest 10 non-holdout attempts only, and reports `actual_attempt_count`, `actual_accuracy`, and `signal_strength` (`insufficient`, `weak`, `stable`) per comparison.
- `ssc-study phase3-eval` now prints attempt count, accuracy, and signal strength per archetype comparison without adding any mutating CLI behavior.
- Added regression coverage for evaluator read-only behavior, holdout exclusion, latest-window derivation, gate-boundary parity, high-priority boss classification, signal strength reporting, probe non-holdout thresholding, order invariance, no repeated archetype within one loop run, and CLI evidence display.
- Verification: `uv run pytest tests/test_phase3_eval.py tests/test_phase3.py tests/test_cli.py tests/test_gates.py -q` passed with `33 passed`; `uv run pytest tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py tests/test_gates.py tests/test_queues.py tests/test_quiz.py -q` passed with `56 passed`; `uv run pytest -q` passed with `242 passed` and the same existing two warnings.

## 2026-06-25 Hardening Pass

- Added nested transaction support in `src/ssc_study/db.py` using `threading.RLock` plus savepoint-backed `db.transaction()`, and replaced connection `assert` checks with `StudyDBError` so optimized Python runs do not silently lose safety checks.
- Made study writes atomic where they matter: quiz attempt persistence plus SM-2 update now commit as one unit; sealed holdout mock creation now performs cap check, session insert, and usage log insert in one transaction; row-to-model parsing is centralized in `Question.from_row`.
- Removed duplicated row parsing in scheduler/queues/gates/quiz and fixed the integration path so Phase 3 probe execution now consumes `Question.from_row` directly.
- Hardened corpus-side resource handling: PyMuPDF documents are always closed, corrupt cached page JSON self-heals by re-extracting, `ssc.nic.in` SSL bypass now emits a warning, CLI key/config failures now return clean `Error:` messages, AI-review label ordering is deterministic, and zero-area crops now raise immediately.
- Added `.env.example` for active provider keys and expanded regression coverage across DB, quiz, holdout, extraction, PDF layout, HTTP download warnings, CLI error handling, AI review delta/merge ordering, crops, and the affected Phase 3/gates paths.
- Verification: `uv run pytest tests/test_db.py tests/test_quiz.py tests/test_holdout.py tests/test_extraction.py tests/test_pdf_layout.py tests/test_http_download.py tests/test_corpus_cli.py tests/test_ai_review.py tests/test_crops_utils.py -q` passed with `56 passed`; `uv run pytest tests/test_phase3.py tests/test_gates.py -q` passed with `18 passed`; `uv run pytest -q` passed with `254 passed` and the same existing two warnings about Python 3.10 support and deprecated `google.generativeai`.

## 2026-06-25 Phase 3b Worker Setup

- Clarified scope from `Plan.md`: original Phase 2 owns corpus/holdout/atlas construction and pattern archetypes; original Phase 3 owns diagnostic grinding over an existing atlas. Model-based paper pattern discovery is not part of the current formal Phase 3 implementation and should be treated as Phase 2c or read-only Phase 3b before runtime integration.
- Created worker coordination docs under `docs/agent_workorders/`: phase scope breakdown, shared guardrails, per-model workorders, and main orchestrator review plan.
- Created isolated worker branches/worktrees:
  - Gemini scope/design: `codex/phase3b-gemini-scope` at `C:\experiments\ssc\gm`
  - DeepSeek tests: `codex/phase3b-deepseek-tests` at `C:\experiments\ssc\ds`
  - Mimo inventory: `codex/phase3b-mimo-inventory` at `C:\experiments\ssc\mm`
- Worker branches are based on `HEAD` commit `61b1490` and may not include current uncommitted main-workspace Phase 3/hardening files. Guardrails instruct workers to report missing files as context gaps instead of inventing replacements.
- Initial `.worktrees/phase3b-deepseek-tests` creation failed due to Windows filename length under deep deprecated assets. Worker worktrees now use short root-level folders and the guardrails require commit plus `git push -u origin <branch>`.

## 2026-06-25 Phase 3b Worker Round 2

- Reviewed round-one worker outputs: Gemini was strongest but overstated the absence of tier-aware reasoning support; Mimo had a useful inventory but falsely claimed Phase 3 tests were missing; DeepSeek produced a useful prose contract but a low-quality pytest artifact.
- Updated canonical worker docs to harden acceptance rules around stale-branch drift, spec-quality vs merge-quality outputs, and contract-test hygiene.
- Added round-two worker package:
  - `docs/agent_workorders/gemini-round2-workorder.md`
  - `docs/agent_workorders/deepseek-round2-workorder.md`
  - `docs/agent_workorders/mimo-round2-workorder.md`
  - `docs/agent_workorders/worker-round2-scoring-rubric.md`
  - `docs/agent_workorders/worker-round2-prompts.md`
- Phase naming is now explicitly stabilized in canonical docs:
  - Phase 2c = exam-paper patterns
  - Phase 3 = user-error patterns
  - Phase 3b = optional shorthand for a read-only advisory layer, not a separate runtime scheduler

## 2026-07-06 Remaining Scope Completion

- Completed remaining Gemini handoff workorders: Phase 2c Exam-Pattern Intelligence, Phase 4 Guardian Planner, and Documentation Consistency.
- Added read-only `patterns_exam.py` and `patterns_priority.py` to calculate exam frequency metrics and priorities.
- Added read-only `guardian.py` daily schedule planner, handling 180 min splits, Tier-1 floor shifts, pulse schedules, and collision resolution.
- Integrated `ssc-study patterns` and `ssc-study guardian` commands into `cli.py`.
- Created comprehensive contract tests in `test_pattern_intelligence_contract.py` and `test_guardian.py`.
- Updated documentation files to resolve Phase 2b and Phase 3 inconsistencies and reflect the current completed state of the repository.
- Completed Phase 1 Web Frontend stitch:
  - Overwrote `templates/landing.html` with a premium, dense exam cockpit.
  - Overwrote `static/app.css` with clean CSS styling featuring outfit typography, color tokens, visual cards, grid buttons, and confirm modals.
  - Overwrote `static/app.js` with premium client-side logic handling elapsed time, time-spent-seconds accumulation per question, marked-for-review, modal warning text counts, and localStorage draft recovery.
  - Registered `ssc-study web` CLI subcommand inside `cli.py`.
  - Added `check_same_thread=False` to SQLite connection calls in `db.py` and `tests/conftest.py` to prevent thread safety errors during ASGI routing/FastAPI tests.
  - Created `tests/test_web.py` for route and landing page testing.

## 2026-07-06 Codex Review Fixes

- Fixed Phase 2c/Phase 4 review blockers after Gemini implementation: committed Phase 3 runtime/test files into branch scope, excluded holdout attempts from `patterns priority`, stopped Guardian from inventing mock days with no mock history, skipped nullable external mock calibrated scores with warnings, and downgraded Phase 4 docs to planner-v1 status.
- Added regression coverage for holdout leakage, fresh-DB Guardian mock recommendations, and nullable external mock calibrated scores.

## 2026-07-06 Phase 1 Frontend Planning Package

- Created the canonical Phase 1 frontend handoff under `docs/phase1_frontend/`.
- The package defines the local FastAPI/Jinja/static MVP, real `foundation_pulse` 200-question split, 5-question smoke mode, no-answer-leak contract, work orders for Grok/Gemini/DeepSeekV4, and the Codex reviewer checklist.
- This pass created planning/spec/prompt files only; it did not implement frontend source code.
