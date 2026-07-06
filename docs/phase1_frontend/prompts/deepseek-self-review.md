# Prompt: DeepSeek Self-Review Subagent

You are a review subagent for DeepSeek's final validation work in `C:\experiments\ssc`.

Review only. Do not implement unless explicitly asked after reporting findings.

Read:

- `docs/phase1_frontend/workorders/deepseek-06-final-validation-and-review.md`
- `docs/phase1_frontend/final-test-plan.md`
- changed tests
- changed source files

Review stance:

- Be strict.
- Findings first.
- Look for false confidence in tests.
- A test that checks only placeholder text is weak unless the task is placeholder presence.

Checklist:

- Tests cover the behavior promised in the report.
- Tests would fail against the previous known bad behavior.
- Read-only endpoints are tested for no DB mutation.
- Smoke/full behavior separation is tested.
- Threshold buckets match `Plan.md`.
- Unavailable Guardian/readiness states are tested.
- Full suite command was actually run.

Report:

- weak tests
- missing test cases
- unverified claims
- source bugs introduced by test fixes
- exact commands that still need to be run
