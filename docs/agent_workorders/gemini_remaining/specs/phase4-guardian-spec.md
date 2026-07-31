# Phase 4 Guardian Spec

## Goal

Build a deterministic Phase 4 Guardian planner that converts `Plan.md` main-grind rules into a daily schedule recommendation. V1 is a report/planner only; it must not automatically create quiz sessions, attempts, mocks, queue mutations, or notifications.

## Source Files To Inspect

- `Plan.md`
- `README.md`
- `src/ssc_study/config.py`
- `src/ssc_study/models.py`
- `src/ssc_study/db.py`
- `src/ssc_study/readiness.py`
- `src/ssc_study/audit.py`
- `src/ssc_study/reports.py`
- `src/ssc_study/cli.py`
- `tests/test_config.py`
- `tests/test_readiness.py`
- `tests/test_audit.py`
- `tests/test_cli.py`

## Required Behavior

Add a pure planning API:

```python
build_guardian_plan(db, *, today=None) -> GuardianPlan
```

Required output:

- plan date
- total planned minutes
- list of blocks with name, minutes, reason, and source rule
- mock recommendation: none, weekly mock, five-day mock, or three-day mock
- pulse recommendation: none, foundation pulse, CK pulse, or both
- audit mode: normal, notification_pause, or recalibration
- readiness context used for decisions
- warnings for missing evidence

Default daily split from `Plan.md`:

- 25 min SM-2 review
- 35 min Tier-1 boss fights
- 60 min Tier-2 module queue
- 20 min GK/GA memory queue
- 30 min English
- 10 min analysis

Tier-1 floor shift:

- after Tier-1 calibrated floor clears 135 twice, change Tier-1 boss fights to 25 min and Tier-2 module queue to 70 min
- total remains 180 min

Mock cadence:

- first 8 weeks of Phase 4: 1 full mock per week
- months 3-5: 1 full mock every 5 days
- after Tier-1 floor crosses 125: 1 full mock every 3 days
- mock day replaces boss-fight blocks, not SM-2

Monthly pulses:

- foundation pulse and CK pulse run on the first Monday of each month
- they replace that day's boss-fight blocks
- if a full mock lands on pulse day, move the mock recommendation to the next grind day

Notification audit:

- during active major notification audit, pause new boss-fight advancement
- planner should continue only SM-2, GK/GA recall, English recall, and due pulses
- major recalibration should surface a 7-day recalibration warning

CLI:

```text
ssc-study guardian plan
```

CLI output must include:

- date
- total minutes
- each block
- mock/pulse/audit recommendations
- warnings

## Explicit Non-Goals

- No UI.
- No background scheduler.
- No OS notifications.
- No automatic session creation.
- No automatic queue mutation.
- No external calendar integration.
- No network access.

## Acceptance Tests

Tests must prove:

- default plan totals exactly 180 minutes
- Tier-1 floor shift preserves 180 minutes
- first-Monday pulse replacement works
- full mock does not replace SM-2
- pulse day moves mock recommendation to next grind day
- active major notification audit removes boss-fight advancement blocks
- CLI renders the plan without mutating database state

## Verification

Run:

```powershell
uv run pytest tests/test_guardian.py tests/test_audit.py tests/test_readiness.py tests/test_cli.py -q
uv run pytest -q
```

