# Work Order: 2026-07-07 Gemini Operator Surface And Review

## Objective

Own the operator-facing half of today's active todo.

Make today's project state easier to act on before and after the user's manual baseline run, without inventing product behavior that the repo does not implement.

## Read first

- `Plan.md`
- `README.md`
- `memory.md`
- `errors.md`
- `checklist.md`
- `docs/agent_workorders/2026-07-07-active-todo-shared-spec.md`
- `src/ssc_study/web.py`
- `src/ssc_study/baseline_web.py`
- `src/ssc_study/static/app.js`
- `src/ssc_study/static/app.css`
- `src/ssc_study/templates/landing.html`
- `tests/test_baseline_web.py`
- `tests/test_web.py`
- `tests/test_phase1_frontend.py`

## Scope

You own:

1. making today's baseline-related workflow clearer for the operator
2. improving honest status/reporting surfaces that help interpret the user's manual baseline run
3. tightening tests around any new operator-facing surface or copy contract
4. keeping the UI or docs aligned with the actual repo state

You do not own:

- running the user's 2-hour baseline
- claiming the web app executes follow-up workflows unless already implemented
- a full design rewrite

## Constraints

- keep FastAPI + Jinja + static JS/CSS
- no React or build pipeline
- keep smoke mode distinct from full baseline behavior
- keep copy short, operational, and honest
- if a capability is advisory or CLI-only, label it clearly
- surgical edits only

## Required tasks

1. Review whether the current local UI/docs already support today's operator workflow.
2. If there is a real gap, implement the smallest surface that helps the user:
   - pre-baseline checklist/status note
   - post-baseline next-step summary
   - honest unavailable/advisory state
3. Ensure any surface distinguishes:
   - manual user baseline work
   - implemented web behavior
   - CLI-only follow-up behavior
4. Add focused rendering/source-contract tests for the exact surface you change.
5. Report any misleading copy or unsupported implied workflow you find, even if you do not change it.

## Required test cases

At minimum, preserve or extend the relevant cases below:

- smoke mode still behaves like smoke mode
- full baseline guidance remains threshold-correct
- operator-facing copy does not imply auto-executed follow-up if only CLI exists
- any new panel/banner/hint renders an explicit unavailable or manual-step state when required

## Example acceptable outputs

- add a small "manual baseline in progress" or "after baseline" status note if it reflects real state
- tighten frontend tests so a copy regression cannot imply unsupported web automation
- improve result-page wording so it clearly separates manual baseline completion from system recommendations

## Example unacceptable outputs

- adding a fake "Start Phase 3" web button if the backend does not support it
- turning today's todo into a large dashboard rewrite
- silently changing threshold messaging away from `Plan.md`

## Verification commands

Run the smallest relevant commands you actually use.

Candidate commands:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```

Run `uv run pytest -q` only if your final changed set justifies it.

## Deliverable report

Include:

- surfaces changed
- copy/status behavior changed
- tests added or changed
- exact commands run
- exact results
- unsupported or misleading workflow claims you found
- remaining operator-facing limitations

