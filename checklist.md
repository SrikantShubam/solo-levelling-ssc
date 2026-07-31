# Checklist

## 2026-07-07 Active Todo

### Current position

- Last landed change: Phase 1 web bridge handoff is in `main` with baseline web flow, frontend assets, and route/test coverage.
- Latest local work: uncommitted hardening across corpus + study internals (`acquisition`, `extraction`, `pdf_layout`, `cli`, `holdout`, `gates`, `scheduler`, `models`, `queues`) plus expanded test coverage.
- Overall project comparison: README + `Plan.md` say Phases 1-4 are broadly implemented, so today should bias toward verification, manual baseline execution, and closing hardening gaps rather than opening new feature scope.

### Today

- [ ] Phase 1 two-hour baseline test block: run one real 200-question baseline/foundation session in the web app and treat it as today’s highest-priority validation pass.
- [ ] During the baseline test, verify the Phase 1 contract end to end: 80/40/40/40 section split, timer behavior, draft recovery, submit integrity, persisted attempt data, scored results, next-step guidance, and no answer leakage before submit.
- [ ] Capture every issue from the two-hour baseline run in `errors.md` or `memory.md` immediately with exact repro notes, severity, and whether it is product, backend, or test-suite fallout.
- [ ] Dispatch workers using `docs/agent_workorders/2026-07-07-worker-dispatch.md`:
  - Grok: hardening + reconciliation
  - Gemini: operator surface + review
- [ ] Reconcile the current uncommitted hardening pass against overall project goals: confirm the touched corpus/study modules are still supporting the Plan rather than drifting into unrelated cleanup.
- [ ] Review the latest local diff and group it into three buckets before more edits: Phase 1 baseline-critical, corpus hardening, and scheduler/holdout/readiness behavior.
- [ ] Run targeted automated verification for the Phase 1 web path after the manual baseline test: `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`.
- [ ] Run targeted automated verification for the current hardening work in touched areas: DB, holdout, extraction, CLI, crops, audit, quiz, queues, and pipeline-compare coverage.
- [ ] Decide by end of day whether the uncommitted hardening set is ready to land as one cohesive change or needs to be split into smaller verifiable commits.

### Done recently

- [x] Land Phase 1 web bridge handoff and final docs/test package.
- [x] Fix Phase 3 bridge review issues for frontend escaping and supported CLI fallback commands.
- [x] Keep full pytest green at the latest recorded checkpoint in `memory.md`.
