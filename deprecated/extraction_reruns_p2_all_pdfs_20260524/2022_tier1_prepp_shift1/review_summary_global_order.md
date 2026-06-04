# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2022_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [8, 19, 26, 35, 43, 44, 46, 47, 49, 53, 57, 58, 61, 64, 68, 69, 71, 73, 99]
- Low-confidence global questions: []
- Manual review count: 19
- Canonical review count: 43

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [8, 19, 26, 35, 43, 44, 46, 47, 49, 53, 57, 58, 61, 64, 68, 69, 71, 73, 99] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 43 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 3 |
| 2 | 3 |
| 3 | 4 |
| 4 | 3 |
| 5 | 2 |
| 6 | 3 |
| 7 | 2 |
| 8 | 4 |
| 9 | 5 |
| 10 | 5 |
| 11 | 5 |
| 12 | 5 |
| 13 | 5 |
| 14 | 5 |
| 15 | 4 |
| 16 | 4 |
| 17 | 3 |
| 18 | 4 |
| 19 | 3 |
| 20 | 3 |
| 21 | 4 |
| 22 | 4 |
| 23 | 4 |
| 24 | 5 |
| 25 | 4 |
| 26 | 2 |
| 27 | 2 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 |  | 2 | high | False | After interchanging the given two numbers and two signs what will be the values of equation (I) and (II) respectively? × and +, 3  |
| 2 | 2 | 1 | 4: CEORSU | 4 | high | False | In a certain code language, 'BEHOLD' is written as 'BDEHLO' and 'INDEED' is written as 'DDEEIN'. How will 'COURSE' be written in t |
| 3 | 3 | 1 | 2: Artefacts | 2 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. (The words mu |
| 4 | 4 | 2 | 3: 182 | 3 | high | False | Which of the following numbers will replace the question mark (?) in the given series? 382, 322, 272, 232, 202, ? |
| 5 | 5 | 2 |  | 2 | high | False | Select the option in which the given figure is embedded (rotation is NOT allowed). |
| 6 | 6 | 2 |  | 2 | high | False | Select the correct combination of mathematical signs to replace the * signs and balance the given equation. 21 * 4 * 156 * 13 * 11 |
| 7 | 7 | 3 | 4: FU | 4 | high | False | Which of the following letter-clusters will replace the question mark (?) in the given series? PK, GT, XC, OL, ? |
| 8 | 8 | 3 |  | None | high | True | Select the set in which the numbers are related in the same way as are the numbers of the following set. (NOTE: Operations should  |
| 9 | 9 | 3 |  | 1 | high | False | Select the correct combination of mathematical signs to sequentially replace the * signs and to balance the given equation. 12 * 2 |
| 10 | 10 | 3 | 3: UVW | 3 | high | False | Three of the following four letter-clusters are alike in a certain way and one is different. Pick the odd one out. |
| 11 | 11 | 4 | 2: View | 2 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. (The words mu |
| 12 | 12 | 4 | 4: Only A | 4 | high | False | Select the cube that can be formed by folding the given sheet along the lines. |
| 13 | 13 | 4 |  | 1 | high | False | Select the correct mirror image of the given combination when the mirror is placed at 'PQ' as shown below. BLZK541M |
| 14 | 14 | 5 |  | 1 | high | False | Select the figure that will replace the question mark (?) in the following figure series. |
| 15 | 15 | 5 | 1: Only conclusion IV follows | 1 | high | False | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 16 | 16 | 6 | 3: 97 | 3 | high | False | In a certain code language, FRUCTUS is coded as 108, and SPRINTER is coded as 119. How will MASCULINE be coded in that language? |
| 17 | 17 | 6 | 2: Both conclusions I and III follows | 2 | high | False | In the following question below are given some statements followed by some conclusions based on those statements. Taking the given |
| 18 | 18 | 6 |  | 2 | high | False | A series is given with one term missing. Select the correct alternative from the given ones that will complete the series. NMRQ, N |
| 19 | 19 | 7 |  | None | high | True | Which figure should replace the question mark (?) if the series were to be continued? 4 B V V T O O 6 6 2 V I 6 4 9 2 T O 4 B 2 B  |
| 20 | 20 | 7 | 2: 64 | 2 | high | False | Select the option that is related to the fifth number in the same way as the second number is related to the first number and the  |
| 21 | 21 | 8 | 1: Population | 1 | high | False | After arranging the given words according to dictionary order, which word will come at ‘Fifth’ position? 1. Popular 2. Population  |
| 22 | 22 | 8 |  | 1 | high | False | Select the set in which the numbers are related in the same way as are the numbers of the following sets. (NOTE : Operations shoul |
| 23 | 23 | 8 | 2: Son-in-law | 2 | high | False | A # B means ‘A is the sister of B’ A @ B means ‘A is the daughter of B’ A & B means ‘A is the husband of B’ A % B means ‘A is the  |
| 24 | 24 | 8 | 2: P – Q + R | 2 | high | False | If A × B means that A is the brother of B, A – B means that A is the sister of B, A + B means that A is the father of B then which |
| 25 | 25 | 9 |  | 1 | high | False | Select the odd group of numbers. (NOTE: Operations should be performed on the whole numbers, without breaking down the numbers int |
| 26 | 1 | 9 | 3: Hockey | None | high | True | The term ‘Back-stick’ is used in which of the following games/sports? |
| 27 | 2 | 9 | 4: Baisakhi | 4 | high | False | Which of the following festivals in Punjab is celebrated to commemorate the formation of the Khalsa Panth? |
| 28 | 3 | 9 | 1: Yoga for the achievement of the Sustainable D | 2 | high | False | What theme was decided to celebrate the second ‘International Day of Yoga’ in India? |
| 29 | 4 | 9 | 1: CaO | 1 | high | False | Chemical formula of quick lime is ________. |
| 30 | 5 | 10 | 4: Joule | 4 | high | False | What is the unit of work done? |
| 31 | 6 | 10 | 1: Vijayawada | 1 | high | False | Which of the following sites do “Not” have nuclear power plant? |
| 32 | 7 | 10 | 3: salvation | 3 | high | False | The Ramakrishna Mission stressed the ideal of __________ through social service and selfless action. |
| 33 | 8 | 10 | 3: 2 October | 3 | high | False | International Non-Violence Day is observed on: |
| 34 | 9 | 10 | 1: Sangama Dynasty | 1 | high | False | Which of the following Dynasties established the kingdom of Vijayanagara? |
| 35 | 10 | 11 | 1: 1981 | None | high | True | When was ‘Vayudoot’ airline setup in India? |
| 36 | 11 | 11 | 2: Erosion | 2 | high | False | Wearing away of landscape by different agents like water, wind and ice is called ________. |
| 37 | 12 | 11 | 1: Nitin Gupta | 1 | high | False | Who has been appointed as the new chairman of the Central Board of Direct Taxes in June 2022? |
| 38 | 13 | 11 | 3: Amjad Ali Khan | 3 | high | False | Who among the following is known as ‘Sarod Samrat’ in Indian Classical Music? |
| 39 | 14 | 11 | 1: Banking method | 1 | high | False | Which of the following is NOT one of the methods of national income estimation? |
| 40 | 15 | 12 | 4: National legislature | 4 | high | False | The term ‘Parliament’ refers to the ____________. |
| 41 | 16 | 12 | 2: Kerala | 4 | high | False | Chief Minister of which state has inaugurated a project of the Women and Child Development department to provide milk and eggs to  |
| 42 | 17 | 12 | 1: Rajasthan | 1 | high | False | A 'Camel Protection and Development Policy' has been announced by the government of ________. |
| 43 | 18 | 12 | 4: Pranab Mukherjee | None | high | True | Who among the following Presidents of India was also the deputy chairman of Planning Commission? |
| 44 | 19 | 12 | 2: convex | None | high | True | In Golgi apparatus, the maturing face is: |
| 45 | 20 | 13 | 4: Brahmo Samaj | 4 | high | False | Raja Ram Mohan Roy founded a reform association known as Brahmo Sabha which was later known as ________. |
| 46 | 21 | 13 | 3: Xylem parenchyma | None | high | True | ________ part of xylem tissue in plants stores food. |
| 47 | 22 | 13 |  | None | high | True | Who among the following composers won the Grammy in 2015 for his album ‘Winds of Samsara’ – a collaboration with South African fla |
| 48 | 23 | 13 | 1: Uttarakhand | 1 | high | False | In which of the following Indian states, Harappan cities have NOT been found? |
| 49 | 24 | 13 | 3: combination reaction | None | high | True | Burning of coal is an example of ________. |
| 50 | 25 | 14 | 1: Right to life and personal liberty | 1 | high | False | The foremost right among rights to freedom is _________. |
| 51 | 1 | 14 |  | 2 | high | False | A dishonest merchant sells goods at a 12.5% loss on the cost price, but uses 28 g weight instead of 36 g. What is his percentage p |
| 52 | 2 | 14 | 3: 90 | 3 | high | False | The HCF of two numbers is 12. Which one of the following can never be their LCM? |
| 53 | 3 | 14 |  | None | high | True | Two circles touch each other externally at P. AB is a direct common tangent to the two circles, A and B are points of contact, and |
| 54 | 4 | 14 | 1: 156 | 1 | high | False | The mean proportion of 169 and 144 is: |
| 55 | 5 | 15 |  | 1 | high | False | The length and breadth of a rectangle are increased by 8% and 5%, respectively. By how much percentage will the area of the rectan |
| 56 | 6 | 15 |  | 4 | high | False | Simplify (cos 45°)/(sec 30° + cosec 30°) |
| 57 | 7 | 15 | 3: 8 | None | high | True | Which of the following numbers is a divisor of (49^15 - 1)? |
| 58 | 8 | 15 |  | None | high | True | In a 1500 m race, Anil beats Bakul by 150 m and in the same race Bakul beats Charles by 75 m. By what distance does Anil beat Char |
| 59 | 9 | 16 | 2: 6.125% | 2 | high | False | ₹2,500, when invested for 8 years at a given rate of simple interest per year, amounted to ₹3,725 on maturity. What was the rate o |
| 60 | 10 | 16 |  | 1 | high | False | The following table shows the number of pages printed by 3 printers during 3 days. Printers / X / Y / Z Days / / / Monday / 130 /  |
| 61 | 11 | 16 | 2: 188 | None | high | True | The batting average for 27 innings of a cricket player is 47 runs. His highest score in an innings exceeds his lowest score by 157 |
| 62 | 12 | 16 | 2: 12 | 2 | high | False | P and Q can complete a project in 15 days and 10 days, respectively. They started doing the work together, but after 2 days, Q had |
| 63 | 13 | 17 |  | 3 | high | False | The pie chart given below shows the number of truck sold by 8 different companies. The total number of truck sold by all these 8 c |
| 64 | 14 | 17 |  | None | high | True | If x^2 - 5x + 1 = 0, then the value of (x^6 + x^4 + x^2 + 1) / 5x^3 = ? |
| 65 | 15 | 17 |  | 2 | high | False | In a right-angled triangle PQR, right-angled at Q, the length of the side PR is 17 units, length of the base QR is 8 units, and le |
| 66 | 16 | 18 |  | 1 | high | False | If (17^3 + 7^3) / (17^2 + 7^2 - k) = 24 , then what is the value of k? |
| 67 | 17 | 18 | 4: 24.5 cm | 2 | high | False | The circumference of the two circles is 198 cm and 352 cm respectively. What is the difference between their radii? |
| 68 | 18 | 18 | 4: 10 cm | None | high | True | Radius of a circle is 10 cm. Angle made by chord AB at the centre of this circle is 60 degree. What is the length of this chord? |
| 69 | 19 | 18 |  | None | high | True | How many spherical lead shots each of diameter 8.4 cm can be obtained from a rectangular solid of lead with dimension 88 cm, 63 cm |
| 70 | 20 | 19 |  | 2 | high | False | The table given below shows the number of spoon manufactured by five factories. Factory / Spoon P / 100 Q / 200 R / 150 S / 50 T / |
| 71 | 21 | 19 |  | None | high | True | In the triangle ABC, AB = 12 cm and AC = 10 cm, and ∠BAC = 60°. What is the value of the length of the side BC? |
| 72 | 22 | 19 |  | 2 | high | False | The value of tan² θ + cot² θ − sec² θ cosec² θ is: |
| 73 | 23 | 20 |  | None | high | True | The following bar graph shows the sales of books (in thousands) from six branches of a publishing company during two consecutive y |
| 74 | 24 | 20 |  | 3 | high | False | If [4(17^3 - 7^3) / (17^2 + 7^2 + p)] = 40, then what is the value of p? |
| 75 | 25 | 20 | 2: ₹48 | 2 | high | False | Riya could not decide between discount of 30% or two successive discounts of 25% and 5%, both given on shopping of ₹3,840. What is |
| 76 | 1 | 21 |  | 4 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 77 | 2 | 21 | 3: She said that she was in no mood to work then | 3 | high | False | Select the correct indirect form of the given sentence. She said, “I am in no mood to work now.” |
| 78 | 3 | 21 | 3: She will be told later by Manu. | 3 | high | False | Select the correct passive form of the given sentence. Manu will tell her later. |
| 79 | 4 | 21 | 3: Have they occupied the villa? | 3 | high | False | Select the correct active form of the given sentence. Has the villa been occupied by them? |
| 80 | 5 | 22 | 2: No error | 4 | high | False | In the given sentence, one word may have been incorrectly spelt. Select the correctly spelt word from the given alternatives. If t |
| 81 | 6 | 22 |  | 1 | high | False | Select the most appropriate ANTONYM of the word ‘SINKS’ from the given sentence. Groups work together to create Christmas parade t |
| 82 | 7 | 22 | 1: equal | 1 | high | False | Select the most appropriate option to fill in the blank. The angles are equal, consequently the sides are ____________. |
| 83 | 8 | 22 | 3: Easy task | 3 | high | False | Select the most appropriate meaning of the given idiom. Like a cakewalk |
| 84 | 9 | 23 | 2: plan to pursue | 2 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. If there is no need to substi |
| 85 | 10 | 23 | 4: Commotion | 4 | high | False | Select the most appropriate synonym of the given word. Confusion |
| 86 | 11 | 23 | 2: have arrived | 2 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. Our guests arrived; they are sittin |
| 87 | 12 | 23 |  | 1 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. During an earthq |
| 88 | 13 | 24 | 2: Hiest | 1 | high | False | Select the INCORRECTLY spelt word. |
| 89 | 14 | 24 | 2: Watching eagerly | 2 | high | False | Select the most appropriate meaning of the given idiom. All eyes |
| 90 | 15 | 24 | 3: looking for his book | 3 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. He was looking into his book  |
| 91 | 16 | 24 | 2: visionary | 2 | high | False | Select the most appropriate collocating word to fill in the blank. Ram was praised for his__________ leadership. |
| 92 | 17 | 24 | 1: cut down | 1 | high | False | Select the most appropriate word segment for the underlined word in the given sentence. Pintu has been advised to reduce smoking b |
| 93 | 18 | 25 |  | 2 | high | False | Select the most appropriate ANTONYM of the given word. Rebellion |
| 94 | 19 | 25 | 3: Coldness | 1 | high | False | Select the most appropriate ANTONYM of the given word. Hospitality |
| 95 | 20 | 25 |  | 3 | high | False | Select the sentence with the appropriate use of adverb of manner. |
| 96 | 21 | 25 | 4: force | 4 | high | False | Select the most appropriate option to fill in blank number 1. |
| 97 | 22 | 26 | 2: embedded | 2 | high | False | Select the most appropriate option to fill in blank number 2. |
| 98 | 23 | 26 | 3: processes | 1 | high | False | Select the most appropriate option to fill in blank number 3. |
| 99 | 24 | 27 | 2: proverbial | None | high | True | Select the most appropriate option to fill in blank number 4. |
| 100 | 25 | 27 | 3: adaptation | 3 | high | False | Select the most appropriate option to fill in blank number 5. |
