# Work Order: DeepSeek 06 - Final Validation And Review

## Objective

Validate the final Phase 3, Guardian, and readiness bridge. Add missing tests and fix only bugs that are proven by those tests.

## Read first

- `Plan.md`
- `grok_critic.md`
- `docs/phase1_frontend/agent-split-final.md`
- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `docs/phase1_frontend/workorders/grok-04-phase3-actionable-flow.md`
- `docs/phase1_frontend/workorders/gemini-05-guardian-readiness-ui.md`
- changed source files from Grok/Gemini
- changed tests from Grok/Gemini

## Constraints

- Test-first for any behavior change.
- Surgical fixes only.
- Do not redesign the UI.
- Do not add browser infrastructure unless already cheap and local.
- No framework, auth, deployment, or schema changes.
- Preserve completed Phase 1 baseline behavior.

## Required review checks

1. Smoke mode remains a validation path only.
2. Full baseline result guidance uses persisted full-result data.
3. `GET /api/phase3/next-action` returns a stable schema and does not mutate DB state.
4. Guardian/readiness summary handles unavailable data honestly.
5. Frontend JS consumes structured backend data instead of hardcoding unsupported claims.
6. Result-page guidance still matches `Plan.md` thresholds:
   - `>= 70%`: boss-fight unlocked / good standing
   - `65-69%`: boss fight with paired remediation
   - `55-64%`: remediation priority
   - `< 55%`: remediation first and excluded from readiness scoring until 65%
7. No correct-answer leakage before submit.
8. Duplicate submit remains idempotent.

## Required tests

Add or update focused tests for:

- Phase 3 next-action schema.
- Optional section filter.
- No-work stop state.
- No DB mutation for read-only next-action endpoint.
- Guardian/readiness unavailable state.
- Frontend rendering hooks for Phase 3 and Guardian/readiness.
- Smoke mode not showing Phase 3 weak-section guidance.

## Verification commands

Run:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

## Deliverable report

Include:

- defects found
- tests added
- bugs fixed
- exact commands run
- exact test results
- residual risks
- claims from Grok/Gemini that were inaccurate or unverified
