# Final Agent Split

## Purpose

This file defines the final Gemini and DeepSeek split after Phase 1 web MVP acceptance and browser smoke confirmation.

The full 200-question baseline run is excluded. It is user work, not coding work.

## Ownership

### Gemini owns UI/product surface

Gemini should make the existing web app clearer and more usable after baseline submission.

Primary files:

- `src/ssc_study/templates/landing.html`
- `src/ssc_study/static/app.js`
- `src/ssc_study/static/app.css`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

Expected output:

- Guardian/readiness panel rendered from structured backend data.
- Phase 3 next action displayed as an operational next step.
- Honest unavailable/advisory states.
- No framework or design-system rewrite.

### DeepSeek owns tests and adversarial validation

DeepSeek should harden the final bridge and review both backend and frontend changes.

Primary files:

- `tests/test_baseline_web.py`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`
- new narrowly scoped tests if needed
- source files only when a tested bug must be fixed

Expected output:

- Route/schema tests.
- Threshold and smoke/full separation tests.
- No-mutation tests for read-only endpoints.
- Frontend rendering contract tests.
- A strict review report of Gemini/Grok claims.

## Sequencing

1. Grok lands backend contract if not already done.
2. Gemini builds UI against the backend contract.
3. DeepSeek validates the combined backend/UI behavior and fixes only test-proven bugs.
4. Codex runs final strict integration review.

## Shared constraints

- Local-only app.
- FastAPI + Jinja + static JS/CSS only.
- No React.
- No auth.
- No deployment.
- No DB schema changes without explicit proof.
- Do not use smoke results to unlock or route Phase 3.
- Do not claim web execution exists unless it is implemented and tested.
- Do not expose correct answers before submit.
