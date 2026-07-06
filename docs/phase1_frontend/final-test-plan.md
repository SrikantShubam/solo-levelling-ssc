# Final Test Plan

## Required focused tests

### Baseline regression

- Smoke start still returns exactly 5 questions and no correct labels.
- Smoke submit still persists exactly one web session and one attempt per question.
- Smoke next steps expose no Phase 3 weak-section guidance.
- Full start still returns exactly 200 questions with the required split.
- Full submit still rejects holdout, unknown, duplicate, wrong-count, and wrong-distribution payloads.
- Duplicate submit remains idempotent.

### Phase 3 next action

- `GET /api/phase3/next-action` returns a stable JSON schema.
- Optional section filter is honored.
- No eligible work returns `action_type=stop` with a useful reason.
- Returned target archetype, action type, and question count match existing `plan_next_action()` behavior.
- The route does not mutate DB state unless explicitly documented and tested.

### Guardian/readiness summary

- Summary endpoint returns `guardian.available=true` when `build_guardian_plan()` succeeds.
- Summary endpoint includes planner mode and total minutes.
- If readiness is unavailable or unsafe to call, the endpoint returns `readiness.available=false` with a reason.
- Exceptions from optional summary sources are translated to honest unavailable states, not HTTP 500s.

### Frontend rendering contract

- Landing page still includes smoke/full controls.
- Result page includes the next-steps container.
- Static JS contains rendering branches for:
  - smoke warning
  - remediation excluded
  - remediation priority
  - paired remediation
  - guardian main grind
  - Phase 3 next action
  - unavailable summary state
- If a browser test is added, cover only one small flow: open landing, start smoke, answer one question, submit, see result.

## Required commands

Agents must run the smallest focused suite first:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
```

Before handoff, run:

```powershell
uv run pytest -q
```

## Report format

Each agent report must include:

- files changed
- behavior changed
- tests added
- exact commands run
- exact pass/fail result
- remaining limitations
