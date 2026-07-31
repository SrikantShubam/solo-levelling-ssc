# 2026-07-07 Worker Dispatch

You are working in `C:\experiments\ssc`.

Read this file fully, then execute only the section for your agent.

If you are Grok, use the `Grok` section.
If you are Gemini, use the `Gemini` section.

Shared rules for both:

- Read the shared spec first.
- Read your workorder second.
- Read the listed source/tests before changing anything.
- Stay inside your assigned scope.
- Verify before claiming success.
- If you find scope drift, report it instead of expanding the task.
- The user's 2-hour baseline run is manual user work, not worker work.

## Shared files to read first

- `Plan.md`
- `README.md`
- `memory.md`
- `errors.md`
- `checklist.md`
- `docs/agent_workorders/2026-07-07-active-todo-shared-spec.md`

## Grok

Your work order is:

- `docs/agent_workorders/2026-07-07-grok-workorder.md`

Mission:

- Reconcile the current uncommitted hardening work against project scope.
- Identify baseline-critical risk vs general hardening.
- Add the smallest missing backend-side tests or fixes required for confidence.

Required review posture:

- test-first for behavior changes
- do not treat assumptions as proof
- prefer focused regressions over broad rewrites

Report:

- diff buckets
- files changed
- tests added or changed
- exact commands run
- exact results
- merge recommendation
- residual risk before the user's baseline block

## Gemini

Your work order is:

- `docs/agent_workorders/2026-07-07-gemini-workorder.md`

Mission:

- Improve the operator-facing clarity around today's baseline workflow.
- Keep the UI/docs honest about what is manual, what is advisory, and what is actually implemented.
- Add the smallest tests needed for any changed operator-facing surface.

Required review posture:

- keep copy operational and restrained
- do not imply unsupported web automation
- preserve smoke/full separation and current threshold meaning

Report:

- surfaces changed
- files changed
- tests added or changed
- exact commands run
- exact results
- unsupported or misleading claims found
- remaining limitations

## Single command to send

Use this exact instruction for either worker:

`Read docs/agent_workorders/2026-07-07-worker-dispatch.md and execute the section for your agent. Implement, test, and self-review before reporting back.`
