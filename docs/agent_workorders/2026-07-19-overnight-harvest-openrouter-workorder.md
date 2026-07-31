# 2026-07-19 Overnight Harvest Extraction — OpenRouter qwen3-vl-8b-instruct

You are working in `C:\experiments\ssc`. This supersedes
`docs/agent_workorders/2026-07-18-overnight-harvest-extraction-workorder.md`
(that dispatch failed before completing a working driver). Read the old one
for background context but follow THIS spec for provider/model/scope.

## Context, validated facts

- 64 PDFs are harvested. 61 are staged at `data/harvest_pdfs/*.pdf`
  (non-compilation). 3 large `*_testbook_compilation.pdf` files still need
  pulling from `manstein@192.168.1.14:~/ssc-pdf-harvest/` via scp if not
  already present locally under `data/harvest_pdfs/`.
- `src/ssc_corpus/cli.py` `_primary_model_spec` now reads the OpenRouter key
  from `SSC_OPENROUTER` first (added today), falling back to older key names.
  `.env` has `SSC_OPENROUTER` set with a funded ($5) OpenRouter key.
- Smoke-tested and confirmed working:
  `uv run ssc-corpus extract-pdf --pdf data/harvest_pdfs/2017_tier1_prepp_2017-08-10_shift1.pdf --out pipeline_output/harvest_smoke_qwen/2017_tier1_prepp_2017-08-10_shift1 --provider openrouter --model qwen/qwen3-vl-8b-instruct --env-file .env`
  Result: 22/23 pages `OK`, 1 page `ERROR` (`json_or_schema_failure`,
  recoverable), 100 questions extracted, `qc_status=INFRA_FAILURE` only
  because of that single bad page (not corruption).
- Measured real cost via OpenRouter's own `/api/v1/key` usage field:
  $0.0227 for 23 pages = ~$0.00099/page. Full 4,527-page harvest (including
  the 3 compilations) is ~$4.47 — comfortably inside the $5 loaded.
- `extract-pdf` already applies a 5-second `page_delay_seconds` automatically
  for `--provider openrouter` (see `cli.py` around `page_delay = 5.0 if
  args.provider == "openrouter"`) — do not remove or override this, it's the
  existing rate-limit courtesy delay.
- Page-level results are cached (`page_json/page_NN.json` skipped on rerun
  unless `--force`), so extraction is naturally resumable per-PDF.

## Task

Write `scripts/run_overnight_harvest.py` (reuse this exact name/location if
a stub already exists from the prior failed dispatch — inspect and fix it
rather than assuming from scratch) that:

1. Pulls the 3 compilation PDFs from the remote if missing locally.
2. Enumerates every PDF in `data/harvest_pdfs/` (should be 64 once step 1
   completes).
3. For each PDF, runs extraction via
   `extract_pdf_with_openai_compatible_vision` (the same function the CLI's
   openrouter path calls — check `src/ssc_corpus/extraction.py` for its
   exact signature) with `provider="openrouter"`,
   `model_name="qwen/qwen3-vl-8b-instruct"`, endpoint
   `https://openrouter.ai/api/v1/chat/completions`, api_key read via
   `SSC_OPENROUTER` (reuse the existing `_first_env_value`/`_primary_model_spec`
   helpers from `cli.py` rather than re-deriving key lookup logic), output
   dir `pipeline_output/harvest_batch/<pdf_stem>/`. Skip PDFs whose output
   already has a complete `merged_questions_global_order.json` unless
   `--force`.
4. Runs multiple PDFs **concurrently** (3-4 at a time — conservative given
   this is a paid key on a fresh account, no prior measurement of concurrent
   rate limits) to finish faster than serial. Page-level work within one PDF
   stays sequential (existing 5s page delay applies per PDF's own page loop).
5. Handles per-page and per-PDF failures without killing the batch: log and
   continue to the next PDF on any exception; a single bad page (like the
   `json_or_schema_failure` seen in the smoke test) should not block the
   rest of that PDF's pages or other PDFs.
6. Writes/updates a live progress manifest
   `pipeline_output/harvest_batch/batch_status.json`: per-PDF status
   (`pending`/`in_progress`/`done`/`failed`), question count, page
   success/fail counts.
7. Tracks and reports cumulative real spend: query
   `https://openrouter.ai/api/v1/key` (using the `SSC_OPENROUTER` key) before
   starting and after finishing, report the delta in USD. Also **hard-stop
   the batch and report clearly** if cumulative usage since batch start
   exceeds $4.90 (safety margin under the $5 loaded) — do not let it run
   past budget unattended.
8. Is safe to re-run / resumable if interrupted, same as before.

## Explicit constraints

- Model/provider are fixed: `openrouter` / `qwen/qwen3-vl-8b-instruct`. Do
  not substitute a different model even if it looks cheaper or faster —
  this was chosen and validated deliberately.
- Do not touch `data/study.db`, do not run any corpus-merge/import step —
  extraction only, output stays in `pipeline_output/harvest_batch/`.
- Do not modify Wave 1/1b/2/3 web-serving code
  (`baseline_web.py`, `corpus_assets.py`, `answer_verification.py`,
  `modality_recrop.py`).
- Do not change the `SSC_OPENROUTER`-first key precedence added to
  `_primary_model_spec` in `cli.py` today, and do not weaken it back to
  picking up the old `openrouter=` key by accident.

## Verification required before reporting done

- Confirm all 3 compilation PDFs pulled and present locally.
- Run the driver against at least 2 more full PDFs beyond the existing smoke
  test, confirm output quality (`merged_questions_global_order.json`
  question counts plausible vs page count) and report per-PDF page
  success/fail breakdown.
- Prove resumability: interrupt mid-run, rerun, confirm cached pages are not
  re-billed/re-extracted.
- Prove the budget hard-stop works (can be tested with a lowered threshold
  in a test, not necessarily by actually spending near $5).
- Run `uv run pytest -q` to confirm nothing else broke.
- Launch the real full 64-PDF batch detached in the background so it
  survives this session ending, and report the exact launch command, the
  live progress manifest path, and the starting `/api/v1/key` usage reading.

## Report format

Files changed/added, concurrency approach, verification results (2+ PDF
test, resumability proof, budget-stop proof, test suite), the exact launch
command for the real batch and confirmation it's running detached, current
manifest path, and starting-vs-current measured spend.
