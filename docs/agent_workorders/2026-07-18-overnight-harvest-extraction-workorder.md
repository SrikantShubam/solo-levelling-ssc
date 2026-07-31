# 2026-07-18 Overnight Harvest Extraction Batch

You are working in `C:\experiments\ssc`. This is a batch-processing task, not a
code-review task: build a driver, then run it to completion overnight.

## Context

64 PDFs were harvested to `data/harvest_pdfs/` (61 clean per-shift papers
already staged there; 3 large "testbook_compilation" PDFs still need pulling
from `manstein@192.168.1.14:~/ssc-pdf-harvest/` via scp if present). A smoke
test already confirmed `ssc-corpus extract-pdf --provider gemini` works
correctly against this harvest format (validated: page 1 of
`2017_tier1_prepp_2017-08-10_shift1.pdf` produced 3 clean questions, 4
options each, correct answers present). Extraction runs ~60-70s/page,
single-threaded, zero rate-limit errors observed on the free Google AI
Studio key in `.env` (`api=` key, read via
`ssc_corpus.extraction.read_api_key`).

## Task

Write `scripts/run_overnight_harvest.py` that:

1. Enumerates every PDF in `data/harvest_pdfs/` (pull the 3 compilation PDFs
   from the remote first if missing — same scp pattern already used for the
   61 clean ones).
2. Runs `extract_pdf_with_gemini` (or shells out to
   `ssc-corpus extract-pdf --provider gemini`) for each PDF into
   `pipeline_output/harvest_batch/<pdf_stem>/`, skipping PDFs whose output
   already has a complete `merged_questions_global_order.json`.
3. Runs **multiple PDFs concurrently** (process pool or asyncio; pick
   whichever fits this codebase's existing conventions with least new
   complexity) to cut overnight wall-clock time. Page-level results are
   already cached per-PDF (`page_json/page_NN.json`, skipped on rerun if
   present and not `--force`) — do not break that; concurrency is across
   PDFs, not needed within a single PDF's page loop.
4. Handles 429/quota errors per-PDF without killing the whole batch: if a
   PDF's extraction raises or reports `api_quota_or_rate_limit` on multiple
   pages, log it, move to the next PDF, and leave it resumable (its cached
   pages stay valid; rerunning the script later resumes from where it left
   off, same as the existing single-PDF page-caching behavior).
5. Writes a running manifest (`pipeline_output/harvest_batch/batch_status.json`
   or similar) tracking per-PDF status: `pending`, `in_progress`, `done`,
   `failed` with reason. Update it as it goes so progress is visible without
   waiting for full completion.
6. Is safe to re-run: if the script itself dies (crash, machine sleep,
   whatever), running it again picks up unfinished/failed PDFs and skips
   completed ones.

## Explicit constraints

- Use the existing free key (`api=` in `.env`) and `models/gemini-3.1-flash-lite`
  (the current `DEFAULT_MODEL`) — do not switch providers or models, do not
  add paid-tier logic, do not prompt for API keys.
- Do not touch `data/study.db` or run any merge-into-corpus step — this
  workorder is extraction only (PDF -> page_json -> merged_questions_global_order.json
  per PDF, staying in `pipeline_output/harvest_batch/`). Corpus ingestion
  (dedup, holdout split, quality gates, importing into `questions` table) is
  explicitly a separate future step — do not attempt it here.
- Do not modify any Wave 1/1b/2/3 code (`baseline_web.py`, `corpus_assets.py`,
  `answer_verification.py`, `modality_recrop.py`) — this is corpus
  acquisition, unrelated to the web-serving gate work already done.
- Concurrency level: pick something conservative enough not to trip Google's
  per-minute request limits even without hard evidence of what that limit
  is — start around 3-4 concurrent PDFs, not higher, since we have no prior
  measurement of the per-minute cap, only that sequential single-PDF usage
  saw zero 429s.

## Verification required before reporting done

- Run the script for at least 2 full PDFs end-to-end and confirm
  `merged_questions_global_order.json` is produced with plausible question
  counts (cross-check against `page_count` in the harvest manifest — a PDF
  reporting far fewer questions than its page count suggests warrants a
  note, not silent success).
- Confirm resumability: kill the script mid-run (Ctrl+C equivalent /
  SIGTERM) after at least one PDF partially completes, rerun it, and show
  that already-cached pages are not re-extracted (check timestamps/logs)
  and the run continues correctly.
- Run existing test suite to confirm nothing broke: `uv run pytest -q`.
- Then launch the real overnight batch run in the background (nohup /
  detached process — this needs to survive the current terminal session
  ending) covering ALL 64 harvested PDFs, and report the launch command
  used plus how to check progress (the batch_status.json path).

## Report format

Files added, concurrency approach chosen and why, verification results
(2-PDF test + resumability proof + test suite), the exact command used to
launch the full overnight run and how it was detached, and the path to the
live progress manifest.
