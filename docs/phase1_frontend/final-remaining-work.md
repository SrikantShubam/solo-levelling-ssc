# Final Remaining Coding Handoff

## Current status

Phase 1 baseline web MVP is implemented and manually smoke-tested by the user. The browser smoke path confirmed that submitted attempts are persisted to SQLite.

Automated coverage currently verifies the backend, route, submit integrity, threshold guidance, and static asset behavior. The latest Codex verification passed:

- `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
- `uv run pytest -q`

The full 200-question baseline run is intentionally excluded from this handoff because it is a user activity, not a coding task.

## Remaining product gap

The app still behaves like a baseline exam console plus CLI recommendations. The next coding target is to turn the recommendation layer into a small actionable product flow:

1. Phase 3 actionable flow: after baseline, expose the next diagnostic target and make it possible to start a supported follow-up session from the web.
2. Guardian/readiness surface: expose the daily plan and readiness state in the web UI without pretending Guardian execution is complete.
3. Final review gate: Codex reviews the combined agent outputs, adds missing tests, and rejects overbuilt or speculative changes.

## Execution order

1. Send `prompts/grok-final.md` to Grok if the Phase 3 backend contract is not already landed.
2. Send `prompts/gemini-final.md` to Gemini for UI/product surface work.
3. Ask Gemini to run `prompts/gemini-self-review.md` as a review subagent before handoff.
4. Send `prompts/deepseek-final.md` to DeepSeek for adversarial tests and final validation.
5. Ask DeepSeek to run `prompts/deepseek-self-review.md` as a review subagent before handoff.
6. Run the tests listed in `final-test-plan.md`.
7. Send `prompts/codex-final-review.md` to Codex for strict integration review.

## Non-negotiables

- Keep local-only FastAPI + Jinja + static JS/CSS.
- No React, auth, deployment, accounts, analytics, or new database schema unless explicitly justified.
- Do not break the completed Phase 1 baseline flow.
- Do not derive diagnostic unlocks from smoke mode.
- Do not expose correct answers before submit.
- Treat CLI features as existing capabilities, but do not claim web execution exists unless implemented and tested.

## Definition of done

- Full baseline result can show a concrete Phase 3 next action based on persisted DB state.
- The user can start or inspect the next supported diagnostic action from the web, not only read generic CLI text.
- Guardian/readiness information is surfaced honestly as planner/readiness state, not full execution.
- Focused tests cover the new endpoints and frontend rendering contract.
- Full test suite remains green.
