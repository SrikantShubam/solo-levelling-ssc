# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2024_tier1_appx_answer_key.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 38 / 100
- Overall status: FAIL
- Structural QC passed: False
- Load errors: []
- Option/correct-answer issue global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
- Missing/invalid chosen-option global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
- Low-confidence global questions: []
- Manual review count: 38
- Canonical review count: 38

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | FAIL | 38 / 100 |
| Four options and correct answer | FAIL | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38] |
| Chosen answer present/valid | WARN | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 38 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 7 |
| 2 | 7 |
| 3 | 7 |
| 4 | 7 |
| 5 | 7 |
| 6 | 3 |
| 7 | 0 |
| 8 | 0 |
| 9 | 0 |
| 10 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 |  | None | high | True | 1. In the following number-pairs, the second number is obtained by applying certain mathematical operations to the first number. I |
| 2 | 2 | 1 |  | None | high | True | 2. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations shou |
| 3 | 3 | 1 |  | None | high | True | 3. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations should |
| 4 | 4 | 1 |  | None | high | True | 4. Three of the following four options are alike in a certain way and thus form a group. Which is the option that does NOT belong  |
| 5 | 5 | 1 |  | None | high | True | 5. Three of the following number-pairs are alike in some manner and hence form a group. Which number-pair does not belong to that  |
| 6 | 6 | 1 |  | None | high | True | 6. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to  |
| 7 | 7 | 1 |  | None | high | True | 7. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations shou |
| 8 | None | 2 |  | None | high | True | constituent digits. E.g. 13 – Operations on 13 such as adding /deleting /multiplying etc., to 13 can be performed. Breaking down 1 |
| 9 | 8 | 2 |  | None | high | True | 8. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations should |
| 10 | 9 | 2 |  | None | high | True | 9. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations shou |
| 11 | 10 | 2 |  | None | high | True | 10. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to |
| 12 | 11 | 2 |  | None | high | True | 11. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 13 | 12 | 2 |  | None | high | True | 12. Three of the following number-pairs are alike in some manner and hence form a group. Which number-pair does not belong to that |
| 14 | 13 | 2 |  | None | high | True | 13. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 15 | 14 | 3 |  | None | high | True | 14. Three of the following four number-pairs are alike in a certain way and thus form a group. Which number-pair does NOT belong t |
| 16 | 15 | 3 |  | None | high | True | 15. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to |
| 17 | 16 | 3 |  | None | high | True | 16. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to |
| 18 | 17 | 3 |  | None | high | True | 17. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations sho |
| 19 | 18 | 3 |  | None | high | True | 18. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to |
| 20 | 19 | 3 |  | None | high | True | 19. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 21 | 20 | 3 |  | None | high | True | 20. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 22 | None | 4 |  | None | high | True | ...performing mathematical operations on 1 and 3 is not allowed.) (18/09/2024 SHIFT-2) |
| 23 | 21 | 4 |  | None | high | True | 21. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 24 | 22 | 4 |  | None | high | True | 22. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations sho |
| 25 | 23 | 4 |  | None | high | True | 23. The second number in the given number-pairs is obtained by performing certain mathematical operation(s) on the first number. T |
| 26 | 24 | 4 |  | None | high | True | 24. Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to |
| 27 | 25 | 4 |  | None | high | True | 25. Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations shoul |
| 28 | 26 | 4 |  | None | high | True | 26. The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations sho |
| 29 | None | 5 |  | None | high | True | pair does not belong to that group? (NOTE: Operations should be performed on the whole numbers, without breaking down the numbers  |
| 30 | 28 | 5 |  | None | high | True | Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to tha |
| 31 | 29 | 5 |  | None | high | True | The second number in the given number-pairs is obtained by performing certain mathematical operation(s) on the first number. The s |
| 32 | 30 | 5 |  | None | high | True | Three of the following numbers are alike in a certain way and one is different. Pick the odd one out. (NOTE : Operations should be |
| 33 | 31 | 5 |  | None | high | True | The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations should  |
| 34 | 32 | 5 |  | None | high | True | Three of the following options are alike in a certain way and thus form a group. Which is the one that does NOT belong to that gro |
| 35 | 33 | 5 |  | None | high | True | The same operation(s) are followed in all the given number pairs except one. Find that odd number pair. (NOTE : Operations should  |
| 36 | 34 | 6 |  | None | high | True | Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to tha |
| 37 | 35 | 6 |  | None | high | True | The second number in the given number pairs is obtained by performing certain mathematical operation(s) on the first number. The s |
| 38 | 36 | 6 |  | None | high | True | Three of the following number-pairs are alike in some manner and hence form a group. Which number-pair does not belong to that gro |
