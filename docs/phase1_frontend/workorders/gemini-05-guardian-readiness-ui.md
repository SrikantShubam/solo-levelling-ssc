# Work Order: Gemini 05 - Guardian And Readiness Web Surface

## Objective

Add a small honest web surface for Guardian planner and readiness state. The UI should help the user understand what to do after baseline without claiming the web app can execute all daily study workflows.

## Read first

- `Plan.md`
- `grok_critic.md`
- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `src/ssc_study/web.py`
- `src/ssc_study/static/app.js`
- `src/ssc_study/static/app.css`
- `src/ssc_study/templates/landing.html`
- `src/ssc_study/guardian.py`
- readiness-related source files if present
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

## Constraints

- Use the existing FastAPI + Jinja + static JS/CSS frontend.
- Do not add React or a build pipeline.
- Do not change the baseline exam flow except where needed to display the summary.
- Keep smoke mode separate from full baseline guidance.
- Do not overstate readiness or Guardian execution. If something is advisory, label it advisory.
- If Stitch MCP is available in your environment, use it for the design pass and cite the Stitch artifact. If it is not available, state that clearly and proceed with a restrained CSS/HTML implementation.

## Tasks

1. Consume the backend contracts from Grok's work if available.
2. Add a compact Guardian/readiness panel to the result page or landing page.
3. Display:
   - Guardian planner mode
   - total minutes
   - mock recommendation
   - pulse recommendation
   - warnings
   - readiness availability/status if available
4. Add clear unavailable states instead of hiding missing backend capabilities.
5. Keep copy short and task-oriented.
6. Add or update tests for template/static rendering hooks and endpoint consumption.

## Acceptance criteria

- Result page remains usable on smoke and full baseline results.
- Guardian/readiness panel renders from structured backend data.
- UI does not claim full Guardian execution exists.
- Static JS/CSS remain local-only.
- Focused web tests pass.
- Full suite passes.

## Deliverable report

Include:

- whether Stitch MCP was actually used
- UI surfaces changed
- backend contracts consumed
- tests added
- exact commands and results
- remaining limitations
