# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2021_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 91 / 100
- Overall status: FAIL
- Structural QC passed: False
- Load errors: []
- Option/correct-answer issue global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
- Missing/invalid chosen-option global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
- Low-confidence global questions: [5, 10, 11, 58, 64, 67, 87, 91]
- Manual review count: 91
- Canonical review count: 91

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | FAIL | 91 / 100 |
| Four options and correct answer | FAIL | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91] |
| Chosen answer present/valid | WARN | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91] |
| Confidence/manual-review flags | WARN | [5, 10, 11, 58, 64, 67, 87, 91] |
| Canonical review routing | WARN | 91 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 2 |
| 4 | 3 |
| 5 | 2 |
| 6 | 1 |
| 7 | 2 |
| 8 | 1 |
| 9 | 2 |
| 10 | 1 |
| 11 | 3 |
| 12 | 2 |
| 13 | 2 |
| 14 | 1 |
| 15 | 3 |
| 16 | 3 |
| 17 | 2 |
| 18 | 3 |
| 19 | 3 |
| 20 | 2 |
| 21 | 3 |
| 22 | 3 |
| 23 | 3 |
| 24 | 3 |
| 25 | 3 |
| 26 | 3 |
| 27 | 2 |
| 28 | 2 |
| 29 | 2 |
| 30 | 2 |
| 31 | 3 |
| 32 | 1 |
| 33 | 0 |
| 34 | 3 |
| 35 | 2 |
| 36 | 2 |
| 37 | 3 |
| 38 | 3 |
| 39 | 3 |
| 40 | 3 |
| 41 | 1 |
| 42 | 1 |
| 43 | 2 |
| 44 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 3 |  | None | high | True | Select the correct option that indicates the arrangement of the given words in the order in which they appear in an English dictio |
| 2 | 2 | 3 |  | None | medium | True | Six letters and symbols, H, h, I, @, % and $, are written on the different faces of a dice. Two position of this dice are shown. S |
| 3 | 3 | 4 |  | None | high | True | Select the number from among the given options that can replace the question mark (?) in the following series. 5, 18, 70, 278, ? |
| 4 | 4 | 4 |  | None | high | True | Select the option that is related to the third term in the same way as the second term is related to the first term. BACTERIA : EX |
| 5 | 5 | 4 |  | None | low | True | If '@' means 'addition', '%' means 'multiplication', '$' means 'division' and '#' means 'subtraction', then find the value of the  |
| 6 | 6 | 5 |  | None | high | True | Select the number from among the given options that can replace the question mark (?) in the following series. 237, 196, 155, 114, |
| 7 | 7 | 5 |  | None | high | True | In a certain language, CHHAPAK is coded as DJKEUGR. How will MALANGA be coded in that language? |
| 8 | 9 | 6 |  | None | high | True | Select the option in which the given figure is embedded (rotation is NOT allowed). |
| 9 | 10 | 7 |  | None | medium | True | The sequence of folding of paper and the manner in which the folded paper has been cut is shown in the following figures. How woul |
| 10 | 11 | 7 |  | None | low | True | Study the given pattern carefully and select the number from among the given options that can replace the question mark (?) in it. |
| 11 | 12 | 8 |  | None | low | True | Select the figure from among the given options that can replace the question mark (?) in the following series. |
| 12 | 13 | 9 |  | None | high | True | Four letter-clusters have been given, out of which three are alike in some manner and one is different. Select the letter-cluster  |
| 13 | 14 | 9 |  | None | high | True | Mohit and Sudesh bought pens and notebooks from the same shop. Mohit bought 3 pens and 6 notebooks by paying an amount of Rs. 180. |
| 14 | 16 | 10 |  | None | high | True | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 15 | 17 | 11 |  | None | high | True | Saloni is the daughter of the only son of Kartik. Nirupama is the mother of Deepak. Yamini's only son, Ankit, is married to Nirupa |
| 16 | 18 | 11 |  | None | high | True | Gaurav exits from the backdoor of his north-facing house and walks 25 m straight, then he takes a left turn and walks 36 m, then h |
| 17 | 19 | 11 |  | None | medium | True | Select the correct water image of the given combination of letters. DFNZSR |
| 18 | 20 | 12 |  | None | high | True | Select the set of classes the relationship among which is best illustrated by the following Venn diagram. [Figure: Concentric circ |
| 19 | 21 | 12 |  | None | high | True | Select the combination of letters that when sequentially placed in the blanks of the given series will complete the series. _ Z _  |
| 20 | 23 | 13 |  | None | high | True | Amit, Gaurav, Hatim, Varun, Yukti and Zaid are sitting in a straight line, all facing the north. Gaurav is fourth to the left of A |
| 21 | 24 | 13 |  | None | high | True | In a certain code language, ‘CROWD’ is coded as 23415924 and ‘TRHICK’ is coded as 162491997. How will ‘FRUGAL’ be coded in that la |
| 22 | 25 | 14 |  | None | high | True | In a certain code language, 6219 means ‘Sachin is a cricketer’ and 2646 means ‘He played from Mumbai’. Which of the following is t |
| 23 | 26 | 15 |  | None | high | True | The British East India Company captured Pondicherry (Puducherry) from the French in the year ______. |
| 24 | 27 | 15 |  | None | high | True | Who among the following Rajput rulers defeated Muhammad Ghori in the First Battle of Tarain in 1191 AD? |
| 25 | 28 | 15 |  | None | high | True | The allocation towards health and well-being was increased by ______ over the previous year in Union Budget 2021-22. |
| 26 | 29 | 16 |  | None | high | True | Which of the following is also known as the ‘White Mountain’? |
| 27 | 30 | 16 |  | None | high | True | Pneumatophores are specialised _______ in hydrophytes. |
| 28 | 31 | 16 |  | None | high | True | Which of the following is an Indirect Tax in India? |
| 29 | 33 | 17 |  | None | high | True | ______ was an important port city in ancient India. |
| 30 | 34 | 17 |  | None | high | True | With which of the following oceans would you associate the ‘Ring of Fire’? |
| 31 | 35 | 18 |  | None | high | True | Who among the following became the Chief Minister of Uttarakhand in March 2021? |
| 32 | 36 | 18 |  | None | high | True | In which of the following states/union territories was an election NOT held during March-April 2021? |
| 33 | 37 | 18 |  | None | high | True | Who among the following is the author of the book ‘The Secret of the Veda’? |
| 34 | 38 | 19 |  | None | high | True | Which of the following teams won the Indian Super League 2020-21? |
| 35 | 39 | 19 |  | None | high | True | The theme for International Mother Earth Day, 2021 was '________'. |
| 36 | 40 | 19 |  | None | high | True | Which of the following Amendments of the Constitution of India added a new fundamental duty under Article 51-A? |
| 37 | 42 | 20 |  | None | high | True | A Ghatam is a ______. |
| 38 | 43 | 20 |  | None | high | True | Tribes of the Nicobar Islands pay their respects to the departed soul of the head of the family during the ________. |
| 39 | 45 | 21 |  | None | high | True | In which year was the ‘Lotteries Regulation Act’ passed? |
| 40 | 46 | 21 |  | None | high | True | The numerical taxonomy of plants is based on which of the following? |
| 41 | 47 | 21 |  | None | medium | True | According to Ramsar Convention, which of the following is World Wetlands Day? |
| 42 | 48 | 22 |  | None | high | True | The former Spanish footballer, Antonio Lopez Habas, was the coach at the Hero ISL 2020-21 of which of the following football teams |
| 43 | 49 | 22 |  | None | high | True | On which day was the National Emblem of India adopted? |
| 44 | 50 | 22 |  | None | high | True | ________ is reducing the degree or intensity of, or eliminating, pollution. |
| 45 | 51 | 23 |  | None | high | True | The average weight of P and his three friends is 55 kg. If P is 4 kg more than the average weight of his three friends, what is P' |
| 46 | 52 | 23 |  | None | high | True | A sold a mobile phone to B at a gain of 25% and B sold it to C at a loss of 10%. If C paid Rs. 5,625 for it, how much did A pay (i |
| 47 | 53 | 23 |  | None | high | True | The angle of elevation of the top of an unfinished tower at a point distant 78 m from its base is 30°. How much higher must the to |
| 48 | 54 | 24 |  | None | high | True | A motorboat whose speed is 20 km/h in still water takes 30 minutes more to go 24 km upstream than to cover the same distance downs |
| 49 | 55 | 24 |  | None | high | True | If 4sin 2 θ = 3(1+ cos θ), 0° < θ < 90°, then what is the value of (2tan θ + 4sin θ - sec θ)? |
| 50 | 56 | 24 |  | None | high | True | Find the greatest number 23a68b, which is divisible by 3 but NOT divisible by 9. |
| 51 | 57 | 25 |  | None | high | True | Some students (only boys and girls) from different schools appeared for an Olympiad exam. 20% of the boys and 15% of the girls fai |
| 52 | 58 | 25 |  | None | high | True | If (x + 6y) = 8, and xy = 2, where x > 0, what is the value of (x 3+ 216y 3)? |
| 53 | 59 | 25 |  | None | high | True | In a ΔABC, points P, Q and R are taken on AB, BC and CA, respectively, such that BQ = PQ and QC = QR. If ∠BAC = 75°, what is the m |
| 54 | 60 | 26 |  | None | high | True | A can finish a piece of the work in 16 days and B can finish it in 12 days. They worked together for 4 days and then A left. B fin |
| 55 | 61 | 26 |  | None | high | True | The value of: sin 23° cos 67° + sec 52° sin 38° + cos 23° sin 67° + cosec 52° cos 38° / cosec² 20° - tan² 70° |
| 56 | 62 | 26 |  | None | medium | True | LCM of two numbers is 56 times their HCF, with the sum of their HCF and LCM being 1710. If one of the two numbers is 240, then wha |
| 57 | 63 | 27 |  | None | high | True | The following bar graph shows exports of cars of type A and B (in Rs. millions) from 2014 to 2018. What is the ratio of the total  |
| 58 | 64 | 27 |  | None | low | True | A certain sum is deposited for 4 years at a rate of 10% per annum on compound interest compounded annually. The difference between |
| 59 | 65 | 28 |  | None | high | True | An equilateral triangle ABC is inscribed in a circle with centre O. D is a point on the minor arc BC and ∠CBD = 40°. Find the meas |
| 60 | 66 | 28 |  | None | high | True | The lengths of the three sides of a right-angled triangle are (x - 1) cm, (x + 1) cm and (x + 3) cm, respectively. The hypotenuse  |
| 61 | None | 29 |  | None | high | True | What is the ratio of the total number of students who scored 140 marks and above to the total number of students who scored marks  |
| 62 | 68 | 29 |  | None | medium | True | The ratio of the monthly incomes of A and B is 11 : 13 and the ratio of their expenditures is 9 : 11. If both of them manage to sa |
| 63 | 69 | 30 |  | None | high | True | A solid cube of side 8 cm is dropped into a rectangular container of length 16 cm, breadth 8 cm and height 15 cm which is partly f |
| 64 | 70 | 30 |  | None | low | True | The number of cars passing the road near a colony from 6 am to 12 noon has been shown in the following histogram. What is the rati |
| 65 | 71 | 31 |  | None | high | True | An item costs Rs. 400. During a festival sale, a company offers a sale discount that offers x% off on its regular price along with |
| 66 | 72 | 31 |  | None | high | True | If x + y + 3 = 0, then find the value of x³ + y³ - 9xy + 9. |
| 67 | 73 | 31 |  | None | low | True | AB is a diameter of a circle with centre O. A tangent is drawn at point A. C is a point on the circle such that BC produced meets  |
| 68 | 74 | 32 |  | None | high | True | Monthly expenditure of a family on different heads is shown in the following pie chart. The amount spent on Children Education, Tr |
| 69 | 76 | 34 |  | None | high | True | Select the most appropriate meaning of the given idiom. Be hard up |
| 70 | 77 | 34 |  | None | high | True | The following sentence has been divided into parts. One of them may contain an error. Select the part that contains the error from |
| 71 | 78 | 34 |  | None | medium | True | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Every / curious  |
| 72 | 79 | 35 |  | None | high | True | Select the most appropriate synonym of the given word. Avert |
| 73 | 80 | 35 |  | None | high | True | Select the option that expresses the given sentence in direct speech. He asked me when I had booked the flight tickets. |
| 74 | 82 | 36 |  | None | high | True | The following sentence has been divided into parts. One of them may contain a grammatical error. Select the part that contains the |
| 75 | 83 | 36 |  | None | high | True | The following sentence has been split into segments. One of them may contain an error. Identify the segment that contains a gramma |
| 76 | 84 | 37 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. The study of earthquakes |
| 77 | 85 | 37 |  | None | high | True | Select the most appropriate option to fill in the blank. The increasing concerns about climate change point to the need for enhanc |
| 78 | 86 | 37 |  | None | high | True | Select the INCORRECTLY spelt word. |
| 79 | 87 | 38 |  | None | high | True | Select the most appropriate ANTONYM of the given word. Raze |
| 80 | 88 | 38 |  | None | high | True | Select the most appropriate synonym of the given word. Retaliate |
| 81 | 89 | 38 |  | None | medium | True | Select the option that can be used as a one-word substitute for the given group of words. To walk aimlessly |
| 82 | 90 | 39 |  | None | high | True | Select the option that expresses the given sentence in passive voice. She handles all tasks efficiently. |
| 83 | 91 | 39 |  | None | high | True | Select the most appropriate ANTONYM of the given word. Modest |
| 84 | 92 | 39 |  | None | medium | True | Select the most appropriate meaning of the given idiom. In the same breath |
| 85 | 93 | 40 |  | None | high | True | Select the most appropriate synonym of the given word. ostentatious |
| 86 | 94 | 40 |  | None | high | True | Select the option that expresses the given sentence in active voice. All weapons were surrendered by them. |
| 87 | 95 | 40 |  | None | low | True | Select the most appropriate option to substitute the underlined segment in the given sentence. If there is no need to substitute i |
| 88 | 96 | 41 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 89 | 98 | 42 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 90 | 99 | 43 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 91 | 100 | 43 |  | None | low | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
