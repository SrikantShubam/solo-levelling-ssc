Files changed/added: none. I read the full workorder and the existing `scripts/run_overnight_harvest.py` stub, but local command execution failed before I could inspect the extraction signature, edit files, run tests, scp PDFs, or launch the detached batch.

Concurrency approach: not implemented. The existing stub is still Gemini-oriented and would need to be converted to OpenRouter/qwen with 3-4 concurrent PDFs, live manifest updates, spend polling, and budget hard-stop.

Verification results: not run. The shell wrapper is globally failing at process setup, including a minimal `Get-Location` in both `C:\experiments\ssc` and `C:\tmp`, with:

```text
windows sandbox: orchestrator_helper_exit_nonzero: setup helper exited with status Some(-1073741502)
```

Exact launch command for the real batch and confirmation it’s running detached: not launched. I cannot honestly claim a background run exists without a working local process path.

Current manifest path: expected by the workorder to be `pipeline_output/harvest_batch/batch_status.json`, but I did not create/update it in this turn.

Starting-vs-current measured spend: not measured. The OpenRouter `/api/v1/key` check requires reading `.env` and making the API request from the local environment, which is blocked by the command runner failure.

