# Prompt: Grok Final Backend Work

You are working in `C:\experiments\ssc`.

Your work order is:

`docs/phase1_frontend/workorders/grok-04-phase3-actionable-flow.md`

Read these files first:

- `Plan.md`
- `grok_critic.md`
- `docs/phase1_frontend/final-remaining-work.md`
- `docs/phase1_frontend/final-spec.md`
- `docs/phase1_frontend/final-test-plan.md`
- `src/ssc_study/baseline_web.py`
- `src/ssc_study/web.py`
- `src/ssc_study/phase3.py`
- `src/ssc_study/gates.py`
- `tests/test_baseline_web.py`
- `tests/test_web.py`

Goal:

Build the smallest backend bridge from baseline results to Phase 3 diagnostic action. The product should stop relying only on generic CLI text and expose a structured next action based on existing Phase 3 logic.

Rules:

- Think before coding and state assumptions.
- Surgical changes only.
- No new framework, auth, deployment, or broad dashboard work.
- Prefer existing functions over new abstractions.
- Do not mutate DB state in a read-only next-action endpoint.
- Do not derive Phase 3 guidance from smoke mode.
- Verify before reporting success.

Required implementation:

1. Add or refine `GET /api/phase3/next-action`.
2. Support optional `section` filtering.
3. Reuse `plan_next_action()` from `phase3.py`.
4. Return a stable schema with action type, reason, target archetype, question count, CLI fallback command, and whether web session start is available.
5. Add focused service/route tests.
6. Preserve all existing Phase 1 baseline behavior.

Run:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

Report:

- files changed
- behavior changed
- tests added
- exact commands run
- exact results
- limitations
