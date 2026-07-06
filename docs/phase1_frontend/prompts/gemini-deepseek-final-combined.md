# Combined Prompt: Gemini + DeepSeek Final Phase 1 Product Bridge

You are working in `C:\experiments\ssc`.

This is a combined handoff prompt for two agents:

- Gemini: UI/product surface implementation.
- DeepSeek: adversarial validation, tests, and review.

Both agents must read this whole file first, then execute only the section assigned to them.

## Shared context

Phase 1 baseline web MVP is implemented and manually smoke-tested by the user. The browser smoke path confirmed that submitted attempts are persisted to SQLite.

The full 200-question baseline run is excluded from this work. That is user activity, not coding work.

The remaining coding goal is to move from "baseline exam plus CLI recommendations" to a minimal local product bridge:

- show a concrete Phase 3 next action after a full baseline
- surface Guardian/readiness state honestly
- keep smoke mode as validation-only
- preserve the completed baseline start/submit/result flow

## Shared files to read first

- `Plan.md`
- `grok_critic.md`
- `docs/phase1_frontend/agent-split-final.md`
- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `docs/phase1_frontend/workorders/gemini-05-guardian-readiness-ui.md`
- `docs/phase1_frontend/workorders/deepseek-06-final-validation-and-review.md`
- `src/ssc_study/web.py`
- `src/ssc_study/baseline_web.py`
- `src/ssc_study/static/app.js`
- `src/ssc_study/static/app.css`
- `src/ssc_study/templates/landing.html`
- `src/ssc_study/phase3.py`
- `src/ssc_study/guardian.py`
- `tests/test_baseline_web.py`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

## Shared rules

- Think before coding. State assumptions in your report.
- Make surgical changes only.
- Keep FastAPI + Jinja + static JS/CSS.
- No React.
- No auth.
- No deployment.
- No account system.
- No analytics.
- No DB schema change unless absolutely necessary and justified.
- Do not break Phase 1 baseline start/submit/result.
- Do not derive Phase 3 guidance from smoke mode.
- Do not expose correct answers before submit.
- Do not claim web execution exists unless it is implemented and tested.
- Verify before reporting success.

## Gemini section: UI/product surface

Gemini owns the visible web product surface.

### Gemini objective

Add a compact Guardian/readiness and Phase 3 next-action surface to the existing web UI. The result page should feel like the next step in the study product, not a generic score page with CLI text.

### Gemini scope

Primary files:

- `src/ssc_study/templates/landing.html`
- `src/ssc_study/static/app.js`
- `src/ssc_study/static/app.css`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

You may touch `src/ssc_study/web.py` only if a small route or payload shape is required and no backend agent has already provided it.

### Gemini tasks

1. Consume existing structured backend data if available:
   - baseline `next_steps`
   - Phase 3 next action
   - Guardian/readiness summary
2. Render a compact post-result panel that shows:
   - smoke warning for smoke mode only
   - section score buckets for full baseline
   - Phase 3 next diagnostic target if available
   - Guardian planner mode and total minutes if available
   - mock recommendation
   - pulse recommendation
   - readiness availability/status if available
   - exact CLI fallback command when web execution is not implemented
3. Add honest unavailable states:
   - readiness unavailable
   - Guardian unavailable
   - no Phase 3 eligible work
4. Keep copy short, operational, and scannable.
5. Preserve the current dense exam cockpit style.
6. If Stitch MCP is available in your environment, use it for the design pass and report the artifact. If it is not available, state clearly: "Stitch MCP was not available/used."

### Gemini acceptance criteria

- Smoke result does not show Phase 3 weak-section guidance.
- Full result can show Phase 3, Guardian, and readiness states from structured data.
- UI does not overclaim daily-study execution.
- Static assets remain local-only.
- Tests cover rendering hooks or endpoint consumption.
- Focused and full test suites pass.

### Gemini self-review before handoff

Before reporting completion, run your own review pass:

- Does the UI use structured backend data where available?
- Does smoke mode show only smoke/full-baseline guidance?
- Does full baseline result show Phase 3, Guardian, and readiness states honestly?
- Is advisory Guardian output labeled advisory?
- Does missing readiness data have an unavailable state?
- Did you add a new JS framework or build pipeline? If yes, revert that direction.
- Are tests checking behavior or only placeholder strings?
- Was Stitch MCP actually used? Do not say yes unless it truly was.

### Gemini report format

Report:

- assumptions
- files changed
- UI behavior changed
- whether Stitch MCP was actually used
- tests added
- exact commands run
- exact test results
- remaining limitations

## DeepSeek section: adversarial validation and tests

DeepSeek owns final validation, tests, and bug fixes proven by tests.

### DeepSeek objective

Review the combined backend/UI bridge with strict skepticism. Add missing tests, prove or disprove implementation claims, and fix only concrete bugs exposed by tests.

### DeepSeek scope

Primary files:

- `tests/test_baseline_web.py`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

You may touch source files only when a test exposes a real bug.

### DeepSeek tasks

1. Verify smoke/full separation:
   - smoke mode is validation-only
   - smoke next steps do not show Phase 3 weak-section guidance
2. Verify `Plan.md` thresholds:
   - `>= 70%`: boss-fight unlocked / good standing
   - `65-69%`: boss fight with paired remediation
   - `55-64%`: remediation priority
   - `< 55%`: remediation first and excluded from readiness scoring until 65%
3. Verify Phase 3 next-action behavior:
   - stable schema
   - optional section filter
   - no-work stop state
   - no DB mutation for read-only endpoint
4. Verify Guardian/readiness summary:
   - planner mode is honest
   - unavailable state is explicit
   - optional failures do not become HTTP 500s unless truly fatal
5. Verify frontend rendering contract:
   - result page contains hooks for smoke warning
   - threshold buckets
   - Phase 3 next action
   - Guardian/readiness panel
   - unavailable states
6. Verify existing safety contracts:
   - no correct-answer leakage before submit
   - duplicate submit remains idempotent
   - holdout questions are rejected/excluded

### DeepSeek acceptance criteria

- Tests would fail against the previously known bad behavior.
- Tests cover behavior, not just placeholder presence.
- Any source edits are minimal and test-driven.
- Focused and full test suites pass.

### DeepSeek self-review before handoff

Before reporting completion, run your own review pass:

- Are the tests actually testing behavior promised in the report?
- Would the tests fail against the previous known bugs?
- Are read-only endpoints tested for no DB mutation?
- Is smoke/full behavior separation tested?
- Do threshold buckets match `Plan.md` exactly?
- Are Guardian/readiness unavailable states tested?
- Was the full suite command actually run?
- Did any fix introduce UI redesign or scope creep?

### DeepSeek report format

Report:

- assumptions
- defects found
- tests added
- bugs fixed
- exact commands run
- exact test results
- residual risks
- any Gemini/Grok claims that were inaccurate or unverified

## Required verification commands

Each agent must run the focused suite first:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```

Before final handoff, each agent must run:

```powershell
uv run pytest -q
```

If a command cannot be run, report the exact reason. Do not claim success without verification.

## Final handoff rule

After both Gemini and DeepSeek complete their assigned sections, send the repo back to Codex using:

`docs/phase1_frontend/prompts/codex-final-review.md`
