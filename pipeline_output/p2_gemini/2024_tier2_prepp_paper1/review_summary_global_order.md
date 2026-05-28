# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2024_tier2_prepp_paper1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 141 / 150
- Overall status: FAIL
- Structural QC passed: False
- Load errors: []
- Option/correct-answer issue global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141]
- Missing/invalid chosen-option global questions: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141]
- Low-confidence global questions: [16, 19, 25, 28, 34, 37, 38, 44, 47, 49, 50, 58, 62, 71, 76, 90, 93, 111, 137]
- Manual review count: 141
- Canonical review count: 141

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | FAIL | 141 / 150 |
| Four options and correct answer | FAIL | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141] |
| Chosen answer present/valid | WARN | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141] |
| Confidence/manual-review flags | WARN | [16, 19, 25, 28, 34, 37, 38, 44, 47, 49, 50, 58, 62, 71, 76, 90, 93, 111, 137] |
| Canonical review routing | WARN | 141 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 3 |
| 4 | 3 |
| 5 | 3 |
| 6 | 3 |
| 7 | 4 |
| 8 | 3 |
| 9 | 3 |
| 10 | 3 |
| 11 | 3 |
| 12 | 2 |
| 13 | 1 |
| 14 | 1 |
| 15 | 2 |
| 16 | 2 |
| 17 | 1 |
| 18 | 1 |
| 19 | 2 |
| 20 | 1 |
| 21 | 3 |
| 22 | 3 |
| 23 | 2 |
| 24 | 1 |
| 25 | 1 |
| 26 | 2 |
| 27 | 2 |
| 28 | 3 |
| 29 | 1 |
| 30 | 3 |
| 31 | 1 |
| 32 | 2 |
| 33 | 3 |
| 34 | 1 |
| 35 | 2 |
| 36 | 2 |
| 37 | 3 |
| 38 | 2 |
| 39 | 2 |
| 40 | 3 |
| 41 | 2 |
| 42 | 1 |
| 43 | 1 |
| 44 | 2 |
| 45 | 1 |
| 46 | 0 |
| 47 | 1 |
| 48 | 1 |
| 49 | 1 |
| 50 | 2 |
| 51 | 1 |
| 52 | 1 |
| 53 | 2 |
| 54 | 1 |
| 55 | 1 |
| 56 | 3 |
| 57 | 3 |
| 58 | 4 |
| 59 | 2 |
| 60 | 3 |
| 61 | 2 |
| 62 | 3 |
| 63 | 3 |
| 64 | 1 |
| 65 | 3 |
| 66 | 3 |
| 67 | 3 |
| 68 | 3 |
| 69 | 1 |
| 70 | 2 |
| 71 | 1 |
| 72 | 0 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 3 |  | None | high | True | ΔABC is inscribed in a circle with Centre O. If AB = 21 cm, BC = 20 cm and AC = 29 cm, then what is the length of the circumradius |
| 2 | 2 | 3 |  | None | high | True | On a 2200 m long circular track, Sarita and Kavita drove their cycles from the same point but in opposite direction with the speed |
| 3 | 3 | 3 |  | None | high | True | In a triangle HJK, HJ = HK. G is a point on HJ such that HG = GK = JK. What is the degree measure of two-third of (∠HGK +∠GKJ)? |
| 4 | 4 | 4 |  | None | high | True | Find the simple interest (in ₹) on ₹2000 at 6.5% per annum rate of interest for the period from 14 February 2023 to 28 April 2023 |
| 5 | 5 | 4 |  | None | high | True | The population of a place increased to 50,000 from 2016 to 2018 at the rate of 6% per annum, and continued the same trend for the  |
| 6 | 6 | 4 |  | None | high | True | If the areas of two similar triangles are in the ratio 121: 225 |
| 7 | 7 | 5 |  | None | high | True | Find the value of Y, if X - 2Y + 2Z = 16, X - Y + Z = 9 and 2X - 3Y - Z = 9. |
| 8 | 8 | 5 |  | None | high | True | Rani and Adya, working separately, can finish a task in 12 days and 16 days, respectively. They work in stretches of one day alter |
| 9 | 9 | 5 |  | None | high | True | Let A and B be two players who are playing the game to hit the target. The probabilities of hitting the target by A and B is 2/3 a |
| 10 | 10 | 6 |  | None | high | True | On the occasion of Republic Day, a retail store offers a scheme where customers can avail a discount of 26% on their total purchas |
| 11 | 11 | 6 |  | None | high | True | Vessel A contains milk and water in the ratio 4 : 5. Vessel B contains milk and water in the ratio 2 : 1. If x litres mixture of A |
| 12 | 12 | 6 |  | None | high | True | The average of first 91 even numbers is |
| 13 | 13 | 7 |  | None | high | True | Find the volume (in cm³, rounded off to 2 decimal places) of a right circular cone of diameter 12 cm and height 5 cm. [Use π = 22/ |
| 14 | 14 | 7 |  | None | high | True | ∛6859 ÷ ∛1296 × (3 ÷ 57) × 42 = ? |
| 15 | 15 | 7 |  | None | high | True | If x = 8 + √5 and y= 8-√5 then the value of x² + y² is: |
| 16 | 16 | 7 |  | None | low | True | A sum of money is to be distributed among 3 friends P, Q and R in the proportion of 5:3:4. If P gets ₹1,500 more than R, what is Q |
| 17 | 17 | 8 |  | None | high | True | If tan(x + y)tan(x - y) = 1, then find the value of tanx. |
| 18 | 18 | 8 |  | None | high | True | Using empirical formula, calculate the mode for the following data. 17, 20, 21, 18, 25, 28, 24, 22, 16, 24, 25, 24 |
| 19 | 19 | 8 |  | None | low | True | If (secθ - tanθ) ÷ (secθ + tanθ) = 1 / 9, θ lies in the first quadrant, then the value of secθ is: |
| 20 | 20 | 9 |  | None | high | True | (a⁷ × b⁸ × c⁷) ÷ (a⁹ × b⁵ × c⁴) in simplified form is: |
| 21 | 21 | 9 |  | None | high | True | By how much is 60% of 75 greater than 1/5 of 25? |
| 22 | 22 | 9 |  | None | medium | True | If the average age of three persons is 56 years and their ages are in the ratio 2:5:7, then find the age of the youngest person. |
| 23 | 23 | 10 |  | None | high | True | A toy is in the form of a cone mounted on a hemisphere. The radius of the hemisphere and that of the cone is 36 cm and height of t |
| 24 | 24 | 10 |  | None | high | True | Anil and Beena are friends, and the difference between their ages is 5 years. Anil's father Dinesh is three times as old as Anil,  |
| 25 | 25 | 10 |  | None | low | True | The height of a right circular cone is 63 cm and the area of its curved surface is five times the area of its base. What is the vo |
| 26 | 26 | 11 |  | None | high | True | A man buys 10 identical articles for a total of ₹15. If he sells each of them for ₹1.7, then his profit percentage will be ____ %  |
| 27 | 27 | 11 |  | None | high | True | Find the median of the following data. (Rounded off to 2 decimal places.) Class interval 0-5 5-10 10-15 15-20 20-25 25-30 30-35 Fr |
| 28 | 28 | 11 |  | None | low | True | Let ABC be a right-angled triangle with a right angle at B. If tan A = √3, then find the value of sin A cos C + cos A sin C and co |
| 29 | 29 | 12 |  | None | high | True | Simplify (5z - 12y)² + (12z + 5y)² - 144z² |
| 30 | 30 | 12 |  | None | high | True | The value of 4³ - 0² + (22/2)² - 8 + 7 × 6 = ______ |
| 31 | 32 | 13 |  | None | high | True | A question is given, followed by two statements labelled I and II. Identify which of the statements is/are sufficient/necessary to |
| 32 | 33 | 14 |  | None | high | True | Select the option figure in which the given figure is embedded as its part (rotation is NOT allowed). |
| 33 | 34 | 15 |  | None | high | True | Given below is a statement (Cause) followed by possible effects numbered I, II, and III. Read the ‘Cause’ carefully and decide whi |
| 34 | 35 | 15 |  | None | low | True | In a certain code language, 'POSE' is coded as '3517' and 'SILK' is coded as '4638'. What is the code for 'S' in the given code la |
| 35 | 36 | 16 |  | None | medium | True | Select the correct mirror image of the given combination when the mirror is placed at line MN as shown. |
| 36 | 37 | 16 |  | None | medium | True | Figure A is related to B in a certain pattern. Following the same pattern, figure C is related to D. Study the pattern and select  |
| 37 | 38 | 17 |  | None | low | True | Select the option figure that will replace the question mark (?) in the figure given below to complete the pattern. |
| 38 | 39 | 18 |  | None | low | True | Select the set in which the numbers are related in the same way as are the numbers of the following sets. (NOTE: Operations should |
| 39 | 40 | 19 |  | None | high | True | How many meaningful English words can be formed using first, third, sixth, and seventh letters of the word RECOGNIZE (when counted |
| 40 | 41 | 19 |  | None | high | True | The following contains two pairs of words which are related to each other in a certain way. Three of the following four word-pairs |
| 41 | 43 | 20 |  | None | high | True | U is the father of N. N is the sister of T. T is the wife of I. I is son of L. How is U related to L? |
| 42 | 44 | 21 |  | None | high | True | Select the correct option that indicates the arrangement of the following words in a logical and meaningful order. 1. Design 2. Te |
| 43 | 45 | 21 |  | None | high | True | Select the correct option that indicates the arrangement of the following words in a logical and meaningful order. 1. Delivery 2.  |
| 44 | 46 | 21 |  | None | low | True | Select the number from among the given options that can replace the question mark (?) in the following series. |
| 45 | None | 22 |  | None | high | True | 9, 5, 6, 10.5, 23, ? |
| 46 | 47 | 22 |  | None | high | True | Each of P, Q, R, S, T, U and V has an exam on a different day of a week, starting from Monday and ending on Sunday of the same wee |
| 47 | 48 | 22 |  | None | low | True | In a certain code language A + B means 'A is the mother of B', A - B means 'A is the brother of B', A x B means 'A is the wife of  |
| 48 | 49 | 23 |  | None | high | True | Four of the following five figures are alike in a certain way and thus form a group. Which is the one that does NOT belong to that |
| 49 | 50 | 23 |  | None | low | True | Identify the figure given in the options which when put in place of the question mark (?) will logically complete the series. |
| 50 | 51 | 24 |  | None | low | True | In the following number-pairs, the second number is obtained by applying certain mathematical operations to the first number. In t |
| 51 | 52 | 25 |  | None | high | True | A question is given, followed by two statements labelled I and II. Identify which of the statements is/are sufficient/necessary to |
| 52 | 53 | 26 |  | None | high | True | Six letters P, Q, S, T, U and V are written on different faces of a dice. Two positions of this dice are shown in the figure. Find |
| 53 | 54 | 26 |  | None | high | True | If 'A' stands for ', 'B' stands for 'x', 'C' stands for '+' and 'D' stands for '-', what will be come in place of the question mar |
| 54 | 55 | 27 |  | None | high | True | Each of the digits in the number 5238641 is arranged in ascending order from left to right. The position(s) of how many digits wil |
| 55 | 56 | 27 |  | None | high | True | A statement is followed by two arguments I and II. Read the statement and the arguments carefully and select the appropriate answe |
| 56 | 57 | 28 |  | None | high | True | Which of the following letter-clusters should replace # and % so that the pattern and relationship followed between the letter-clu |
| 57 | 58 | 28 |  | None | high | True | O, P, Q, R, S and T are sitting around a circular table facing the centre(but not necessarily in the same order). P sits second to |
| 58 | 59 | 28 |  | None | low | True | Read the given statements and conclusions carefully. Assuming that the information given in the statement(s) is true, even if it a |
| 59 | 60 | 29 |  | None | high | True | In a certain code language, 'she gardens daily' is coded as 'ak jb mp' and 'where is she' is coded as 'mp pt kt'. How is 'she' cod |
| 60 | 61 | 30 |  | None | high | True | Select the correct spelling of the incorrectly spelt word in the given sentence. The trainer tried to guage the learners' understa |
| 61 | 62 | 30 |  | None | high | True | Select the most appropriate meaning of the underlined word. "He walked leisurely towards the entrance." |
| 62 | 63 | 30 |  | None | low | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 63 | 64 | 31 |  | None | high | True | Parts of a sentence are given below in jumbled order. Select the option that gives the correct logical sequence to form a meaningf |
| 64 | 65 | 32 |  | None | high | True | Select the most appropriate option to fill in the blank. No other book in the series captivated readers as ______ as the final ins |
| 65 | 66 | 32 |  | None | high | True | A sentence has been split up into segments and given below in jumbled order. While the first and the last segments of the sentence |
| 66 | 67 | 33 |  | None | high | True | Select the option that expresses the given sentence in reported speech. Direct Speech: 'I am determined to publish my findings,' t |
| 67 | 68 | 33 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. One who cannot make a mistake |
| 68 | 69 | 33 |  | None | medium | True | Select the most appropriate homophone from the options to fill in the blank. We should ______ away all prejudices to live in harmo |
| 69 | 70 | 34 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 70 | 72 | 35 |  | None | high | True | Select the option that expresses the given sentence in direct speech. "The teacher informed that the exam had been postponed." |
| 71 | 73 | 35 |  | None | low | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 72 | 74 | 36 |  | None | high | True | Select the most appropriate option to fill in the blank. "Rashid was not able to _____ the pain after the accident." |
| 73 | 75 | 36 |  | None | high | True | Select the option that expresses the given sentence in passive voice. "Did you hear that noise?" |
| 74 | 76 | 37 |  | None | high | True | Select the option that expresses the given sentence in direct speech. "The District Magistrate ordered the police to work all nigh |
| 75 | 77 | 37 |  | None | high | True | Select the most appropriate meaning of the underlined idiom. "The team decided to pull out all the stops for their upcoming presen |
| 76 | 78 | 37 |  | None | low | True | Select the option that expresses the given sentence in passive voice. "Everyone was surprised at his speech." |
| 77 | 79 | 38 |  | None | high | True | Complete the dialogue for Person B using the correct idiom. "Person A: I am so nervous. I don't think I should make the speech tom |
| 78 | 80 | 38 |  | None | high | True | Select the most appropriate option to fill in the blank. "Luck does not always favour us, so we must always depend ______ our own  |
| 79 | 82 | 39 |  | None | high | True | Select the most appropriate option to fill in the blank. "The mango is the_________ fruit." |
| 80 | 83 | 39 |  | None | medium | True | Select the option that expresses the given sentence in passive voice. "The explosion caused serious damage in Ukraine." |
| 81 | 84 | 40 |  | None | high | True | Select the most appropriate ANTONYM of the word given below. "Enhance" |
| 82 | 85 | 40 |  | None | high | True | Select the option that can be used as a one-word substitute for the given group of words. "A sudden and violent change or upheaval |
| 83 | 86 | 40 |  | None | medium | True | Select the most appropriate ANTONYM of the given word. Generous |
| 84 | 87 | 41 |  | None | high | True | Parts of the following sentence have been given as options. Select the option that contains an error. It takes me an hour to get t |
| 85 | 88 | 41 |  | None | high | True | Select the most appropriate pronoun to fill in the blank. Mr. Amit Kumar, Proprietor of Xyling Pens is known for ______ honesty an |
| 86 | 90 | 42 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 87 | 92 | 43 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 88 | None | 44 |  | None | high | True | Select the most appropriate option to fill in blank number 3. |
| 89 | 93 | 44 |  | None | high | True | In the following passage, some words have been deleted. Read the passage carefully and select the most appropriate option to fill  |
| 90 | 94 | 45 |  | None | low | True | Read the given passage and answer the questions that follow. Subhas Chandra Bose, a prominent Indian nationalist leader, was convi |
| 91 | None | 47 |  | None | high | True | What ultimately undermined the INA's efforts to free India from British rule? |
| 92 | 97 | 48 |  | None | high | True | Read the given passage and answer the questions that follow. Subhas Chandra Bose, a prominent Indian nationalist leader, was convi |
| 93 | 98 | 49 |  | None | low | True | Algae are photosynthetic creatures that have pigments that aid in photosynthesis, such as chlorophyll. They do not, however, have  |
| 94 | None | 50 |  | None | high | True | What does the term 'multiphyletic group' mean in the context of algae? |
| 95 | 99 | 50 |  | None | medium | True | Algae are photosynthetic creatures that have pigments that aid in photosynthesis, such as chlorophyll. They do not, however, have  |
| 96 | 100 | 51 |  | None | high | True | Algae are photosynthetic creatures that have pigments that aid in photosynthesis, such as chlorophyll. They do not, however, have  |
| 97 | None | 52 |  | None | high | True | What is the central theme of the passage? |
| 98 | None | 53 |  | None | high | True | Select the most appropriate synonym of the word 'Inherent'. |
| 99 | 103 | 53 |  | None | medium | True | Read the given passage and answer the questions that follow. The French Revolution is a revolutionary movement that occurred in Fr |
| 100 | 104 | 54 |  | None | high | True | Read the given passage and answer the questions that follow. The French Revolution is a revolutionary movement that occurred in Fr |
| 101 | 106 | 55 |  | None | high | True | Which of the following sentences is/are true? i. All isoclines are expansion paths but all expansion paths are not isoclines. ii.  |
| 102 | 107 | 56 |  | None | high | True | Which of the following is a monoatomic gas? |
| 103 | 108 | 56 |  | None | high | True | Select the most appropriate answer from the options given below regarding Census 2011. Statement 1. The population of India has in |
| 104 | 109 | 56 |  | None | medium | True | What is the name of the ion with a charge of -1? |
| 105 | 110 | 57 |  | None | high | True | In December 1991, which act was amended to bring public enterprises under the purview of the Board for Industrial and Financial Re |
| 106 | 111 | 57 |  | None | high | True | Which theory, independently introduced in 1923, led to the concept of acid-base conjugate pairs? |
| 107 | 112 | 57 |  | None | high | True | Who mentioned ecosystem as 'the basic unit in ecology' in 1956? |
| 108 | 113 | 58 |  | None | high | True | Identify the naturally occurring aluminum oxide mineral that usually forms hexagonal barrel-shaped prisms. |
| 109 | 114 | 58 |  | None | high | True | The Bharatmala project of the Government of India comes under which of the following Ministries of India? |
| 110 | 115 | 58 |  | None | high | True | Mathura was the second capital of ______ dynasty. |
| 111 | 116 | 58 |  | None | low | True | Which of the following statements is/are correct? |
| 112 | 117 | 59 |  | None | high | True | Charcot-Marie-Tooth disease is caused by duplication of the peripheral myelin protein-22 (PMP22) gene on which chromosome? |
| 113 | 118 | 59 |  | None | medium | True | Which portal allowed stakeholders seamless access to information related to funding, documentation, project monitoring, and approv |
| 114 | 119 | 60 |  | None | high | True | Who among the following was the first Home Minister of Independent India? |
| 115 | 120 | 60 |  | None | high | True | What was the status of the agricultural sector in India before the Green Revolution? |
| 116 | 121 | 60 |  | None | medium | True | In which year did Walter Fleming stain the chromosomes to see them clearly and describe the entire process of mitosis? |
| 117 | 122 | 61 |  | None | high | True | Which of the following Constitutional Amendment Acts made the president bound by the advice of the council of ministers headed by  |
| 118 | 123 | 61 |  | None | high | True | Match the books in List 1 with their authors in List 2. List 1 (Books) List 2 (Authors) A. The Philosophy of the Bomb 1. Sachindra |
| 119 | 124 | 62 |  | None | high | True | The rotating columns of air that occur over water bodies and are generally less severe than land tornadoes are known as: |
| 120 | 125 | 62 |  | None | high | True | In which of the following cases did the Supreme Court direct that, 'the Parliament cannot take away or abridge any of the fundamen |
| 121 | 126 | 62 |  | None | high | True | Who urged political parties to engage in discussions that inspire unity rather than division and promote ideas instead of personal |
| 122 | 127 | 63 |  | None | high | True | Who won the title at the World Chess Armageddon Asia & Oceania event in April 2023? |
| 123 | 128 | 63 |  | None | high | True | Select the option that is true regarding the following two statements labelled Assertion (A) and Reason (R). A. The first battle o |
| 124 | 129 | 63 |  | None | medium | True | In the year 2020, National Digital Health Mission was launched on which of the following occasions? |
| 125 | 130 | 64 |  | None | high | True | Which Indian city experiences the LEAST difference in average temperature between its hottest and coldest months? |
| 126 | 131 | 65 |  | None | high | True | Which of the following technologies allows real-time communication over the Internet, such as voice and video calls, without requi |
| 127 | 132 | 65 |  | None | high | True | What is the primary advantage of being able to insert and delete slides in an MS PowerPoint presentation? |
| 128 | 133 | 65 |  | None | high | True | Which method is used to protect sensitive information during data transmission? |
| 129 | 134 | 66 |  | None | high | True | Which is the correct keyboard shortcut for adjusting the column width in MS Excel? |
| 130 | 135 | 66 |  | None | high | True | Which action should be taken in Microsoft Outlook to send a received email to another person, while keeping the original message f |
| 131 | 136 | 66 |  | None | high | True | What security mechanism ensures that system updates are installed without user intervention? |
| 132 | 137 | 67 |  | None | high | True | Which keyboard shortcut is used for adding bullets in MS Word 2010? |
| 133 | 138 | 67 |  | None | high | True | Which device is commonly used to connect computers within a LAN? |
| 134 | 139 | 67 |  | None | high | True | What is the primary reason DRAM needs to be refreshed periodically? |
| 135 | 141 | 68 |  | None | high | True | Which feature in MS Word allows the user to apply a consistent look across text elements such as headings, titles and subtitles? |
| 136 | 142 | 68 |  | None | high | True | What is the main purpose of using a template when creating a presentation in MS PowerPoint? |
| 137 | 143 | 68 |  | None | low | True | Which of the following best describes Electronic Mail (E-mail)? |
| 138 | 144 | 69 |  | None | high | True | Match the Task Manager tabs in column A with their respective functionalities in column B. Column A Column B 1. Processes usage a) |
| 139 | 146 | 70 |  | None | high | True | Which of the following statements about computer memory is/are correct? RAM is volatile memory, meaning it loses data when power i |
| 140 | 147 | 70 |  | None | high | True | Select which of the given statement(s) is/are True or False for the Central Processing Unit (CPU) of the Computer Systems. (i) The |
| 141 | 149 | 71 |  | None | high | True | Match the file locating features in column A with their corresponding functionalities in column B. Column A / Column B 1. Search B |
