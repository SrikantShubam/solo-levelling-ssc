# Phase Comparison Report

## Architecture Changes

- `P1`: Original llm-only extraction phase using Gemini page-image extraction without deterministic answer evidence.
- `P2`: Precision pipeline added layout crops, HSV green-answer evidence, and canonical QC on top of Gemini extraction.
- `P2_patch1`: Patch1 added structural failure investigation and metadata after the all-PDF rerun exposed quota pages being merged as empty output.
- `P2_patch3`: Patch3 retries 11 failed PDFs with Gemini Flash Lite, recovering ~1414 questions vs NIM's ~291.

## Results Table

| PDF | Phase | Questions | Expected | QC | Structural | Failure | Provider/Model |
|---|---|---:|---:|---|---|---|---|
|  | P1 |  |  |  |  |  |  |
|  | P2 | 100 | None | BLOCKED | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; precision evidence layer |
|  | P2_patch1 |  |  |  |  |  |  |
|  | P2_patch3 |  |  |  |  |  |  |
| 2019_tier1_prepp_shift1.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2019_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2019_tier1_prepp_shift1.pdf | P2_patch1 | 100 | 100 | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2019_tier1_prepp_shift1.pdf | P2_patch3 |  |  |  |  |  |  |
| 2019_tier2_prepp_english.pdf | P1 |  |  |  |  |  |  |
| 2019_tier2_prepp_english.pdf | P2 |  |  |  |  |  |  |
| 2019_tier2_prepp_english.pdf | P2_patch1 | 200 | None | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2019_tier2_prepp_english.pdf | P2_patch3 |  |  |  |  |  |  |
| 2019_tier2_prepp_quant.pdf | P1 |  |  |  |  |  |  |
| 2019_tier2_prepp_quant.pdf | P2 |  |  |  |  |  |  |
| 2019_tier2_prepp_quant.pdf | P2_patch1 | 100 | None | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2019_tier2_prepp_quant.pdf | P2_patch3 |  |  |  |  |  |  |
| 2020_tier1_prepp_shift1.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2020_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2020_tier1_prepp_shift1.pdf | P2_patch1 | 100 | 100 | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2020_tier1_prepp_shift1.pdf | P2_patch3 |  |  |  |  |  |  |
| 2020_tier2_kdcampus_answer_key.pdf | P1 |  |  |  |  |  |  |
| 2020_tier2_kdcampus_answer_key.pdf | P2 |  |  |  |  |  |  |
| 2020_tier2_kdcampus_answer_key.pdf | P2_patch1 | None | None | ERROR | FAIL | model_refusal | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2020_tier2_kdcampus_answer_key.pdf | P2_patch3 | 191 | None | INFRA_FAILURE | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2021_tier1_prepp_shift1.pdf | P1 |  |  |  |  |  |  |
| 2021_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2021_tier1_prepp_shift1.pdf | P2_patch1 | 91 | 100 | FAIL | FAIL | json_or_schema_failure | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2021_tier1_prepp_shift1.pdf | P2_patch3 | 91 | 100 | FAIL | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2021_tier1_sscportal_shift1_response_sheet.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2021_tier1_sscportal_shift1_response_sheet.pdf | P2 |  |  |  |  |  |  |
| 2021_tier1_sscportal_shift1_response_sheet.pdf | P2_patch1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2021_tier1_sscportal_shift1_response_sheet.pdf | P2_patch3 |  |  |  |  |  |  |
| 2021_tier2_prepp_english.pdf | P1 |  |  |  |  |  |  |
| 2021_tier2_prepp_english.pdf | P2 |  |  |  |  |  |  |
| 2021_tier2_prepp_english.pdf | P2_patch1 | 200 | None | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2021_tier2_prepp_english.pdf | P2_patch3 |  |  |  |  |  |  |
| 2022_tier1_prepp_shift1.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2022_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2022_tier1_prepp_shift1.pdf | P2_patch1 | 100 | 100 | BLOCKED | PASS | None | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2022_tier1_prepp_shift1.pdf | P2_patch3 |  |  |  |  |  |  |
| 2022_tier2_prepp_paper1.pdf | P1 |  |  |  |  |  |  |
| 2022_tier2_prepp_paper1.pdf | P2 |  |  |  |  |  |  |
| 2022_tier2_prepp_paper1.pdf | P2_patch1 | 81 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2022_tier2_prepp_paper1.pdf | P2_patch3 | 150 | None | BLOCKED | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2023_tier1_prepp_shift1.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2023_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2023_tier1_prepp_shift1.pdf | P2_patch1 | 0 | 100 | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2023_tier1_prepp_shift1.pdf | P2_patch3 | 100 | 100 | BLOCKED | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2023_tier2_prepp_paper1.pdf | P1 |  |  |  |  |  |  |
| 2023_tier2_prepp_paper1.pdf | P2 |  |  |  |  |  |  |
| 2023_tier2_prepp_paper1.pdf | P2_patch1 | 0 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2023_tier2_prepp_paper1.pdf | P2_patch3 | 150 | None | BLOCKED | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier1_appx_answer_key.pdf | P1 |  |  |  |  |  |  |
| 2024_tier1_appx_answer_key.pdf | P2 |  |  |  |  |  |  |
| 2024_tier1_appx_answer_key.pdf | P2_patch1 | 0 | 100 | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier1_appx_answer_key.pdf | P2_patch3 |  |  |  |  |  |  |
| 2024_tier1_prepp_shift1.pdf | P1 |  |  |  |  |  |  |
| 2024_tier1_prepp_shift1.pdf | P2 |  |  |  |  |  |  |
| 2024_tier1_prepp_shift1.pdf | P2_patch1 | 3 | 100 | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier1_prepp_shift1.pdf | P2_patch3 | 94 | 100 | FAIL | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | P1 | 100 | 100 | PASS_WITH_MANUAL_REVIEW | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | P2 |  |  |  |  |  |  |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | P2_patch1 | 0 | 100 | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier1_sscportal_sep09_shift1_response_sheet.pdf | P2_patch3 | 100 | 100 | BLOCKED | PASS |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier2_prepp_paper1.pdf | P1 |  |  |  |  |  |  |
| 2024_tier2_prepp_paper1.pdf | P2 |  |  |  |  |  |  |
| 2024_tier2_prepp_paper1.pdf | P2_patch1 | 7 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier2_prepp_paper1.pdf | P2_patch3 | 141 | 150 | FAIL | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | P1 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | P2 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | P2_patch1 | 0 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier2_sscportal_jan18_response_sheet.pdf | P2_patch3 | 150 | 100 | FAIL | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | P1 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | P2 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | P2_patch1 | 0 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier2_sscportal_jan19_response_sheet.pdf | P2_patch3 | 97 | 100 | INFRA_FAILURE | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | P1 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | P2 |  |  |  |  |  |  |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | P2_patch1 | 9 | None | FAIL | FAIL | api_quota_or_rate_limit | google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata |
| 2024_tier2_sscportal_jan20_response_sheet.pdf | P2_patch3 | 150 | 100 | FAIL | FAIL |  | google_ai_studio / models/gemini-3.1-flash-lite; Gemini retry of NIM-failed PDFs |
