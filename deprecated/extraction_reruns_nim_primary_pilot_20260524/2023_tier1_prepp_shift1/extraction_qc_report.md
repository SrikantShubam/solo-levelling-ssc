# Extraction QC Report

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2023_tier1_prepp_shift1.pdf`
- Overall status: FAIL
- Questions: 19 / 100
- Structural QC passed: False
- Canonical review count: 6

## Modality Counts

| Modality | Count |
|---|---:|
| math_formula | 3 |
| text_only | 13 |
| visual_options | 2 |
| visual_stimulus | 1 |

## Evidence Counts

| Evidence status | Count |
|---|---:|
| PASS_LLM_ONLY | 3 |
| PASS_WITH_EVIDENCE | 12 |
| PASS_WITH_MANUAL_REVIEW | 4 |

## Blocking / Review Reasons

| Global Q | Page | Modality | Evidence | Reasons |
|---:|---:|---|---|---|
| 4 | 3 | math_formula | PASS_WITH_EVIDENCE | malformed_options, chosen_option_missing |
| 5 | 6 | visual_options | PASS_WITH_MANUAL_REVIEW | correct_option_unresolved_or_conflict |
| 9 | 23 | text_only | PASS_WITH_MANUAL_REVIEW | correct_option_unresolved_or_conflict |
| 10 | 23 | text_only | PASS_WITH_MANUAL_REVIEW | correct_option_unresolved_or_conflict |
| 11 | 23 | text_only | PASS_LLM_ONLY | chosen_option_missing |
| 18 | 28 | math_formula | PASS_WITH_MANUAL_REVIEW | correct_option_unresolved_or_conflict |
