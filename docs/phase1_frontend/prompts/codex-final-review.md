# Prompt: Codex Final Integration Review

You are Codex reviewing the final Grok and Gemini outputs in `C:\experiments\ssc`.

Read first:

- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `docs/phase1_frontend/workorders/grok-04-phase3-actionable-flow.md`
- `docs/phase1_frontend/workorders/gemini-05-guardian-readiness-ui.md`
- changed source files
- changed tests

Review stance:

- Be strict.
- Findings first.
- Reject overclaims.
- Reject untested behavior.
- Do not accept "Stitch-oriented" as "Stitch MCP used."
- Do not accept advisory CLI text as web execution.

Checklist:

- Phase 1 baseline start/submit/result still works.
- Smoke mode remains a validation path only.
- Full baseline result guidance uses persisted result data.
- Phase 3 endpoint is stable, tested, and does not mutate state by accident.
- Guardian/readiness panel is honest about advisory vs executable behavior.
- No correct answer leakage before submit.
- No new framework or deployment scope.
- Tests cover changed behavior, not just placeholder strings.

Required verification:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

Final report:

- accepted changes
- rejected or fixed issues
- exact verification results
- remaining product gaps
