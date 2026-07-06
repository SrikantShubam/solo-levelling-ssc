# Prompt: Gemini Final UI Work

You are working in `C:\experiments\ssc`.

Your work order is:

`docs/phase1_frontend/workorders/gemini-05-guardian-readiness-ui.md`

Read these files first:

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

Goal:

Add a compact Guardian/readiness web surface that makes the post-baseline product flow clearer without claiming the web app can execute all daily study workflows.

Rules:

- Use existing FastAPI + Jinja + static JS/CSS.
- No React, build pipeline, auth, deployment, or account system.
- Keep smoke and full baseline guidance separate.
- Do not overstate Guardian execution. Label advisory planner output honestly.
- If Stitch MCP is available, use it for the design pass and report the artifact. If it is not available, say so clearly.
- Keep copy short and operational.

Required implementation:

1. Consume Grok's backend contract if it has landed.
2. Add a Guardian/readiness panel to the result page or landing page.
3. Show planner mode, total minutes, mock recommendation, pulse recommendation, warnings, and readiness availability/status.
4. Add unavailable states for missing backend data.
5. Add tests for rendering hooks and structured endpoint consumption.

Run:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

Report:

- whether Stitch MCP was actually used
- files changed
- UI behavior changed
- tests added
- exact commands run
- exact results
- limitations
