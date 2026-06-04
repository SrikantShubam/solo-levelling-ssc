# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2023_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 19 / 100
- Overall status: FAIL
- Structural QC passed: False
- Load errors: [{'page': 1, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 2, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 4, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 5, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 8, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 9, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 10, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 11, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 12, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 13, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 14, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 15, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 16, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 17, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 18, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 19, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 20, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 21, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 22, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 25, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 26, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}, {'page': 27, 'warnings': ['ERROR TimeoutError: The read operation timed out'], 'failure_type': 'layout_class_unsupported', 'retryable': False}]
- Option/correct-answer issue global questions: [4]
- Missing/invalid chosen-option global questions: [4, 11]
- Low-confidence global questions: []
- Manual review count: 2
- Canonical review count: 6

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | FAIL | 22 failures |
| Expected question count | FAIL | 19 / 100 |
| Four options and correct answer | FAIL | [4] |
| Chosen answer present/valid | WARN | [4, 11] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 6 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 4 |
| 4 | 0 |
| 5 | 0 |
| 6 | 1 |
| 7 | 3 |
| 8 | 0 |
| 9 | 0 |
| 10 | 0 |
| 11 | 0 |
| 12 | 0 |
| 13 | 0 |
| 14 | 0 |
| 15 | 0 |
| 16 | 0 |
| 17 | 0 |
| 18 | 0 |
| 19 | 0 |
| 20 | 0 |
| 21 | 0 |
| 22 | 0 |
| 23 | 4 |
| 24 | 5 |
| 25 | 0 |
| 26 | 0 |
| 27 | 0 |
| 28 | 2 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 5 | 3 | 3: Cousin | 1 | high | False | Ganesh was taking a walk with his mother’s brother’s father’s granddaughter. Who was he walking with? |
| 2 | 6 | 3 | 4: T 6 5 2 E K b | 2 | high | False | Select the correct mirror image of the given figure when the mirror is placed at MN as shown below. Te29EKP M ______ N |
| 3 | 7 | 3 | 2: AH | 2 | high | False | Which of the following letter-clusters will replace the question mark (?) in the given series? UV, OY, IB, EE, ? |
| 4 | 8 | 3 | 3: 15 : 9 | None | high | True | The second number in the given number-pairs is obtained by performing certain mathematical operation(s) on the first number. The s |
| 5 | 13 | 6 |  | 2 | high | False | Select the figure from the options that can replace the question mark (?) and complete the given pattern. |
| 6 | 14 | 7 | 1: Figure 1 | 1 | high | False | Select the Venn diagram that best illustrates the relationship between the following classes. Ticket, Aeroplane, Rail |
| 7 | 15 | 7 | 3: HJKP | 3 | high | False | Four letter-clusters have been given, out of which three are alike in some manner and one is different. Select the odd letter-clus |
| 8 | 16 | 7 | 4: 96 | 4 | high | False | Select the option that is related to the fifth number in the same way as the second number is related to the first number and the  |
| 9 | 6 | 23 |  | 4 | high | False | Select the most appropriate ANTONYM of the underlined word in the given sentence. Henry is so servile that other people take advan |
| 10 | 7 | 23 |  | 4 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A thing fit to eat. |
| 11 | 8 | 23 | 3: Not brave | None | high | True | Select the most appropriate meaning of the given idiom. Lily-livered |
| 12 | 9 | 23 | 1: Enthusiastic | 3 | high | False | Select the most appropriate synonym of the given word. Zealous |
| 13 | 10 | 24 | 4: impress | 2 | high | False | Select the most appropriate option that can substitute the underlined word in the given sentence. She had an ability to persuade o |
| 14 | 11 | 24 | 3: instil | 3 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. We must remember that what we |
| 15 | 12 | 24 | 1: Any better choice won’t be received by him th | 1 | high | False | Select the option that expresses the given sentence in passive voice. He won’t receive any better choice than this from anywhere. |
| 16 | 13 | 24 | 3: Weak | 3 | high | False | Select the most appropriate synonym of the given word. Feeble |
| 17 | 14 | 24 | 4: association | 4 | high | False | Select the correct spelling of the underline word. They denied having any association with the terrorists. |
| 18 | 24 | 28 |  | 1 | high | False | Select the most appropriate option to fill in blank no. 4. |
| 19 | 25 | 28 | 4: breaks into | 4 | high | False | Select the most appropriate option to fill in blank no. 5. |
