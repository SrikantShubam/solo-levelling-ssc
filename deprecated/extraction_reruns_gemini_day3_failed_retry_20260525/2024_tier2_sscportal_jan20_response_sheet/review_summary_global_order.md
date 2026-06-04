# Full PDF Visual Extraction

- Source PDF: `answer_key_candidates_staging\2024_tier2_sscportal_jan20_response_sheet.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 150 / None
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [19, 34, 40, 109, 114, 116]
- Low-confidence global questions: []
- Manual review count: 6
- Canonical review count: 29

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 150 / None |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [19, 34, 40, 109, 114, 116] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 29 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 0 |
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
| 13 | 2 |
| 14 | 2 |
| 15 | 1 |
| 16 | 2 |
| 17 | 3 |
| 18 | 2 |
| 19 | 3 |
| 20 | 3 |
| 21 | 2 |
| 22 | 1 |
| 23 | 2 |
| 24 | 3 |
| 25 | 3 |
| 26 | 0 |
| 27 | 3 |
| 28 | 3 |
| 29 | 3 |
| 30 | 3 |
| 31 | 3 |
| 32 | 3 |
| 33 | 3 |
| 34 | 3 |
| 35 | 3 |
| 36 | 3 |
| 37 | 2 |
| 38 | 2 |
| 39 | 2 |
| 40 | 2 |
| 41 | 2 |
| 42 | 2 |
| 43 | 2 |
| 44 | 3 |
| 45 | 4 |
| 46 | 3 |
| 47 | 3 |
| 48 | 4 |
| 49 | 4 |
| 50 | 3 |
| 51 | 3 |
| 52 | 4 |
| 53 | 4 |
| 54 | 4 |
| 55 | 3 |
| 56 | 0 |
| 57 | 4 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 3: 1330 | 3 | high | False | ABCD is a quadrilateral in which diagonal BD = 70 cm, AI |
| 2 | 2 | 1 | 4: 47 hours | 1 | high | False | A tank when full can be emptied by an outlet pipe A in 5.6 hours, while an inlet pipe B can fill the same empty tank in 7 hours. I |
| 3 | 3 | 3 | 3: 21 : 10 | 3 | high | False | If a : b = 2 : 3, b : c = 5 : 7, then find the ratio c : a. |
| 4 | 4 | 3 |  | 1 | high | False | In a circle centered at O, a diameter AB is extended to a point C outside the circle. CD is a tangent at point D on the circle. If |
| 5 | 5 | 3 |  | 3 | high | False | If x = 4 + √6 and y= 4 - √6 then the value of x² + y² is: |
| 6 | 6 | 4 | 2: p^2 / (q * sqrt(q^2 - p^2)) | 2 | high | False | If cos27° = p/q, then find the value of cosec27° - cos63°. |
| 7 | 7 | 4 | 3: 93 | 3 | high | False | The average of first 92 even numbers is |
| 8 | 8 | 4 | 4: 25z^2 + 74y^2 | 4 | high | False | Simplify (5z - 7y)^2 + (7z + 5y)^2 - 49z^2 |
| 9 | 9 | 5 | 1: 41/841 | 1 | high | False | Let PQR be a right angled triangle, right-angled at R. Let PQ = 29 cm, QR = 21 cm and ∠Q = θ. Find the value of cos ² θ – sin ² θ. |
| 10 | 10 | 5 | 2: (a¹) × (b⁻⁵) × (c⁻²) | 2 | high | False | (a⁵ × b³ × c⁷) / (a⁴ × b⁸ × c⁹) in simplified form is: |
| 11 | 11 | 5 | 4: 31128 | 4 | high | False | Which number among 38211, 38121, 32118, and 31128 is divisible by 24? |
| 12 | 12 | 6 | 2: 10.29 km/hr | 2 | high | False | P and Q take part in 400 m race. P runs at 12 km/hr. P gives Q a start of 20 m and still beats him by 13 seconds. The speed of Q i |
| 13 | 13 | 6 | 4: 58 | 4 | high | False | The ratio of the ages of two friends is 4 : 3 which will become 6 : 5 after 4 years. What will be the sum of their ages (in years) |
| 14 | 14 | 6 | 4: 14/255 | 4 | high | False | If sin A = 5/13, then find the value of (cos A - 2 tan A) / (sin A + 3 tan A). |
| 15 | 15 | 7 | 3: 810 | 3 | high | False | A man sells a mobile phone for ₹680 and loses something. If he had sold it for ₹1070, his gain would have been double the former l |
| 16 | 16 | 7 | 3: 17248 | 3 | high | False | If the diameter of the base of a cone is 56 cm and its curved surface area is 3080 cm², then what will be its volume (in cm³)? (Us |
| 17 | 17 | 7 | 1: Independent | 2 | high | False | If A and B are two events such that P(A∪B) = 3/4, P(A∩B) = 1/4 and P(Aᶜ) = 2/3, then P(B) is: |
| 18 | 18 | 8 | 4: 47.5 | 4 | high | False | Find the median of the following data. Class interval 0 – 20 20 – 40 40 – 60 60 – 80 80 – 100 Frequency 9 16 24 15 4 |
| 19 | 19 | 8 | 2: 8030220 | None | high | True | Two years ago, the population of a town was 9487500. Due to migration to big cities, it decreases every year at the rate of 8%. Th |
| 20 | 20 | 8 | 4: ₹480 | 4 | high | False | Adi and Dia together have ₹1,440. If 3/10 of Adi's amount is equal to 3/5 of Dia's amount, how much amount does Dia have? |
| 21 | 21 | 9 | 1: 2³ × 9³ × 13² × 19² | 1 | high | False | The LCM of 2³ × 9² × 13, 2² × 13² × 19 and 9³ × 13² × 19² is: |
| 22 | 22 | 9 |  | 1 | high | False | 8 kg of maize costing ₹51 per kg, is mixed with 9 kg of maize costing ₹68 per kg. The average per kg price of mixed maize is: |
| 23 | 23 | 9 | 3: 26 | 3 | high | False | Find the simple interest (in ₹) on ₹2000 at 6.5% per annum rate of interest for the period from 13 February 2023 to 27 April 2023 |
| 24 | 24 | 10 | 2: 14.5 | 2 | high | False | The age of some students is given in years as 12, 13, 16, 18,14, 19, 13, 17, 15 and 11. The median age (in years) of the students  |
| 25 | 25 | 10 | 2: 16.67% | 2 | high | False | Murlidhar, the owner of a grocery store, offers a discount scheme 'buy 5 water bottles get 1 for free' to his customers. What is t |
| 26 | 26 | 10 | 2: 12 years | 2 | high | False | The present ages of Sweeta and Suman are in the ratio 4 : 5 |
| 27 | 27 | 11 | 3: 200000 | 3 | high | False | Amit gets 6% increase in his sale amount in the first year and 20% in the second year, with that his present sale is ₹254400, what |
| 28 | 28 | 11 | 2: 17.70 | 1 | high | False | Akshay places three identical rings of diameter 21 cm in such a manner that each one touches the other two rings. He observes that |
| 29 | 29 | 11 | 2: 67° | 2 | high | False | In a circle with centre O, an arc ABC subtends an angle of 134° at the centre of the circle. The chord AB is produced to a point P |
| 30 | 30 | 12 | 4: 864 | 4 | high | False | The ratio between the length and the breadth of a rectangular park is 3 : 2, and the perimeter of the park is 120 m. Find the area |
| 31 | 1 | 12 |  | 2 | high | False | Identify the figure given in the options which when put in place of the question mark (?) will logically complete the series. |
| 32 | 2 | 13 | 4: Data in statements (I) and (II) together are  | 4 | high | False | A question is followed by two statements numbered (I) and (II). You have to decide whether the data provided in the statements are |
| 33 | 3 | 13 |  | 1 | high | False | Read the following information and answer the question which follows. “Like seasoned gardeners, Gardener G practices crop rotation |
| 34 | 4 | 14 | 4: 521 - 20 | None | high | True | Four number-pairs have been given, out of which three are alike in some manner and one is different. Select the one that is differ |
| 35 | 5 | 14 | 3: 3 | 1 | high | False | In a certain code language, ‘CURB’ is coded as ‘3517’ and ‘BOAT’ is coded as ‘4638’. What is the code for ‘B’ in the given code la |
| 36 | 6 | 15 | 1: Figure 1 | 1 | high | False | Select the option figure that will replace the question mark (?) in the figure given below to complete the pattern. |
| 37 | 7 | 16 |  | 2 | high | False | Select the option figure in which the given figure is embedded as its part (rotation is NOT allowed). |
| 38 | 8 | 16 |  | 1 | high | False | What will come in the place of the question mark (?) in the following equation, if '+' and '-' are interchanged and 'x' and '÷' ar |
| 39 | 9 | 17 | 4: 8 | 4 | high | False | Select the number from among the given options that can replace the question mark (?) in the following series. 98, 50, 26, 14, ?,  |
| 40 | 10 | 17 | 1: One | None | high | True | How many six-lettered meaningful words can be formed using all these letters but each letter only once in the word. R F I G E D |
| 41 | 11 | 17 | 1: 1, 5, 2, 4, 3 | 1 | high | False | Select the correct option that indicates the arrangement of the following words in a logical and meaningful order. 1. Set goals 2. |
| 42 | 12 | 18 | 4: Data in Statements I and II together is suffi | 4 | high | False | A question is given, followed by two statements labelled I and II. Identify which of the statements is/are sufficient to answer th |
| 43 | 13 | 18 | 1: Wife's Father's Mother's Brother | 2 | high | False | In a certain code language, P + Q means ‘P is the mother of Q’, P – Q means ‘P is the brother of Q’, P x Q means ‘P is the wife of |
| 44 | 14 | 19 | 3: Both I and II are possible effects. | 3 | high | False | Given below is a statement (Cause) followed by possible effects numbered I, II and III. Read the ‘Cause’ carefully and decide whic |
| 45 | 15 | 19 | 4: 28 | 4 | high | False | Paras ranked 5th from the top and 24th from the bottom in his class. How many students are there in his class? |
| 46 | 16 | 19 | 3: # = VYD % = KNS | 3 | high | False | Which of the following letter-clusters should replace # and % so that the pattern and relationship followed between the letter-clu |
| 47 | 17 | 20 | 3: Mother's mother's brother | 3 | high | False | In a certain code language, A + B means ‘A is the mother of B’, A – B means ‘A is the brother of B’, A x B means ‘A is the wife of |
| 48 | 18 | 20 | 4: Figure 4 | 4 | high | False | Select the correct mirror image of the given combination when the mirror is placed at line MN as shown. 4BvGF72 |
| 49 | 19 | 20 | 3: 54 | 2 | high | False | Seven people A, B, C, D, E, F and G, scored different marks (out of 100) in an exam. G scored the lowest marks. B scored second hi |
| 50 | 20 | 21 | 2: One | 2 | high | False | Each of the digits in the number 3571869 is arranged in ascending order from left to right. The position(s) of how many digits wil |
| 51 | 21 | 21 | 3: x+-÷ - Text | 3 | high | False | Three of the following four pairs are alike in a certain way and thus form a group. Which is the pair that does not belong to that |
| 52 | 22 | 22 |  | 3 | high | False | Figure A is related to B in a certain pattern. Following the same pattern, figure C is related to D. Study the pattern and select  |
| 53 | 23 | 23 | 4: Neither conclusion (I) nor (II) is true. | 4 | high | False | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 54 | 24 | 23 | 3: Both I and II follow. | 2 | high | False | In this question, a statement is followed by two courses of action, numbered I and II. You must assume everything in the statement |
| 55 | 25 | 24 | 2: Figure 2 | 2 | high | False | Select the correct mirror image of the given combination when the mirror is placed at line MN as shown. 47F29M8 |
| 56 | 26 | 24 | 3: 123 | 3 | high | False | 17 is related to 159 following a certain logic. Following the same logic, 11 is related to 105. To which of the following is 13 re |
| 57 | 27 | 24 |  | 4 | high | False | Four of the following five figures are alike in a certain way and thus form a group. Which is the one that does NOT belong to that |
| 58 | 28 | 25 |  | 1 | high | False | In a certain code language, ‘he enjoys music’ is coded as ‘lo po jo’ and ‘music and dance’ is coded as ‘kb jo fk’. How is ‘music’  |
| 59 | 29 | 25 | 1: 3, 4, 1, 2, 5 | 4 | high | False | Select the correct option that indicates the arrangement of the following words in a logical and meaningful order. 1. Plant 2. Pol |
| 60 | 30 | 25 |  | 2 | high | False | M, N, O, X, Y and Z are sitting around a circular table facing the centre (but not necessarily in the same order). O is an immedia |
| 61 | 1 | 27 | 4: He said that he would need a copy of the docu | 2 | high | False | Select the option that expresses the given sentence in indirect speech. He said, "I shall need a copy of the documents." |
| 62 | 2 | 27 | 4: ABDC | 4 | high | False | Sentences of a paragraph are given below. While the first and the last sentences (1 and 6) are in the correct order, the sentences |
| 63 | 3 | 27 | 1: democracy | 1 | high | False | Select the most appropriate option that can substitute the underlined words in the given sentence. The nation has chosen the gover |
| 64 | 4 | 28 |  | 2 | high | False | Select the most appropriate ANTONYM of the given word. Thrifty |
| 65 | 5 | 28 |  | 3 | high | False | Select the most appropriate idiom to fill in the blank. A lot of people are still ______ over the GDP issue. |
| 66 | 6 | 28 | 3: finest | 3 | high | False | Select the most appropriate option to fill in the blank. Prescription safety glasses provide the _______________ tailored protecti |
| 67 | 7 | 29 | 4: Indispensable | 4 | high | False | Select the correct spelling of the incorrectly spelt word in the given sentence. Good characteristics are indispensible to succeed |
| 68 | 8 | 29 | 2: Narcissist | 2 | high | False | Select the option that can be used as a one-word substitute for the given group of words. Someone who loves and admires himself th |
| 69 | 9 | 29 | 1: Q, R, S, P | 1 | high | False | A sentence has been split up into segments and given below in jumbled order. While the first and the last segments of the sentence |
| 70 | 10 | 30 |  | 2 | high | False | Parts of a sentence are given below in jumbled order. Arrange the parts in the correct order to form a meaningful sentence. Throug |
| 71 | 11 | 30 |  | 1 | high | False | Select the option that can be used as a one-word substitute for the given group of words. Someone who walks on foot |
| 72 | 12 | 30 | 2: Practitionaire | 4 | high | False | Select the INCORRECTLY spelt word. |
| 73 | 13 | 31 | 3: a colour | 1 | high | False | Select the most appropriate option to fill in the blank. The blueberries in the basket are blue. The denotation of the word 'blue' |
| 74 | 14 | 31 | 1: The soldier told his fellow soldiers that he  | 1 | high | False | Select the option that expresses the given sentence in reported speech. The soldier said to his fellow soldiers, "I have buried ou |
| 75 | 15 | 31 | 3: Exacerbate | 3 | high | False | Select the most appropriate ANTONYM of the word given below. Ameliorate |
| 76 | 16 | 32 | 4: Blasphemy | 4 | high | False | Select the option that can be used as a one-word substitute for the given group of words. Speaking disrespectfully about sacred or |
| 77 | 17 | 32 |  | 3 | high | False | Select the option that expresses the following sentence in passive voice. After we come to power at the Centre, we will conduct a  |
| 78 | 18 | 32 | 2: I, you and she | 2 | high | False | The following sentence has been split into four segments. Identify the segment that contains a grammatical error. I, you and she/  |
| 79 | 19 | 33 | 2: Charm | 2 | high | False | Select the most appropriate synonym of the given word. Charisma |
| 80 | 20 | 33 |  | 2 | high | False | Select the option that expresses the given sentence in passive voice. Scientists have recently discovered a new species of marine  |
| 81 | 21 | 33 | 3: arena | 3 | high | False | Select the most appropriate option that can substitute the underlined words in the given sentence. In the makeshift place of activ |
| 82 | 22 | 34 | 4: laughter | 4 | high | False | Select the most appropriate option to fill in the blank. The comedian's jokes were so funny that the entire audience erupted in __ |
| 83 | 23 | 34 | 3: Kanhaiya asked me if I wanted to sing. | 3 | high | False | Select the option that expresses the given sentence in indirect speech. Kanhaiya said to me, “Do you want to sing?” |
| 84 | 24 | 34 | 3: not my cup of tea | 3 | high | False | Complete the dialogue for Person B using the correct idiom. Person A: We are all going to the club this weekend. Do you want to co |
| 85 | 25 | 35 | 3: Let your car not be parked here. | 3 | high | False | Select the option that expresses the given sentence in passive voice. Don't park your car here. |
| 86 | 26 | 35 | 1: most interesting | 1 | high | False | Select the most appropriate option to fill in the blank. This is the __________ book that I have read till now. |
| 87 | 27 | 35 | 2: the | 1 | high | False | Select the most appropriate article to fill in the blank. Rabindranath Tagore, __________ poet, was famous for his poetical work,  |
| 88 | 28 | 36 | 3: has done everything | 1 | high | False | The given sentence is divided into four segments. Identify the segment that contains a grammatical error. When I returned to the o |
| 89 | 29 | 36 | 2: Pleasant | 1 | high | False | Select the most appropriate ANTONYM of the given word. Melancholy |
| 90 | 30 | 36 | 4: physical | 3 | high | False | Select the most appropriate option to fill in blank 1. |
| 91 | 31 | 37 | 3: dying | 3 | high | False | Select the most appropriate option to fill in blank 2. |
| 92 | 32 | 37 | 2: loneliness | 2 | high | False | Select the most appropriate option to fill in blank 3. |
| 93 | 33 | 38 | 2: spirituality | 2 | high | False | Select the most appropriate option to fill in blank 4. |
| 94 | 34 | 38 | 2: mental development | 2 | high | False | Cognitive development in a child is related to: |
| 95 | 35 | 39 | 2: Analytical skill | 2 | high | False | Which skill is used by a reader when he gathers information and breaks it down in a logical pattern to solve a problem? |
| 96 | 36 | 39 | 2: To learn new information to avail opportunity | 2 | high | False | According to the passage, what is the role of reading? |
| 97 | 37 | 40 | 4: Critical skill | 4 | high | False | Which skill is used by a reader when he evaluates the same information and makes judgments based on evidence? |
| 98 | 38 | 40 | 3: scum | 3 | high | False | Select the most appropriate synonym of the word 'impurities' from the options given below. |
| 99 | 39 | 41 | 3: To facilitate the separation of liquid from s | 3 | high | False | In the extraction process described, what is the purpose of allowing the water and fine sediment at the bottom of the tank to sett |
| 100 | 40 | 41 | 1: Informative and instructional | 1 | high | False | What is the overall tone of the passage? |
| 101 | 41 | 42 | 4: The intricate process of harvesting and proce | 4 | high | False | What is the central theme of the passage describing the extraction process of indigo dye from the Indigofera plant? |
| 102 | 42 | 42 | 1: Exercise releases endorphins, contributing to | 1 | high | False | Which of the following is a fact mentioned in the passage? |
| 103 | 43 | 43 | 3: Informative | 3 | high | False | Determine the tone of the passage by choosing the option that reflects the overall emotional quality of the writing. |
| 104 | 44 | 43 |  | 1 | high | False | Select the option that provides an accurate summary of the main points discussed in the passage. |
| 105 | 45 | 44 | 4: Importance of Regular Physical Activities | 4 | high | False | Select the most appropriate title for the given passage. |
| 106 | 1 | 44 | 4: Connecting India to the World in Amrit Kaal:  | 1 | high | False | Which theme encapsulates Wings India 2024, the Aviation Expo, that was inaugurated by Union Minister for Civil Aviation in January |
| 107 | 2 | 44 | 1: Coulomb's law | 2 | high | False | The equation F = k (q1 * q2 / r^2) is representation of: (Where F is the attractive or repulsive electric force of two point charg |
| 108 | 3 | 45 | 4: An advocate of supreme court for at least ten | 4 | high | False | Which of the following is NOT the qualification for the appointment of judges of supreme court? |
| 109 | 4 | 45 | 3: BWk | None | high | True | Which letter code indicates mid-latitude desert climate in Köppen climate classification? |
| 110 | 5 | 45 | 2: third | 2 | high | False | The Kushan emperor Kanishka, who ruled from the late first to the early/ mid-second century AD was the __________ Kushan ruler. |
| 111 | 6 | 45 | 3: Forest Owlet | 1 | high | False | Which endemic species of owl of Central India is listed as Endangered in the IUCN Red List since 2018? |
| 112 | 7 | 46 | 4: 1972 | 1 | high | False | In which year was the fluid mosaic model proposed by Singer and Nicolson? The model commonly represented cell membrane structure a |
| 113 | 8 | 46 | 2: To calculate Purchasing Power Parities (PPPs) | 2 | high | False | What is the primary goal of the International Comparison Programme (ICP), led by the United Nations Statistics Division (UNSD)? |
| 114 | 9 | 46 | 1: Tryptophan | None | high | True | Which amino acid is a precursor to serotonin, a neurotransmitter that regulates your appetite, sleep and mood? |
| 115 | 10 | 47 | 2: Secunderabad | 2 | high | False | Which of the following is the headquarters of the South Central Zone of Indian Railways? |
| 116 | 11 | 47 | 1: 16.8% | None | high | True | According to Census of India 2011, what was the recorded population growth rate of Hindu religion? |
| 117 | 12 | 47 | 2: MILAN (Minority Loan Accounting for NMDFC) | 1 | high | False | What is the name of the software launched by the National Minorities Development and Finance Corporation (NMDFC) for digitising lo |
| 118 | 13 | 48 | 2: Yamuna | 4 | high | False | Which of the following is NOT an antecedent river in India? |
| 119 | 14 | 48 |  | 1 | high | False | Which substance is commonly used as an acid-base indicator, which turns red in acidic solutions and blue in basic solutions? |
| 120 | 15 | 48 |  | 2 | high | False | In which of the following years did Mahatma Gandhi lead the Satyagraha and hunger strike for the first time in India? |
| 121 | 16 | 48 | 1: Champakam Doraijan Case, 1951 | 3 | high | False | In which of the following cases did the Supreme court of India give a ruling that, 'in case of any conflict between the fundamenta |
| 122 | 17 | 49 | 4: Muhammad bin Tughluq | 3 | high | False | Who was the first sultan (in the recorded history of the Dargah Sharif) to visit the shrine of khwaja Muinuddin Chisti? |
| 123 | 18 | 49 | 4: United Nations Framework Convention on Climat | 4 | high | False | Which international treaty was adopted in 1992 to combat global warming and prepare for its effects? |
| 124 | 19 | 49 | 4: Satwiksairaj Rankireddy | 1 | high | False | Who set a new Guinness World Record for the fastest badminton shot, measuring a speed of 565 km/hr in July 2023? |
| 125 | 20 | 49 | 2: 1932 | 2 | high | False | When did James Chadwick prove the existence of the neutron – an elementary particle devoid of any electric charge? |
| 126 | 21 | 50 | 3: VV Giri | 4 | high | False | Who among the following was the President of India when India launched its first Nuclear test in Pokhran? |
| 127 | 22 | 50 | 1: Archimedes | 3 | high | False | Who discovered the laws of levers and pulleys, which allow us to move heavy objects using small forces? |
| 128 | 23 | 50 | 4: Wheat and rice | 4 | high | False | The productivity of which of the following crops had initially increased due to the Green Revolution? |
| 129 | 24 | 51 |  | 2 | high | False | Which of the following best defines liberalisation? |
| 130 | 25 | 51 | 2: Hockey | 2 | high | False | In which sport did India defeat Pakistan 2-1 to lift the Men's Junior Asia Cup in 2023, overtaking them in winning the maximum tit |
| 131 | 1 | 51 | 1: .exe | 1 | high | False | Which file extension is most commonly used for executable installation files on a Windows system? |
| 132 | 2 | 52 | 4: Storing the BIOS or firmware | 4 | high | False | ROM is primarily used for which of the following purposes? |
| 133 | 3 | 52 | 2: For providing an additional layer of security | 2 | high | False | What is the purpose of enabling passwords on a PC? |
| 134 | 4 | 52 | 3: Editing emails that are yet to be sent | 3 | high | False | Which of the following actions can typically be performed in the Outbox? |
| 135 | 5 | 52 | 1: An antivirus program relying on system utilit | 1 | high | False | Which of the following scenarios correctly illustrates the interdependence of system software and application software? |
| 136 | 6 | 53 | 3: Ctrl + M | 3 | high | False | Which keyboard shortcut is used to increase the indent in a paragraph in MS Word 2010? |
| 137 | 7 | 53 | 2: Press Esc | 2 | high | False | How can you exit a slide show and return to editing mode in MS PowerPoint? |
| 138 | 8 | 53 | 1: Hashing | 1 | high | False | The ________ method is commonly used to verify the integrity of data. |
| 139 | 9 | 53 | 1: File -> New -> Blank Presentation | 1 | high | False | What are the correct steps for creating a blank presentation in MS PowerPoint? |
| 140 | 10 | 54 |  | 2 | high | False | Which option in MS Word allows a user to align text within a document to the left, center, right, or justify it across the page? |
| 141 | 11 | 54 | 3: Fiber Optic Cable | 3 | high | False | What type of media is commonly used for WAN communication? |
| 142 | 12 | 54 | 3: The existing rows are shifted down. | 3 | high | False | What happens when a user inserts a new row into an MS Excel worksheet? |
| 143 | 13 | 54 |  | 1 | high | False | Why do desktop and laptop operating systems require more advanced memory management techniques than embedded systems? |
| 144 | 14 | 55 | 2: Counts the number of cells | 2 | high | False | What does the function COUNT() do in MS Excel 2010? |
| 145 | 15 | 55 | 4: Layer 3 Switch | 4 | high | False | In a Local Area Network (LAN), which of the following is most commonly used to ensure that data packets are efficiently forwarded  |
| 146 | 16 | 55 | 3: Only 1 | 3 | high | False | Which of the following statements about the Central Processing Unit (CPU) is/are correct? The CPU is often referred to as the 'bra |
| 147 | 17 | 57 | 3: 8 bits | 2 | high | False | What is the size of each ASCII character in bits? |
| 148 | 18 | 57 | 2: Unusual system slowdowns and unexpected error | 2 | high | False | What is a common sign that a computer might be infected with a virus? |
| 149 | 19 | 57 | 3: It marks the start and end of each part in a  | 2 | high | False | In a multipart email message, what does the boundary parameter in the Content-Type header signify? |
| 150 | 20 | 57 | 4: To prompt for permission before making system | 4 | high | False | What is the role of User Account Control (UAC) in Windows when modifying system settings? |
