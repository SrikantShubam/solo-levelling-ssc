# Prompt For Gemini

You are Gemini acting as a senior product-minded frontend engineer.

You do not have MCP access in this workflow. Use local files only. Treat
`docs/phase1_frontend/workorders/gemini-02-stitch-ui-and-frontend.md` as the Stitch-oriented design
brief.

Read these files first:

- `docs/phase1_frontend/spec.md`
- `docs/phase1_frontend/test-cases.md`
- `docs/phase1_frontend/workorders/gemini-02-stitch-ui-and-frontend.md`
- Any backend files created for the Phase 1 web contract.

Your task:

Build the Phase 1 local exam frontend after the backend contract exists.

UI requirements:

- Build an exam cockpit, not a marketing page.
- Local Jinja templates plus static CSS/JS only.
- No React, Next.js, Vue, Svelte, Vite, or Node build step.
- Landing page shows readiness and section counts.
- Exam view supports answer selection, navigation, marked-for-review, elapsed timer, localStorage
  draft restore, and submit confirmation.
- Result view shows total score and section breakdown.
- Never show correct answers before submit.

Design direction:

- Dense and focused.
- Desktop-first but mobile usable.
- Use strong typography and deliberate color.
- Avoid generic AI purple styling.
- Keep the interface calm under exam pressure.

Implementation rules:

- Do not hardcode fake questions.
- Do not change question selection logic.
- Do not introduce auth, deployment, analytics, or accounts.
- Keep the frontend simple enough for pytest route/HTML smoke tests.

Tests:

- Add or update tests proving the landing page renders, static assets are served, and the result
  payload can be rendered.
- If a browser test dependency is already available, add one smoke browser test. If not, do not add
  a heavy dependency for v1.

Output format:

1. Summary of UI files changed.
2. How to run the local frontend.
3. Tests added.
4. Commands run with results.
5. Any remaining design or testing risk.

