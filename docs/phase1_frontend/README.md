# Phase 1 Frontend MVP Handoff

## Current truth

The Phase 1 frontend is not implemented yet. The backend already has CLI support for a
`foundation_pulse` baseline through `ssc-study quiz --session-type foundation_pulse --count 200`.
That path enforces the required split and excludes holdout questions, but it is not a web UI.

This package exists so Grok, Gemini, DeepSeekV4, and Codex can work in an agentic flow without
guessing scope.

## Execution order

1. Read `spec.md` and `test-cases.md`.
2. Send `prompts/grok.md` to Grok for backend contract implementation.
3. Send `prompts/gemini.md` to Gemini for the Stitch-oriented UI and frontend implementation.
4. Send `prompts/deepseekv4.md` to DeepSeekV4 for adversarial tests and edge cases.
5. After all model outputs land in the repo, send `prompts/reviewer.md` to Codex.
6. Codex reviews the diff using `review-plan.md`, adds missing validation tests, then verifies.

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

