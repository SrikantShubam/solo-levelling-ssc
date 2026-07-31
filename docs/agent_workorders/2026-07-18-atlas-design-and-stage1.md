# Atlas Construction — Design Decision + Stage 1 Activation

## The decision (made at orchestrator level, grounded in corpus measurement)

Plan.md Phase 2 says "normalize atlas to roughly 160-240 archetypes" via
embedding clustering. Measurement against the live corpus changes this
recommendation. Two facts:

1. The codebase already contains a complete, hand-authored, syllabus-aligned
   archetype taxonomy: **48 `ArchetypeDef`s** in `src/ssc_study/archetypes.py`
   with `ensure_default_archetypes()` + `assign_archetypes()` +
   `classify_question()` — fully written, tested, and **never run** (archetypes
   table has 0 rows; `questions.archetype_id` is NULL on all 2,355 rows;
   `embedding_blob` is NULL on all 2,355 — `update_all_embeddings()` also
   never ran).
2. Rule coverage measured now: **61% (1,083 of 1,769 non-holdout) match a
   rule archetype**; the unmatched 39% is concentrated in English (310) and
   GK/GA (234) — exactly the sections where keyword rules should fail
   (comprehension, para-jumbles, arbitrary facts).

**Recommendation: staged hybrid, not pure clustering.**

- The 48-archetype hand taxonomy is the right BACKBONE: named, interpretable,
  syllabus-aligned, and — critically — correctly sized for THIS corpus. With
  ~1,567 web-safe questions today, 160-240 archetypes would be ~7-10
  questions each, which cannot support 10-question probes + 25% holdout +
  SM-2 review without immediate repetition. 48 archetypes ≈ 30-50 questions
  each is the sustainable granularity now. Granularity can rise later as the
  Hermes corpus harvest grows the pool.
- Embeddings are the COVERAGE layer, not the primary partition: use them to
  place the unmatched 39% and to surface candidate new archetypes — not to
  replace the named taxonomy.

Push back on Plan.md's 160-240 explicitly in the design record: that number
predates the current corpus reality. Revisit it only after the corpus grows
past ~5,000 clean questions.

## Staging

- **Stage 1 (this workorder): activate the rule taxonomy.** Deterministic,
  interpretable, unblocks the entire Phase 3 loop today. ~61% assigned;
  remainder left NULL for Stage 2.
- **Stage 2 (later workorder): embedding coverage.** Run
  `update_all_embeddings`, then assign each unmatched question to the nearest
  archetype centroid ABOVE a cosine-similarity threshold; below threshold →
  leave NULL and log as a candidate-new-archetype cluster for human naming.
  Never force-fit below threshold.
- **Stage 3 (later, human-in-loop): granularity tuning.** Split over-large
  archetypes (e.g. Syllogisms=132) by tier_difficulty/subtype where the split
  is pedagogically real; name the dense unmatched English/GK clusters Stage 2
  surfaces. This stage needs human judgment on names — do not automate naming.

---

## Stage 1 Work Order (for codex)

You are working in `C:\experiments\ssc`. Read this full file first, then
`src/ssc_study/archetypes.py` and `src/ssc_study/gates.py` (the Phase 3
consumer of archetypes) before changing anything.

### Scope — activate the existing rule-based atlas, nothing more

1. Add a rerunnable script `scripts/build_atlas_stage1.py` (follow the
   `scripts/remap_baseline_assets.py` convention) that:
   - Calls `ensure_default_archetypes(db)` to populate the `archetypes` table
     from `ARCHETYPE_DEFS`.
   - Calls `assign_archetypes(db)` (or the correct existing entrypoint — read
     the module to confirm the exact function and signature) to backfill
     `questions.archetype_id` for every non-holdout question a rule matches.
   - Is idempotent: re-running does not duplicate archetype rows or thrash
     existing assignments (upsert by archetype name+section; only set
     archetype_id where currently NULL OR where the rule result changed).
   - Prints a report: archetypes created, questions assigned, questions left
     unassigned (NULL) by section, and the per-archetype question count.
2. Do NOT invent new archetypes, do NOT touch holdout questions' assignment
   in a way that could leak holdout content into probes, and do NOT modify
   the eligibility/quality gates in `baseline_web.py`.
3. If `ensure_default_archetypes`/`assign_archetypes` have bugs that block
   activation (e.g. they never persisted because of a real defect), fix the
   minimal defect and add a regression test — but report exactly what you
   changed and why; do not silently rewrite the taxonomy.

### Verification required

- Run the script against `data/study.db`; paste the exact report output.
- Confirm: `archetypes` row count > 0; `questions.archetype_id` non-NULL
  count matches the reported assigned count; the ~61% coverage figure is in
  the same ballpark (a large deviation means a bug — investigate).
- Confirm holdout questions were handled per existing holdout rules (state
  how).
- `uv run pytest -q` full suite green; add/adjust tests for the script.
- Confirm a Phase 3 consumer can now see archetypes: run whatever existing
  read-only command surfaces archetypes (e.g. `ssc-study` archetype summary
  / gates path) and show it returns non-empty.

### Out of scope

Embedding computation, centroid assignment, clustering, granularity changes,
naming new archetypes, corpus expansion. Those are Stage 2/3.

### Report format

Files changed, script + exact command, counts (archetypes created, assigned,
unassigned-by-section), tests added, exact verification output, residual risk.
