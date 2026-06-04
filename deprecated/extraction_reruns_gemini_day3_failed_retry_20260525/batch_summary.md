# Gemini Retry Summary

- Source baseline: `extraction_reruns/p2_all_pdfs_20260524/batch_summary.json`
- Consolidated retry folder: `extraction_reruns/gemini_day3_failed_retry_20260525`

| PDF | Old Count | New Count | Delta | Old QC | New QC | Structural |
|---|---:|---:|---:|---|---|---|
| 2020_tier2_kdcampus_answer_key.pdf |  | 191 | 191 | ERROR | INFRA_FAILURE | INFRA_FAILURE |
| 2021_tier1_prepp_shift1.pdf | 91 | 91 | 0 | FAIL | FAIL | FAIL |
| 2022_tier2_prepp_paper1.pdf | 81 | 150 | 69 | FAIL | BLOCKED | PASS |
| 2023_tier1_prepp_shift1.pdf | 0 | 100 | 100 | FAIL | BLOCKED | PASS |
| 2023_tier2_prepp_paper1.pdf | 0 | 150 | 150 | FAIL | BLOCKED | PASS |
| 2024_tier1_prepp_shift1.pdf | 3 | 94 | 91 | FAIL | FAIL | FAIL |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | 0 | 100 | 100 | FAIL | BLOCKED | PASS |
| 2024_tier2_prepp_paper1.pdf | 7 | 141 | 134 | FAIL | FAIL | FAIL |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | 0 | 150 | 150 | FAIL | BLOCKED | PASS |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | 0 | 97 | 97 | FAIL | INFRA_FAILURE | INFRA_FAILURE |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | 9 | 150 | 141 | FAIL | BLOCKED | PASS |
