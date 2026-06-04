# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2020_tier2_kdcampus_answer_key.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 191 / None
- Overall status: INFRA_FAILURE
- Structural QC passed: False
- Load errors: [{'page': 18, 'warnings': ["ERROR RESPONSE: ValueError: Invalid operation: The `response.text` quick accessor requires the response to contain a valid `Part`, but none were returned. The candidate's [finish_reason](https://ai.google.dev/api/generate-content#finishreason) is 4. Meaning that the model was reciting from copyrighted material."], 'failure_type': 'model_refusal', 'retryable': False}]
- Option/correct-answer issue global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191]
- Missing/invalid chosen-option global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191]
- Low-confidence global questions: []
- Manual review count: 191
- Canonical review count: 191

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | FAIL | 1 failures |
| Expected question count | PASS | 191 / None |
| Four options and correct answer | FAIL | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191] |
| Chosen answer present/valid | WARN | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 191 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 9 |
| 2 | 11 |
| 3 | 3 |
| 4 | 2 |
| 5 | 7 |
| 6 | 8 |
| 7 | 2 |
| 8 | 8 |
| 9 | 4 |
| 10 | 7 |
| 11 | 5 |
| 12 | 6 |
| 13 | 6 |
| 14 | 6 |
| 15 | 6 |
| 16 | 6 |
| 17 | 6 |
| 18 | 0 |
| 19 | 6 |
| 20 | 6 |
| 21 | 6 |
| 22 | 6 |
| 23 | 6 |
| 24 | 6 |
| 25 | 7 |
| 26 | 5 |
| 27 | 6 |
| 28 | 6 |
| 29 | 5 |
| 30 | 7 |
| 31 | 6 |
| 32 | 5 |
| 33 | 6 |
| 34 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.1. |
| 2 | 2 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.2. |
| 3 | 3 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.3. |
| 4 | 4 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.4. |
| 5 | 5 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.5. |
| 6 | 6 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.6. |
| 7 | 7 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.7. |
| 8 | 8 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.8. |
| 9 | 9 | 1 |  | None | high | True | Select the most appropriate option to fill in blank no.9. |
| 10 | 10 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.10. |
| 11 | 11 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.1. |
| 12 | 12 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.2. |
| 13 | 13 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.3. |
| 14 | 14 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.4. |
| 15 | 15 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.5. |
| 16 | 16 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.6. |
| 17 | 17 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.7. |
| 18 | 18 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.8. |
| 19 | 19 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.9. |
| 20 | 20 | 2 |  | None | high | True | Select the most appropriate option to fill in blank no.10. |
| 21 | 21 | 3 |  | None | high | True | What do you understand by the term ‘instant coffee attitude’? |
| 22 | 22 | 3 |  | None | high | True | When an activity requires too much effort we feel: |
| 23 | 23 | 3 |  | None | high | True | Why did the young lady approach the piano teacher for music lessons? |
| 24 | 24 | 4 |  | None | high | True | What kind of attitude does the writer advocate for a life of fulfilment? |
| 25 | 25 | 4 |  | None | high | True | What does 'bread making' attitude consist of? |
| 26 | 26 | 5 |  | None | high | True | Which of the following is NOT a key element inherent to any theatre? |
| 27 | 27 | 5 |  | None | high | True | The visually impaired do NOT feel secluded in the Blind Opera group because they can: |
| 28 | 28 | 5 |  | None | high | True | What is the biggest problem in presenting the troupe on stage? |
| 29 | 29 | 5 |  | None | high | True | The members of Blind Opera demonstrate that: |
| 30 | 30 | 5 |  | None | high | True | What is the happy occasion mentioned in the beginning of the passage? |
| 31 | 31 | 5 |  | None | high | True | What is the binding factor for the members of Blind Opera? |
| 32 | 32 | 5 |  | None | high | True | The greater intent behind Blind Opera is to: |
| 33 | 33 | 6 |  | None | high | True | Which of the following statements is FALSE? |
| 34 | 34 | 6 |  | None | high | True | Which of the following statements contradicts the writer's view? |
| 35 | 35 | 6 |  | None | high | True | How do the actors of Blind Opera ascertain they are on stage? |
| 36 | 36 | 6 |  | None | high | True | Select the most appropriate option to fill in blank no.1. |
| 37 | 37 | 6 |  | None | high | True | Select the most appropriate option to fill in blank no.2. |
| 38 | 38 | 6 |  | None | high | True | Select the most appropriate option to fill in blank no.3. |
| 39 | 39 | 6 |  | None | high | True | Select the most appropriate option to fill in blank no.4. |
| 40 | 40 | 6 |  | None | high | True | Select the most appropriate option to fill in blank no.5. |
| 41 | 41 | 7 |  | None | high | True | Traditional ways of recreation, such as puppetry, are dying because: |
| 42 | 42 | 7 |  | None | high | True | Which of the following statements testifies that puppetry was popular in artistic circles? |
| 43 | 43 | 8 |  | None | high | True | The upper limbs of stick puppets are made of: |
| 44 | 44 | 8 |  | None | high | True | Which of the following is NOT a benefit of the art of puppetry? |
| 45 | 45 | 8 |  | None | high | True | Which of the following statements about string puppets is FALSE? |
| 46 | 46 | 8 |  | None | high | True | Where did the art of puppetry first come into being? |
| 47 | 47 | 8 |  | None | high | True | Limbs of the puppets are loosely-jointed: |
| 48 | 48 | 8 |  | None | high | True | The word puppet is derived from the Latin word: |
| 49 | 49 | 8 |  | None | high | True | The above passage is: |
| 50 | 50 | 8 |  | None | high | True | A light source is placed behind the shadow puppets so that: |
| 51 | 51 | 9 |  | None | high | True | In what way does noise become a status symbol? |
| 52 | 52 | 9 |  | None | high | True | According to a survey conducted by AIIMS, noise does NOT cause: |
| 53 | 53 | 9 |  | None | high | True | Noise can be differentiated from other pollutants because: |
| 54 | 54 | 9 |  | None | high | True | Recreational noise is created during: |
| 55 | 55 | 10 |  | None | high | True | Which of the following statements is FALSE? (1) Loudspeakers with low decibel sound can cause palpitations. (2) Several studies ha |
| 56 | 56 | 10 |  | None | high | True | Select the option that expresses the given sentence in direct speech. The teacher ordered the students to go straight to their cla |
| 57 | 57 | 10 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. If you have / re |
| 58 | 58 | 10 |  | None | high | True | Select the option that expresses the given sentence in active voice. Elaborate plans are being made for Aarushi’s destination wedd |
| 59 | 59 | 10 |  | None | high | True | Select the option that expresses the given sentence in active voice. May you be blessed with health and happiness! (1) May health  |
| 60 | 60 | 10 |  | None | high | True | Select the most appropriate synonym of the given word. Judicious |
| 61 | 61 | 10 |  | None | high | True | Select the option that expresses the given sentence in reported speech. She said, “I wish I could fly like a butterfly!” (1) She e |
| 62 | 62 | 11 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 63 | 63 | 11 |  | None | high | True | Select the option that expresses the given sentence in reported speech. She said, “It is my birthday next week.” |
| 64 | 64 | 11 |  | None | high | True | Select the option that expresses the given sentence in direct speech. The commander ordered the soldiers to march ahead and not to |
| 65 | 65 | 11 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 66 | 66 | 11 |  | None | high | True | Select the option that expresses the given sentence in active voice. Walking zones have been demarcated using paints and cones by  |
| 67 | 67 | 12 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The more harder  |
| 68 | 68 | 12 |  | None | high | True | Select the option that expresses the given sentence in direct speech. My sister suggested that we go for a walk in the fresh air. |
| 69 | 69 | 12 |  | None | high | True | Select the option that expresses the given sentence in direct speech. The students asked how they would benefit from online classe |
| 70 | 70 | 12 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 71 | 71 | 12 |  | None | high | True | Select the most appropriate meaning of the given idiom. A square deal |
| 72 | 72 | 12 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. I will spend / m |
| 73 | 73 | 13 |  | None | high | True | Select the most appropriate meaning of the given idiom. To have an axe to grind |
| 74 | 74 | 13 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 75 | 75 | 13 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 76 | 76 | 13 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 77 | 77 | 13 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 78 | 78 | 13 |  | None | high | True | Select the option that expresses the given sentence in passive voice. The commanding officer ordered the troops to march ahead. |
| 79 | 79 | 14 |  | None | high | True | Select the most appropriate meaning of the given idiom. To meet one's Waterloo |
| 80 | 80 | 14 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 81 | 81 | 14 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. An entertainer who performs difficult ph |
| 82 | 82 | 14 |  | None | high | True | Select the most appropriate meaning of the given idiom. To hit below the belt |
| 83 | 83 | 14 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 84 | 84 | 14 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 85 | 85 | 15 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 86 | 86 | 15 |  | None | high | True | Select the option that expresses the given sentence in direct speech. Father told the children that there was some good news for t |
| 87 | 87 | 15 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 88 | 88 | 15 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. Strong dislike between two persons |
| 89 | 89 | 15 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The investigator asked me, “Did you see or hear anything i |
| 90 | 90 | 15 |  | None | high | True | Select the option that expresses the given sentence in direct speech. The little boy asked his teacher if she had always been good |
| 91 | 91 | 16 |  | None | high | True | Select the most appropriate ANTONYM of the given word. Thwart |
| 92 | 92 | 16 |  | None | high | True | Select the option that expresses the given sentence in direct speech. Smriti greeted me and asked me where I was working then. |
| 93 | 93 | 16 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. We yet / have ti |
| 94 | 94 | 16 |  | None | high | True | Select the option that expresses the given sentence in direct speech. Raza requested his parents to forgive him that time and prom |
| 95 | 95 | 16 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 96 | 96 | 16 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 97 | 97 | 17 |  | None | high | True | Select the most appropriate meaning of the given idiom. To turn the corner |
| 98 | 98 | 17 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. This dog seems / |
| 99 | 99 | 17 |  | None | high | True | Select the most appropriate synonym of the given word. Penalise |
| 100 | 100 | 17 |  | None | high | True | Select the option that expresses the given sentence in passive voice. Do not touch any items displayed on glass shelves. |
| 101 | 101 | 17 |  | None | high | True | Select the option that expresses the given sentence in passive voice. People write autobiographies for various reasons. |
| 102 | 102 | 17 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 103 | 110 | 19 |  | None | high | True | Select the option that expresses the given sentence in active voice. Efforts are being made by us to reduce crowding in core city  |
| 104 | 111 | 19 |  | None | high | True | Select the option that expresses the given sentence in passive voice. The audience is applauding the wonderful performance. |
| 105 | 112 | 19 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. This renowned /  |
| 106 | 113 | 19 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The allies / of  |
| 107 | 114 | 19 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Mr. Das, my frie |
| 108 | 115 | 19 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Scarcely had I / |
| 109 | 116 | 20 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. Made of artificial substance or material |
| 110 | 117 | 20 |  | None | high | True | Select the option that expresses the given sentence in active voice. Enough money will have been saved by me for a new house by ne |
| 111 | 118 | 20 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 112 | 119 | 20 |  | None | high | True | Select the option that expresses the given sentence in active voice. All previous ages are far surpassed in knowledge by our age. |
| 113 | 120 | 20 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 114 | 121 | 20 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The strain cause |
| 115 | 122 | 21 |  | None | high | True | Select the option that expresses the given sentence in active voice. Let these ancient texts be preserved for posterity. |
| 116 | 123 | 21 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 117 | 124 | 21 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The girl lay dow |
| 118 | 125 | 21 |  | None | high | True | Select the option that expresses the given sentence in passive voice. Light the lamp of knowledge in every heart. |
| 119 | 126 | 21 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. He went / to the |
| 120 | 127 | 21 |  | None | high | True | Select the option that expresses the given sentence in reported speech. Harry said to me, “Don’t wear this expensive watch to scho |
| 121 | 128 | 22 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The teacher says, “Every action has an equal and opposite  |
| 122 | 129 | 22 |  | None | high | True | Select the segment in which a word has been INCORRECTLY used. The children were so exhausted that they sank warily into bed. |
| 123 | 130 | 22 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 124 | 131 | 22 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 125 | 132 | 22 |  | None | high | True | Select the option that expresses the given sentence in passive voice. You must sign the contract before you start working. |
| 126 | 133 | 22 |  | None | high | True | Select the most appropriate ANTONYM of the given word. Indigenous |
| 127 | 134 | 23 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Have you / ever  |
| 128 | 135 | 23 |  | None | high | True | Select the option that expresses the given sentence in direct speech. Her parents asked her if the match proposed by them would be |
| 129 | 136 | 23 |  | None | high | True | Select the most appropriate option to fill in the blank. The workers ________ against the new labour laws. |
| 130 | 137 | 23 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 131 | 138 | 23 |  | None | high | True | Select the most appropriate meaning of the given idiom. To read between the lines |
| 132 | 139 | 23 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The city turned  |
| 133 | 140 | 24 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 134 | 141 | 24 |  | None | high | True | Select the most appropriate ANTONYM of the given word. Remorse |
| 135 | 142 | 24 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 136 | 143 | 24 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 137 | 144 | 24 |  | None | high | True | Select the option that expresses the given sentence in passive voice. What did you do to help the migrant labourers during the pan |
| 138 | 145 | 24 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. One who possesses several talents |
| 139 | 146 | 25 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. No longer in use |
| 140 | 147 | 25 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 141 | 148 | 25 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 142 | 149 | 25 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. A decision on which one cannot go back |
| 143 | 150 | 25 |  | None | high | True | Select the option that expresses the given sentence in passive voice. I could not use his laptop as it was password protected. |
| 144 | 151 | 25 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Your name / prec |
| 145 | 152 | 25 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 146 | 153 | 26 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 147 | 154 | 26 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The Chief Minister said, “All exams shall be cancelled thi |
| 148 | 155 | 26 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The old man said, “I was walking in my garden at six o’clo |
| 149 | 156 | 26 |  | None | high | True | Select the option that expresses the given sentence in direct speech. The actor said that what he did in films was something he ha |
| 150 | 157 | 26 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 151 | 158 | 27 |  | None | high | True | Select the option that expresses the given sentence in direct speech. My friend asked me where I planned to go for a vacation. |
| 152 | 159 | 27 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. You should / ava |
| 153 | 160 | 27 |  | None | high | True | Select the option that expresses the given sentence in active voice. Absolute liberty is enjoyed by us in matters of food and dres |
| 154 | 161 | 27 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The old man said to her, “Good luck to you! May you succee |
| 155 | 162 | 27 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. The manager / to |
| 156 | 163 | 27 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. Central character in a story or play |
| 157 | 164 | 28 |  | None | high | True | Select the option that expresses the given sentence in reported speech. "Please lend me some money, Raman. I need it urgently," sa |
| 158 | 165 | 28 |  | None | high | True | Select the segment in which a word has been INCORRECTLY used. Is the Abominable Snowman a friction of the mountaineers' imaginatio |
| 159 | 166 | 28 |  | None | high | True | Select the option that expresses the given sentence in reported speech. Harsh said, "How happy I am to receive the best student aw |
| 160 | 167 | 28 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 161 | 168 | 28 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 162 | 169 | 28 |  | None | high | True | Select the most appropriate meaning of the given idiom. Keep your head |
| 163 | 170 | 29 |  | None | high | True | Select the most appropriate meaning of the given idiom. To rise like a phoenix |
| 164 | 171 | 29 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 165 | 172 | 29 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 166 | 173 | 29 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 167 | 174 | 29 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. He was unable /  |
| 168 | 175 | 30 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 169 | 176 | 30 |  | None | high | True | Select the option that will improve the underlined part of the given sentence. In case no improvement is needed, select ‘No improv |
| 170 | 177 | 30 |  | None | high | True | Select the most appropriate option to fill in the blank. The more he tried to solve the mystery, the more ______ he felt. |
| 171 | 178 | 30 |  | None | high | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. He often / persi |
| 172 | 179 | 30 |  | None | high | True | Select the most appropriate option to fill in the blank. He was ______ at his brother’s refusal to help him financially. |
| 173 | 180 | 30 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 174 | 181 | 30 |  | None | medium | True | Select the most appropriate synonym of the given word. Sequestered |
| 175 | 182 | 31 |  | None | high | True | Select the option that expresses the given sentence in passive voice. Give her a 50% raise in salary. |
| 176 | 183 | 31 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 177 | 184 | 31 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The captain announced, "The flight will be delayed due to  |
| 178 | 185 | 31 |  | None | high | True | Select the most appropriate option to fill in the blank. Have you ________________ with the difficulties you might have to face? |
| 179 | 186 | 31 |  | None | high | True | Select the option that expresses the given sentence in reported speech. The children said to the nurse, "Reema slipped and fell fr |
| 180 | 187 | 31 |  | None | high | True | Select the option that expresses the given sentence in passive voice. Have you placed an order for a cake? |
| 181 | 189 | 32 |  | None | high | True | Select the segment in which a word has been INCORRECTLY used. He had an amazing capacity to condone up the most delectable dishes  |
| 182 | 190 | 32 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. To free from restraint |
| 183 | 191 | 32 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. Only on the surface of something |
| 184 | 192 | 32 |  | None | high | True | Select the option that expresses the given sentence in reported speech. She said to her mother, “May I have another slice of cake? |
| 185 | 193 | 32 |  | None | high | True | Select the option that expresses the given sentence in direct speech. Mother said that when we pluck a flower it dies so we should |
| 186 | 195 | 33 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. A long wooden seat with a back for peopl |
| 187 | 196 | 33 |  | None | high | True | Select the most appropriate meaning of the given idiom. Against one's grain |
| 188 | 197 | 33 |  | None | high | True | Select the option that expresses the given sentence in active voice. A defamation case is being filed by him against his business  |
| 189 | 198 | 33 |  | None | high | True | Select the INCORRECTLY spelt word. |
| 190 | 199 | 33 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 191 | 200 | 33 |  | None | high | True | Select the option that expresses the given sentence in active voice. Were you sent summons by the court? |
