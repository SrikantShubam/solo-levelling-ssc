# 2026-07-20 Harvest Ingestion — Corrected (ID Namespacing + Full Leak Masking)

You are working in `C:\experiments\ssc`. This corrects and continues from
the blocked attempt in
`docs/agent_workorders/2026-07-20-harvest-ingestion-workorder.md` — read its
report at `docs/agent_workorders/2026-07-20-harvest-ingestion-last-message.md`
first, plus the evidence files it produced:
`reports/harvest_ingestion/leak_source_audit.tsv` and
`reports/harvest_ingestion/blocked_collision_report.json`.

## What the blocked run already established (verified independently, trust it)

1. **All 64 harvested PDFs are answer-leaking sources**, with real
   per-PDF evidence in `leak_source_audit.tsv` (quantified
   `positive_evidence_questions` counts and sample quotes, not a blanket
   guess). All 64 are already registered in `ANSWER_LEAKING_SOURCES` in
   `src/ssc_study/corpus_assets.py` — do not undo this registration, it's
   correct and already verified.
2. **236 question_id collisions** between the harvest and the existing
   2,355-row corpus, plus **218 duplicate question_ids within the harvest
   batch itself**. Root cause (confirmed via
   `blocked_collision_report.json` collision samples): harvested PDFs and
   the original corpus both source from prepp.in/testbook, whose extracted
   `question_id` field is the *provider's own internal numeric ID*, which
   is not unique across independently-extracted PDFs — completely
   unrelated papers/re-bundled compilations reuse the same provider ID for
   the same underlying question. `INSERT OR REPLACE` keyed on this raw ID
   would silently overwrite live corpus rows that already have attempt
   history and SM-2 state. The prior run correctly stopped before importing
   anything — `data/study.db` is unchanged (verified: 2355 questions, 410
   attempts, 4 sessions, 204 sm2_state, all identical to before).

## Required fix: namespace harvest question_ids before import

Do not modify the shared loader (`src/ssc_study/loader.py`) or its ID
fallback logic — that's used for the original corpus's import path too and
should not change behavior there. Instead, **before** calling `ssc-study
import`, rewrite the `question_id` (and `resolved_question_id` if present)
field in every harvested `merged_questions_global_order.json` file so it is
guaranteed unique and clearly namespaced, e.g.
`f"harvest_{pdf_name}_q{global_question_number}"`. Do this for every
question in every one of the 64
`pipeline_output/harvest_batch/<pdf_stem>/merged_questions_global_order.json`
files. This must be deterministic (same input always produces the same
namespaced ID, so re-running is idempotent) and must not collide with any
existing corpus ID (the `harvest_` prefix combined with these specific
pdf_names guarantees this — the original corpus's pdf_names never carry
this prefix).

After rewriting, re-run the collision forecast the blocked attempt used and
confirm **zero** collisions with the existing 2,355 rows and **zero**
duplicates within the harvest batch. If any remain, find out why (e.g. two
different pages producing the same global_question_number for the same PDF
— a real extraction bug worth reporting, not silently overwriting) before
proceeding.

## Then proceed through the original workorder's remaining steps

Follow `docs/agent_workorders/2026-07-20-harvest-ingestion-workorder.md`
Steps 2 (masking — now actually run it, using the already-registered
`ANSWER_LEAKING_SOURCES` list and the already-completed audit) through 6
(final before/after preflight measurement) exactly as specified there. Key
points repeated because they matter:

- Masking: reuse `remap_question_assets`/`mask_answer_leaking_crop`
  (existing, proven functions) against every newly-registered source.
  Manually open and describe at least 8 masked crops across at least 4
  different sources to confirm no leak remains and content is intact.
  Given ~4,500+ questions across 64 leaking sources, script this in bulk —
  do not do it one-by-one by hand, but the manual-description requirement
  for a sample still applies for genuine verification.
- Import: re-run the collision-safety check one more time immediately
  before the real `ssc-study import` call (belt-and-suspenders — confirm
  the namespacing fix actually holds at the moment of import, not just
  when you first checked it).
- Protected tables (`attempts`, `sessions`, `sm2_state`) must be unchanged
  after import — verify counts before and after.
- Modality/evidence spot-check (Step 4), atlas backfill (Step 5), and the
  final before/after `get_baseline_preflight()` comparison (Step 6) all
  still apply as originally specified.

## Verification required before reporting done

- Proof the ID-namespacing fix eliminated all collisions/duplicates (exact
  before/after counts).
- Masking counts and manual verification (per the original workorder's
  requirements).
- Import collision-safety proof, protected-table unchanged proof.
- Modality spot-check outcome.
- Atlas backfill counts.
- Full before/after `get_baseline_preflight()` comparison — this is the
  headline number: how many genuinely web-safe questions did this ingestion
  add.
- `uv run pytest -q` results.

## Report format

Same as the original workorder: ID-namespacing fix and re-verified
collision-safety proof, masking counts + manual verification, import
collision-safety proof, modality spot-check outcome, atlas backfill counts,
full before/after preflight numbers (headline deliverable), test suite
results, residual risk.
