# Human Review Showcase: 2019 Tier-1 Shift 1

- Source: `C:\experiments\ssc\answer_key_candidates_staging\2019_tier1_prepp_shift1.pdf`
- Questions extracted: 100 / 100
- Structural QC: True
- Precision QC status: BLOCKED
- Blocking review count: 2
- Canonical review count: 19
- Missing chosen-option questions: [17, 29, 32, 40, 41, 42, 43, 50, 62, 65, 67, 68, 69, 70, 72, 74, 100]

## Blocking Human Review Rows

| Q | Raw Gemini correct | Deterministic | Reasons | Question crop |
|---:|---|---|---|---|
| 13 | 4 | AMBIGUOUS | correct_option_unresolved_or_conflict | `C:\experiments\ssc\extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\assets\question_crops\2019_tier1_prepp_shift1_p05_q013_question.png` |
| 21 | 4 | AMBIGUOUS | correct_option_unresolved_or_conflict | `C:\experiments\ssc\extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\assets\question_crops\2019_tier1_prepp_shift1_p07_q021_question.png` |

## Evidence Counts

| Evidence status | Count |
|---|---:|
| PASS_WITH_EVIDENCE | 98 |
| PASS_WITH_MANUAL_REVIEW | 2 |

## Correct-Answer Evidence Sources

| Source | Count |
|---|---:|
| ambiguous_rgb_hsv_option_crop | 2 |
| rgb_hsv_option_crop | 98 |

## Modality Counts

| Modality | Count |
|---|---:|
| dice | 2 |
| math_formula | 22 |
| table_di | 7 |
| text_only | 63 |
| visual_options | 5 |
| visual_stimulus | 1 |

## Manual Review Entry Points

- Main JSON: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\merged_questions_global_order.json`
- QC report: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\extraction_qc_report.md`
- Review worklist: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\review_worklist.md`
- Page images: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\page_images`
- Question/option crops: `extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\assets\question_crops`
