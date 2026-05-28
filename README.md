# solo-levelling-ssc

SSC CGL question corpus extracted from 19 PDFs (2019-2024, Tier 1 & 2) using Gemini flash-lite.

## Stats

- **2355 questions** across 19 PDFs
- **99.3% precision** (valid question text + options + numbering)
- **~97% recall** on extractable content
- **67% answer coverage** (higher on portal response sheets, lower on prepp papers)
- Pipeline: `gemini-3.1-flash-lite` at 60 RPM, spot-fixed with `gemini-3.5-flash` for tricky pages

## Structure

```
pipeline_output/p2_gemini/   ← winning pipeline output
  {pdf_name}/
    merged_questions_global_order.json   ← final merged questions
    page_json/                           ← per-page extraction results
    review_summary_*.md                  ← QC reports
deprecated/                  ← old pipeline attempts
src/                         ← extraction pipeline code
reports/                     ← phase comparison reports
```

## Pipeline

`ssc-corpus extract-pdf --pdf <path> --out <dir> --provider gemini --model models/gemini-3.1-flash-lite`

Run with `--help` for full options. Requires a `.env` file with `api=<gemini-key>`.

## Status

Phase 2 (Corpus Extraction) is complete. Ready for Phase 2b (SQLite, holdout, atlas) or Phase 3/4.
