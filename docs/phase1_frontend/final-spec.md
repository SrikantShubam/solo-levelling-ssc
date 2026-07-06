# Final Product Bridge Spec

## Goal

Move from "baseline exam plus CLI suggestions" to a minimal local study product bridge. The user should finish a baseline, see the next diagnostic target, and have a web surface for the next supported action.

## Scope

### In scope

- A structured backend contract for Phase 3 next action.
- A small web endpoint that exposes the next Phase 3 action in JSON.
- A result-page UI section that uses the backend contract rather than hardcoded generic copy.
- A Guardian/readiness panel that displays existing planner/readiness status if already available.
- Tests for route behavior, schema stability, threshold handling, and frontend rendering hooks.

### Out of scope

- Full daily-study web rewrite.
- Authentication or multi-user support.
- Deployment.
- New JavaScript framework.
- New database schema unless the implementer proves the existing schema cannot support the smallest viable bridge.
- Sealed mock scheduling UI.
- Full final-readiness dashboard.

## Backend contract

### Phase 3 next action

Add or preserve a route similar to:

`GET /api/phase3/next-action?section=<optional>`

Expected response shape:

```json
{
  "action_type": "probe|remediation|boss_fight|sm2_review|stop",
  "reason": "human-readable reason",
  "section": "Quant/DI",
  "target_archetype_id": 123,
  "target_archetype_name": "Time and Work",
  "question_count": 10,
  "can_start_web_session": false,
  "cli_command": "ssc-study phase3"
}
```

If web session start is implemented, `can_start_web_session` may be true and the response must include a stable follow-up URL or endpoint.

### Guardian/readiness summary

Add or preserve a route similar to:

`GET /api/study/summary`

Expected response shape:

```json
{
  "guardian": {
    "available": true,
    "mode": "planner",
    "total_minutes": 180,
    "mock_recommendation": "none",
    "pulse_recommendation": "none",
    "warnings": []
  },
  "readiness": {
    "available": true,
    "status": "not_ready",
    "missing_reasons": []
  }
}
```

If readiness code cannot be safely reused, return `available=false` with an honest reason. Do not fabricate readiness status.

## UI requirements

- Keep the current dense exam cockpit style.
- Result page must distinguish smoke mode from full baseline.
- Smoke mode must recommend the full baseline only.
- Full baseline should show:
  - section score buckets from `Plan.md`
  - next Phase 3 target if available
  - Guardian/readiness summary if available
  - exact CLI fallback command when web execution is not implemented
- Avoid long explanatory copy. Prefer compact labels, status chips, and one-line reasons.

## Data rules

- Use persisted session/result data.
- Use existing Phase 3 and Guardian functions where possible.
- Holdout questions must remain excluded from normal flows.
- Correct answers must remain server-only before submit.
- Web guidance must not claim execution happened unless the code actually creates a session or persisted action.
