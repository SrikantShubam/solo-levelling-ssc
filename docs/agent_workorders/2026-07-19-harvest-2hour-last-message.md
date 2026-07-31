Files changed/added: `scripts/run_overnight_harvest.py`, `tests/test_overnight_harvest.py`. Pulled the 3 missing compilation PDFs into `data/harvest_pdfs/`, bringing staged PDFs to 64.

Model+pacing decisions with real numbers: using `openrouter` / `qwen/qwen3-vl-32b-instruct`. I left the shared CLI’s 5s OpenRouter delay untouched and bypassed it in the batch driver with `--page-delay-seconds 0.25`. Fresh timing run: 2 PDFs, 55 pages, 435.14s elapsed, 0 page failures, 208 questions total. That is 7.91s/page combined at concurrency 2, or about 15.82s/page per PDF worker.

Concurrency chosen and 2-hour-target math: full run is 4,527 pages, so 2 hours requires 0.629 pages/sec. The timing sample implies one sequential PDF worker is ~0.0632 pages/sec, so PDF-only concurrency needs ~10 workers, but the 1,091-page compilation would be a 4.8h long tail if sequential. I updated the runner so PDFs over 200 pages use 4 page workers. Final launch uses PDF concurrency 12 and large-PDF page workers 4; honest projection is roughly 75-90 minutes if provider behavior stays near the timing sample. Current manifest projection is lower because it includes cached pages from the stopped first launch.

Verification results: `uv run pytest -q` passed: 434 passed, 7 warnings. Budget-stop behavior is covered in `tests/test_overnight_harvest.py`. The real batch is running detached; verified live process command lines for `uv.exe` and child Python processes.

Exact launch command:
```powershell
uv run python scripts\run_overnight_harvest.py --out pipeline_output\harvest_batch --skip-remote-pull --concurrency 12 --page-delay-seconds 0.25 --large-pdf-page-workers 4 --large-pdf-page-threshold 200
```

Manifest path: `pipeline_output/harvest_batch/batch_status.json`.

Starting spend reading for the final detached launch: `$0.160047885`. Latest manifest snapshot showed `$0.275898373` current usage, 3 PDFs done, 12 in progress, 49 pending, 449/4527 pages completed/cached.