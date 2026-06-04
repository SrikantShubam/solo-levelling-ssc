# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2020_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [3, 14, 22, 48, 68, 69, 70, 72, 74]
- Low-confidence global questions: []
- Manual review count: 9
- Canonical review count: 44

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [3, 14, 22, 48, 68, 69, 70, 72, 74] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 44 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 2 |
| 3 | 4 |
| 4 | 3 |
| 5 | 2 |
| 6 | 4 |
| 7 | 3 |
| 8 | 4 |
| 9 | 5 |
| 10 | 5 |
| 11 | 5 |
| 12 | 5 |
| 13 | 5 |
| 14 | 3 |
| 15 | 4 |
| 16 | 3 |
| 17 | 4 |
| 18 | 3 |
| 19 | 4 |
| 20 | 4 |
| 21 | 4 |
| 22 | 4 |
| 23 | 4 |
| 24 | 4 |
| 25 | 4 |
| 26 | 3 |
| 27 | 3 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 3: Ducks : Quack | 3 | high | False | Select the option in which the words share the same relationship as that shared by the given pair of words. Horses : Neigh |
| 2 | 2 | 1 | 2: Both conclusions I and III follow | 2 | high | False | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 3 | 3 | 2 |  | None | high | True | Select the figure from among the given options that can replace the question mark (?) in the following series. |
| 4 | 4 | 2 | 2: Figure 2 | 2 | high | False | Select the option figure that is embedded in the given figure (rotation is NOT allowed). |
| 5 | 5 | 3 | 3: & | 3 | high | False | A cube is made by folding the given sheet. In the cube so formed, what would be the symbol on the opposite side of the # symbol? |
| 6 | 6 | 3 | 1: 139 | 1 | high | False | Select the number from among the given options that can replace the question mark (?) in the following series. 24, 35, 51, 73, 102 |
| 7 | 7 | 3 | 3: 112 | 3 | high | False | Select the option that is related to the third number in the same way as the second number is related to the first number. 12 : 60 |
| 8 | 8 | 3 | 4: 5, 2, 1, 6, 4, 3 | 4 | high | False | Select the correct option that indicates the arrangement of the given words in the order in which they appear in an English dictio |
| 9 | 9 | 4 | 4: NJFA | 4 | high | False | Four letter-clusters have been given, out of which three are alike in some manner and one is different. Select the letter-cluster  |
| 10 | 10 | 4 |  | 4 | high | False | P, L, T, B, N and D are six members of a business family. N is the son of B, who is not the mother of N. L is the brother of B. D  |
| 11 | 11 | 4 |  | 1 | high | False | Select the correct combination of mathematical signs that can sequentially replace the * signs and balance the given equation. 42  |
| 12 | 12 | 5 | 4: Figure 4 | 4 | high | False | The sequence of folding a piece of paper and the manner in which the folded paper has been cut is shown in the following figures.  |
| 13 | 13 | 5 | 1: Figure 1 | 1 | high | False | Select the correct mirror image of the given combination when the mirror is placed at 'PQ' as shown. |
| 14 | 14 | 6 |  | None | high | True | Out of the total number of players, 100/3 % are in hotel X and the remaining are in hotel Y. If 20 players from hotel Y are shifte |
| 15 | 15 | 6 |  | 4 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. Depression :  |
| 16 | 16 | 6 |  | 3 | high | False | How many triangles are there in the given figure? |
| 17 | 17 | 6 | 4: XVVU | 4 | high | False | Select the letter-cluster from among the given options that can replace the question mark (?) in the following series. PNNA, RPPE, |
| 18 | 18 | 7 | 1: Figure 1 | 1 | high | False | Select the Venn diagram that best illustrates the relationship among the following classes. Women, Researchers, Introverts |
| 19 | 19 | 7 | 3: 24 | 3 | high | False | Study the given pattern carefully and select the number that can replace the question mark (?) in it. 4 7 6 15 ? 21 44 68 60 |
| 20 | 20 | 7 | 3: 17 : 307 | 3 | high | False | Four number-pairs have been given, out of which three are alike in some manner and one is different. Select the number-pair that i |
| 21 | 21 | 8 |  | 2 | high | False | Select the combination of letters that when sequentially placed in the blanks of the given series will complete the series. L_UA_Z |
| 22 | 22 | 8 |  | None | high | True | In a certain code language, ‘AROUND’ is coded as ‘52182412144’ and ‘FIX’ is coded as ‘63624’. How will ‘PLASTIC’ be coded in that  |
| 23 | 23 | 8 |  | 1 | high | False | Select the option in which the numbers are related in the same way as are the numbers of the following set. (25, 18, 225) |
| 24 | 24 | 8 | 3: Weight | 3 | high | False | Four words have been given, out of which three are alike in some manner and one is different. Select the word that is different. |
| 25 | 25 | 9 |  | 1 | high | False | In a certain code language, 'PERMIT' is written as 'VVLNOG'. How will 'INERTIA' be written in that language? |
| 26 | 1 | 9 | 3: He was the founder of Brahmo Samaj. | 3 | high | False | Which of the following statements about Swami Dayanand Saraswati is INCORRECT? |
| 27 | 2 | 9 |  | 3 | high | False | Who among the following is a Padma Vibhushan awardee of 2021? |
| 28 | 3 | 9 |  | 4 | high | False | Who among the following was one of the founders of the Hindustan Republic Association? |
| 29 | 4 | 9 |  | 3 | high | False | In which of the following years was the Second Round Table Conference in London held? |
| 30 | 5 | 10 |  | 2 | high | False | In which of the following years was the Planning Commission of India set up? |
| 31 | 6 | 10 |  | 4 | high | False | As per the Union Budget of 2021-22, how many regional national institutes of virology will be set up? |
| 32 | 7 | 10 |  | 1 | high | False | Electron-volt is a unit of ______. |
| 33 | 8 | 10 | 3: Umesh Sharma | 3 | high | False | Who among the following was elected as the President of Veterinary Council of India in January 2021? |
| 34 | 9 | 10 | 3: Khetri | 3 | high | False | Which of the following places is famous for a copper mine? |
| 35 | 10 | 11 |  | 4 | high | False | ________ is the structural and functional unit of kidney. |
| 36 | 11 | 11 |  | 4 | high | False | Unique Transaction Reference number is a ________ character code used to uniquely identify a transaction in the RTGS system. |
| 37 | 12 | 11 | 4: Sutlej | 4 | high | False | Gurdwara Patalpuri Sahib is located on the bank of river ________. |
| 38 | 13 | 11 |  | 4 | high | False | Who among the following won the ‘3rd Rabindranath Tagore Literary Prize’ for his novel ‘The City and The Sea’ in December 2020? |
| 39 | 14 | 11 | 3: Impulse | 3 | high | False | Which of the following has the same dimension as that of linear momentum? |
| 40 | 15 | 12 |  | 3 | high | False | In December 2020, the Ministry of Home Affairs declared the entire State of ______ as a ‘disturbed area’ for six more months under |
| 41 | 16 | 12 | 4: Royal Challengers Bangalore | 4 | high | False | For which of the following franchise teams did AB de Villiers play in IPL 2020? |
| 42 | 17 | 12 | 4: Nubra | 4 | high | False | In Leh, the first ever ice climbing festival was celebrated in ______ valley in January 2021. |
| 43 | 18 | 12 | 4: Convection | 4 | high | False | Which of the following is a process in which hot, less dense materials rise upward and are replaced by colder, more dense material |
| 44 | 19 | 12 | 4: Meghalaya | 1 | high | False | Baghmara Pitcher Plant Sanctuary is located in which of the following states? |
| 45 | 20 | 13 |  | 3 | high | False | Who among the following replaced Morarji Desai as the Prime Minister of India in 1979? |
| 46 | 21 | 13 |  | 2 | high | False | Which of the following schemes is aimed at helping accelerate the uptake of broadband internet services? |
| 47 | 22 | 13 | 3: Forensic science | 3 | high | False | Which of the following is the application of sciences such as physics, chemistry, biology, computer science and engineering to mat |
| 48 | 23 | 13 |  | None | high | True | Who won the Toyota Thailand Open Women's Singles Title in Bangkok in January 2021? |
| 49 | 24 | 13 | 2: Gopalpur | 2 | high | False | Which of the following is NOT a town/city on the west coast of India? |
| 50 | 25 | 14 | 2: Al-Biruni | 2 | high | False | Who among the following had written Kitab-ul-Hind that gave an incisive description of early 11th Century India? |
| 51 | 1 | 14 |  | 2 | high | False | Study the following table and answer the question: Number of cars sold by dealers A, B, C, D & E during first six months of 2018.  |
| 52 | 2 | 14 | 3: 21/4 | 1 | high | False | Let ΔABC ~ ΔPQR and ar(ΔABC)/ar(ΔPQR) = 144/49. If AB = 12 cm, BC = 7 cm and AC = 9 cm, then PR (in cm) is equal to: |
| 53 | 3 | 15 | 1: (5√3)/3 | 1 | high | False | If (cos^2 θ)/(cot^2 θ + sin^2 θ - 1) = 3, 0° < θ < 90°, then the value of (tan θ + cosec θ) is: |
| 54 | 4 | 15 | 2: 36 | 2 | high | False | If 8(x + y)^3 - 27(x - y)^3 = (5y - x)(Ax^2 + By^2 + Cxy) , then what is the value of (A + B - C)? |
| 55 | 5 | 15 | 3: 19 | 3 | high | False | If x + y = 4 and 1/x + 1/y = 16/15, then what is the value of (x^3 + y^3)? |
| 56 | 6 | 15 | 3: 9.6 cm | 3 | high | False | Δ ABC ~ Δ PQR. The areas of Δ ABC and Δ PQR are 64 cm^2 and 81 cm^2, respectively and AD and PT are the medians of Δ ABC and Δ PQR |
| 57 | 7 | 16 | 4: √46 | 4 | high | False | A chord 21 cm long is drawn in a circle of diameter 25 cm. The perpendicular distance of the chord from the centre is: |
| 58 | 8 | 16 | 2: 391 : 566 | 4 | high | False | Study the table and answer the question. Table shows District-wise data of the number of primary school teachers posted in schools |
| 59 | 9 | 16 | 2: 10 : 3 | 2 | high | False | X, Y are two points in a river. Points P and Q divide the straight line XY into three equal parts. The river flows along XY and th |
| 60 | 10 | 17 | 2: 7 | 2 | high | False | When x is subtracted from each of 19, 28, 55 and 91, the numbers so obtained in this order are in proportion. What is the value of |
| 61 | 11 | 17 | 1: sec² θ + 1 | 1 | high | False | cosec θ / (cosec θ - 1) + cosec θ / (cosec θ + 1) - tan² θ, 0° < θ < 90°, is equal to: |
| 62 | 12 | 17 | 3: 73500 | 3 | high | False | The income of A is 45% more than the income of B and the income of C is 60% less than the sum of the incomes of A and B. The incom |
| 63 | 13 | 17 | 1: 120 | 1 | high | False | Length of each side of a rhombus is 13 cm and one of the diagonal is 24 cm. What is the area (in cm²) of the rhombus? |
| 64 | 14 | 18 | 3: 1014 | 3 | high | False | Study the following table and answer the question: Number of cars sold by dealers A, B, C, D & E during first six months of 2018.  |
| 65 | 15 | 18 | 1: 28° | 1 | high | False | Sides AB and DC of a cyclic quadrilateral ABCD are produced to meet at E and sides AD and BC are produced to meet at F. If ∠ADC =  |
| 66 | 16 | 18 | 4: 2016, 2018 | 4 | high | False | Study the table and answer the question. In the table, production and sale (in 1000 tonnes) of a certain product of a company over |
| 67 | 17 | 19 | 4: 1 | 4 | high | False | Find the value of cot 25° cot 35° cot 45° cot 55° cot 65°. |
| 68 | 18 | 19 | 1: 3 1/8 | None | high | True | Some fruits are bought at 15 for ₹140 and an equal number of fruits at 10 for ₹120. If all the fruits are sold at ₹132 per dozen,  |
| 69 | 19 | 19 | 1: 1634 | None | high | True | What is the compound interest (in ₹) on a sum of ₹8192 for 1 1/4 years at 15% per annum, if interest is compounded 5-monthly? |
| 70 | 20 | 19 | 2: 6 days | None | high | True | To do a certain work, A and B work on alternate days with B beginning the work on the first day. A alone can complete the same wor |
| 71 | 21 | 20 | 3: 724 | 3 | high | False | If x + 1/x = 4, then the value of x^5 + 1/x^5 is: |
| 72 | 22 | 20 | 4: 74.7 | None | high | True | The average of 28 numbers is 77. The average of first 14 numbers is 74 and the average of last 15 numbers is 84. If the 14th numbe |
| 73 | 23 | 20 | 2: 2 | 2 | high | False | The value of 20 ÷ 5 of 8 × [9 ÷ 6 × (6 - 3)] - (10 ÷ 2 of 20) is: |
| 74 | 24 | 20 | 3: 9 | None | high | True | If the 5-digit number 676xy is divisible by 3, 7 and 11, then what is the value of (3x - 5y)? |
| 75 | 25 | 21 | 4: 100 : 121 | 4 | high | False | A shopkeeper earns a profit of 21% after selling a book at 21% discount on the printed price. The ratio of the cost price and sell |
| 76 | 1 | 21 | 4: No substitution | 4 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, sel |
| 77 | 2 | 21 |  | 2 | high | False | Select the option that expresses the given sentence in passive voice. The invigilator is advising the students not to carry calcul |
| 78 | 3 | 21 | 1: Voilence | 4 | high | False | Select the INCORRECTLY spelt word. |
| 79 | 4 | 22 |  | 3 | high | False | Select the option that expresses the given sentence in indirect speech. “Everything is going to be alright,” said the doctor. |
| 80 | 5 | 22 |  | 3 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A herd or flock of animals being driven  |
| 81 | 6 | 22 |  | 2 | high | False | Select the most appropriate ANTONYM of the given word. Gradual |
| 82 | 7 | 22 | 4: procure | 3 | high | False | Select the most appropriate option to fill in the blank. India is formally moving ahead to ________ 21 MIG-29 and 12 Sukhoi-30MKI  |
| 83 | 8 | 23 | 4: we will have | 4 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. Had you / not re |
| 84 | 9 | 23 |  | 4 | high | False | The following sentence has been divided into parts. One of them contains an error. Select the part that contains the error from th |
| 85 | 10 | 23 |  | 2 | high | False | Select the most appropriate meaning of the given idiom. Bang for the buck |
| 86 | 11 | 23 |  | 2 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the right order to form a meaningful and coher |
| 87 | 12 | 24 | 4: To set higher goals | 4 | high | False | Select the most appropriate meaning of the given idiom. Raise the bar |
| 88 | 13 | 24 |  | 2 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A group of three novels or plays, each c |
| 89 | 14 | 24 |  | 3 | high | False | Select the most appropriate option to fill in the blank. Work and domestic _______ made Kajal short-tempered. |
| 90 | 15 | 24 | 4: Rule | 4 | high | False | Select the most appropriate synonym of the given word. Regime |
| 91 | 16 | 25 |  | 3 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the right order to form a meaningful and coher |
| 92 | 17 | 25 |  | 1 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, sel |
| 93 | 18 | 25 | 4: Universal | 4 | high | False | Select the most appropriate synonym of the given word. Generic |
| 94 | 19 | 25 | 4: Pieceful | 4 | high | False | Select the INCORRECTLY spelt word. |
| 95 | 20 | 26 |  | 2 | high | False | Select the most appropriate ANTONYM of the given word. Seize |
| 96 | 21 | 26 |  | 4 | high | False | Select the most appropriate option to fill in blank number 1. |
| 97 | 22 | 26 | 1: between | 1 | high | False | Select the most appropriate option to fill in blank number 2. |
| 98 | 23 | 27 |  | 1 | high | False | Select the most appropriate option to fill in blank number 3. |
| 99 | 24 | 27 |  | 3 | high | False | Select the most appropriate option to fill in blank number 4. |
| 100 | 25 | 27 | 1: soothe | 1 | high | False | Select the most appropriate option to fill in blank number 5. |
