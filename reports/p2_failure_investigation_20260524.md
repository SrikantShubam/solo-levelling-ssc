# P2 Extraction Failure Investigation

- Source batch summary: `C:\experiments\ssc\extraction_reruns\p2_all_pdfs_20260524\batch_summary.json`
- PDFs inspected: 19

## Action Summary

| Bucket | Count |
|---|---:|
| fallback_needed | 2 |
| quarantine | 1 |
| rerun_needed | 9 |
| usable_with_review | 7 |

## PDF Matrix

| PDF | Class | Expected | Extracted | QC | Failure | Error pages | Action |
|---|---|---:|---:|---|---|---:|---|
| 2019_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 100 | BLOCKED |  | 0 | usable_with_review |
| 2019_tier2_prepp_english.pdf | tier2_section_booklet |  | 200 | BLOCKED |  | 0 | usable_with_review |
| 2019_tier2_prepp_quant.pdf | tier2_section_booklet |  | 100 | BLOCKED |  | 0 | usable_with_review |
| 2020_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 100 | BLOCKED |  | 0 | usable_with_review |
| 2020_tier2_kdcampus_answer_key.pdf | coaching_pdf_with_answers |  |  | ERROR | model_refusal | 0 | fallback_needed |
| 2021_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 91 | FAIL | json_or_schema_failure | 4 | fallback_needed |
| 2021_tier1_sscportal_shift1_response_sheet.pdf | response_sheet_green_answer | 100 | 100 | PASS_WITH_MANUAL_REVIEW |  | 0 | usable_with_review |
| 2021_tier2_prepp_english.pdf | tier2_section_booklet |  | 200 | BLOCKED |  | 0 | usable_with_review |
| 2022_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 100 | BLOCKED |  | 0 | usable_with_review |
| 2022_tier2_prepp_paper1.pdf | tier2_section_booklet |  | 81 | FAIL | api_quota_or_rate_limit | 27 | rerun_needed |
| 2023_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 0 | FAIL | api_quota_or_rate_limit | 28 | rerun_needed |
| 2023_tier2_prepp_paper1.pdf | tier2_section_booklet |  | 0 | FAIL | api_quota_or_rate_limit | 56 | rerun_needed |
| 2024_tier1_appx_answer_key.pdf | answer_key_notice_or_non_question | 100 | 0 | FAIL | api_quota_or_rate_limit | 10 | quarantine |
| 2024_tier1_prepp_shift1.pdf | coaching_pdf_with_answers | 100 | 3 | FAIL | api_quota_or_rate_limit | 43 | rerun_needed |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | response_sheet_green_answer | 100 | 0 | FAIL | api_quota_or_rate_limit | 39 | rerun_needed |
| 2024_tier2_prepp_paper1.pdf | tier2_section_booklet |  | 7 | FAIL | api_quota_or_rate_limit | 69 | rerun_needed |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | response_sheet_green_answer |  | 0 | FAIL | api_quota_or_rate_limit | 61 | rerun_needed |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | response_sheet_green_answer |  | 0 | FAIL | api_quota_or_rate_limit | 36 | rerun_needed |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | response_sheet_green_answer |  | 9 | FAIL | api_quota_or_rate_limit | 54 | rerun_needed |
