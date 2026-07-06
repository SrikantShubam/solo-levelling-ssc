# Work Order: Gemini 02 Stitch UI And Frontend

## Objective

Build the local Phase 1 exam UI after the backend contract exists. The UI must let the user take a
smoke exam and the full baseline exam through a browser.

## Important constraint

Gemini may not have MCP access in this workflow. Do not depend on MCP calls. Use this file as the
Stitch-oriented design brief and implement from local files.

## Design direction

Design an exam cockpit, not a SaaS homepage.

Visual intent:

- Dense, focused, test-center feel.
- Clear question hierarchy.
- High-contrast answer controls.
- A persistent question navigator.
- Calm warning states for unanswered questions and underfilled datasets.
- No purple-default AI aesthetic.
- No generic hero section.

Suggested palette:

- Background: warm paper or slate-tinted neutral.
- Primary action: deep green or ink blue.
- Warning: amber.
- Error: muted red.
- Answered state: green.
- Marked state: amber.
- Current question: strong outline.

## Frontend behavior

- Render landing/preflight state.
- Start smoke exam.
- Start full exam only when backend says it is ready.
- Render one question at a time.
- Save selected answers in browser localStorage by `exam_id`.
- Track per-question elapsed time approximately.
- Support previous/next navigation.
- Support direct question grid navigation.
- Support marked-for-review state in the browser.
- Confirm submit and show unanswered count.
- Render result summary after submit.

## Implementation constraints

- Use Jinja templates plus static CSS/JS.
- Do not add React, Next.js, Vue, Svelte, Vite, or a Node build step.
- Do not expose correct answers before submit.
- Do not hardcode fake questions.
- Do not change backend selection logic.
- Keep UI source small and readable.

## Minimum pages/components

- Landing/preflight page.
- Exam page/app shell.
- Result view.
- Shared error banner.
- Static CSS file.
- Static JS file.

## Tests to add or support

- Landing page route renders.
- Static CSS and JS routes serve assets.
- HTML contains smoke/full controls.
- JS can render a smoke payload shape.
- Submit confirmation includes unanswered count.
- Result renderer handles section breakdown.

## Acceptance criteria

- User can complete a smoke exam without touching the terminal after server start.
- UI prevents full baseline start when backend preflight says underfilled.
- UI restores a local draft after refresh.
- UI submits only question IDs, selected answers, and timing data.
- UI never renders correct answer labels before submit.

## Output required

Report:

- Templates/static files changed.
- Backend files touched, if any.
- Tests added or updated.
- Exact commands and results.
- Screenshots if available, but do not block on screenshots.

