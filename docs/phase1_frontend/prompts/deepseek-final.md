# Prompt: DeepSeek Final Validation Work

You are working in `C:\experiments\ssc`.

Your work order is:

`docs/phase1_frontend/workorders/deepseek-06-final-validation-and-review.md`

Read these files first:

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

Goal:

Act as the adversarial validation agent for the final local web bridge. Add missing tests, prove or disprove the implementation claims, and fix only concrete bugs exposed by tests.

Rules:

- Test-first for behavior changes.
- Make surgical changes only.
- No UI redesign.
- No new framework, auth, deployment, or schema work.
- Do not accept agent reports as proof. Verify against code and tests.
- Do not claim success until commands pass.

Review priorities:

1. Smoke mode must not expose Phase 3 weak-section guidance.
2. Full baseline guidance must match `Plan.md` thresholds.
3. Phase 3 next-action endpoint must return a stable schema.
4. Read-only endpoints must not mutate DB state.
5. Guardian/readiness summary must degrade honestly when unavailable.
6. Frontend JS must render structured backend data without unsupported claims.
7. No correct answers can leak before submit.
8. Duplicate submit must remain idempotent.

Required tests:

- Phase 3 next-action route/schema tests.
- Optional section filter tests.
- No-work stop-state tests.
- No-mutation tests for read-only endpoints.
- Guardian/readiness unavailable-state tests.
- Frontend rendering hook/source-contract tests.

Run:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

Report:

- defects found
- tests added
- bugs fixed
- exact commands run
- exact results
- residual risks
- any Grok/Gemini claims that were inaccurate or unverified
