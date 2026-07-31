Hermes invocation failed. Exact remote error:

```text
bash: line 1: hermes: command not found
```

What happened:
- `scp` of `2026-07-18-hermes-ssc-pdf-harvest.md` to `~/ssc_harvest_workorder.md` completed successfully.
- The requested SSH Hermes command exited with code `1`.
- Retrieval command output was:

```text
===MANIFEST===
===LISTING===
```

No manifest contents were returned, and `ls` produced no directory listing for `~/ssc-pdf-harvest/`.

Verified PDFs landed in `~/ssc-pdf-harvest/`: `0`

