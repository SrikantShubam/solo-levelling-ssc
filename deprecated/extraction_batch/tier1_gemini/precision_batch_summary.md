# Precision Extraction Batch Summary

| Run | QC | Qs | Structural | Evidence | LLM-only | Manual/blocking | RGB evidence | Ambiguous | Unavailable |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2019_tier1_prepp_shift1 | BLOCKED | 100 | True | 98 | 0 | 2/2 | 98 | 2 | 0 |
| 2020_tier1_prepp_shift1 | BLOCKED | 100 | True | 48 | 13 | 39/39 | 82 | 1 | 17 |
| 2021_tier1_sscportal_shift1_response_sheet | PASS_WITH_MANUAL_REVIEW | 100 | True | 100 | 0 | 0/0 | 100 | 0 | 0 |
| 2022_tier1_prepp_shift1 | BLOCKED | 100 | True | 0 | 67 | 33/33 | 0 | 0 | 100 |
| 2023_tier1_prepp_shift1 | BLOCKED | 100 | True | 65 | 12 | 23/23 | 79 | 0 | 21 |
| 2024_tier1_sscportal_sep09_shift1_response_sheet | BLOCKED | 100 | True | 98 | 0 | 2/2 | 98 | 0 | 2 |

## Notes

- `Manual/blocking` is `PASS_WITH_MANUAL_REVIEW` evidence count / blocking review count.
- Chosen-option gaps are non-blocking; correct-answer conflicts, ambiguous deterministic evidence, or unresolved complex visual/table/math rows are blocking.
- `raw_page_result.json` and per-question `raw_gemini_record` retain the original LLM extraction before canonical QC.
