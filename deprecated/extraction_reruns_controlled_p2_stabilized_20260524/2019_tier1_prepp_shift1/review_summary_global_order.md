# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2019_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 13 / 100
- Overall status: FAIL
- Structural QC passed: False
- Load errors: [{'page': 3, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 4, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 5, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 6, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 7, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 8, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 9, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 10, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 11, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 12, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 13, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 16, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 17, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 18, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 19, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 20, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 21, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 22, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 23, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 24, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 25, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 26, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 27, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 28, 'warnings': ['ERROR HTTP 400: {"status":400,"title":"Bad Request","detail":"Function id \'3afd112d-ad66-4d29-81b6-e7d6f8225e07\': DEGRADED function cannot be invoked"}'], 'failure_type': 'layout_class_unsupported', 'retryable': False}]
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [8]
- Low-confidence global questions: []
- Manual review count: 1
- Canonical review count: 1

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | FAIL | 24 failures |
| Expected question count | FAIL | 13 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [8] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 1 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 3 |
| 3 | 0 |
| 4 | 0 |
| 5 | 0 |
| 6 | 0 |
| 7 | 0 |
| 8 | 0 |
| 9 | 0 |
| 10 | 0 |
| 11 | 0 |
| 12 | 0 |
| 13 | 0 |
| 14 | 4 |
| 15 | 4 |
| 16 | 0 |
| 17 | 0 |
| 18 | 0 |
| 19 | 0 |
| 20 | 0 |
| 21 | 0 |
| 22 | 0 |
| 23 | 0 |
| 24 | 0 |
| 25 | 0 |
| 26 | 0 |
| 27 | 0 |
| 28 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 4: k, l, k, l, m | 1 | high | False | Select the set of letters that when sequentially placed in the blanks of the given letter series will complete the series. k_lmml_ |
| 2 | 2 | 1 | 4: 3, 1, 5, 2, 4 | 4 | high | False | Arrange the following words in the order in which they appear in an English dictionary. 1. Rightly 2. Rigidly 3. Righteous 4. Rigo |
| 3 | 3 | 2 | 3: Figure 3 | 3 | high | False | Select the figure that can replace the question mark (?) in the following series. |
| 4 | 4 | 2 | 1: 91 | 1 | high | False | Study the given pattern carefully and select the number that can replace the question mark (?) in it. 6 21 14 40 500 ? 8 25 7 |
| 5 | 5 | 2 | 4: Submarine | 1 | high | False | Four words have been given, out of which three are alike in some manner, while one is different. Select the odd word. |
| 6 | 23 | 14 | 1: Shashi Tharoor | 4 | high | False | Name the author who won the Sahitya Akademi Award 2019 for his book - An Era of Darkness: The British Empire in India. |
| 7 | 24 | 14 | 3: Maharashtra | 3 | high | False | Veteran freedom fighter, social reformer and feminist Savithribai Phule hailed from which of the following states of India? |
| 8 | 25 | 14 | 4: Oman | None | high | True | Sultan Qaboos bin Said of ________, the Arab world's longest-serving ruler and with a reputation for quiet diplomacy passed away r |
| 9 | 1 | 14 | 2: 11 | 2 | high | False | The area of Δ ABC is 44 cm². If D is the midpoint of BC and E is the midpoint of AB, then the area (in cm²) of ΔBDE is: |
| 10 | 2 | 15 | 1: 0 | 1 | high | False | If the number 1005x4 is completely divisible by 8, then the smallest integer in place of x will be: |
| 11 | 3 | 15 | 3: 1 : 4 | 3 | high | False | If the base radius of 2 cylinders are in the ratio 3 : 4 and their heights are in the ratio 4 : 9, then the ratio of their volumes |
| 12 | 4 | 15 | 2: 18/11 | 2 | high | False | If x, y, z are three integers such that x + y = 8, y + z = 13 and z + x = 17, then the value of x²/yz is: |
| 13 | 5 | 15 | 2: A | 2 | high | False | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. |
