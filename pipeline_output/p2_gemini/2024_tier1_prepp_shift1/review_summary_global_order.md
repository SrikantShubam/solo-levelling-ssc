# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2024_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 94 / 100
- Overall status: FAIL
- Structural QC passed: False
- Load errors: []
- Option/correct-answer issue global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94]
- Missing/invalid chosen-option global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94]
- Low-confidence global questions: [9, 11, 17, 54, 77, 82, 87, 93]
- Manual review count: 94
- Canonical review count: 94

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | FAIL | 94 / 100 |
| Four options and correct answer | FAIL | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94] |
| Chosen answer present/valid | WARN | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94] |
| Confidence/manual-review flags | WARN | [9, 11, 17, 54, 77, 82, 87, 93] |
| Canonical review routing | WARN | 94 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 2 |
| 4 | 2 |
| 5 | 2 |
| 6 | 3 |
| 7 | 2 |
| 8 | 2 |
| 9 | 2 |
| 10 | 2 |
| 11 | 1 |
| 12 | 3 |
| 13 | 2 |
| 14 | 0 |
| 15 | 3 |
| 16 | 3 |
| 17 | 3 |
| 18 | 3 |
| 19 | 4 |
| 20 | 2 |
| 21 | 3 |
| 22 | 3 |
| 23 | 1 |
| 24 | 3 |
| 25 | 3 |
| 26 | 1 |
| 27 | 3 |
| 28 | 2 |
| 29 | 3 |
| 30 | 1 |
| 31 | 2 |
| 32 | 2 |
| 33 | 3 |
| 34 | 3 |
| 35 | 3 |
| 36 | 2 |
| 37 | 3 |
| 38 | 2 |
| 39 | 3 |
| 40 | 2 |
| 41 | 1 |
| 42 | 1 |
| 43 | 2 |
| 44 | 1 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 3 |  | None | high | True | Three statements are given, followed by three conclusions numbered I, II and III. Assuming the statements to be true, even if they |
| 2 | 2 | 3 |  | None | medium | True | The position of how many letters will remain unchanged, if all the letters in the word BINDER are arranged in English alphabetical |
| 3 | 3 | 4 |  | None | high | True | In a certain code language: 'A + B' means 'A is the mother of B'; 'A - B' means 'A is the brother of B'; 'A × B' means 'A is the w |
| 4 | 4 | 4 |  | None | medium | True | Identify the figure given in the options which when put in place of '?' will logically complete the series. |
| 5 | 5 | 5 |  | None | high | True | ‘WISK’ is related to ‘DRHP’ in a certain way based on the English alphabetical order. In the same way, ‘LENT’ is related to ‘OVMG’ |
| 6 | 6 | 5 |  | None | high | True | Two sets of numbers are given below. In each set of numbers, certain mathematical operation(s) on the first number result(s) in th |
| 7 | 7 | 6 |  | None | high | True | Select the number from the given options to complete the series: 25, 30, 40, 55, 75, ___ |
| 8 | 8 | 6 |  | None | high | True | The position(s) of how many letters will remain unchanged if all the letters in the word ‘ENTOMB’ are arranged in English alphabet |
| 9 | 9 | 6 |  | None | low | True | Six words Eat, Cry, Play, Sleep, Run and Bath are written on different faces of a dice. Three positions of this dice are shown in  |
| 10 | 10 | 7 |  | None | high | True | Two different positions of the same dice with faces T, O, B, L, Y and V are shown below. Select the letter that will be on the fac |
| 11 | 11 | 7 |  | None | low | True | Select the word-pair that best represents a similar relationship to the one expressed in the pair of words given below. Virus : Pa |
| 12 | 12 | 8 |  | None | high | True | Select the set in which the numbers are related in the same way as are the numbers of the given sets: (213, 157), (185, 129) |
| 13 | 13 | 8 |  | None | high | True | Three of the following four options are alike in a certain way and thus form a group. Which is the one that does NOT belong to tha |
| 14 | 15 | 9 |  | None | high | True | In a certain code language, ‘FACED’ is written as ‘GZDDE’ and ‘VACAY’ is written as ‘WZDZZ’. How will ‘LABOR’ be written in that l |
| 15 | 16 | 9 |  | None | high | True | Which two signs should be interchanged to make the following equation correct? 247 ÷ 13 + 16 × 3 - 148 = 119 |
| 16 | 17 | 10 |  | None | high | True | How many triangles are there in the given figure? |
| 17 | 18 | 10 |  | None | low | True | Select the correct mirror image of the given figure when the mirror is placed at MN. |
| 18 | 19 | 11 |  | None | high | True | Select the figure from the given option that can replace the question mark (?) in the following series. |
| 19 | 20 | 12 |  | None | high | True | In a certain code language, 'FIVE' is written as '12184410' and 'FOUR' is written as '12304236'. How will 'THREE' be written in th |
| 20 | 21 | 12 |  | None | high | True | Select the correct mirror image of the given figure when the mirror is placed at MN as shown below. |
| 21 | 22 | 12 |  | None | medium | True | In the following series, only one letter-cluster is incorrect. Select the incorrect letter-cluster: YCG, IMQ, SVZ, CGK, MQU |
| 22 | 23 | 13 |  | None | high | True | Based on the English alphabetical order, three of the following four letter-clusters are alike in a certain way and thus form a gr |
| 23 | 24 | 13 |  | None | high | True | What will come in the place of the question mark (?) in the following equation, if '+' and '-' are interchanged and '×' and '÷' ar |
| 24 | 26 | 15 |  | None | high | True | Who among the following is the world-renowned exponent of the bamboo flute? |
| 25 | 27 | 15 |  | None | high | True | What is net investment? |
| 26 | 28 | 15 |  | None | high | True | India won the ICC Men Cricket World Cup for the first time in which of the following years? |
| 27 | 29 | 16 |  | None | high | True | Match the following - Institutes a. Asiatic Society of Bengal b. Sanskrit College of Benaras c. Fort William College d. Calcutta M |
| 28 | 30 | 16 |  | None | high | True | Kathakali, one of the classical dances of India, is predominantly performed in which of the following states of India? |
| 29 | 31 | 16 |  | None | medium | True | Identify the oldest iron and steel company of India from the following options. |
| 30 | 32 | 17 |  | None | high | True | The magnificent Kailasa temple at Ellora was built during the reign of which Rashtrakuta king? |
| 31 | 33 | 17 |  | None | high | True | In which state/UT is the Hemis festival celebrated? |
| 32 | 34 | 17 |  | None | high | True | Which of the following is the largest artificial lake of Asia? |
| 33 | 35 | 18 |  | None | high | True | In 2002, Zakir Hussain became the youngest percussionist to be honored with which award? |
| 34 | 36 | 18 |  | None | high | True | Microbes like Rhizobium, Nitrosomonas, and Nitrobacter are used for: |
| 35 | 37 | 18 |  | None | high | True | With reference to the Sepoy Mutiny of 1857, on which of the following dates did the soldiers at Meerut start their journey to Delh |
| 36 | 38 | 19 |  | None | high | True | Who among the following was selected as the Sherpa for India’s G20 hosted in 2022-23? |
| 37 | 39 | 19 |  | None | high | True | Purvanchal Himalayas does NOT comprise of: |
| 38 | 40 | 19 |  | None | high | True | In which year did India make its Olympic debut in hockey? |
| 39 | 41 | 19 |  | None | medium | True | A student, on his school assignment, is taking a session on how to make compost at home for using it at a park. Which fundamental  |
| 40 | 42 | 20 |  | None | high | True | In August 2022, the Ministry of Social Justice and Empowerment launched the _______ scheme, with an aim to provide comprehensive r |
| 41 | 43 | 20 |  | None | high | True | Which is the National Mission for Financial Inclusion to ensure access to financial services, namely, a basic savings and deposits |
| 42 | 44 | 21 |  | None | high | True | Which of the following plays was NOT written by Harshavardhana? |
| 43 | 45 | 21 |  | None | high | True | The organisms that do not have a defined nucleus or organelles are classified into ______ Kingdom. |
| 44 | 46 | 21 |  | None | medium | True | Which Article of the Constitution of India provides that 'there shall be a Vice President of India'? |
| 45 | 47 | 22 |  | None | high | True | A javelin thrown by an athlete is in ________ motion. |
| 46 | 48 | 22 |  | None | high | True | The green revolution technology resulted in an increase in the production of cereal crops from 72.4 million tons in 1965-66 to ___ |
| 47 | 49 | 22 |  | None | medium | True | Calculate the oxidation number of ‘S’ in H2S2O7. |
| 48 | 50 | 23 |  | None | high | True | Which of the following is NOT an amendment made to the Airport Economic Regulatory Authority (AERA) Amendment Act, 2021? |
| 49 | 51 | 24 |  | None | high | True | Which digits should come in place * and $, respectively, if the number 72864*$ is divisible by both 8 and 5? |
| 50 | 52 | 24 |  | None | high | True | The given table shows the number of soaps sold by four different companies in 4 different months. The total no. of soaps sold by c |
| 51 | 53 | 24 |  | None | medium | True | In a triangle PQR, S is a point on the side QR such that PS⊥QR. Then which of the following options is true? |
| 52 | 54 | 25 |  | None | high | True | Simplify: 15.5 - [3 - {7 - (5 - (14.5 - 13.5))}] |
| 53 | 55 | 25 |  | None | high | True | The incomes of P, Q, and R are in the ratio 10 : 12 : 9, and their expenditures are in the ratio 12 : 15 : 8. If Q saves 25% of hi |
| 54 | 56 | 25 |  | None | low | True | The classification of 100 students based on the marks obtained by them in English and Mathematics in an examination is given in th |
| 55 | 57 | 26 |  | None | high | True | In triangles ABC and DEF, AB = FD and ∠A = ∠D. The two triangles are congruent by SAS criterion if: |
| 56 | 58 | 27 |  | None | high | True | Two pipes, A and B, can fill a tank in 10 minutes and 20 minutes, respectively. The pipe C can empty the tank in 30 minutes. All t |
| 57 | 59 | 27 |  | None | high | True | A payment of ₹120 is made with ₹10, ₹5, and ₹2 coins. A total of 25 coins are used. Which of the following is the number of ₹10 co |
| 58 | 60 | 27 |  | None | high | True | If 28.9 : x :: x : 36.1, and x > 0, then find the value of x. |
| 59 | 61 | 28 |  | None | high | True | Study the given pie chart carefully and answer the question that follows. The given pie chart shows that the number of successful  |
| 60 | 62 | 28 |  | None | high | True | The height of a cylinder is 20 cm. The lateral surface area is 1760 cm². Its volume is: |
| 61 | 63 | 29 |  | None | high | True | Raj divides ₹1,200 in the ratio 2 : 1 : 3 among three of his friends. The amount equal to the sum of three times the largest share |
| 62 | 64 | 29 |  | None | high | True | A shopkeeper marked an article at ₹5,000. The shopkeeper allows successive discounts of 20%, 15%, and 10%. The selling price of th |
| 63 | 65 | 29 |  | None | medium | True | The average of 12 numbers is 48. The average of the first 5 numbers is 45, and the average of the next 4 numbers is 52. If the 10t |
| 64 | 66 | 30 |  | None | high | True | Find the value of the following expression. √((1+sinθ)/(1-sinθ)) |
| 65 | 68 | 31 |  | None | high | True | Let t = 2/5, then the value of the expression t^3 + (3/5)^3 + 9/5 t is: |
| 66 | 69 | 31 |  | None | high | True | M and N walk along a circular track. They start at 5:00 a.m. from the same point in the opposite directions. M and N walk at a spe |
| 67 | 71 | 32 |  | None | high | True | If x + 1/x = 15, then the value of (7x^2 - 9x + 7) / (x^2 - x + 1) is: |
| 68 | 72 | 32 |  | None | medium | True | Study the given table and answer the question that follows. The given table shows the production of different types of refrigerato |
| 69 | 73 | 33 |  | None | high | True | The measures of the three angles of a triangle are in the ratio 17 : 13 : 15. Find the positive difference between the greatest an |
| 70 | 74 | 33 |  | None | high | True | If 2cosec²θ + 3cot²θ = 17, then the value of 'θ' when 0° ≤ θ ≤ 90° is: |
| 71 | 75 | 33 |  | None | high | True | A certain sum of money becomes seven times itself when invested at a certain rate of simple interest, in 14 years. How much time ( |
| 72 | 76 | 34 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words: A false idea or belief |
| 73 | 77 | 34 |  | None | high | True | Identify the most appropriate ANTONYM of the given word: Secure |
| 74 | 78 | 34 |  | None | medium | True | Select the most appropriate option to substitute the underlined segment in the given sentence: Gourav was no good than a foolish p |
| 75 | 79 | 35 |  | None | high | True | Select the option that corrects the error in the given sentence: He ran quick to catch the bus. |
| 76 | 80 | 35 |  | None | high | True | Select the most appropriate synonym of the given word: Acquiesce |
| 77 | 81 | 35 |  | None | low | True | Select the option that can be used as a one-word substitute for the given group of words: That which cannot be conquered |
| 78 | 82 | 36 |  | None | high | True | Select the most appropriate synonym for the underlined word in the given sentence: His ambition in life is to become a happy and s |
| 79 | 83 | 36 |  | None | high | True | Read the sentence carefully and select the most suitable idiom to fill in the blank: The renowned publisher decided to withdraw a  |
| 80 | 84 | 37 |  | None | high | True | Select the most appropriate ANTONYM of the given word: Receive |
| 81 | 85 | 37 |  | None | high | True | Select the option that expresses the following sentence in passive voice: Sonam does not like bananas. |
| 82 | 86 | 37 |  | None | low | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 83 | 87 | 38 |  | None | high | True | Select the option that can be used as a one-word substitute for the underlined group of words: In Indian mythology, most of the As |
| 84 | 88 | 38 |  | None | high | True | Select the option that expresses the given sentence in passive voice: Someone has taken my secret diary. |
| 85 | 89 | 39 |  | None | high | True | Select the most appropriate synonym of the bracketed word in the following sentence to fill in the blank: During Covid times, many |
| 86 | 90 | 39 |  | None | high | True | Select the most appropriate meaning of the underlined word in the given sentence: He is an atheist, although he respects everyone' |
| 87 | 91 | 39 |  | None | low | True | Select the most appropriate meaning of the underlined idiom in the following sentence: In my new office, all employees were differ |
| 88 | 92 | 40 |  | None | high | True | Select the INCORRECTLY spelt word: |
| 89 | 93 | 40 |  | None | high | True | The following sentence has been divided into four segments. Identify the segment that contains an error: Mrs. Sreelakshmi’s / musi |
| 90 | 95 | 41 |  | None | high | True | Select the INCORRECTLY spelt word: |
| 91 | 97 | 42 |  | None | high | True | Comprehension: In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate  |
| 92 | None | 43 |  | None | high | True | The author brings out the human elements in his story. This common element of sympathy and sacrifice is given a new (3)_____ by th |
| 93 | 99 | 43 |  | None | low | True | Comprehension: In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate  |
| 94 | 100 | 44 |  | None | high | True | Comprehension: In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate  |
