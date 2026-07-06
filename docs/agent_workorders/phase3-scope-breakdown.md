# Phase 3 Scope Breakdown

## Source Of Truth

Use `Plan.md` first, then the Phase 3 spec files under `docs/superpowers/specs/`, then current code.

## What The Original Plan Says

### Phase 1: Foundation Gate

Purpose:
- Establish the user's baseline through a 200-question diagnostic.
- Manually tag baseline questions by foundation concept.
- Decide whether areas enter boss fights, paired remediation, or remediation-first mode.

Where it lays:
- Before the full system is trusted for readiness scoring.
- It becomes operationally useful after the system can store attempts, tags, sessions, and evaluation state.

Pattern recognition:
- Not the main pattern-mining phase.
- It collects user baseline data and concept labels.

### Phase 2: Corpus, Holdout, Atlas

Purpose:
- Extract PYQs and solution booklets.
- Seal holdout data.
- Normalize the atlas to roughly 160-240 archetypes.
- Build shared Reasoning archetypes, pattern archetypes, and memory fact cards.

Where it lays:
- Before Phase 3.
- It creates the question corpus and archetype map that Phase 3 diagnoses.

Pattern recognition:
- This is where paper-level pattern recognition belongs in the original plan.
- Current implementation uses keyword/rule-based archetype classification, not a first-class LLM pattern-mining engine.

### Phase 3: Diagnostic Grinding

Purpose:
- Probe each unlocked archetype with 10 timed questions.
- Infer failure cause from student labels, rule inference, and manual arbitration.
- Route each archetype to SM-2, boss fights, remediation, or high-priority boss fights.

Where it lays:
- After the corpus and atlas exist.
- Before the daily 180-minute main grind.

Pattern recognition:
- Phase 3 does not originally discover paper patterns from scratch.
- It diagnoses user performance against the existing atlas.
- The only model mention is future batched arbitration of failure causes after local Qwen exists.

### Phase 4: Main Grind

Purpose:
- Run the daily 180-minute training schedule.
- Consume SM-2, boss fights, Tier-2 modules, GK/GA memory, English, and analysis queues.

Where it lays:
- After Phase 3 has created enough reliable diagnostics.

Pattern recognition:
- Not a discovery phase.
- It consumes scheduled work based on prior diagnostics.

## Current Honest Status

Current Phase 3 is core-complete for deterministic orchestration and evaluation:
- `src/ssc_study/phase3.py` coordinates bounded diagnostic actions.
- `src/ssc_study/phase3_eval.py` compares predicted route vs actual recent outcome.
- Evaluation is read-only, excludes holdout attempts, uses the latest non-holdout window, and reports signal strength.

Phase 2c is complete for read-only exam-paper pattern intelligence:
- `src/ssc_study/patterns_exam.py` aggregates question statistics, signal strength, and mock blueprints over non-holdout questions.
- `src/ssc_study/patterns_priority.py` combines exam frequencies with user diagnostic signals to recommend priorities.
- `ssc-study patterns` CLI command groups let users run these queries.

Phase 4 planner v1 is complete for Guardian daily schedule recommendation:
- `src/ssc_study/guardian.py` implements daily schedule recommendations, mock cadence, monthly pulses, and pause conditions.
- `ssc-study guardian plan` CLI command displays the recommended daily schedule.
- This is not full Phase 4 execution: it does not create sessions, run mocks, mutate queues, or automate the main grind.

Recommended naming:
- Treat model-based paper pattern discovery as `Phase 2c` if it builds the atlas before diagnostics.
- Treat it as `Phase 3b` if it augments the already-built atlas while preserving Phase 3 runtime boundaries.

Preferred direction for this repo:
- Keep exam-paper pattern recognition in `Phase 2c`.
- Keep user-error pattern recognition in `Phase 3`, with `Phase 3b` used only as optional shorthand for a read-only advisory layer.
- Do not let model-discovered patterns mutate queues, routes, gates, readiness, archetypes, or mock generation until they pass evaluation.

## What Pattern Recognition Actually Means Here

There are two different pattern problems and they must stay separate:

1. Exam-paper patterns
- section mix
- archetype frequency
- tier/year distribution
- blueprint-level mock guidance

This is corpus-driven and belongs to `Phase 2c`.

2. User-error patterns
- repeated wrong archetypes
- repeated concept gaps
- timing-pressure failures
- decay or careless-error signals

This is attempt-driven and belongs to `Phase 3`.
