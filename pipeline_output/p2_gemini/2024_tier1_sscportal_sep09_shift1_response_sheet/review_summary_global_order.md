# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2024_tier1_sscportal_sep09_shift1_response_sheet.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [2, 29, 31, 33, 34, 36, 37, 38, 39, 41, 44, 49, 74, 89]
- Low-confidence global questions: []
- Manual review count: 14
- Canonical review count: 16

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [2, 29, 31, 33, 34, 36, 37, 38, 39, 41, 44, 49, 74, 89] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 16 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 3 |
| 3 | 3 |
| 4 | 2 |
| 5 | 2 |
| 6 | 0 |
| 7 | 1 |
| 8 | 2 |
| 9 | 2 |
| 10 | 3 |
| 11 | 2 |
| 12 | 3 |
| 13 | 4 |
| 14 | 4 |
| 15 | 4 |
| 16 | 4 |
| 17 | 4 |
| 18 | 4 |
| 19 | 0 |
| 20 | 3 |
| 21 | 3 |
| 22 | 2 |
| 23 | 3 |
| 24 | 3 |
| 25 | 3 |
| 26 | 3 |
| 27 | 3 |
| 28 | 2 |
| 29 | 3 |
| 30 | 3 |
| 31 | 3 |
| 32 | 3 |
| 33 | 3 |
| 34 | 3 |
| 35 | 3 |
| 36 | 2 |
| 37 | 2 |
| 38 | 0 |
| 39 | 1 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 4: 1375 | 4 | high | False | What will come in place of the question mark (?) in the following equation, if '+' and '-' are interchanged and 'x' and '÷' are in |
| 2 | 2 | 1 | 2: 187 | None | high | True | 31 is related to 152 by certain logic. Following the same logic, 47 is related to 168. To which of the following is 66 related, fo |
| 3 | 3 | 2 | 2: T | 2 | high | False | Six letters Q, Z, V, T, L and A are written on different faces of a dice. Two positions of this dice are shown in the figures belo |
| 4 | 4 | 2 | 2: 358 - 152 | 2 | high | False | In the following number-pairs, the second number is obtained by applying certain mathematical operations to the first number. In t |
| 5 | 5 | 2 | 4: MJBO | 4 | high | False | In a certain code language, 'NAME' is written as 'FNBO' and 'NANO' is written as 'POBO'. How will 'NAIL' be written in that langua |
| 6 | 6 | 3 | 2: Hexagon - 8 sides | 2 | high | False | The question contains pairs of words that are related to each other in a certain way. Three of the following four word pairs are a |
| 7 | 7 | 3 | 2: Four | 2 | high | False | The position of how many letters will remain unchanged if each of the letters in the word ‘NIGHTMARES’ is re-arranged in the Engli |
| 8 | 8 | 3 | 2: 33 | 2 | high | False | What will come in the place of ‘?’ in the following equation, if ‘+’ and ‘-‘ are interchanged and ‘x’ and ‘÷’ are interchanged? 5  |
| 9 | 9 | 4 | 2: (153, 217) | 2 | high | False | Select the option in which the numbers share the same relationship as that shared by the given pair of numbers. (149, 213) (168, 2 |
| 10 | 10 | 4 | 2: Figure 2 | 2 | high | False | Select the correct mirror image of the given figure when the mirror is placed at MN as shown below. yTfr93n / N |
| 11 | 11 | 5 | 1: QDS | 1 | high | False | Select the option that is related to the fifth letter-cluster in the same way as the second letter-cluster is related to the first |
| 12 | 12 | 5 | 1: Only I follows | 1 | high | False | Three statements are given followed by three conclusions numbered I, II and III. Assuming the statements to be true, even if they  |
| 13 | 13 | 7 | 1: Figure 1 | 1 | high | False | Select the correct mirror image of the given figure when the mirror is placed at MN as shown. |
| 14 | 14 | 8 |  | 2 | high | False | Identify the option figure that when put in place of the question mark (?) will logically complete the series. |
| 15 | 15 | 8 | 4: YM72 | 4 | high | False | Which of the four options will replace the question mark (?) in the following series? UE 88, VG 84, WI 80, XK76, ? |
| 16 | 16 | 9 | 4: KPLPQLPSKP | 4 | high | False | Select the option that represents the letters that when placed from left to right in the blanks below will complete the letter ser |
| 17 | 17 | 9 |  | 2 | high | False | Identify the figure from the given options, which when put in place of the question mark (?), will logically complete the series. |
| 18 | 18 | 10 | 4: 21 | 4 | high | False | Six numbers 21, 22, 23, 24, 25 and 26 are written on different faces of a dice. Three positions of this dice are shown in the figu |
| 19 | 19 | 10 | 1: 21 | 2 | high | False | How many triangles are there in the given figure? |
| 20 | 20 | 10 | 1: aa | 1 | high | False | In a certain code language, ‘what where how’ is written as ‘aa dd ff’; ‘where there that’ is written as ‘dd zz pp’ and ‘which what |
| 21 | 21 | 11 | 2: Both II and III conclusion follow | 2 | high | False | Three statements are given followed by three conclusions numbered I, II and III. Assuming the statements to be true, even if they  |
| 22 | 22 | 11 | 1: UWSV | 1 | high | False | Which of the following terms will replace the question mark (?) in the given series? YZUW, ?, QTQU, MQOT, INMS |
| 23 | 23 | 12 | 2: iii | 2 | high | False | In a certain code language, ‘A + B’ means ‘A is the mother of B’, ‘A – B’ means ‘A is the father of B’, ‘A $ B’ means ‘A is the so |
| 24 | 24 | 12 | 4: 671 | 4 | high | False | 19 is related to 209 following a certain logic. Following the same logic, 27 is related to 297. To which of the following is 61 re |
| 25 | 25 | 12 | 4: 206 | 4 | high | False | Which of the following numbers will replace the question mark (?) in the given series? 1, 3, 10, 41, ?, 1237 |
| 26 | 1 | 13 | 1: 1973 | 3 | high | False | In which year was Project Tiger launched in India? |
| 27 | 2 | 13 | 4: Uttar Pradesh | 4 | high | False | Lathmar Holi is primarily celebrated in the state of: |
| 28 | 3 | 13 | 3: Bharat Ratna | 2 | high | False | Which of the following awards was won by Lata Mangeshkar in the year 2001? |
| 29 | 4 | 13 | 2: Rudradaman I | None | high | True | Details about Sudarshana lake is given in a rock inscription at Girnar (Junagarh), which was composed to record the achievements o |
| 30 | 5 | 14 | 4: Microfinance Institutions Network | 1 | high | False | __________ is an industry association and self-regulatory organisation (SRO) whose primary objective is to work towards the robust |
| 31 | 6 | 14 | 3: Article 226 | None | high | True | Which article has a similar provision to that of Article 32 and deals with writ jurisdiction? |
| 32 | 7 | 14 | 3: He shall not be entitled, without payment of  | 3 | high | False | Which of the following is NOT a condition for the President's office in India? |
| 33 | 8 | 14 | 3: A flower with both androecium and gynoecium | None | high | True | Which of the following statements best defines the monoecious? |
| 34 | 9 | 15 | 1: Grammy | None | high | True | Mohan Veena player, Pandit Vishwa Mohan Bhatt won the __________ Award in the year 1994. |
| 35 | 10 | 15 | 2: Jitendra Singh | 2 | high | False | Who is Union Minister of State (Independent Charge) for Science and Technology as of July 2023? |
| 36 | 11 | 15 | 2: Decomposition of calcium carbonate | None | high | True | Which of the following decomposition reactions is NOT a redox reaction? |
| 37 | 12 | 15 | 3: Dinabandhu Mitra | None | high | True | Who among the following has authored the play ‘Nil Darpan’? |
| 38 | 13 | 16 | 4: Swami Sahajanand Saraswati | None | high | True | Who among the following formed the Bihar Provincial Kisan Sabha in 1929? |
| 39 | 14 | 16 | 1: Deccan lava plateau | None | high | True | Which plateaus are very fertile because they are rich in black soil that is very good for farming? |
| 40 | 15 | 16 | 4: CsOH>KOH>NaOH>LiOH | 1 | high | False | Which of the following is a correct order of basicity? |
| 41 | 16 | 16 | 4: Tissue-organ grade organisation - Euplectella | None | high | True | Which of the following pairs is INCORRECT regarding the grade of organisation and its example? |
| 42 | 17 | 17 | 3: Mumbai | 3 | high | False | The head office of Board of Control for Cricket in India (BCCI) is located in ________. |
| 43 | 18 | 17 | 4: Physiological density | 4 | high | False | When the analysis of population density is done by calculating it through net cultivated area, then the measure is termed as: |
| 44 | 19 | 17 | 1: Pallava | None | high | True | Mahendravarman I was the ruler of which of the following dynasties? |
| 45 | 20 | 17 | 4: Inconsistent regulatory environment | 4 | high | False | What challenge does foreign investment often face in India? |
| 46 | 21 | 18 | 2: Madhya Pradesh | 2 | high | False | Which of the following states is the biggest producer of Pulses? |
| 47 | 22 | 18 | 3: Atmaram Pandurang | 3 | high | False | Who founded the Prarthana Samaj in Mumbai in 1867? |
| 48 | 23 | 18 | 4: MK Stalin | 4 | high | False | Who is the Chief Minister of Tamil Nadu as of July 2023? |
| 49 | 24 | 18 | 1: Kolkata | None | high | True | In which city was the first golf club of India situated? |
| 50 | 25 | 20 | 2: Narendra Modi | 3 | high | False | Which Indian among the following has his name in Time Magazine’s list of ‘100 most influential people of 2021’? |
| 51 | 1 | 20 | 2: 14.94% | 2 | high | False | A grocer professes to sell rice at the cost price, but uses a fake weight of 870 g for 1 kg. Find his profit percentage (correct t |
| 52 | 2 | 20 | 4: 1 | 4 | high | False | The value of cos²29° + cos²61° is: |
| 53 | 3 | 21 | 1: 140 s | 1 | high | False | In a circular race of 840 m, A and B start running in the same direction at the same time from the same point at the speeds of 6 m |
| 54 | 4 | 21 | 4: 26 | 4 | high | False | Let O be the centre of the circle and AB and CD are two parallel chords on the same side of the radius. OP is perpendicular to AB  |
| 55 | 5 | 21 | 2: These have two equal sides and the same perim | 2 | high | False | Which of the following statements is sufficient to conclude that two triangles are congruent? |
| 56 | 6 | 22 | 3: 1 | 3 | high | False | The given table shows the percentage of marks obtained by three students in three different subjects in an institute. (maximum mar |
| 57 | 7 | 22 | 2: 5 minutes | 2 | high | False | Fill pipe P is 21 times faster than fill pipe Q. If Q can fill a cistern in 110 minutes, find the time it takes to fill the cister |
| 58 | 8 | 23 | 2: Tarun | 2 | high | False | The following table shows the marks (out of 100) obtained by five students in five different subjects. Student/Subject Maths Physi |
| 59 | 9 | 23 | 1: 13 | 1 | high | False | R pays ₹100 to P with ₹5, ₹2 and ₹1 coins. The total number of coins used for paying are 40. What is the number of coins of denomi |
| 60 | 10 | 23 | 4: 15 : 4 | 4 | high | False | The radii of the two cones are in the ratio of 2 : 5 and their volumes are in the ratio of 3 : 5. What is the ratio of their heigh |
| 61 | 11 | 24 | 1: 2 | 1 | high | False | Which of the following can be the value of ‘k’ so that the number 217924k is divisible by 6? |
| 62 | 12 | 24 | 1: 8 | 1 | high | False | In an election between two candidates, y% of the voters did not vote. 10% of the votes cast were declared invalid, while all the v |
| 63 | 13 | 24 | 3: 300 | 3 | high | False | An article is marked at ₹550. If it is sold at a discount of 40%, then the selling price becomes 10% more than its cost price. Wha |
| 64 | 14 | 25 | 4: 8 cm | 4 | high | False | If the sum of two sides of an equilateral triangle is 16 cm, then find the third side. |
| 65 | 15 | 25 | 3: x - 3 | 3 | high | False | Simplify (x^2-9)/(x+3) |
| 66 | 16 | 25 | 2: 2019 | 1 | high | False | The following table shows the total candidates appeared and number of candidates present, in different exam centres – P, Q and R.  |
| 67 | 17 | 26 | 3: 35 cm | 3 | high | False | The distance between the centres of two circles of radii 22 cm and 10 cm is 37 cm. If the points of contact of a direct common tan |
| 68 | 18 | 26 | 2: 0 | 2 | high | False | The value of sin² 30 – sin² 40 + sin² 45 – sin² 55 – sin² 35 + sin² 45 – sin²50 + sin² 60 is: |
| 69 | 19 | 26 | 2: 2 : 3 | 2 | high | False | The average marks (out of 100) of boys and girls in an examination are 75 and 80, respectively. If the average marks of all the st |
| 70 | 20 | 27 | 1: 54 | 1 | high | False | Rajesh, in his printing press, got an order to print some books, out of which he completed 17/27 of the order in 34 days. In how m |
| 71 | 21 | 27 | 3: x^2 + 10x + 25 | 3 | high | False | Simplify (x^3 + 15x^2 + 75x + 125) / (x^2 - 25) * (x - 5). |
| 72 | 22 | 27 | 2: 25/9 | 2 | high | False | If cosecθ = 5/3, then evaluate (sec^2θ - 1) * cot^2θ * (1 + cot^2θ). |
| 73 | 23 | 28 | 4: 1, 10 | 4 | high | False | Which of the following can be the value of k, if (88 ÷ 8 × k - 3 × 3) / (6^2 - 7 × 5 + k^2) = 1? |
| 74 | 24 | 28 | 2: 91 1/6% | None | high | True | Read the given information and answer the question that follows. The following table gives the percentage of marks obtained by sev |
| 75 | 25 | 29 | 2: 564914 | 2 | high | False | Mohan borrows a sum of ₹4,22,092 at the rate of 20% per annum simple interest. At the end of the first year, he repays ₹21,679 tow |
| 76 | 1 | 29 | 3: Deadly | 3 | high | False | Select the most appropriate synonym of the given word. Fatal |
| 77 | 2 | 29 | 3: Domnica composes lovely tunes. | 3 | high | False | Select the option that expresses the given sentence in active voice. Lovely tunes are composed by Domnica. |
| 78 | 3 | 30 | 1: Invalidate | 1 | high | False | Select the option that expresses the opposite meaning of the underlined word. The explosive used is of my own formulation, and I c |
| 79 | 4 | 30 | 4: no informations | 4 | high | False | The following sentence has been divided into four segments. Identify the segment that contains an error. Mr. Abhilash and his fami |
| 80 | 5 | 30 | 1: Lethal | 1 | high | False | Select the most appropriate synonym of the given word. Toxic |
| 81 | 6 | 31 | 4: Carat | 4 | high | False | Select the word which means the same as the group of words given. Unit of weight for precious stones |
| 82 | 7 | 31 | 3: Multilingual | 3 | high | False | Select the option that can be used as a one-word substitute for the underlined group of words. She is proficient in speaking many  |
| 83 | 8 | 31 | 3: The tiger was seen by Ishika in the forest. | 3 | high | False | Select the option that expresses the given sentence in passive voice. Ishika saw the tiger in the forest. |
| 84 | 9 | 32 | 3: Contentious | 2 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A person who likes to argue about anythi |
| 85 | 10 | 32 | 4: sequential art in a traditional | 4 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. ‘Spy Family’ is a graphic nov |
| 86 | 11 | 32 | 2: extremely good | 1 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. My brother perfo |
| 87 | 12 | 33 | 4: Relevent | 2 | high | False | Select the INCORRECTLY spelt word. |
| 88 | 13 | 33 | 3: philanthropic | 3 | high | False | Select the most appropriate synonym to replace the underlined word in the given sentence. No altruistic act is truly sincere. |
| 89 | 14 | 33 | 4: Insinuation | None | high | True | Select the most appropriate synonym of the given word. Innuendo |
| 90 | 15 | 34 | 3: narrow | 3 | high | False | Select the most appropriate option to fill in the blank. Vinod had a ________ escape in the car accident. |
| 91 | 16 | 34 | 1: Anecdote | 1 | high | False | Select the option that can be used as a one-word substitute for the given phrase. A short interesting story about a real person or |
| 92 | 17 | 34 | 2: intimidate | 2 | high | False | Select the most appropriate synonym of the word in bold. We’d better watch our step and not give him any excuse to harass us furth |
| 93 | 18 | 35 | 1: To have bigger things to take care of than th | 1 | high | False | Select the most appropriate meaning of the given idiom. To have bigger fish to fry |
| 94 | 19 | 35 | 1: B | 1 | high | False | In the following sentence, four words are underlined out of which one word is misspelt. Identify the INCORRECTLY spelt word. After |
| 95 | 20 | 35 | 2: studying since two o'clock | 2 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. She has been studying for two o'clo |
| 96 | 21 | 36 | 4: However | 4 | high | False | Select the most appropriate option to fill in blank number 1. |
| 97 | 22 | 36 | 2: foresee | 2 | high | False | Select the most appropriate option to fill in blank number 2. |
| 98 | 23 | 37 | 2: Moreover | 4 | high | False | Select the most appropriate option to fill in blank number 3. |
| 99 | 24 | 37 | 3: Besides | 1 | high | False | Select the most appropriate option to fill in blank number 4. |
| 100 | 25 | 39 | 1: Therefore | 1 | high | False | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
