# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2023_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [8, 18, 26, 28, 35, 36, 40, 41, 43, 44, 45, 49, 54, 55, 61, 72, 73, 74, 83, 92]
- Low-confidence global questions: []
- Manual review count: 20
- Canonical review count: 35

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [8, 18, 26, 28, 35, 36, 40, 41, 43, 44, 45, 49, 54, 55, 61, 72, 73, 74, 83, 92] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 35 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 1 |
| 2 | 3 |
| 3 | 4 |
| 4 | 2 |
| 5 | 2 |
| 6 | 1 |
| 7 | 3 |
| 8 | 4 |
| 9 | 5 |
| 10 | 5 |
| 11 | 5 |
| 12 | 5 |
| 13 | 5 |
| 14 | 4 |
| 15 | 4 |
| 16 | 4 |
| 17 | 4 |
| 18 | 3 |
| 19 | 3 |
| 20 | 4 |
| 21 | 5 |
| 22 | 4 |
| 23 | 4 |
| 24 | 5 |
| 25 | 4 |
| 26 | 3 |
| 27 | 2 |
| 28 | 2 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 |  | 2 | high | False | Select the option figure which is embedded in the given figure. (Rotation is NOT allowed). |
| 2 | 2 | 2 | 4: 3, 6, 5, 2, 4, 1 | 4 | high | False | Select the option that represents the correct order of the given words as they would appear in an English dictionary. 1. Warriors  |
| 3 | 3 | 2 | 1: Only conclusion III follows | 1 | high | False | Three statements are given, followed by four conclusions numbered I, II, III and IV. Assuming the statements to be true, even if t |
| 4 | 4 | 2 | 1: Smell | 1 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. (The words mu |
| 5 | 5 | 3 | 3: Cousin | 1 | high | False | Ganesh was taking a walk with his mother’s brother’s father’s granddaughter. Who was he walking with? |
| 6 | 6 | 3 | 4: Figure 4 | 2 | high | False | Select the correct mirror image of the given figure when the mirror is placed at MN as shown below. Te 2 9 E K P M ————— N |
| 7 | 7 | 3 | 2: AH | 2 | high | False | Which of the following letter-clusters will replace the question mark (?) in the given series? UV, OY, IB, EE, ? |
| 8 | 8 | 3 | 3: 15 : 9 | None | high | True | The second number in the given number-pairs is obtained by performing certain mathematical operation(s) on the first number. The s |
| 9 | 9 | 4 |  | 2 | high | False | Select the figure that will replace the question mark (?) in the following figure series. |
| 10 | 10 | 4 | 3: 3 | 3 | high | False | Three different positions of the same dice are shown. Find the number on the face opposite the face showing ‘1’. |
| 11 | 11 | 5 | 1: (33, 11, 9) | 1 | high | False | Select the set in which the numbers are related in the same way as are the numbers of the following sets. (55, 11, 25) (64,16, 16) |
| 12 | 12 | 5 | 4: CJU | 4 | high | False | Select the option that is related to the sixth letter-cluster in the same way as the first letter-cluster is related to the second |
| 13 | 13 | 6 |  | 2 | high | False | Select the figure from the options that can replace the question mark (?) and complete the given pattern. |
| 14 | 14 | 7 | 1: Figure 1 | 1 | high | False | Select the Venn diagram that best illustrates the relationship between the following classes. Ticket, Aeroplane, Rail |
| 15 | 15 | 7 | 3: HJKP | 3 | high | False | Four letter-clusters have been given, out of which three are alike in some manner and one is different. Select the odd letter-clus |
| 16 | 16 | 7 | 4: 96 | 4 | high | False | Select the option that is related to the fifth number in the same way as the second number is related to the first number and the  |
| 17 | 17 | 8 | 1: 39 | 2 | high | False | Which of the following numbers will replace the question mark (?) in the given series? 8, 15, 26, ? , 56, 75 |
| 18 | 18 | 8 | 2: 3624 | None | high | True | Select the option that is related to the third term in the same way as the second term is related to the first term and the sixth  |
| 19 | 19 | 8 | 4: 3 | 4 | high | False | Three different positions of the same dice are shown. Find the number on the face opposite the face showing ‘4’. |
| 20 | 20 | 8 | 3: 10 | 3 | high | False | Select the option that is related to the fifth number in the same way as the second number is related to the first number and the  |
| 21 | 21 | 9 | 4: 92 | 4 | high | False | In a certain code language, 'ASK' is written as '62' and 'BYE' is written as '64'. How will 'CRY' be written in that language? |
| 22 | 22 | 9 | 4: ÷ − × + | 4 | high | False | Select the correct combination of mathematical signs that can sequentially replace the * signs and balance the given equation. 256 |
| 23 | 23 | 9 | 4: O L O X E L Y | 4 | high | False | Select the option that represents the letters that, when placed from left to right in the following blanks, will complete the lett |
| 24 | 24 | 9 | 2: EMDRF | 2 | high | False | In a certain code language, 'TABLE' is coded as ELEAT and 'SWING' is coded as GNLWS. How will 'FRAME' be coded in the same languag |
| 25 | 25 | 9 |  | 1 | high | False | Which two signs should be interchanged to make the given equation correct? 588 ÷ 28 × 32 + 72 − 160 = 760 |
| 26 | 1 | 10 | 4: 13.40 m | None | high | True | The length of the badminton court for singles is: |
| 27 | 2 | 10 | 4: The Comptroller and Auditor General | 4 | high | False | Who is the Administrative Head of the Indian Audit and Accounts Department? |
| 28 | 3 | 10 | 3: PM-ABHIM | None | high | True | Which of the following is the largest pan-India scheme to strengthen health care infrastructure across the country with focus on p |
| 29 | 4 | 10 | 4: Raksha Bandhan | 4 | high | False | Which of the following festivals is associated with the term ‘ties of protection’? |
| 30 | 5 | 10 | 1: Anshu Malik | 1 | high | False | In October 2021, 19-year-old ________ won the silver medal at the World Wrestling Championship. |
| 31 | 6 | 11 | 1: Bihar | 1 | high | False | ________ emerged as the poorest state as per the first-ever Multi-dimensional Poverty Index (MPI) prepared by Niti Aayog and launc |
| 32 | 7 | 11 |  | 1 | high | False | The consumption of fixed capital is also known as ________. |
| 33 | 8 | 11 | 4: Vitasta | 4 | high | False | The Vedic Aryans lived in the area called Sapt-Sindhu, which means area drained by seven rivers. One of the rivers among the seven |
| 34 | 9 | 11 |  | 1 | high | False | In Chola administration, ________ was the assembly in the villages which were inhabited predominantly by the Brahmanas. |
| 35 | 10 | 11 |  | None | high | True | Which of the following states is NOT a part of the Tapi Basin? |
| 36 | 11 | 12 | 4: Helium | None | high | True | Which of the following is used as a cooling medium for the Large Hadron Collider (LHC) and the superconducting magnets in MRI scan |
| 37 | 12 | 12 | 1: Bharatanatyam and Kathakali | 3 | high | False | In 2018, Google Doodle celebrated the 100th birthday of Mrinalini Sarabhai. She is an exponent of which of the following dance for |
| 38 | 13 | 12 | 2: Shaivism | 2 | high | False | Bharatanatyam expresses South Indian religious themes and spiritual ideas of ________. |
| 39 | 14 | 12 | 2: Vilayat Khan | 1 | high | False | Who among the following musicians is popular for his mastery over the musical instrument Sitar? |
| 40 | 15 | 12 | 3: India | None | high | True | Which of the following countries was the host of AFC Women's Asia Cup Football-2022? |
| 41 | 16 | 13 | 2: Chess | None | high | True | Ms Bhakti Pradip Kulkarni was conferred with the Arjuna Award 2022 for her outstanding contribution in which of the following spor |
| 42 | 17 | 13 | 2: Subhas Chandra Bose | 3 | high | False | Who among the following was the founder of 'Tiger Legion' or 'Free India Legion'? |
| 43 | 18 | 13 |  | None | high | True | Name a reproductive strategy in which parasites take advantage of the care of other individuals of the same species or different s |
| 44 | 19 | 13 | 1: (C), (B), (A) | None | high | True | On the basis of tribal population (2011), identify the option that arranges the following states in ascending order. A. Madhya Pra |
| 45 | 20 | 13 | 3: 1980 | None | high | True | In which industrial policy was the investment limit for tiny industry/unit increased to ₹2 lakh? |
| 46 | 21 | 14 | 3: Fred Hoyle | 2 | high | False | Which scientist thought of the concept of steady state of the universe? |
| 47 | 22 | 14 | 2: i-b, ii-a, iii-d, iv-c | 2 | high | False | Match the columns. Colum-A (Class) Column-B (Common name) i. Chlorophyceae a. Brown algae ii. Phaeophyceae b. Green algae iii. Rho |
| 48 | 23 | 14 | 2: Ricardian theory of rent | 2 | high | False | Ryotwari system of revenue collection in India, introduced by the British, was based on the ________. |
| 49 | 24 | 14 | 2: Jacobus Henricus van 't Hoff | None | high | True | Who received the Nobel Prize in 1901 for ‘recognition of the extraordinary services rendered by the discovery of the laws of chemi |
| 50 | 25 | 15 | 2: Articles 5 to 11 | 2 | high | False | Which of the following Articles of the Indian Constitution are related to citizenship? |
| 51 | 1 | 15 | 4: 105 5/19 % | 4 | high | False | If A is 95% of B, then what per cent of A is B? |
| 52 | 2 | 15 | 2: 20% | 2 | high | False | The marked price of mustard oil is 25% more than its cost price. At what percentage less than the marked price should it be sold t |
| 53 | 3 | 15 | 1: 24 2/5 | 1 | high | False | A can complete a piece of work in 25 days while B can complete the same work in 30 days. They work on alternate basis, starting wi |
| 54 | 4 | 16 |  | None | high | True | As part of his journey, a person travels 120 km at 80 km/h, the next 100 km at 40 km/h, and comes back to the starting point at 75 |
| 55 | 5 | 16 |  | None | high | True | 8 men can complete a work in 45 days. 8 women can complete the same work in 18 days. In how many days will 5 men and 8 women, toge |
| 56 | 6 | 16 |  | 1 | high | False | 6^25 + 6^26 + 6^27 + 6^28 is divisible by: |
| 57 | 7 | 16 |  | 1 | high | False | Study the given table and answer the question that follows. The table shows the classification of 100 students based on the marks  |
| 58 | 8 | 17 | 2: 16 cm | 3 | high | False | Two concentric circles are of radii 10 cm and 6 cm. Find the length of the chord of the larger circle which touches the smaller ci |
| 59 | 9 | 17 |  | 1 | high | False | If sin (a + b) = 1 and cos (a - b) = 1/2, then find a. |
| 60 | 10 | 17 | 1: 60 s | 1 | high | False | A train 900 m long is running at 108 km/h. How long will it take to clear a 900 m long platform completely? |
| 61 | 11 | 17 |  | None | high | True | If 7b - 1/4b = 7, then what is the value of 16b^2 + 1/49b^2? |
| 62 | 12 | 18 | 2: BC=YZ | 2 | high | False | If m∠C=m∠Z and AC=XZ, then which of the following conditions is necessary for ΔABC and ΔXYZ to be congruent? |
| 63 | 13 | 18 | 3: 14/3 | 3 | high | False | In the given figure, PAB is a secant and PT is a tangent to the circle from P. If PT = 8 cm, PA = 6 cm and AB = x cm, then the val |
| 64 | 14 | 18 | 1: A | 1 | high | False | A shopkeeper offers the following two discount schemes. A) Buy 3 get 4 free B) Buy 5 get 6 free Which scheme has the maximum disco |
| 65 | 15 | 19 |  | 4 | high | False | The following bar chart represents the gross amount (in ₹ lakhs) and total cost (in ₹ lakhs) of a firm. [Image of bar chart] In or |
| 66 | 16 | 19 |  | 3 | high | False | In what time will ₹10,000 at 4% per annum, produce the same interest as ₹8,000 does in 4 years at 5% simple interest? |
| 67 | 17 | 19 | 2: 5 | 2 | high | False | A man, a boy and a woman can finish a work in 10 days, 15 days and 30 days, respectively. In how many days can the work be finishe |
| 68 | 18 | 20 | 2: 1/4 | 2 | high | False | If cos θ = √3/2, then tan² θ cos² θ =? |
| 69 | 19 | 20 | 4: - 327 | 4 | high | False | What is the value of (3x³ + 5x²y + 12xy² + 7y³), when x = - 4 and y = - 1? |
| 70 | 20 | 20 | 2: 51 | 2 | high | False | If the four numbers, 39, 117, 17 and y are in proportion, then find the value of y. |
| 71 | 21 | 20 | 4: 310.464 cm³ | 4 | high | False | The volume of a sphere of radius 4.2 cm is: (Use π = 22/7) |
| 72 | 22 | 21 |  | None | high | True | If (a + b + c) = 16, and (a² + b² + c²) = 90, find the value of (ab + bc + ca). |
| 73 | 23 | 21 |  | None | high | True | If {(3 sin θ – cos θ) / (cos θ + sin θ)} = 1, then the value of cot θ is: |
| 74 | 24 | 21 | 1: 120 sec | None | high | True | Two runners, Sony and Mony, start running on a circular track of length 200 m at speeds of 18 and 24 km/h, respectively, in the sa |
| 75 | 25 | 21 | 1: 8 | 1 | high | False | What will be the remainder when (265)⁴⁰⁸¹+9 is divided by 266? |
| 76 | 1 | 21 |  | 1 | high | False | The following sentence has been split into four segments. Identify the segment that contains an error. Neetu have been / waiting f |
| 77 | 2 | 22 | 1: Over | 1 | high | False | Select the most appropriate ANTONYM of the underlined word. Her dog can climb under the fence. |
| 78 | 3 | 22 | 4: gliterring | 4 | high | False | Select the INCORRECTLY spelt word in the given sentence. The village beggars, no longer ill at ease in the gathering of gliterring |
| 79 | 4 | 22 | 4: The financial results will be announced by th | 4 | high | False | Select the option that expresses the given sentence in passive voice. The company's board of directors will announce the financial |
| 80 | 5 | 22 | 1: The participants of the competition are waiti | 1 | high | False | Select the grammatically correct sentence. |
| 81 | 6 | 23 |  | 4 | high | False | Select the most appropriate ANTONYM of the underlined word in the given sentence. Henry is so servile that other people take advan |
| 82 | 7 | 23 |  | 4 | high | False | Select the option that can be used as a one-word substitute for the given group of words. A thing fit to eat. |
| 83 | 8 | 23 | 3: Not brave | None | high | True | Select the most appropriate meaning of the given idiom. Lily-livered |
| 84 | 9 | 23 | 1: Enthusiastic | 3 | high | False | Select the most appropriate synonym of the given word. Zealous |
| 85 | 10 | 24 | 4: impress | 2 | high | False | Select the most appropriate option that can substitute the underlined word in the given sentence. She had an ability to persuade o |
| 86 | 11 | 24 | 3: instil | 3 | high | False | Select the most appropriate option that can substitute the underlined segment in the given sentence. We must remember that what we |
| 87 | 12 | 24 | 1: Any better choice won't be received by him th | 1 | high | False | Select the option that expresses the given sentence in passive voice. He won't receive any better choice than this from anywhere. |
| 88 | 13 | 24 | 3: Weak | 3 | high | False | Select the most appropriate synonym of the given word. Feeble |
| 89 | 14 | 24 | 4: association | 4 | high | False | Select the correct spelling of the underline word. They denied having any associasion with the terrorists. |
| 90 | 15 | 25 | 2: Become very confused when you are trying to e | 2 | high | False | Select the most appropriate meaning of the underlined idiom in the given sentence. Pooja tried to explain the problem, but soon sh |
| 91 | 16 | 25 | 2: DCAB | 2 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 92 | 17 | 25 |  | None | high | True | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 93 | 18 | 25 | 3: as beautiful as | 3 | high | False | Select the most appropriate option to fill in the blank. She is __________ a peacock in the blue satin saree. |
| 94 | 19 | 26 | 3: BCDA | 3 | high | False | Sentences of a paragraph are given below in jumbled order. Arrange the sentences in the correct order to form a meaningful and coh |
| 95 | 20 | 26 | 2: scent | 2 | high | False | Select the most appropriate homonym to fill in the blank. The hunter dogs followed the hyena’s ________. |
| 96 | 21 | 26 | 3: considered | 1 | high | False | Select the most appropriate option to fill in blank no. 1. |
| 97 | 22 | 27 | 3: awareness | 3 | high | False | Select the most appropriate option to fill in blank no. 2. |
| 98 | 23 | 27 | 1: Since | 1 | high | False | Select the most appropriate option to fill in blank no. 3. |
| 99 | 24 | 28 |  | 1 | high | False | Select the most appropriate option to fill in blank no. 4. |
| 100 | 25 | 28 | 4: breaks into | 4 | high | False | Select the most appropriate option to fill in blank no. 5. |
