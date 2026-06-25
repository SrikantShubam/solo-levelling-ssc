# DeepSeek Pattern Intelligence Test Spec

## Context Gaps

- `src/ssc_study/phase3.py` — missing from worktree (exists in main workspace)
- `src/ssc_study/phase3_eval.py` — missing from worktree (exists in main workspace)
- `tests/test_phase3.py` — missing from worktree (exists in main workspace)
- `tests/test_phase3_eval.py` — missing from worktree (exists in main workspace)

These files were read from the main workspace for context. All spec assertions about the
existing Phase 3 planner are based on the main-workspace version at commit `61b1490`.

## Not Yet Implemented

The following production modules do not exist in either worktree or main:

- `src/ssc_study/pattern_intelligence.py` — the v1 module should expose:
  - `analyze_exam_patterns(db, *, tier=None, years=None, exclude_holdout=True) -> ExamPatternReport`
  - `analyze_user_error_patterns(db, *, latest_window=50, min_attempts=5, exclude_holdout=True) -> UserPatternReport`
  - `combine_pattern_priorities(exam_report, user_report) -> PatternPriorityReport`
- `ExamPatternReport` — section/tier/year/archetype distributions, evidence question IDs,
  signal strength, optional advisory mock blueprint
- `UserPatternReport` — repeated archetypes, concept tags, timing weakness,
  accuracy weakness, decay candidates, source attempt/question IDs, signal strength
- `PatternPriorityReport` — combined advisory priority with confidence weighting

All tests in `test_pattern_intelligence_contract.py` are expected to fail with
`ImportError` or `NameError` until these are implemented.

---

## Desired Contract

### `analyze_exam_patterns`

```
analyze_exam_patterns(db, *, tier=None, years=None, exclude_holdout=True) -> ExamPatternReport
```

- Read-only: no inserts, updates, or deletes on any DB table.
- When `exclude_holdout=True`, holdout question IDs must never appear in evidence.
- Report must include: section, archetype, tier, year, evidence question IDs, signal strength.
- Signal strength: `"insufficient"` (<5 evidence questions), `"weak"` (5-9), `"stable"` (10+).
- Advisory mock blueprint is optional but must not create sessions or mutate queues.
- Must not read attempts at all.

### `analyze_user_error_patterns`

```
analyze_user_error_patterns(db, *, latest_window=50, min_attempts=5, exclude_holdout=True) -> UserPatternReport
```

- Read-only: no inserts, updates, or deletes on any DB table.
- When `exclude_holdout=True`, attempts linked to holdout questions must never contribute.
- Must prefer the latest N attempt window over all-time evidence.
- Must separate timing weakness (correct but slow) from accuracy weakness (wrong).
- Report must include: repeated wrong archetypes, concept clusters, timing patterns,
  careless-error candidates, decay candidates, source attempt IDs, signal strength.

### `combine_pattern_priorities`

```
combine_pattern_priorities(exam_report, user_report) -> PatternPriorityReport
```

- Output is advisory only. No DB mutation.
- Low-confidence signals (not `"stable"`) are downweighted.
- High exam weight + high user weakness ranks above any other combination.
- Does not require or mutate any DB object.

### Phase Boundary

- `plan_next_action` from Phase 3 must not import or call pattern intelligence functions.
- Phase 3 orchestration must be invariant to whether pattern reports exist.

---

## Test Strategy

1. Use `in_memory_db` / `study_db` or `seeded_db` from `conftest.py` for DB fixtures.
2. Seed synthetic questions, archetypes, and attempts directly via `conn.execute`.
3. Snapshots compare core table row counts and column values before/after.
4. Mock or monkey-patch future pattern functions when testing Phase 3 boundary.
5. Expected failure until production code exists; tests document the contract precisely.
