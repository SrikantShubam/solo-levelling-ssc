# Remaining Scope Audit Report

## 1. Confirmed Implemented

The following features and structures are confirmed implemented in the repository:

1. **SQLite Database Schema and Migrations**:
   - The database contains support for sessions, attempts, archetypes, fact cards, and external mocks.
   - The `external_mocks` table and migrations for session types (like `sealed_mock`) are defined:
     - [src/ssc_study/db.py:137-144](file:///c:/experiments/ssc/src/ssc_study/db.py#L137-L144): Table creation for `external_mocks`.
     - [src/ssc_study/db.py:184](file:///c:/experiments/ssc/src/ssc_study/db.py#L184): Migration 13 updating check constraints to include `sealed_mock`.
2. **Phase 2b Features**:
   - SM-2 spaced repetition review logic: [src/ssc_study/scheduler.py](file:///c:/experiments/ssc/src/ssc_study/scheduler.py) and [src/ssc_study/sm2.py](file:///c:/experiments/ssc/src/ssc_study/sm2.py).
   - Interactive quiz loops and session tracking: [src/ssc_study/quiz.py](file:///c:/experiments/ssc/src/ssc_study/quiz.py).
   - Fact cards generation: [src/ssc_study/cards.py](file:///c:/experiments/ssc/src/ssc_study/cards.py).
   - Keyword-based archetype classification: [src/ssc_study/archetypes.py](file:///c:/experiments/ssc/src/ssc_study/archetypes.py).
   - Semantic search with sentence-transformers and FAISS: [src/ssc_study/embeddings.py](file:///c:/experiments/ssc/src/ssc_study/embeddings.py).
   - Notification audit pause and triggers: [src/ssc_study/audit.py](file:///c:/experiments/ssc/src/ssc_study/audit.py).
   - Readiness dashboard calculations: [src/ssc_study/readiness.py](file:///c:/experiments/ssc/src/ssc_study/readiness.py).
3. **Phase 3 Orchestration and Evaluation**:
   - Bounded Phase 3 orchestration loop (probes, remediation, boss fights, SM-2):
     - [src/ssc_study/phase3.py:90-135](file:///c:/experiments/ssc/src/ssc_study/phase3.py#L90-L135): `run_phase3_loop` orchestration logic.
     - [src/ssc_study/cli.py:287-318](file:///c:/experiments/ssc/src/ssc_study/cli.py#L287-L318): CLI subcommand `ssc-study phase3` integration.
   - Read-only Phase 3 route and accuracy evaluation:
     - [src/ssc_study/phase3_eval.py:37-112](file:///c:/experiments/ssc/src/ssc_study/phase3_eval.py#L37-L112): `evaluate_phase3_predictions` calculation.
     - [src/ssc_study/cli.py:319-358](file:///c:/experiments/ssc/src/ssc_study/cli.py#L319-L358): CLI subcommand `ssc-study phase3-eval` integration.

---

## 2. Confirmed Remaining

The following components are confirmed as remaining (not yet implemented in the source code):

1. **Phase 2c Exam-Pattern Intelligence**:
   - The read-only corpus pattern analysis APIs (`analyze_exam_patterns` and `combine_pattern_priorities`) do not exist.
   - The CLI subcommands `ssc-study patterns exam` and `ssc-study patterns priority` do not exist.
   - Evidence: There are no files matching `*pattern*` in `src/ssc_study` except for config/test references, and [src/ssc_study/cli.py](file:///c:/experiments/ssc/src/ssc_study/cli.py) does not contain a `patterns` group or command.
2. **Phase 4 Guardian Main-Grind Scheduler**:
   - The planning API `build_guardian_plan` does not exist.
   - The CLI subcommand `ssc-study guardian plan` does not exist.
   - Evidence: There are no files matching `*guardian*` in `src/ssc_study/`, and [src/ssc_study/cli.py](file:///c:/experiments/ssc/src/ssc_study/cli.py) does not contain a `guardian` group or command.
3. **Documentation Updates (Documentation Drift)**:
   - Resolving inconsistencies in the README.md and referencing Phase 2c / Phase 4 remains to be completed.

---

## 3. Documentation Drift

The following instances of documentation drift have been identified:

1. **Phase 2b Status Inconsistency**:
   - [README.md:141](file:///c:/experiments/ssc/README.md#L141) ("Approval: Phase 2b is MVP-complete, but not plan-complete.") and [README.md:157](file:///c:/experiments/ssc/README.md#L157) ("Missing for full Phase 2b approval...") describe Phase 2b as partially incomplete.
   - However, [README.md:416-426](file:///c:/experiments/ssc/README.md#L416-L426) ("Current Verdict: Phase 2b is fully implemented and approved.") explicitly states that Phase 2b is fully approved.
2. **Phase 3 Status Inconsistency**:
   - The status table at [README.md:111](file:///c:/experiments/ssc/README.md#L111) lists Phase 3 as "Upcoming" (🔜).
   - However, deterministic Phase 3 orchestration and read-only evaluations are already fully implemented and verified (see [memory.md:20-43](file:///c:/experiments/ssc/memory.md#L20-43) and [src/ssc_study/phase3.py](file:///c:/experiments/ssc/src/ssc_study/phase3.py)).
3. **Phase 2c Omission**:
   - Phase 2c (exam-pattern intelligence) is not represented at all in the README.md status table ([README.md:106-113](file:///c:/experiments/ssc/README.md#L106-L113)).

---

## 4. Implementation Risk

Key implementation risks to manage in upcoming workorders:

1. **DB/Model Mutating Operations**:
   - *Risk*: Phase 2c and Phase 4 are strictly read-only and planning-focused layers. Any accidental write operation to the SQLite database will violate specifications.
   - *Mitigation*: Ensure connections are used in read-only mode where possible, and execute no `INSERT`, `UPDATE`, or `DELETE` statements on core tables.
2. **Holdout Question Leakage**:
   - *Risk*: Generating blueprints or calculating pattern distributions using holdout questions (`is_holdout = 1`) violates the holdout policy.
   - *Mitigation*: Ensure all SQL queries in the pattern analysis filter with `is_holdout = 0` or equivalent holdout protection logic.
3. **Complex Schedule Conflicts in Guardian**:
   - *Risk*: Pulse days (first Monday of the month) and mock cadences can conflict. If they collide, the mock must be pushed to the next grind day.
   - *Mitigation*: Build unit tests testing the date boundary and collision rules specifically.

---

## 5. Recommended Workorder Order

The recommended sequence of execution is:

1. **gemini-01-remaining-audit.md** (Current): Establishes baseline findings.
2. **gemini-02-phase2c-pattern-intelligence.md**: Implements Phase 2c read-only pattern reporting.
3. **gemini-03-phase4-guardian.md**: Implements Phase 4 daily grind scheduler recommendations, pulling data from both diagnostics (Phase 3) and pattern reports (Phase 2c).
4. **gemini-04-docs-consistency.md**: Finalizes documentation to reflect the completed state of the repository.

---

## 6. Evidence

The following files and line numbers form the evidence for the implementation state:

- **Sealed Mock Migration**: [src/ssc_study/db.py:184](file:///c:/experiments/ssc/src/ssc_study/db.py#L184)
- **Phase 3 Orchestration Loop**: [src/ssc_study/phase3.py:90-135](file:///c:/experiments/ssc/src/ssc_study/phase3.py#L90-L135)
- **Phase 3 Evaluation Report Logic**: [src/ssc_study/phase3_eval.py:37-112](file:///c:/experiments/ssc/src/ssc_study/phase3_eval.py#L37-L112)
- **Phase 3 CLI commands**: [src/ssc_study/cli.py:287-358](file:///c:/experiments/ssc/src/ssc_study/cli.py#L287-L358)
- **Absent Pattern Module**: No `patterns.py` exists in `src/ssc_study/`.
- **Absent Guardian Module**: No `guardian.py` exists in `src/ssc_study/`.
- **Drift: Phase 3 Status Table**: [README.md:111](file:///c:/experiments/ssc/README.md#L111)
- **Drift: Phase 2b Critic**: [README.md:141-170](file:///c:/experiments/ssc/README.md#L141-170)
- **Approved Verdict**: [README.md:416-426](file:///c:/experiments/ssc/README.md#L416-L426)
