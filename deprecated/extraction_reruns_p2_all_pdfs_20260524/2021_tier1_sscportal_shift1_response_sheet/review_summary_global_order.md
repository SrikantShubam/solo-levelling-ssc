# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2021_tier1_sscportal_shift1_response_sheet.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: PASS_WITH_MANUAL_REVIEW
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [18, 26, 29, 31, 34, 35, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 50, 79, 94, 98]
- Low-confidence global questions: []
- Manual review count: 21
- Canonical review count: 21

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [18, 26, 29, 31, 34, 35, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 50, 79, 94, 98] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 21 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 3 |
| 2 | 3 |
| 3 | 1 |
| 4 | 2 |
| 5 | 3 |
| 6 | 4 |
| 7 | 3 |
| 8 | 2 |
| 9 | 0 |
| 10 | 4 |
| 11 | 4 |
| 12 | 5 |
| 13 | 4 |
| 14 | 5 |
| 15 | 4 |
| 16 | 4 |
| 17 | 4 |
| 18 | 3 |
| 19 | 4 |
| 20 | 0 |
| 21 | 3 |
| 22 | 4 |
| 23 | 3 |
| 24 | 3 |
| 25 | 4 |
| 26 | 4 |
| 27 | 4 |
| 28 | 4 |
| 29 | 4 |
| 30 | 2 |
| 31 | 2 |
| 32 | 1 |
| 33 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 3: NCOESMH | 3 | high | False | In a certain language, CHHAPAK is coded as DJKEUGR. How will MALANGA be coded in that language? |
| 2 | 2 | 1 | 3: Hatim | 3 | high | False | Amit, Gaurav, Hatim, Varun, Yukti and Zaid are sitting in a straight line, all facing the north. Gaurav is fourth to the left of A |
| 3 | 3 | 1 | 2: +, ÷, ×, −, = | 2 | high | False | Select the correct combination of mathematical signs that can sequentially replace the * signs and balance the given equation. 60  |
| 4 | 4 | 2 | 3: 73 | 3 | high | False | Select the number from among the given options that can replace the question mark (?) in the following series. 237, 196, 155, 114, |
| 5 | 5 | 2 | 1: L, X, V, X, V, Z, C, Z, X, C | 1 | high | False | Select the combination of letters that when sequentially placed in the blanks of the given series will complete the series. _ Z _  |
| 6 | 6 | 2 | 3: 63 | 3 | high | False | If '@' means 'addition', '%' means 'multiplication', '$' means 'division' and '#' means 'subtraction', then find the value of the  |
| 7 | 7 | 3 | 1: Figure 1 | 1 | high | False | Select the option in which the given figure is embedded (rotation is NOT allowed). |
| 8 | 8 | 4 | 4: Figure 4 | 4 | high | False | The sequence of folding a piece of paper and the manner in which the folded paper has been cut is shown in the following figures.  |
| 9 | 9 | 4 | 1: Only conclusion II follows. | 1 | high | False | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 10 | 10 | 5 | 4: Figure 4 | 4 | high | False | Select the correct water image of the given combination of letters. D F N Z S R |
| 11 | 11 | 5 | 3: 3, 1, 5, 4, 2 | 3 | high | False | Select the correct option that indicates the arrangement of the given words in the order in which they appear in an English dictio |
| 12 | 12 | 5 | 1: ZLRQGV | 1 | high | False | Select the option that is related to the third term in the same way as the second term is related to the first term. BACTERIA : EX |
| 13 | 13 | 6 | 1: 21 | 1 | high | False | Study the given pattern carefully and select the number from among the given options that can replace the question mark (?) in it. |
| 14 | 14 | 6 | 4: LGV | 4 | high | False | Select the letter-cluster from among the given options that can replace the question mark (?) in the following series. TSF, RPJ, P |
| 15 | 15 | 6 | 3: 1512021921 | 3 | high | False | In a certain code language, ‘CROWD’ is coded as 23415924 and ‘TRHICK’ is coded as 162491997. How will ‘FRUGAL’ be coded in that la |
| 16 | 16 | 6 | 4: Father | 4 | high | False | Saloni is the daughter of the only son of Kartik. Nirupama is the mother of Deepak. Yamini’s only son, Ankit, is married to Nirupa |
| 17 | 17 | 7 | 4: @ | 4 | high | False | Six letters and symbols, H, h, I, @, % and S, are written on the different faces of a dice. Two positions of this dice are shown.  |
| 18 | 18 | 7 | 1: 736 | None | high | True | Select the option that is related to the third number in the same way as the second number is related to the first number. 223 : 3 |
| 19 | 19 | 7 | 4: GTQ | 4 | high | False | Four letter-clusters have been given, out of which three are alike in some manner and one is different. Select the letter-cluster  |
| 20 | 20 | 8 | 1: Figure 1 | 1 | high | False | Select the figure from among the given options that can replace the question mark (?) in the following series. |
| 21 | 21 | 8 | 2: 6246 | 2 | high | False | In a certain code language, 6219 means ‘Sachin is a cricketer’ and 2646 means ‘He played from Mumbai’. Which of the following is t |
| 22 | 22 | 10 | 2: Grandfathers, Fathers, Males | 2 | high | False | Select the set of classes the relationship among which is best illustrated by the following Venn diagram. [Figure: Concentric circ |
| 23 | 23 | 10 | 1: 22 m, North | 1 | high | False | Gaurav exits from the backdoor of his north-facing house and walks 25 m straight, then he takes a left turn and walks 36 m, then h |
| 24 | 24 | 10 | 2: ₹138 | 2 | high | False | Mohit and Sudesh bought pens and notebooks from the same shop. Mohit bought 3 pens and 6 notebooks by paying an amount of ₹180. Su |
| 25 | 25 | 10 | 3: 1110 | 3 | high | False | Select the number from among the given options that can replace the question mark (?) in the following series. 5, 18, 70, 278, ? |
| 26 | 1 | 11 | 1: All observable characteristics | None | high | True | The numerical taxonomy of plants is based on which of the following? |
| 27 | 2 | 11 | 2: 26th January 1950 | 2 | high | False | On which day was the National Emblem of India adopted? |
| 28 | 3 | 11 | 2: Tirath Singh Rawat | 2 | high | False | Who among the following became the Chief Minister of Uttarakhand in March 2021? |
| 29 | 4 | 11 | 4: 137% | None | high | True | The allocation towards health and well-being was increased by ______ over the previous year in Union Budget 2021-22. |
| 30 | 5 | 12 | 1: Sri Aurobindo | 3 | high | False | Who among the following is the author of the book ‘The Secret of the Veda’? |
| 31 | 6 | 12 | 2: roots | None | high | True | Pneumatophores are specialised ______ in hydrophytes. |
| 32 | 7 | 12 | 1: 22 March | 1 | high | False | Which of the following days is celebrated as ‘World Water Day’? |
| 33 | 8 | 12 | 3: Prithviraj Chauhan | 3 | high | False | Who among the following Rajput rulers defeated Muhammad Ghori in the First Battle of Tarain in 1191 AD? |
| 34 | 9 | 12 | 1: 1998 | None | high | True | In which year was the ‘Lotteries Regulation Act’ passed? |
| 35 | 10 | 13 | 1: large, narrow-mouthed earthenware pot used as | None | high | True | A Ghatam is a ______. |
| 36 | 11 | 13 | 1: Goods and Services Tax | 1 | high | False | Which of the following is an Indirect Tax in India? |
| 37 | 12 | 13 | 1: Ossuary Feast | None | high | True | Tribes of the Nicobar Islands pay their respects to the departed soul of the head of the family during the ______. |
| 38 | 13 | 13 | 2: I, II and III | None | high | True | Which of the following statements is/are correct? I.Only marketed goods are considered while estimating Gross Domestic Product (GD |
| 39 | 14 | 14 | 1: Tamralipti | None | high | True | _______ was an important port city in ancient India. |
| 40 | 15 | 14 | 1: Abatement | None | high | True | _______ is reducing the degree or intensity of, or eliminating, pollution. |
| 41 | 16 | 14 | 4: Mumbai City FC | None | high | True | Which of the following teams won the Indian Super League 2020-21? |
| 42 | 17 | 14 | 1: ATK Mohun Bagan | None | high | True | The former Spanish footballer, Antonio Lopez Habas, was the coach at the Hero ISL 2020-21 of which of the following football teams |
| 43 | 18 | 14 | 3: Dhaulagiri I | None | high | True | Which of the following is also known as the ‘White Mountain’? |
| 44 | 19 | 15 | 4: Pacific | 4 | high | False | With which of the following oceans would you associate the ‘Ring of Fire’? |
| 45 | 20 | 15 | 2: Eighty-Sixth Amendment Act, 2002 | None | high | True | Which of the following Amendments of the Constitution of India added a new fundamental duty under Article 51-A? |
| 46 | 21 | 15 | 1: Restore our Earth | None | high | True | The theme for International Mother Earth Day, 2021 was ‘______’. |
| 47 | 22 | 15 | 3: Bihar | None | high | True | In which of the following states/union territories was an election NOT held during March-April 2021? |
| 48 | 23 | 16 | 1: 1761 | None | high | True | The British East India Company captured Pondicherry (Puducherry) from the French in the year _______. |
| 49 | 24 | 16 | 3: 2nd February | 3 | high | False | According to Ramsar Convention, which of the following is World Wetlands Day? |
| 50 | 25 | 16 | 2: a half | None | high | True | At least _______ of the carbon dioxide fixation on earth is carried out by algae through photosynthesis. |
| 51 | 1 | 16 | 1: 5,000 | 1 | high | False | A sold a mobile phone to B at a gain of 25% and B sold it to C at a loss of 10%. If C paid ₹5,625 for it, how much did A pay (in ₹ |
| 52 | 2 | 17 | 1: 3 | 1 | high | False | The value of (sin23°cos67° + sec52°sin38° + cos23°sin67° + cosec52°cos38°) / (cosec²20° - tan²70°) is: |
| 53 | 3 | 17 | 2: 3 h 10 m | 2 | high | False | A motorboat whose speed is 20 km/h in still water takes 30 minutes more to go 24 km upstream than to cover the same distance downs |
| 54 | 4 | 17 | 3: 28° | 3 | high | False | AB is a diameter of a circle with centre O. A tangent is drawn at point A. C is a point on the circle such that BC produced meets  |
| 55 | 5 | 17 | 2: 9 | 2 | high | False | A can finish a piece of the work in 16 days and B can finish it in 12 days. They worked together for 4 days and then A left. B fin |
| 56 | 6 | 18 | 4: 4 | 4 | high | False | A solid cube of side 8 cm is dropped into a rectangular container of length 16 cm, breadth 8 cm and height 15 cm which is partly f |
| 57 | 7 | 18 | 2: 224 | 2 | high | False | If (x + 6y) = 8, and xy = 2, where x > 0, what is the value of (x³ + 216y³)? |
| 58 | 8 | 18 | 2: 5 : 6 | 2 | high | False | The following bar graph shows exports of cars of type A and B (in ₹ millions) from 2014 to 2018. What is the ratio of the total ex |
| 59 | 9 | 19 | 2: 30 | 2 | high | False | In a Δ ABC, points P, Q and R are taken on AB, BC and CA, respectively, such that BQ = PQ and QC = QR. If ∠BAC = 75°, what is the  |
| 60 | 10 | 19 | 1: 3√15 - 4 | 1 | high | False | If 4sin² θ = 3(1 + cosθ), 0° < θ < 90°, then what is the value of (2tanθ + 4sinθ − secθ)? |
| 61 | 11 | 19 | 2: 10 | 2 | high | False | The lengths of the three sides of a right-angled triangle are (x – 1) cm, (x + 1) cm and (x + 3) cm, respectively. The hypotenuse  |
| 62 | 12 | 19 | 1: 20,000 | 1 | high | False | A certain sum is deposited for 4 years at a rate of 10% per annum on compound interest compounded annually. The difference between |
| 63 | 13 | 21 | 2: 40 | 2 | high | False | An item costs ₹400. During a festival sale, a company offers a sale discount that offers x% off on its regular price along with a  |
| 64 | 14 | 21 | 1: 5 : 6 | 1 | high | False | The number of cars passing the road near a colony from 6 am to 12 noon has been shown in the following histogram. What is the rati |
| 65 | 15 | 21 | 4: 50% | 4 | high | False | Monthly expenditure of a family on different heads is shown in the following pie chart. The amount spent on Children Education, Tr |
| 66 | 16 | 22 | 2: 239685 | 2 | high | False | Find the greatest number 23a68b, which is divisible by 3 but NOT divisible by 9. |
| 67 | 17 | 22 | 3: 20° | 4 | high | False | An equilateral triangle ABC is inscribed in a circle with centre O. D is a point on the minor arc BC and ∠CBD = 40°. Find the meas |
| 68 | 18 | 22 | 3: 4,000 | 3 | high | False | The ratio of the monthly incomes of A and B is 11 : 13 and the ratio of their expenditures is 9 : 11. If both of them manage to sa |
| 69 | 19 | 22 | 2: 58 | 2 | high | False | The average weight of P and his three friends is 55 kg. If P is 4 kg more than the average weight of his three friends, what is P' |
| 70 | 20 | 23 | 1: -18 | 1 | high | False | If x + y + 3 = 0, then find the value of x³ + y³ - 9xy + 9. |
| 71 | 21 | 23 | 1: 110 : 137 | 1 | high | False | The given histogram represents the marks of students in Mathematics test of a certain class. The total number of students is 350.  |
| 72 | 22 | 23 | 3: 52√3 | 3 | high | False | The angle of elevation of the top of an unfinished tower at a point distant 78 m from its base is 30°. How much higher must the to |
| 73 | 23 | 24 | 3: 43 1/2 | 3 | high | False | Find the value of the following expression: 372 ÷ 56 × 7 - 5 + 2 |
| 74 | 24 | 24 | 4: 210 | 4 | high | False | LCM of two numbers is 56 times their HCF, with the sum of their HCF and LCM being 1710. If one of the two numbers is 240, then wha |
| 75 | 25 | 24 | 3: 500 | 3 | high | False | Some students (only boys and girls) from different schools appeared for an Olympiad exam. 20% of the boys and 15% of the girls fai |
| 76 | 1 | 25 | 4: All tasks are handled efficiently by her. | 4 | high | False | Select the option that expresses the given sentence in passive voice. She handles all tasks efficiently. |
| 77 | 2 | 25 | 2: They surrendered all weapons. | 2 | high | False | Select the option that expresses the given sentence in active voice. All weapons were surrendered by them. |
| 78 | 3 | 25 | 2: have assured | 2 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. If there is no need to substi |
| 79 | 4 | 25 | 4: Conceited | None | high | True | Select the most appropriate ANTONYM of the given word. Modest |
| 80 | 5 | 26 | 4: Seismology | 4 | high | False | Select the option that can be used as a one-word substitute for the given group of words. The study of earthquakes |
| 81 | 6 | 26 | 4: no substitution required | 4 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. If there is no need to substitute i |
| 82 | 7 | 26 | 2: Have very little money | 1 | high | False | Select the most appropriate meaning of the given idiom. Be hard up |
| 83 | 8 | 26 | 4: want to | 4 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Every / curious  |
| 84 | 9 | 27 | 1: the very well-directed film | 3 | high | False | The following sentence has been divided into parts. One of them may contain an error. Select the part that contains the error from |
| 85 | 10 | 27 | 1: Tution | 1 | high | False | Select the INCORRECTLY spelt word. |
| 86 | 11 | 27 | 2: He said to me, “When did you book the flight  | 2 | high | False | Select the option that expresses the given sentence in direct speech. He asked me when I had booked the flight tickets. |
| 87 | 12 | 27 | 1: this year it reflect badly | 1 | high | False | The following sentence has been divided into parts. One of them may contain a grammatical error. Select the part that contains the |
| 88 | 13 | 28 | 1: achieving | 1 | high | False | Select the most appropriate option to fill in the blank. The increasing concerns about climate change point to the need for enhanc |
| 89 | 14 | 28 | 1: Amble | 1 | high | False | Select the option that can be used as a one-word substitute for the given group of words. To walk aimlessly |
| 90 | 15 | 28 | 1: showy | 1 | high | False | Select the most appropriate synonym of the given word. ostentatious |
| 91 | 16 | 28 | 2: Say two contradictory things at the same time | 2 | high | False | Select the most appropriate meaning of the given idiom. In the same breath |
| 92 | 17 | 29 | 1: Build | 1 | high | False | Select the most appropriate ANTONYM of the given word. Raze |
| 93 | 18 | 29 | 2: react | 2 | high | False | Select the most appropriate synonym of the given word. Retaliate |
| 94 | 19 | 29 | 4: Prevent | None | high | True | Select the most appropriate synonym of the given word. Avert |
| 95 | 20 | 29 | 1: No one were | 1 | high | False | The following sentence has been split into segments. One of them may contain an error. Identify the segment that contains a gramma |
| 96 | 21 | 30 | 1: population | 1 | high | False | Select the most appropriate option to fill in blank no.1. |
| 97 | 22 | 30 | 2: illegal | 2 | high | False | Select the most appropriate option to fill in blank no.2. |
| 98 | 23 | 31 | 4: encroachment | None | high | True | Select the most appropriate option to fill in blank no.3. |
| 99 | 24 | 31 | 2: Moreover | 4 | high | False | Select the most appropriate option to fill in blank no.4. |
| 100 | 25 | 32 | 1: conducive | 1 | high | False | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
