# Phase 1 Frontend MVP Handoff

## Current truth

The Phase 1 web frontend is fully implemented and integrated. The application can be started locally via the CLI command `ssc-study web`. It serves a premium, dense exam cockpit UI for both Smoke Exams and the Full Baseline Exam, and automatically provides recommendations and next steps based on the scored results.

## Execution order

1. Read `spec.md` and `test-cases.md`.
2. Send `prompts/grok.md` to Grok for backend contract implementation.
3. Send `prompts/gemini.md` to Gemini for the Stitch-oriented UI and frontend implementation.
4. Send `prompts/deepseekv4.md` to DeepSeekV4 for adversarial tests and edge cases.
5. After all model outputs land in the repo, send `prompts/reviewer.md` to Codex.
6. Codex reviews the diff using `review-plan.md`, adds missing validation tests, then verifies.

## Final bridge package

After the baseline web MVP and manual browser smoke are accepted, use these files for the remaining coding bridge:

- `final-remaining-work.md`: current status, execution order, and definition of done.
- `final-spec.md`: backend/UI contract for the Phase 3, Guardian, and readiness bridge.
- `final-test-plan.md`: focused regression and acceptance tests.
- `agent-split-final.md`: final Grok/Gemini/DeepSeek ownership split.
- `workorders/grok-04-phase3-actionable-flow.md`: Grok backend work order.
- `workorders/gemini-05-guardian-readiness-ui.md`: Gemini UI work order.
- `workorders/deepseek-06-final-validation-and-review.md`: DeepSeek validation and review work order.
- `prompts/grok-final.md`: sendable Grok prompt.
- `prompts/gemini-final.md`: sendable Gemini prompt.
- `prompts/deepseek-final.md`: sendable DeepSeek prompt.
- `prompts/gemini-deepseek-final-combined.md`: single combined prompt file for both Gemini and DeepSeek.
- `prompts/gemini-self-review.md`: Gemini review-subagent prompt.
- `prompts/deepseek-self-review.md`: DeepSeek review-subagent prompt.
- `prompts/codex-final-review.md`: final strict review prompt.

## Work order map

- `workorders/grok-01-backend-contract.md`: backend/API contract, preflight, submit, result, data safety.
- `workorders/gemini-02-stitch-ui-and-frontend.md`: exam UI, static frontend behavior, design brief.
- `workorders/deepseekv4-03-tests-and-edge-cases.md`: tests, failure modes, double-submit and integrity checks.

## Non-negotiables

- Full baseline must use the real non-holdout `foundation_pulse` split: 80 Quant/DI, 40 Reasoning,
  40 English, 40 GK/GA.
- Smoke mode must exist so the frontend can be tested quickly.
- Do not expose correct answers to the browser before submit.
- Do not introduce a JavaScript framework for v1.
- Do not add auth, accounts, deployment, analytics, or cloud dependencies.
- Do not change the database schema unless the implementer proves the existing schema cannot support
  the MVP.
- Existing CLI behavior must keep working.

## Expected implementation outcome

The user can run a local web command, open a browser, take a short smoke exam, submit it, and see
results. With a populated eligible database, the same UI can run the full 200-question baseline.
