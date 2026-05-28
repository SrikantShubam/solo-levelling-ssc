# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2022_tier2_prepp_paper1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 150 / None
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [7, 35, 39, 41, 53, 54, 106, 110, 113, 115, 119, 121, 123, 125, 128, 145]
- Low-confidence global questions: []
- Manual review count: 16
- Canonical review count: 18

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 150 / None |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [7, 35, 39, 41, 53, 54, 106, 110, 113, 115, 119, 121, 123, 125, 128, 145] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 18 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 3 |
| 2 | 3 |
| 3 | 4 |
| 4 | 4 |
| 5 | 4 |
| 6 | 4 |
| 7 | 3 |
| 8 | 4 |
| 9 | 4 |
| 10 | 3 |
| 11 | 3 |
| 12 | 3 |
| 13 | 3 |
| 14 | 3 |
| 15 | 1 |
| 16 | 3 |
| 17 | 2 |
| 18 | 1 |
| 19 | 2 |
| 20 | 2 |
| 21 | 3 |
| 22 | 4 |
| 23 | 3 |
| 24 | 4 |
| 25 | 4 |
| 26 | 4 |
| 27 | 4 |
| 28 | 3 |
| 29 | 3 |
| 30 | 2 |
| 31 | 1 |
| 32 | 1 |
| 33 | 1 |
| 34 | 1 |
| 35 | 1 |
| 36 | 1 |
| 37 | 1 |
| 38 | 1 |
| 39 | 1 |
| 40 | 1 |
| 41 | 1 |
| 42 | 3 |
| 43 | 4 |
| 44 | 4 |
| 45 | 4 |
| 46 | 4 |
| 47 | 4 |
| 48 | 4 |
| 49 | 4 |
| 50 | 4 |
| 51 | 3 |
| 52 | 4 |
| 53 | 4 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 4: 44 20/29 | 4 | high | False | There are three taps of diameter 2 cm, 3 cm and 4 cm, respectively. The ratio of the water flowing through them is equal to the ra |
| 2 | 2 | 1 | 1: 22 : 25 | 1 | high | False | Two numbers are, respectively, 10% and 25% more than the third number. The ratio of the two numbers is: |
| 3 | 3 | 1 | 3: 8:9:12 | 3 | high | False | A, B and C did certain investments and the ratio of their time periods is 3 : 2 : 7 respectively. Ratio of the profits of A, B and |
| 4 | 4 | 2 | 3: 1,56,250 | 3 | high | False | A bike is sold for ₹87,500 by allowing a discount of 44% on its marked price. The marked price (in ₹) of the bike is: |
| 5 | 5 | 2 | 2: 0 | 2 | high | False | A,B, C are three points such that AB = 9 cm, BC = 11 cm and AC = 20 cm. The number of circles passing through points A,B,C is: |
| 6 | 6 | 2 | 2: 11/21 | 2 | high | False | A glass jar contains 6 white, 8 black, 4 red and 3 blue marbles. If a single marble is chosen at random from the jar, what is the  |
| 7 | 7 | 3 | 4: 28.33 | None | high | True | Find the mode for the given distribution (rounded off to two decimal places). Class Interval: 5-10, 10-15, 15-20, 20-25, 25-30, 30 |
| 8 | 8 | 3 | 4: ₹1,680 | 4 | high | False | If interest be compounded half-yearly, then find the compound interest on ₹8,000 at the rate of 20% per annum for 1 year. |
| 9 | 9 | 3 | 3: 308 | 3 | high | False | A basket contains 350 eggs. If 12% of the eggs are rotten, how many eggs are good enough to be sold? |
| 10 | 10 | 3 | 4: 18 cm | 3 | high | False | A circle touches all four sides of a quadrilateral ABCD. If AB = 18 cm, BC = 21 cm and AD = 15 cm, then length CD is: |
| 11 | 11 | 4 | 3: 4851 cm³ | 3 | high | False | What is the volume of the largest sphere that can be carved out of a wooden cube of sides 21 cm? (π = 22/7) |
| 12 | 12 | 4 | 4: 7 | 4 | high | False | Find the value of the given expression. √8 + √1681 |
| 13 | 13 | 4 | 4: 46 | 4 | high | False | Find the value of given expression. 30 - [40 - {56 - (25 - 13 - 12)}] |
| 14 | 14 | 4 | 1: 21120 | 1 | high | False | The ratio of the incomes of two employees is 7 : 4, and the ratio of their expenditures is 3 : 1. If each of them manages to save  |
| 15 | 15 | 5 | 2: 72.96% | 2 | high | False | If radius of a sphere is decreased by 48%, then by what percent does its surface area decrease? |
| 16 | 16 | 5 | 4: 2 | 4 | high | False | The product of the two numbers is 1500 and their HCF is 10. The number of such possible pairs is/are: |
| 17 | 17 | 5 | 2: 23.08% | 2 | high | False | A man buys a machine for Rs.5,000. After one year, he sells it for Rs.6000. After two years, again he buys the same machine at Rs. |
| 18 | 18 | 5 | 3: 0 | 3 | high | False | Evaluate the following. sin 25° sin 65° – cos 25° cos 65°. |
| 19 | 19 | 6 | 2: Only (i) and (iii) | 2 | high | False | In ΔPQR,PQ=QR and O is an interior point of ΔPQR such that ∠OPR=∠ORP. Consider the following statements: (i) ΔPQR is an isosceles  |
| 20 | 20 | 6 | 3: 7.98 | 3 | high | False | A man can row 10 km/h in still water. When the river is running at a speed of 4.5 km/h, then it takes him 2 h to row to a place an |
| 21 | 21 | 6 | 3: 45 | 3 | high | False | Find the average of the cubes of the first five natural numbers. |
| 22 | 22 | 6 | 1: 221 | 1 | high | False | For what value of m will the system of equations 17x+my+102=0 and 23x+299y+138=0 have infinite number of solutions? |
| 23 | 23 | 7 | 4: 1100 | 4 | high | False | A rectangular park is 120 m long and 104 m wide. A 1-m wide path runs along the boundary of the park, remaining completely inside  |
| 24 | 24 | 7 | 3: 29.16 litres | 4 | high | False | 40 litres of milk are kept in a container. 4 litres of milk were removed from this container and replaced with water. This procedu |
| 25 | 25 | 7 | 2: 3 1/3 % | 2 | high | False | The difference of simple interest from two banks on ₹8,000 in 3 years is ₹800. If the rate of interest per annum in two banks are  |
| 26 | 26 | 8 | 1: 45° and 15° | 1 | high | False | If tan(A + B) = √3 and tan(A - B) = 1/√3; 0° < (A + B) < 90°; A > B, then the values of A and B are ________, respectively. |
| 27 | 27 | 8 | 3: 172.5 | 3 | high | False | Two ships are on the opposite of a light house such that all three of them are collinear. The angles of depression of the two ship |
| 28 | 28 | 8 | 1: 20 | 1 | high | False | The arithmetic mean of the following data is ________. 23, 17,20,19,21 |
| 29 | 29 | 8 | 1: 4 | 1 | high | False | The number 5769116 is divisible by which of the following numbers? |
| 30 | 30 | 9 | 1: 14 | 1 | high | False | If 1/x + x = 4, then find 1/x^2 + x^2. |
| 31 | 1 | 9 | 3: Daughter's daughter | 3 | high | False | 'A # B' means 'A is the brother of B'. 'A @ B' means 'A is the daughter of B'. 'A & B' means 'A is the husband of B'. 'A % B' mean |
| 32 | 2 | 9 | 3: 7 : 352 | 3 | high | False | The second number in the given number-pairs is obtained by performing certain mathematical operation(s) on the first number. The s |
| 33 | 3 | 9 | 1: D | 2 | high | False | Six friends A, B, C, D, E and F are standing in a circle facing the centre. B is between F and C, A is between E and D, and F is t |
| 34 | 4 | 10 | 2: rʞɒɿTɒƧm | 2 | high | False | Select the correct mirror image of the given combination when the mirror is placed at 'PQ' as shown below. mS5aT7rakr |
| 35 | 5 | 10 | 1: Both I and II follow | None | high | True | In this question, a statement is followed by two courses of action, numbered I and II. You must assume everything in the statement |
| 36 | 6 | 10 | 2: Either data in statement I or statement II is | 1 | high | False | Given below is a question followed by two statements I and II. Read both the statements carefully to decide which one of them is s |
| 37 | 7 | 11 | 3: 5 | 3 | high | False | If + means –, – means ×, × means ÷, and ÷ means +, what will be the value of the following expression? 5 ÷ 5 + 5 – 10 × 10 = ? |
| 38 | 8 | 11 | 1: Data in statements I and II together is suffi | 1 | high | False | A question is given, followed by two statements numbered (I) and (II). You have to decide whether the data provided in the stateme |
| 39 | 9 | 11 | 4: 323 | None | high | True | Select the number from among the given options that can replace the question mark (?) in the following series. 58, 179, ?, 492, 68 |
| 40 | 10 | 12 | 2: Keynote | 2 | high | False | Three of the following words are alike in some manner and hence form a group. Which word does NOT belong to that group? (The words |
| 41 | 11 | 12 | 1: 100 | None | high | True | In a certain code language, ‘PAINT’ is written as ‘80’ and ‘DROP’ is written as ‘59’. How will ‘MARKET’ be written in that languag |
| 42 | 12 | 12 | 4: 4,5,6,2,3,1 | 4 | high | False | A number has been denoted to each of the given letters. Select the option from the following four possible arrangements of these n |
| 43 | 13 | 13 | 1: Figure 1 | 1 | high | False | Select the figure from the options that can replace the question mark (?) and complete the pattern. |
| 44 | 14 | 13 | 3: E W T G R Q W | 3 | high | False | Select the option that represents the letters that, when placed from left to right in the following blanks, will complete the lett |
| 45 | 15 | 13 | 4: × - ÷ + | 4 | high | False | Select the correct combination of mathematical signs to sequentially replace the * signs and balance the given equation. 21 * 3 *  |
| 46 | 16 | 14 | 1: Figure 1 | 1 | high | False | The sequence of folding a piece of paper and the manner in which the folded paper has been cut is shown below. Choose a figure whi |
| 47 | 17 | 14 | 2: # = FHT, % = NFJ | 4 | high | False | Which of the following letter-clusters should replace # and % so that the pattern and relationship followed between the letter-clu |
| 48 | 18 | 14 | 1: Two | 1 | high | False | All 32 students in a class are standing in a row facing north. Akash is 12th from the right end while Priya is 18th from the left  |
| 49 | 19 | 15 |  | 1 | high | False | Select the option in which the following figure is embedded. (Rotation is NOT allowed) |
| 50 | 20 | 16 | 3: Only 2 does not follow. | 3 | high | False | Three Statements are given followed by four conclusions numbered 1, 2, 3,and 4. Assuming the statements to be true, even if they s |
| 51 | 21 | 16 | 3: Both I and II are effects of independent caus | 4 | high | False | In this question, two statements I and II have been given. These statements may be independent causes or effects of independent ca |
| 52 | 22 | 16 | 4: Son | 4 | high | False | ‘A # B’ means ‘A is the brother of B’. ‘A @ B’ means ‘A is the daughter of B’. ‘A & B’ means ‘A is the husband of B’. ‘A % B’ mean |
| 53 | 23 | 17 |  | None | high | True | Out of the following five figures, four are alike in some manner and one differs from these in that manner. Select the odd figure. |
| 54 | 24 | 17 | 3: (16, 43, 22) | None | high | True | Select the set in which the numbers are related in the same way as are the numbers of the following sets. (NOTE : Operations shoul |
| 55 | 25 | 18 | 1: Figure 1 | 1 | high | False | Out of the following five figures, four are alike in some manner and one differs from these in that manner. Select the odd figure. |
| 56 | 26 | 19 |  | 2 | high | False | Figure A is related to B in a certain pattern. Following the same pattern, figure C is related to D. Study the pattern and select  |
| 57 | 27 | 19 | 3: 17 – 9 – 17 – 15 – 6 | 3 | high | False | In a certain language, the word CLOCK is written as 4 – 13 – 17 – 4 – 12. How will you write PHONE in the same language? |
| 58 | 28 | 20 | 3: Only conclusion II is true | 2 | high | False | In the following question, the statement is followed by two conclusions. Which of the two conclusions is/are true? Statement: M <  |
| 59 | 29 | 20 | 2: Figure 2 | 2 | high | False | Select the figure from among the given options that can replace the question mark (?) in the following series. |
| 60 | 30 | 21 | 3: If only II follows | 2 | high | False | Directions: A statement is given followed by two inferences I and II. You have to consider the statement to be true even if it see |
| 61 | 1 | 21 | 4: Tiny | 4 | high | False | Select the most appropriate ANTONYM of the underlined word. The colossal building stood amidst the ruins bearing signs of Victoria |
| 62 | 2 | 21 | 4: Sabotage | 2 | high | False | Select the option that can be used as a one-word substitute for the given group of words. Willful destruction |
| 63 | 3 | 22 | 3: ACBD | 1 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 64 | 4 | 22 | 3: face | 3 | high | False | Select the most appropriate option to fill in the blank. A good leader should be ready to ________ criticism. |
| 65 | 5 | 22 | 1: Barely managed to escape | 1 | high | False | Select the most appropriate meaning of the highlighted idiom. The youth involved in the accident escaped by the skin of his teeth. |
| 66 | 6 | 22 | 3: route | 3 | high | False | Select the correct homonym from the given options to fill in the blank. Which________does the minister take to reach the Assembly? |
| 67 | 7 | 23 | 4: S, P | 4 | high | False | For the four-sentence (S1 to S4) paragraph below, sentences S1 and S4 are given. From the options P, Q, R and S select the appropr |
| 68 | 8 | 23 | 2: No error | 1 | high | False | The following sentence has been divided into parts. One of them may contain an error. Select the part that contains the error from |
| 69 | 9 | 23 | 3: aloud | 3 | high | False | Select the most appropriate option to fill in the blank. Vishal is going to read the story _________. |
| 70 | 10 | 24 | 1: My father give up | 1 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. My father give u |
| 71 | 11 | 24 | 4: Desedent | 4 | high | False | Select the INCORRECTLY spelt word. |
| 72 | 12 | 24 | 2: Raghav asked Meera if she was upset with him. | 2 | high | False | Select the option that expresses the given sentence in reported speech. Raghav said to Meera, “Are you upset with me?” |
| 73 | 13 | 24 | 1: Someone has completed the task. | 1 | high | False | Select the option that expresses the given sentence in active voice. The task has been completed. |
| 74 | 14 | 25 | 3: Books can be bought online from Amazon. | 3 | high | False | Select the option that expresses the given sentence in passive voice. We can buy books online from Amazon. |
| 75 | 15 | 25 | 4: less tragic than | 1 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. If there is no need to substi |
| 76 | 16 | 25 | 2: d, a, b, c | 1 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 77 | 17 | 25 | 2: Lenient | 2 | high | False | Select the most appropriate ANTONYM of the underlined word. The new Principal of the school is stern, yet he understands the needs |
| 78 | 18 | 26 | 2: kill | 4 | high | False | Select the most appropriate option to fill in the blank. The friends decided to play cards to _________ time while waiting for the |
| 79 | 19 | 26 | 1: BDCA | 1 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 80 | 20 | 26 | 1: Shikha said that the heavy rain that week had | 1 | high | False | Select the option that expresses the given sentence in reported speech. Shikha said, “The heavy rain this week has spoiled all my  |
| 81 | 21 | 26 | 1: Narcissist | 1 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A person who admires himself or herself  |
| 82 | 22 | 27 | 4: systemetic | 4 | high | False | Identify the INCORRECTLY spelt word in the given sentence. One part of the philosophy of life’s meaning consists of the systemetic |
| 83 | 23 | 27 | 4: fashion | 4 | high | False | Replace the underlined word with its synonym to make the sentence more meaningful. Narcotic drug addiction is in vogue these days, |
| 84 | 24 | 27 | 3: at a stone's throw | 3 | high | False | Select the appropriate idiom that can replace the underlined phrase in the following sentence. My father’s office is at a close di |
| 85 | 25 | 27 | 2: BDAC | 2 | high | False | Given below are four jumbled sentences. Select the option that gives their correct logical sequence. A. They stand undefeated in t |
| 86 | 26 | 28 | 4: more | 4 | high | False | Select the most appropriate option to fill in the blank. The house they bought was__________spacious than their previous house. |
| 87 | 27 | 28 | 1: DCAB | 1 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 88 | 28 | 28 | 4: Please consider my request. | 3 | high | False | Select the option that expresses the given sentence in active voice. My request should be considered. |
| 89 | 29 | 29 | 2: My brother forbade me to play in the rain. | 2 | high | False | Select the option that expresses the given sentence in indirect speech. My brother said to me, “Don’t play in the rain.” |
| 90 | 30 | 29 | 2: a | 2 | high | False | Select the most appropriate option to fill in blank number 1. |
| 91 | 31 | 29 | 1: consists | 1 | high | False | Select the most appropriate option to fill in blank number 2. |
| 92 | 32 | 30 | 3: on | 3 | high | False | Select the most appropriate option to fill in blank number 3. |
| 93 | 33 | 30 | 3: few | 3 | high | False | Select the most appropriate option to fill in blank number 4. |
| 94 | 34 | 31 | 3: 5.86 lakh | 3 | high | False | In 2019, how many Indian students went abroad? |
| 95 | 35 | 32 | 4: China | 4 | high | False | Which of the following countries is not very popular with Indian students for studies? |
| 96 | 36 | 33 | 2: from the Immigration Statistics Report | 2 | high | False | How do we know the number of students getting visas for studies in UK? |
| 97 | 37 | 34 | 4: Indians going abroad for higher studies | 4 | high | False | The passage is mainly about |
| 98 | 38 | 35 | 3: Decline | 3 | high | False | Select the most appropriate ANTONYM of the word 'accept' from the passage. |
| 99 | 39 | 36 | 2: Lake Heaven | 4 | high | False | Select an appropriate title for the passage. |
| 100 | 40 | 37 | 3: Serene | 3 | high | False | What is the tone of the passage? |
| 101 | 41 | 38 | 3: A pair of shorts | 3 | high | False | What is the protagonist wearing in the bus? |
| 102 | 42 | 39 | 2: a Chinese spy balloon flying over US and Cana | 2 | high | False | The passage is mainly about |
| 103 | 43 | 40 | 2: Both A and B are true and B is the correct re | 1 | high | False | Read the statements given below. A. The US Air Force shot down the Chinese balloon over US territorial waters. B. Tensions between |
| 104 | 44 | 41 | 3: it's reconnaissance aircraft saw the antennas | 3 | high | False | How did US make sure that the Balloon flying over its territory was a ‘spy’ balloon? |
| 105 | 45 | 42 | 1: adjoining | 1 | high | False | The word 'contiguous' means |
| 106 | 1 | 42 | 3: Minhaj-us-Siraj | None | high | True | Who composed Tabaqat-i-Nasiri in the Delhi Sultanate period? |
| 107 | 2 | 42 | 3: Resistance of a wire depends on the length an | 3 | high | False | Identify the correct statement. |
| 108 | 3 | 43 | 2: Andre Marie Ampere | 1 | high | False | Which scientist suggested that the magnet must also exert an equal and opposite force on the current-carrying conductor? |
| 109 | 4 | 43 | 2: 1950 | 1 | high | False | In which year was the Estimates Committee constituted for the first time in India? |
| 110 | 5 | 43 | 1: 1 and 2 only | None | high | True | Identify which of the following statements are correct. 1.Hindustan Copper Limited (HCL) was incorporated on 9 November 1967. 2.Th |
| 111 | 6 | 43 | 1: Directive Principles of State Policy | 1 | high | False | Which part of the Constitution of India consists of the idea of a Welfare State? |
| 112 | 7 | 44 | 3: Finance Commission | 3 | high | False | Which of the following is constituted under Article 280 of the Constitution of India? |
| 113 | 8 | 44 | 4: Only statements I and II | None | high | True | In India, which of the following statements is true about the National Investment Fund? Statements: I. It was created in 2005. II. |
| 114 | 9 | 44 | 4: Madhya Pradesh | 4 | high | False | Bhimbetka, a noted site of the Palaeolithic period, is located in which state of India? |
| 115 | 10 | 44 | 4: a-ii, b-i, c-iv, d-iii | None | high | True | Match List-I and List-II regarding the National Sports awards 2022. List-I a) Arjun Award b) Dronacharya Award Regular c) Dronacha |
| 116 | 11 | 45 | 2: Indian Councils Act, 1909 | 2 | high | False | The Act that is also known as ‘Morley-Minto Reforms’ is: |
| 117 | 12 | 45 | 4: Thiamine | 4 | high | False | Which of the following was the first B vitamin discovered in 1897? |
| 118 | 13 | 45 | 2: 1924 | 3 | high | False | In which year did Albert Einstein predict a new state of matter, the Bose-Einstein condensate (BEC), based on a quantum formulatio |
| 119 | 14 | 45 | 1: 10th | None | high | True | What was India's rank in the Asia-Pacific Personalised Health Index released by the Economist Intelligence Unit in January 2021? |
| 120 | 15 | 46 | 3: Both Statements A and B correct | 3 | high | False | Which of the following options is correct regarding sexually transmitted disease (STD)? Statement A: Sexually transmitted diseases |
| 121 | 16 | 46 | 3: Agonist | None | high | True | What do you call the type of drugs that mimic the natural messenger by switching on the receptor? |
| 122 | 17 | 46 | 4: The southeast monsoon season | 4 | high | False | Identify a type of season that is NOT a part of the four seasons of India. |
| 123 | 18 | 46 | 4: A, B and C | None | high | True | Which of the following statements are correct regarding the benefits of the retired President of India? A. The former President of |
| 124 | 19 | 47 | 1: Switzerland – Denmark – Japan – Niger | 3 | high | False | Which option correctly represents the countries in decreasing order of HDI, as released in September 2022? |
| 125 | 20 | 47 | 2: 1 and 3 only | None | high | True | Identify which of the following statements about agriculture in India are correct. 1. Rabi crops are sown in India from October to |
| 126 | 21 | 47 | 1: Bihar | 1 | high | False | Which state recorded the lowest literacy rate in the 2011 census? |
| 127 | 22 | 47 | 4: Vitamin K | 4 | high | False | Deficiency of which of the following vitamins causes excessive bleeding from wounds? |
| 128 | 23 | 48 | 4: A only | None | high | True | Which of the following statements is/are correct regarding changes to Atal Pension Yojana Scheme (APY) done in 2022? A. According  |
| 129 | 24 | 48 | 4: Construction of school buildings | 4 | high | False | Which of the following is considered a capital expense? |
| 130 | 25 | 48 | 1: 6 Ω | 1 | high | False | A light bulb working on a 18 V battery draws a current of 3 A. What will be the resistance of the bulb? |
| 131 | 1 | 48 | 1: Trojan | 1 | high | False | _______ is a type of malware that is often disguised as legitimate software. |
| 132 | 2 | 49 | 4: Ribbon | 2 | high | False | In MS-Excel 365 which of the following appears across the top of the screen and below the title bar and contains all the commands, |
| 133 | 3 | 49 | 3: Solid-State Drive | 3 | high | False | ________ is also known as electronic disk. |
| 134 | 4 | 49 | 4: Registers | 2 | high | False | ________ is a high-speed device used in CPU that is utilised to store data temporarily during processing. |
| 135 | 5 | 49 | 2: Cache memory stores data in permanent use. | 2 | high | False | Which among the following statements is incorrect? |
| 136 | 6 | 50 | 4: Custom Print | 4 | high | False | Which of the following option of print settings is used to choose only specific pages in MS-Word 365? |
| 137 | 7 | 50 | 1: Control Panel | 1 | high | False | _______ displays a list of utility configure the computer system and install software and hardware. |
| 138 | 8 | 50 | 4: A :10 | 3 | high | False | Which of the following is correct option in MS-Excel 365, if a value in a cell of column A and row 10 is to be referred in a funct |
| 139 | 9 | 50 | 2: uploading | 2 | high | False | While _______, data transfers from the customers' machine to the server. |
| 140 | 10 | 51 | 2: Can print multiple copies at a time | 1 | high | False | Which among the following is incorrect about Laser Printers? |
| 141 | 11 | 51 | 2: changing the color behind the selected text | 2 | high | False | Shading option in MS-Word 365 is used for ________. |
| 142 | 12 | 51 | 3: All are e-mail service providers | 3 | high | False | Which of the following is NOT an example of e-mail service provider? I. Outlook II. Gmail III. Yandex |
| 143 | 13 | 52 | 3: Trojan self-replicate and infects other files | 2 | high | False | Which among the following statements is incorrect? |
| 144 | 14 | 52 | 3: main | 4 | high | False | The memory unit that communicates directly with the CPU is called ______ memory. |
| 145 | 15 | 52 | 4: Instruction Buffer Register (IBR) | None | high | True | The instruction that is not to be executed immediately is placed in the ______. |
| 146 | 16 | 52 | 4: 15 | 4 | high | False | Video Graphics Array connectors are those which connect the monitor to a computer's video card and has ______ holes. |
| 147 | 17 | 53 | 2: F5 | 2 | high | False | Which of the following is keyboard shortcut to reload the current page in Google search engine? |
| 148 | 18 | 53 | 1: Ctrl + K | 1 | high | False | Which among the following keyboard shortcuts is used to insert a hyperlink for the selected text in Microsoft Word? |
| 149 | 19 | 53 | 3: Gateway | 3 | high | False | _______ is a passage to connect two networks that may work on different networking models. |
| 150 | 20 | 53 | 2: Third-party | 2 | high | False | _______ cookies track you and expose your privacy. |
