# Phase 2c And Phase 3 Pattern Intelligence Design

## Goal

Separate pattern intelligence into two audited layers: exam-paper pattern intelligence for the corpus and mock blueprints, and user-error pattern intelligence for attempt diagnostics. Both layers start read-only so model or heuristic output cannot silently change queues, gates, readiness, archetypes, sessions, attempts, SM-2, or mock generation.

## Phase Taxonomy

`Plan.md` is the source of truth for phase meaning.

- Phase 1: Foundation Gate. Establish the user's baseline with the 200-question diagnostic and foundation concept tags.
- Phase 2: Corpus, Holdout, Atlas. Extract questions, seal holdout, and build the raw atlas inputs.
- Phase 2b: Study Runtime Primitives. SQLite, loader, queues, SM-2, gates, holdout policy, readiness primitives, and current rule-based archetypes.
- Phase 2c: Exam Pattern Intelligence. Analyze non-holdout corpus structure, section weights, tier/year distribution, archetype frequency, and advisory mock blueprints.
- Phase 3: User Diagnostic Intelligence. Analyze attempts, wrong-answer patterns, timing failures, concept gaps, decay signals, and route predictions.
- Phase 4: Main Grind. Consume validated signals for daily scheduling, mock cadence, and readiness decisions.

## Design

### Exam Pattern Intelligence

Exam pattern analysis answers: "What does SSC ask, in what distribution, and what should a mock roughly look like?"

The v1 report should include:
- section distribution
- tier distribution
- year distribution
- archetype distribution
- source question IDs
- non-holdout question count
- signal strength: `insufficient`, `weak`, `stable`
- advisory mock blueprint by section/archetype/tier

Rules:
- Exclude holdout questions.
- Do not read attempts.
- Do not create sessions or mocks.
- Do not update archetypes or readiness.

### User Error Pattern Intelligence

User-error analysis answers: "Where is this user repeatedly failing, and what kind of failure is it?"

The v1 report should include:
- repeated wrong archetypes
- repeated wrong concept tags
- timing-pressure patterns
- careless-error candidates
- decay-after-review candidates
- source attempt IDs
- source question IDs
- latest-window size
- signal strength: `insufficient`, `weak`, `stable`

Rules:
- Exclude holdout-linked attempts.
- Prefer latest-window evidence over all-time evidence.
- Separate low accuracy from slow timing.
- Do not update queues, gates, readiness, archetypes, attempts, sessions, or SM-2.

### Priority Combiner

The combiner answers: "What should be inspected or trained first if both exam importance and user weakness matter?"

Initial formula:

```text
priority = exam_importance * user_weakness * confidence
```

Rules:
- Output is advisory only.
- Low-confidence patterns are downweighted.
- No runtime Phase 3 action consumes the combiner in v1.

## Public Interfaces

Expected future APIs:

```python
analyze_exam_patterns(db, *, tier=None, years=None, exclude_holdout=True) -> ExamPatternReport
analyze_user_error_patterns(db, *, latest_window=50, min_attempts=5, exclude_holdout=True) -> UserPatternReport
combine_pattern_priorities(exam_report, user_report) -> PatternPriorityReport
```

Expected future CLI:

```text
ssc-study patterns exam
ssc-study patterns user
ssc-study patterns priority
```

The CLI is report-only in v1.

## Anti-Overfitting Rules

- Holdout data is validation-only and cannot generate exam or user patterns.
- A pattern without source question IDs or attempt IDs is not actionable.
- Sparse evidence must be visibly sparse.
- A mock blueprint should be evaluated separately before it becomes a mock generator input.
- User weakness must not override exam frequency without confidence and minimum support.
- Model-generated hypotheses must be treated as hypotheses until promoted by tests and audit.

## Acceptance Criteria

- Phase docs clearly distinguish Phase 2c exam-pattern intelligence from Phase 3 user-error intelligence.
- Read-only reports can be generated from the DB without mutating core tables.
- Tests prove holdout exclusion, latest-window behavior, signal strength, and no runtime coupling.
- Worker workorders assign inventory/design/test work without allowing production implementation.
