# Native Pipeline Comparison Audit

## Status
- Pipeline 1 is deprecated for corpus generation and retained only for historical/manual comparison.
- Pipeline 2 is the active extraction path.

## Input Status
- Pipeline 1 run dir: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1`
- Pipeline 1 source (`page_json/*.json`): cached (28 files)
- Pipeline 2 run dir: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1`
- Pipeline 2 source (`merged_questions_global_order.json`): cached existing merged artifact

## Model Routing
- Fallback model used: no

## Row Counts
- Pipeline 1 rows: 100
- Pipeline 2 rows: 100
