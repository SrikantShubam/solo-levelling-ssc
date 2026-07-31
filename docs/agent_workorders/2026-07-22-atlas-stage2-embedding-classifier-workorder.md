# 2026-07-22 Atlas Stage 2 — Embedding-Based Archetype Coverage Expansion

You are working in `C:\experiments\ssc`. This is Stage 2 of the archetype
atlas, following Stage 1 (`scripts/build_atlas_stage1.py`, already landed
and idempotent — read it fully before starting, reuse its conventions).
This is 100% local/free work: `sentence-transformers` (confirmed installed,
v5.5.1) runs on-device, no API calls, no external accounts, no cost.

## Background

Stage 1 used keyword/rule-based matching to assign `archetype_id` to
questions. Current real coverage of the *servable* (web-safe) pool:

| Section | Tagged / Servable |
|---|---|
| Reasoning | 636/778 (82%) |
| English | 869/1600 (54%) |
| Quant/DI | 1388/2699 (51%) |
| GK/GA | 493/1057 (47%) |

Total: 3,389 of 5,841 servable questions are usable by Phase 3's
diagnostic loop; the rest are safe/verified but have no archetype and are
invisible to probing. The 48 archetypes already exist across all 5
sections (`archetypes` table: Quant/DI 12, Reasoning 12, English 13, GK/GA
10, Computer Knowledge 1) — this workorder does NOT create new archetypes,
it only extends coverage of the existing ones using semantic similarity
instead of keyword rules.

`src/ssc_study/embeddings.py` already provides everything needed:
`compute_question_embedding`, `update_all_embeddings`,
`get_embedding`/embedding storage in `questions.embedding_blob`, and a
cosine similarity helper. Read this file fully before writing anything new
— reuse it, don't reimplement embedding logic.

## Task

1. Run `update_all_embeddings` (or confirm it's already been run and
   coverage is complete) so every non-holdout question has a stored
   embedding.
2. For each of the 48 archetypes, build a **centroid embedding**: the mean
   (normalized) vector of all currently `archetype_id`-tagged, non-holdout
   questions belonging to that archetype (the Stage 1 rule-matched seed
   set for that archetype).
3. **Validate the approach before applying it at scale**: hold out a
   sample of already-tagged questions (e.g. 15-20% per archetype, stratified),
   hide their `archetype_id`, reclassify them via nearest-centroid cosine
   similarity, and measure how often the correct archetype is recovered at
   various similarity thresholds. Pick a threshold that gives high
   precision (correct archetype recovered) even if it costs some recall —
   this mirrors the whole project's standing rule: only assign when
   confident, never guess. Report this validation result with real
   numbers before proceeding to the real backfill.
4. Using the validated threshold, classify every currently-untagged,
   **non-holdout** question (regardless of whether it's currently
   `available`/servable or excluded for other reasons — tag what you can,
   the serving gate already handles servability separately) by nearest
   centroid. Assign `archetype_id` only when similarity clears the
   validated threshold; leave untagged otherwise.
5. Do NOT assign `archetype_id` to holdout rows, matching Stage 1's
   existing behavior exactly (Stage 1 confirmed `holdout_archetype_non_null: 0`
   — preserve this invariant).
6. Write this as a rerunnable, idempotent script:
   `scripts/build_atlas_stage2.py` (mirror Stage 1's CLI conventions:
   `--db` flag, clear stdout summary). Running it again later (e.g. after
   more questions get verified) should only touch newly-untagged rows, not
   reprocess or flip already-Stage-1-or-Stage-2-tagged ones.

## Explicit constraints

- Do not modify `scripts/build_atlas_stage1.py` or its existing behavior.
- Do not create, rename, merge, or delete any archetype in the
  `archetypes` table — this is coverage expansion only, same 48 categories.
- Do not touch `data/study.db` tables other than `questions.archetype_id`
  and `questions.embedding_blob`.
- Do not call any external API or require any credential — this must work
  fully offline/locally. If you find yourself needing network access,
  stop and reconsider the approach.
- Protected tables (`attempts`, `sessions`, `sm2_state`) and all existing
  `question_id`s/row counts must be unchanged — this only updates two
  columns on existing rows, never inserts/deletes rows.

## Verification required before reporting done

- Embedding coverage before/after (`get_embedding_stats`).
- Validation-phase results: threshold chosen, and precision/recall at that
  threshold on the held-out sample, per section.
- Real backfill counts: how many previously-untagged non-holdout questions
  got a new `archetype_id`, broken down by section and by archetype.
- Updated per-section tagged/servable coverage table (same format as the
  "before" table above) — this is the headline result.
- Confirm holdout rows still have zero archetype assignments.
- Confirm protected tables and row counts unchanged.
- Run `uv run pytest -q`, paste exact results.

## Report format

Embedding coverage before/after, validation methodology and chosen
threshold with precision numbers, backfill counts by section/archetype,
updated coverage table (headline), protected-table proof, test suite
results, residual risk (e.g. sections/archetypes that remain
under-covered even after this pass, and why).
