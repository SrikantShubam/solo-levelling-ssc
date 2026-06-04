# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2023_tier2_prepp_paper1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 150 / None
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [5, 9, 10, 13, 16, 18, 19, 24, 25, 28, 30, 34, 54, 81, 110, 111, 121, 123, 124, 125, 129, 132, 138, 139, 149]
- Low-confidence global questions: []
- Manual review count: 25
- Canonical review count: 31

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 150 / None |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [5, 9, 10, 13, 16, 18, 19, 24, 25, 28, 30, 34, 54, 81, 110, 111, 121, 123, 124, 125, 129, 132, 138, 139, 149] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 31 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 3 |
| 2 | 3 |
| 3 | 3 |
| 4 | 3 |
| 5 | 3 |
| 6 | 3 |
| 7 | 3 |
| 8 | 3 |
| 9 | 3 |
| 10 | 3 |
| 11 | 3 |
| 12 | 2 |
| 13 | 3 |
| 14 | 3 |
| 15 | 3 |
| 16 | 3 |
| 17 | 3 |
| 18 | 2 |
| 19 | 2 |
| 20 | 3 |
| 21 | 2 |
| 22 | 2 |
| 23 | 3 |
| 24 | 3 |
| 25 | 3 |
| 26 | 3 |
| 27 | 3 |
| 28 | 3 |
| 29 | 3 |
| 30 | 3 |
| 31 | 3 |
| 32 | 2 |
| 33 | 2 |
| 34 | 2 |
| 35 | 2 |
| 36 | 2 |
| 37 | 2 |
| 38 | 2 |
| 39 | 2 |
| 40 | 2 |
| 41 | 2 |
| 42 | 3 |
| 43 | 2 |
| 44 | 3 |
| 45 | 3 |
| 46 | 3 |
| 47 | 4 |
| 48 | 2 |
| 49 | 3 |
| 50 | 3 |
| 51 | 3 |
| 52 | 3 |
| 53 | 3 |
| 54 | 3 |
| 55 | 3 |
| 56 | 1 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 1: -38 | 1 | high | False | The average of 25, 46 and ‘y’ is 11. What is the value of ‘y’? |
| 2 | 2 | 1 | 3: 160 m | 3 | high | False | From the top of a tower, the angle of depression of the top of a 10 m high building is 60°. If the distance between the tower and  |
| 3 | 3 | 1 | 1: 21% | 1 | high | False | A merchant fixes the sale price of his goods at 42% above the cost price. He sells his goods at a 15% discount marked price. His p |
| 4 | 4 | 2 | 3: 11 | 3 | high | False | A set of data presented in the form of a frequency distribution table with class intervals and their respective frequencies had a  |
| 5 | 5 | 2 | 1: 60° | None | high | True | An equilateral triangle ABC surmounts a square BCDE. The value of ∠EAB + 3∠AEB is: |
| 6 | 6 | 2 | 4: 195 | 4 | high | False | The marks obtained by 15 students out of a maximum of 25 in a test are given as 13, 11, 16, 15, 18, 12, 13, 14, 10, 22, 15, 21, 20 |
| 7 | 7 | 3 | 2: ₹1,65,000 | 2 | high | False | Two friends A and B started a business by investing ₹1,50,000 and ₹2,50,000, respectively. They agreed to distribute their earning |
| 8 | 8 | 3 | 3: 4500 | 3 | high | False | The ratio of the length, width and height of a closed cuboid is given as 6 : 3 : 2. The total surface area of this cuboid is given |
| 9 | 9 | 3 | 4: 26.67% | None | high | True | B purchased 15 kg apples at the rate of ₹180 per kg from a wholesaler who uses a weight of 950 grams for the kg weight. B sold all |
| 10 | 10 | 4 | 3: 29/25 | None | high | True | If P(A ∪ B) = 5/9, P(Ā ∪ B̄) = 13/27, P(A) = 11/18, then the odds against the event B are: |
| 11 | 11 | 4 | 4: 120 kg | 4 | high | False | The average weight of the first thirteen persons among fourteen persons is 78 kg. The weight of the 14th person is 39 kg more than |
| 12 | 12 | 4 | 1: 53.2% | 1 | high | False | What is the single discount equivalent to the successive discounts of 20%, 35%, and 10%? |
| 13 | 13 | 5 | 1: 5/338 | None | high | True | Three cards are drawn one after another with replacement from a pack of cards. What is the probability of getting first card a Jac |
| 14 | 14 | 5 | 1: 20 | 1 | high | False | At a certain time in a park, the number of heads and the number of legs of monkeys and human visitors were counted, and it was fou |
| 15 | 15 | 5 | 1: 432 | 1 | high | False | Vipin travels one-third of the distance of a journey at a speed of 30 km/h and the remaining distance at a speed of 40 km/h. If he |
| 16 | 16 | 6 | 3: 131 : 77 | None | high | True | 80 litres of a mixture of spirit and water in the ratio 7 : 9 is present in a container A. 20 litres of the mixture is transferred |
| 17 | 17 | 6 | 1: 1728 | 1 | high | False | A solid cube, whose each edge is of length 48 cm, is melted. Identical solid cubes, each of volume 64 cm³, are made out of this mo |
| 18 | 18 | 6 | 2: 1/72 | None | high | True | What is the value of [1/8 + {1/6 × (36/45 ÷ 24/25) - (12/21 × 14/15 ÷ 24/45)} + 27/36]? |
| 19 | 19 | 7 | 2: 36 m | None | high | True | Two pillars of equal height stand on either side of a roadway which is 150 m wide. At a point in the road between pillars, the ele |
| 20 | 20 | 7 | 4: 20 | 4 | high | False | The cost of 2 pencils and 3 pens is ₹55 and the cost of 7 pencils and 2 pens is ₹65. What is the total price (in ₹) of one pen and |
| 21 | 21 | 7 | 4: 7 : 11 : 10 | 4 | high | False | If P : Q = 3 : 4 and Q : R = 4 : 7, then find the value of (P + Q) : (Q + R) : (R + P). |
| 22 | 22 | 8 | 1: 56 | 1 | high | False | A six-digit number 11p9q4 is divisible by 24. Then the greatest possible value for pq is: |
| 23 | 23 | 8 | 4: 2 | 4 | high | False | The compound interest on ₹10,000 at 20% per annum is ₹4,641. If the compounding is done half-yearly, then for how many years was t |
| 24 | 24 | 8 | 1: 2016 | None | high | True | Hari, Kamal and Lalit contested an election in which 6050 votes were polled and none of the votes were invalid. Kamal got 42% more |
| 25 | 25 | 9 | 3: 9 7/27 | None | high | True | A and B can complete a job together in 12.5 days; B and C can complete the same job together in 18.75 days, while C and A can comp |
| 26 | 26 | 9 | 4: 26 years | 4 | high | False | The average age of A, B and C is 20 years. Two years ago the sum of the ages of A and B was 6 more than that of C. Find the presen |
| 27 | 27 | 9 | 1: 31/66 | 1 | high | False | Find the value of √1.24 × √2.79 / √2.64 × √5.94 |
| 28 | 28 | 10 | 2: 1 | None | high | True | If A = 58^2 - 25^2 / 46^2 - 37^2, B = 26^2 - 15^2 / 56^2 - 15^2, then the value of 1/B - 20/A is: |
| 29 | 29 | 10 | 4: 420 | 4 | high | False | The simple interest earned on ₹2,800 at a rate of 10% per annum for 3 years is ₹x and ₹1,736 is the simple interest earned on ₹6,2 |
| 30 | 30 | 10 | 4: r ≥ 10.25 | None | high | True | One chord of a circle is given as 20.5 cm. Then the radius (r) of the circle must be: |
| 31 | 1 | 11 | 1: Only conclusion IV is true. | 1 | high | False | A statement is followed by four conclusions. Which of the conclusions is/are true based on the given statement? Statement: I < M < |
| 32 | 2 | 11 | 1: Only I is a possible reason. | 1 | high | False | Given below is a statement followed by two possible reasons numbered I and II. Read the statement carefully and decide which of th |
| 33 | 3 | 11 | 3: 19114 | 3 | high | False | What should come in place of the question mark (?) in the given series? 18, 74, 298, 1194, 4778, ? |
| 34 | 4 | 12 | 1: Figure 1 | None | high | True | Identify the figure given in the options which when put in place of (?) will logically complete the series. |
| 35 | 5 | 12 | 4: 55 | 4 | high | False | What approximate value will come in place of the question mark (?) in the following equation? 49.85 – 5.31 + 9.97 = ? |
| 36 | 6 | 13 | 1: (3, 3, 9) | 1 | high | False | Select the set in which the numbers are related in the same way as are the numbers of the following sets. (NOTE: Operations should |
| 37 | 7 | 13 | 1: 5, 2, 3, 1, 4 | 1 | high | False | Select the correct option that indicates the arrangement of the given words in a logical and meaningful order. 1. Shirt piece 2.Th |
| 38 | 8 | 13 | 2: CJRSB | 2 | high | False | Select the combination of letters that when sequentially placed in the blanks of the given series will complete the series. A_DF G |
| 39 | 9 | 14 | 2: One | 2 | high | False | Each of the digits in the number 7148356 is arranged in ascending order from left to right. The position of how many digits will r |
| 40 | 10 | 14 | 4: 469 | 4 | high | False | What will come in the place of the question mark (?) in the following equation if '+' and '-' are interchanged and 'x'and '÷' are  |
| 41 | 11 | 14 | 2: 10 | 2 | high | False | A certain number of people are sitting in a row, facing north. N is sitting third to the left of P. M is sitting third to the left |
| 42 | 12 | 15 | 2: Close : Distant | 2 | high | False | Three of the following word pairs are alike in some manner and hence form a group. Which word pair does not belong to that group?  |
| 43 | 13 | 15 | 4: 479 | 4 | high | False | What will come in the place of the question mark (?) in the following equation if '+' and '-' are interchanged and 'x'and '÷' are  |
| 44 | 14 | 15 | 2: Statements I and II together are not sufficie | 2 | high | False | A question is given, followed by two statements labelled I and II. Identify which of the statements is/are sufficient to answer th |
| 45 | 15 | 16 | 3: B | 3 | high | False | Four of the following five figures are alike in a certain way and thus form a group. Which is the one that does NOT belong to that |
| 46 | 16 | 16 | 3: Neither inference I nor II is true. | 1 | high | False | One statement is given, and it is followed by two inferences numbered I and II. Read the statement and decide which of the inferen |
| 47 | 17 | 16 | 3: Both (I) and (II) together are needed. | 3 | high | False | In this question, a question is followed by two statements numbered (I) and (II). You have to decide whether the data provided in  |
| 48 | 18 | 17 | 4: Steep | 4 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. (The words mu |
| 49 | 19 | 17 | 2: 633 | 2 | high | False | What will come in the place of the question mark (?) in the following equation if '+' and '-' are interchanged and 'x'and '÷' are  |
| 50 | 20 | 17 | 1: Father | 1 | high | False | Q is the mother of R. P is the husband of Q. S is the brother of R. How is P related to S? |
| 51 | 21 | 18 | 2: A | 2 | high | False | Seven people, A, B, C, D, E, F and G are sitting in a straight line, facing north. Only three people sit to the left of D. Only tw |
| 52 | 22 | 18 | 3: AZPYRY | 3 | high | False | Select the combination of letters that when sequentially placed in the blanks of the given series will make it logically complete. |
| 53 | 23 | 19 |  | 3 | high | False | Figure A is related to B in a certain pattern. Following the same pattern, figure C is related to D. Study the pattern and select  |
| 54 | 24 | 19 | 4: One | None | high | True | How many meaningful English words can be formed with the second, fourth, fifth, and sixth letters of the word HOCKEY (when counted |
| 55 | 25 | 20 | 2: 11-89 | 2 | high | False | Three of the following four number-pairs are alike in a certain way and thus form a group. Which is the pair that does not belong  |
| 56 | 26 | 20 | 2: MCWDLQ | 2 | high | False | In a certain code language, ‘BUTTER’ is coded as ‘CWWSC0’ and ‘THEORY’ is coded as ‘UJHNPV’. How will ‘LATENT’ be coded in that la |
| 57 | 27 | 20 | 2: Only conclusion (II) follows | 2 | high | False | Read the given statements and conclusions carefully. You have to take the given statements to be true even if they seem to be at v |
| 58 | 28 | 21 | 2: Figure 2 | 2 | high | False | Select the option figure that will replace the question mark (?) in the figure given below to complete the pattern. |
| 59 | 29 | 21 | 4: 3 | 4 | high | False | In a certain code language, ‘CARD’ is coded as ‘7359’, ‘SERV’ is coded as ‘1256’and ‘PACK’ is coded as ‘8497’. What is the code fo |
| 60 | 30 | 22 | 3: Figure 3 | 3 | high | False | When the below given diagram is folded in the shape of a cube which symbol will face opposite to '^'? |
| 61 | 1 | 22 | 3: whom I | 3 | high | False | Parts of the following sentence have been given as options. Select the option that contains an error. This is the book whom I want |
| 62 | 2 | 23 | 3: respect those | 3 | high | False | Parts of the following sentence have been given as options. Select the option that contains an error. Everyone should respect thos |
| 63 | 3 | 23 | 1: B | 4 | high | False | The following sentence has been divided into four parts. One of them contains an error. Select the part that contains the error fr |
| 64 | 4 | 23 | 4: The speaker's emphasiss is | 1 | high | False | Parts of the following sentence have been given as options. Select the option that contains an error. The speaker's emphasiss is o |
| 65 | 5 | 24 | 3: vacillates | 3 | high | False | The given sentence has an error which has been underlined. The underlined word is given as options with some changes. Select the o |
| 66 | 6 | 24 | 3: will have done | 3 | high | False | Select the most appropriate option to fill in the blank. By this time tomorrow, I ________ the work assigned to me. |
| 67 | 7 | 24 | 1: Hold onto | 1 | high | False | Select the most appropriate phrasal verb to fill in the blank. . ________ that thought. It will be a great idea someday. |
| 68 | 8 | 25 | 2: He said that two and two make four. | 2 | high | False | Select the option that expresses the given sentence in indirect speech. He said, “Two and two make four.” |
| 69 | 9 | 25 | 3: The director presented the award to her. | 3 | high | False | Select the option that expresses the given sentence in active voice. The award was presented to her by the director. |
| 70 | 10 | 25 | 3: insignificant | 3 | high | False | Read the given sentence carefully and fill in the blank by selecting the correct synonym of the word given in the brackets. The au |
| 71 | 11 | 26 | 3: granary | 3 | high | False | Select the option that can be used as a one-word substitute for the underlined part of the given sentence. There is a place for gr |
| 72 | 12 | 26 | 4: Who taught you English grammar and compositio | 4 | high | False | Select the option that expresses the following sentence in active voice. By whom were you taught English grammar and composition? |
| 73 | 13 | 26 | 1: The principal said to me, “You are in-charge  | 1 | high | False | Select the most appropriate option in direct speech. |
| 74 | 14 | 27 | 2: Despite the pain, Sarah decided to go ahead w | 2 | high | False | Select the sentence which gives the most appropriate meaning of the given idiom. Bite the bullet |
| 75 | 15 | 27 | 4: The students eagerly awaited their results. | 4 | high | False | Select the option that arranges the given words to form a grammatically correct and meaningful sentence. The students eagerly thei |
| 76 | 16 | 27 | 2: rose | 2 | high | False | Select the most appropriate option to fill in the blank. Robin watched as the smoke ________ steadily from the chimney. |
| 77 | 17 | 28 | 2: most challenging | 2 | high | False | Select the most appropriate option in the superlative degree that can substitute the underlined segment in the given sentence. Thi |
| 78 | 18 | 28 | 4: live in first floor | 3 | high | False | The following sentence has been divided into parts. One of them may contain an error. Select the part that contains the error from |
| 79 | 19 | 28 | 2: articulation | 2 | high | False | Select the option that can be used as a one-word substitute for the underlined phrase in the following sentence. She was known for |
| 80 | 20 | 29 | 2: He said that he had bought that book for his  | 2 | high | False | Select the option that expresses the given sentence in indirect speech. He said, “I bought this book for my brother.” |
| 81 | 21 | 29 | 1: Let the access be denied. | None | high | True | Select the option that expresses the given sentence in passive voice. Access denied. |
| 82 | 22 | 29 | 1: has seen | 1 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. We / has seen /  |
| 83 | 23 | 30 | 4: wise | 4 | high | False | Select the option that rectifies the underlined part of the given sentence. In case no correction is needed, select ‘No correction |
| 84 | 24 | 30 | 4: Throw a round stone to create ripples in the  | 4 | high | False | The given sentence has an error. Choose the option that corrects the error Throw a rounder stone to create ripples in the water. |
| 85 | 25 | 30 | 2: a universal | 2 | high | False | Select the option that rectifies the underlined part of the given sentence. In case no correction is needed, select ‘No correction |
| 86 | 26 | 31 | 2: more | 2 | high | False | Select the option that will improve the underlined part of the following sentence. He is taller and most handsome than his friend. |
| 87 | 27 | 31 | 3: cold | 3 | high | False | Select the most appropriate option to fill in the blank. The girl was ________ as she was drenched in the rain. |
| 88 | 28 | 31 | 3: oar | 3 | high | False | Select the most appropriate option to fill in the blank. You use an ________ to steer a boat. |
| 89 | 29 | 32 |  | 1 | high | False | Select the most appropriate idiom to fill in the blank. Despite their differences, the two politicians decided to _________ and wo |
| 90 | 30 | 32 | 2: focus | 2 | high | False | Select the most appropriate option to fill in blank no. 1. |
| 91 | 31 | 33 |  | 4 | high | False | Select the most appropriate option to fill in blank no. 2. |
| 92 | 32 | 33 | 2: perpetuate | 2 | high | False | Select the most appropriate option to fill in blank no. 3. |
| 93 | 33 | 34 | 1: engage | 1 | high | False | Select the most appropriate option to fill in blank no. 4. |
| 94 | 34 | 34 | 4: Descriptive | 4 | high | False | Identify the structure of the passage. |
| 95 | 35 | 35 | 1: Steel is used in almost every tool and machin | 1 | high | False | Why is steel often called the backbone of modern industry? |
| 96 | 36 | 35 | 2: Informative | 3 | high | False | What is the tone of the passage? |
| 97 | 37 | 36 | 1: Steel Industry | 1 | high | False | Select an appropriate title for the passage from the given options. |
| 98 | 38 | 36 | 1: The Migratory Journey of the Sapphire-winged  | 3 | high | False | Select the most appropriate title for the given passage. |
| 99 | 39 | 37 | 4: Researchers are using satellite tracking devi | 4 | high | False | Which statement best reflects a fact mentioned in the given passage? |
| 100 | 40 | 37 | 4: Glimpse | 4 | high | False | Identify the most appropriate ANTONYM of the word ‘stare’ from the passage. |
| 101 | 41 | 38 |  | 1 | high | False | Based on the given passage, which of the following inferences can be made? |
| 102 | 42 | 38 | 4: Turns grapes into wine | 4 | high | False | What does the fermentation process do? |
| 103 | 43 | 39 | 3: Juicy | 3 | high | False | Based on your reading of the passage, select the most appropriate word which best describes ‘luscious’. |
| 104 | 44 | 39 | 2: California | 2 | high | False | In which region do grapes ripen in August? |
| 105 | 45 | 40 | 1: Grapes and its uses | 3 | high | False | Select the most appropriate title for the passage. |
| 106 | 1 | 40 | 3: Dr Zakir Hussain | 3 | high | False | Who was the second vice-President of India? |
| 107 | 2 | 41 | 4: A-4, B-1, C-2, D-3 | 4 | high | False | Match the following Characteristics/Other Name Name of River A. Area of Badland topography 1. Godavari B. Vridh Ganga 2. Brahmaput |
| 108 | 3 | 41 | 2: Personal income | 3 | high | False | Which of the following options represents the total income earned by individuals from all the sources before deduction of personal |
| 109 | 4 | 42 | 2: A-3, B-1, C-4, D-2 | 2 | high | False | Match List-I with List-II. List-I (Chemical compound) List-II (Spices) A. Curcuminoids 1. Cardamom B. 1,8-cineole 2. Black pepper  |
| 110 | 5 | 42 | 2: Hiuen Tsang | None | high | True | According to which of the following foreign travellers did Dhruvasena II attend Harsha's assembly at Prayag (Allahabad)? |
| 111 | 6 | 42 | 1: Karnataka | None | high | True | The Constitution (Scheduled Tribes) Order (Fourth Amendment) Bill, 2022 was passed in Rajya Sabha in December 2022. It seeks to am |
| 112 | 7 | 43 | 4: 1-B, 2-C, 3-A | 4 | high | False | Match the following subject matters with their concerned Articles. a 1. Superintendence, direction and control of elections to be  |
| 113 | 8 | 43 | 2: A-iv, B-i, C-ii, D-iii | 2 | high | False | Match the positions in List I with the states in List II, related to the 36th National Games 2022, and select the correct answer f |
| 114 | 9 | 44 | 4: Mediterranean regions | 4 | high | False | Which of the following are some regions in the world, known for their thriving citrus fruit production? |
| 115 | 10 | 44 | 1: about 4,50,00,00,000 years | 1 | high | False | Based on current scientific knowledge, it is currently postulated that the Earth has an estimated age of: |
| 116 | 11 | 44 | 2: Kinetic Energy | 2 | high | False | What kind of energy is associated with falling coconuts, speeding cars, rolling stones and flying aircraft? |
| 117 | 12 | 45 | 3: A-1, B-2, C-3, D-4 | 1 | high | False | Match the following details regarding Phase-I of Bharatmala Project. Scheme Targeted Length (in km) A. Economic corridors 1. 9000  |
| 118 | 13 | 45 | 4: Chhattisgarh | 4 | high | False | In September 2022, the Government of __________ decided to launch a campaign aimed at women's safety titled 'Hamar Beti Hamar Maan |
| 119 | 14 | 45 | 3: Rajasthan | 3 | high | False | According to Census of India 2011, in which of the following states was the gap in the literacy rates of males and females, highes |
| 120 | 15 | 46 | 4: i-a, ii-c, iii-b | 4 | high | False | Match the following Prime Ministers of India with the Five-Year Plans they initiated. List-1 (Prime Ministers) i : Jawaharlal Nehr |
| 121 | 16 | 46 | 4: Swaran Singh Committee | None | high | True | Which Committee had suggested a penalty or punishment for the non-performance of Fundamental Duties? |
| 122 | 17 | 46 | 1: Glaucoma | 1 | high | False | Among the choices listed, which one is NOT a form of cancer? |
| 123 | 18 | 47 | 3: Uttar Pradesh | None | high | True | In September 2022,the ____________ Assembly sets aside one day for women MLAs to speak about women issues such as safety, health,  |
| 124 | 19 | 47 | 2: Abdul Hamid Lahori | None | high | True | Who among the following has written the ‘Badshah Nama’? |
| 125 | 20 | 47 | 2: 6.17 × 10⁻²¹ J | None | high | True | What will be the average kinetic energy per molecule in SI units for an ideal gas at a temperature of 25°C? |
| 126 | 21 | 47 | 3: Limited access to essential services for marg | 3 | high | False | Which of the following is a possible criticism of privatisation? |
| 127 | 22 | 48 | 2: Inert gases | 2 | high | False | What are the elements in group zero commonly known as? |
| 128 | 23 | 48 | 2: A 3, B 4, C 2, D 1 | 2 | high | False | Match List-I with List-II. List-I (Acid) List-II (Food Source) A. Carbonic acid 1. Mustard oil B. Lauric acid 2. Butter C. Butyric |
| 129 | 24 | 49 | 3: Only (i) and (iii) | None | high | True | Identify the INCORRECTLY matched pair(s) of the British Governor-Generals of India and the events with which they are associated.  |
| 130 | 25 | 49 | 3: Malaria | 3 | high | False | Among the following diseases, which one is NOT inherited? |
| 131 | 1 | 49 | 4: Internet Service Provider | 4 | high | False | A/An ______ is an organisation that connects its subscriber’s computer using modem to the Internet. |
| 132 | 2 | 50 | 4: Netscape | None | high | True | Which of the following is an example of GUI-based user agent in email? |
| 133 | 3 | 50 | 3: Layout | 3 | high | False | In MS Office 365, the Page Setup dialog box can be found under which of the following tabs? |
| 134 | 4 | 50 | 1: two | 1 | high | False | When the sender and receiver of an email are on the same system, we need only ______ user agents. |
| 135 | 5 | 51 | 3: View | 3 | high | False | In File Explorer of Windows 11, which of the following tabs includes the ‘hidden items’ option? |
| 136 | 6 | 51 | 3: Providing temporary storage for data that the | 3 | high | False | What is the primary purpose of RAM (Random Access Memory) in a computer? |
| 137 | 7 | 51 | 3: The intersection of a row and a column in a w | 3 | high | False | What is a cell in Microsoft Excel? |
| 138 | 8 | 52 | 1: Switch | None | high | True | Which networking device operates at Layer 2 of the OSI model and forwards data based on MAC addresses? |
| 139 | 9 | 52 | 1: Tape drive | None | high | True | Which backup device provides a convenient way to create system images and complete backups, but may require a lengthy restoration  |
| 140 | 10 | 52 | 2: It adds up the values in a range. | 2 | high | False | In MS-Excel 2019, what does the SUM function do? |
| 141 | 11 | 53 | 1: Facebook | 1 | high | False | Which of the following is NOT an example of web browser? |
| 142 | 12 | 53 | 2: To store frequently used data for faster acce | 2 | high | False | What is the function of the cache memory in a computer's memory hierarchy? |
| 143 | 13 | 53 | 2: Ctrl + C | 2 | high | False | What is the keyboard shortcut for 'Copy' in most Windows applications? |
| 144 | 14 | 54 |  | 3 | high | False | What is a ‘Firewall’ in the context of network security? |
| 145 | 15 | 54 | 3: cache | 3 | high | False | A high speed memory is placed between the Central Processing Unit (CPU) and the primary memory known as ________ memory. |
| 146 | 16 | 54 | 3: Memory Address Register | 3 | high | False | In computer registers, MAR stands for ________. |
| 147 | 17 | 55 |  | 4 | high | False | What is a ‘Trojan’ in the context of network security? |
| 148 | 18 | 55 | 4: To view how the document will appear when pri | 4 | high | False | In Microsoft Word, what is the purpose of the ‘Print Preview’ feature? |
| 149 | 19 | 55 |  | None | high | True | In File Explorer of Windows 10, the keyboard shortcut ‘Num Lock + Asterisk sign (*)’ is used to ________. |
| 150 | 20 | 56 | 2: Touchscreen | 2 | high | False | Which of the following is an example of the input device in a computer? |
