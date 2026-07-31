# 2026-07-17 Wave 2b: Answer Re-Verification Pass

You are working in `C:\experiments\ssc`. Read this file fully before changing
anything. This is Wave 2 work, running after Wave 2a (passages) has already
landed — read `docs/agent_workorders/2026-07-17-wave1-baseline-corpus-safety-workorder.md`,
its `wave1b` follow-up, and `2026-07-17-wave2a-passage-groups-workorder.md`
for context on what already exists before you start.

## Context

The web-safe baseline gate (`src/ssc_study/baseline_web.py`,
`_web_baseline_rejection_reason`) currently excludes:
- 155 rows with `evidence_status IN ('PASS_LLM_ONLY', 'BLOCKED')` — answers
  with no verified answer-key evidence — reason `unverified_answer`.
- 8 rows where `correct_option_text` disagrees with the option text at
  `correct_option_label`, or the label isn't among the parsed options at all
  — reason `answer_integrity_failure`.

These are excluded, not fixed. Your job is to actually verify or correct as
many of these as the available evidence supports, and leave the rest
excluded (never guess).

## Ground truth sources available

1. **Response-sheet / answer-key crop images** (raw, unmasked originals —
   these still exist untouched; Wave 1b only removed corrupted *masked*
   copies, never the originals) for the seven sources in
   `src/ssc_study/corpus_assets.py::ANSWER_LEAKING_SOURCES`. These crops show
   a green check / red X next to each option — that is direct ground truth
   for the correct answer. Read the raw crop at `question_crop_path`
   (unmasked, under `.../question_crops/...` or `.../page_images/...`, NOT
   `.../question_crops_masked/...`) to determine the marked correct option.
2. **`answer_key_candidates_staging/`** — already contains the source PDFs
   plus a `candidate_manifest.csv` and staging dossiers
   (`candidate_review_summary.md`, `staging_fix_dossier.md`). Read these
   first; this directory may already contain prior answer-key reconciliation
   work you can reuse rather than redo.
3. For sources with no visible answer-key marking and no staging evidence,
   there may be no way to verify beyond the existing extraction. If so,
   leave the row excluded — do not invent an answer from model reasoning
   alone (that is exactly what `PASS_LLM_ONLY` already means and why it's
   excluded).

## Required reading before changing anything

- `src/ssc_study/corpus_assets.py` (masking, `ANSWER_LEAKING_SOURCES`)
- `src/ssc_study/baseline_web.py` (`_has_answer_integrity_failure`,
  `_UNVERIFIED_EVIDENCE_STATUSES`, `_web_baseline_rejection_reason`)
- `src/ssc_corpus/ai_review.py` (existing evidence/review conventions — the
  corpus already has a notion of AI-assisted review with deterministic label
  ordering; follow its conventions rather than inventing a new evidence
  pipeline)
- `answer_key_candidates_staging/candidate_review_summary.md` and
  `staging_fix_dossier.md`
- `tests/test_baseline_web.py`, `tests/test_ai_review.py`

## Scope

1. For every row currently excluded as `unverified_answer` or
   `answer_integrity_failure`, attempt to resolve it against ground truth:
   - If the row's `pdf_name` is in `ANSWER_LEAKING_SOURCES`, read the raw
     crop and determine the marked correct option programmatically or via
     scripted visual inspection; update `correct_option_label`,
     `correct_option_text`, and `evidence_status` (promote to an evidence
     status that reflects verified answer-key evidence — check
     `evidence_status` conventions in `models.py`/existing rows for the
     right value, e.g. reuse `PASS_WITH_EVIDENCE` if the semantics fit, or
     add a new explicit status if they don't — do not silently overload an
     existing status to mean something new without checking first).
   - Otherwise, check `answer_key_candidates_staging/` for existing
     reconciliation data for that `pdf_name`/question.
   - If neither ground truth source resolves the row, leave it excluded.
2. For the 8 `answer_integrity_failure` rows specifically: these are cases
   where the current `correct_option_label`/`correct_option_text` disagree
   internally — resolve by picking whichever value the ground-truth source
   confirms, not by arbitrary preference for one field over the other.
3. Write this as a rerunnable script (following the
   `scripts/remap_baseline_assets.py` convention from Wave 1) rather than a
   one-off interactive edit, so the orchestrator can re-run it against the
   canonical `data/study.db` after your changes land.

## Out of scope

- Passage/RC linking (Wave 2a, already done)
- Modality reclassification, re-cropping the two whole-page-only sources
  (Wave 2c, runs after this)
- Masking policy / `corpus_assets.py` changes

## Landmine to avoid

Do not read masked crops as ground truth — they have had the answer
annotation deliberately cropped away by Wave 1/1b. You must read the raw,
unmasked originals for this work.

## Verification required before reporting done

- Run `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q`
  and `uv run pytest -q`, paste exact results.
- Report exact counts: rows resolved from crop ground truth, rows resolved
  from staging data, rows still excluded and why, per exclusion reason
  before/after.
- Manually confirm at least 3 resolved rows by describing what the raw crop
  or staging source actually showed and what value you set.

## Report format

Files changed, script added and exact command to run it, counts (resolved
vs. still-excluded per reason), tests added, exact verification commands and
results, residual risk for later waves.
