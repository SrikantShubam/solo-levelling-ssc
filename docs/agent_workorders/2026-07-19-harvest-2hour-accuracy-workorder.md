# 2026-07-19 Harvest Extraction — 2-Hour Target, Accuracy-Prioritized

You are working in `C:\experiments\ssc`. This supersedes and corrects
`docs/agent_workorders/2026-07-19-overnight-harvest-openrouter-workorder.md`
(that dispatch was stopped before writing code — no batch was launched, no
spend beyond the single smoke test). Read the old workorder for background,
but follow THIS spec for model/concurrency/pacing — the old one targeted
"overnight" and was too conservative for the real constraint: **user wants
this done in about 2 hours, with accuracy prioritized over minimizing cost
further** (cost is already effectively a non-issue at this scale).

## Corrected facts driving this workorder

- **Model is now `qwen/qwen3-vl-32b-instruct`**, not 8b. Real OpenRouter
  pricing: 32b = $0.104/M input, $0.416/M output — both components cheaper
  than 8b ($0.117/$0.455), so switching is a strict win on cost AND a step
  up in model capability. Do not use 8b or any other model.
- **Real measured throughput** from the existing single-PDF smoke test
  (`pipeline_output/harvest_smoke_qwen/2017_tier1_prepp_2017-08-10_shift1/`):
  23 pages took 6m21s serially = ~16.6s/page, which includes a fixed 5-second
  `page_delay_seconds` currently hardcoded for `--provider openrouter` in
  `src/ssc_corpus/cli.py` (`page_delay = 5.0 if args.provider ==
  "openrouter" else 0.0`, used in two places). That delay was calibrated for
  a conservative/overnight pace and is now the main obstacle to the 2-hour
  target.
- Total harvest: 4,527 pages across 64 PDFs (61 already staged at
  `data/harvest_pdfs/*.pdf`; 3 `*_testbook_compilation.pdf` files still need
  pulling from `manstein@192.168.1.14:~/ssc-pdf-harvest/` via scp).
- To finish 4,527 pages in ~2 hours (7200s), you need combined throughput of
  roughly 0.63 pages/sec across all concurrent work. Do the actual math
  yourself against whatever real per-page latency you observe once the
  fixed delay is reduced — do not just copy the number above blindly, verify
  it against a fresh timing sample early in your work.
- `SSC_OPENROUTER` key in `.env` is funded ($5, ~$0.03 used by the smoke
  test so far). Real cost is a non-issue here — optimize for hitting the
  2-hour target and extraction accuracy, not for shaving more cost.

## Task

Write/fix `scripts/run_overnight_harvest.py` (rename to
`scripts/run_harvest_batch.py` if you prefer — check if a stub already
exists from the stopped prior dispatch and decide whether to keep or
replace it) that:

1. Pulls the 3 compilation PDFs from remote if not already local.
2. For the `openrouter` provider path specifically, reduce or remove the
   fixed 5-second `page_delay_seconds` in `cli.py` (or bypass it by calling
   `extract_pdf_with_openai_compatible_vision` directly with a much smaller
   delay, e.g. 0-1s) — the existing per-request exponential backoff on 429
   (already in `extraction.py`) is the real safety net, not a blanket fixed
   sleep. If you change the CLI default, verify no other caller/test depends
   on the 5s value; if changing shared code is risky, call the underlying
   extraction function directly with the batch driver's own delay instead of
   touching `cli.py`'s constant.
3. Runs many PDFs **concurrently** — size the concurrency from your own
   fresh timing measurement to plausibly land the full batch around 2 hours
   with reasonable margin, not right at the edge. Do not go so high that a
   single provider-side rate-limit wall causes mass failures; if you observe
   429s clustering, back off concurrency rather than pushing through.
4. Model: `qwen/qwen3-vl-32b-instruct`, provider `openrouter`, key via
   `SSC_OPENROUTER` (already wired as first-priority in
   `_primary_model_spec` in `cli.py` — reuse that, don't re-derive key
   lookup).
5. Per-PDF and per-page failure isolation: one bad page or PDF must not
   kill the batch. Resumable via existing page-level JSON caching.
6. Live progress manifest `pipeline_output/harvest_batch/batch_status.json`:
   per-PDF status, question counts, page success/fail counts, and a
   **running elapsed-time-vs-projected-completion estimate** so progress
   toward the 2-hour target is visible without reading logs.
7. Budget safety: query `https://openrouter.ai/api/v1/key` (via
   `SSC_OPENROUTER`) before starting; hard-stop the batch and report clearly
   if cumulative usage since batch start exceeds $4.90. This is a safety
   rail only — the real target is time and accuracy, not squeezing cost.
8. Output goes to `pipeline_output/harvest_batch/<pdf_stem>/` — do not touch
   `data/study.db`, do not run any corpus-merge/import step, do not modify
   Wave 1/1b/2/3 web-serving code.

## Verification required before reporting done

- Fresh timing measurement: run at least 2 PDFs through the new pacing and
  report actual seconds/page achieved (not the old 16.6s number — a new
  one).
- Show the concurrency-vs-2-hour-target math explicitly using that fresh
  number, and state your chosen concurrency and why it's not cutting it too
  close to provider rate limits.
- Run `uv run pytest -q` to confirm nothing broke from the `cli.py`/delay
  change.
- Launch the real full 64-PDF batch detached in the background (survives
  this session), confirm it's running, report launch command, manifest
  path, and the starting `/api/v1/key` usage reading.
- State your honest projection for total wall-clock completion time based
  on measured (not assumed) throughput — if it's not going to land near 2
  hours, say so plainly rather than rounding optimistically.

## Report format

Files changed/added, model+pacing decisions with the real numbers behind
them, fresh timing measurement, concurrency chosen and 2-hour-target math,
verification results, exact launch command for the real batch, manifest
path, starting spend reading, and honest completion-time projection.
