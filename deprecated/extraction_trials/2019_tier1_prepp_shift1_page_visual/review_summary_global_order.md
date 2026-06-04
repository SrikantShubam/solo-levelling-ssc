# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2019_tier1_prepp_shift1.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / 100
- Overall status: PASS_WITH_MANUAL_REVIEW
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [17, 29, 32, 40, 41, 42, 43, 50, 62, 65, 67, 68, 69, 70, 72, 74, 100]
- Low-confidence global questions: []
- Manual review count: 17

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / 100 |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [17, 29, 32, 40, 41, 42, 43, 50, 62, 65, 67, 68, 69, 70, 72, 74, 100] |
| Confidence/manual-review flags | PASS | [] |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 3 |
| 3 | 2 |
| 4 | 3 |
| 5 | 4 |
| 6 | 3 |
| 7 | 4 |
| 8 | 2 |
| 9 | 4 |
| 10 | 5 |
| 11 | 5 |
| 12 | 5 |
| 13 | 5 |
| 14 | 4 |
| 15 | 4 |
| 16 | 3 |
| 17 | 4 |
| 18 | 3 |
| 19 | 4 |
| 20 | 4 |
| 21 | 4 |
| 22 | 4 |
| 23 | 3 |
| 24 | 3 |
| 25 | 4 |
| 26 | 4 |
| 27 | 4 |
| 28 | 1 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 4: k, l, k, l, m | 1 | high | False | Select the set of letters that when sequentially placed in the blanks of the given letter series will complete the series. k_lmml_ |
| 2 | 2 | 1 | 4: 3, 1, 5, 2, 4 | 4 | high | False | Arrange the following words in the order in which they appear in an English dictionary. 1. Rightly 2. Rigidly 3. Righteous 4. Rigo |
| 3 | 3 | 2 | 3: Figure 3 | 3 | high | False | Select the figure that can replace the question mark (?) in the following series. |
| 4 | 4 | 2 | 1: 91 | 1 | high | False | Study the given pattern carefully and select the number that can replace the question mark (?) in it. 6 21 14 40 500 ? 8 25 7 |
| 5 | 5 | 2 | 4: Submarine | 1 | high | False | Four words have been given, out of which three are alike in some manner, while one is different. Select the odd word. |
| 6 | 6 | 3 | 1: Figure 1 | 1 | high | False | The sequence of folding a piece of paper and the manner in which the folded paper has been cut is shown in the following figures.  |
| 7 | 7 | 3 | 3: 162 | 3 | high | False | Select the option that is related to the third number in the same way as the second number is related to the first number and the  |
| 8 | 8 | 4 | 1: 5 | 1 | high | False | The given Venn diagram represents employees in an organisation: The triangle represents executives, the circle represents females, |
| 9 | 9 | 4 | 3: 7 and 4 | 3 | high | False | Which two numbers should be interchanged to make the given equation correct? 9 + 7 × 5 - 18 ÷ 2 = 3 × 4 - 10 + 45 ÷ 5 |
| 10 | 10 | 4 | 4: Figure 4 | 4 | high | False | Which of the option figures is the exact mirror image of the given figure when the mirror is held at the right side? RST2PK9LOX |
| 11 | 11 | 5 | 4: 1 | 3 | high | False | Two positions of the same dice are shown. Select the number that will be on the face opposite to the one showing 6. |
| 12 | 12 | 5 | 1: 41 | 1 | high | False | The ratio of the present ages of Asha and Lata is 5 : 6. If the difference between their ages is 6 years, then what will be Lata's |
| 13 | 13 | 5 | 4: Either conclusion I or II follows. | 4 | high | False | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it app |
| 14 | 14 | 5 | 3: 20-7-15-20-3-8 | 3 | high | False | In a certain code language, ‘HARVEST’ is coded as ‘22-21-7-24-20-3-10’. How will ‘FARMER’ be coded as in that language? |
| 15 | 15 | 6 | 4: 67 - 76 + 43 = 100 | 4 | high | False | In the following equations, if '+' is interchanged with '-' and '6' is interchanged with '7', then which equation would be correct |
| 16 | 16 | 6 | 3: 107 | 3 | high | False | Select the number that can replace the question mark (?) in the following series. 17, 21, 30, 46, 71, ? |
| 17 | 17 | 6 | 3: 33 | None | high | True | How many rectangles are there in the given figure? |
| 18 | 18 | 7 | 1: (313, 322, 340) | 1 | high | False | Select the option in which the numbers are related in the same way as are the numbers in the given set. (269, 278, 296) |
| 19 | 19 | 7 | 3: Hunger | 3 | high | False | Select the option that is related to the third word in the same way as the second word is related to the first word. Medicine : Di |
| 20 | 20 | 7 | 3: Grandson | 3 | high | False | Amit is the brother of Sonia. Jyoti is the sister of Nikita. Sonia is the daughter of Satish's father. Nikita is the daughter of K |
| 21 | 21 | 7 | 4: Ammeter : Current | 4 | high | False | Select the option in which the words share the same relationship as that shared by the given pair of words. Clock : Time |
| 22 | 22 | 8 | 4: Figure 4 | 4 | high | False | Select the option figure in which the given figure is embedded (rotation is NOT allowed). |
| 23 | 23 | 8 | 3: FVKO | 3 | high | False | Four letter-clusters have been given, out of which three are alike in some manner, while one is different. Select the odd letter-c |
| 24 | 24 | 9 | 3: CZGPXTBV | 3 | high | False | In a certain code language, WARDROBE is written as YXVYXHJV. How will ACCURATE be written as in that language? |
| 25 | 25 | 9 | 1: WLD | 1 | high | False | Select the letter-cluster that can replace the question mark (?) in the following series. CXB, HUI, MRP, ROW, ? |
| 26 | 1 | 9 | 4: Gotabaya Rajapaksa | 4 | high | False | As of February 2020, who is the President of Sri Lanka? |
| 27 | 2 | 9 | 3: Chhattisgarh | 1 | high | False | As on January 2020, Shri Bhupesh Baghel is the Chief Minister of which of the following states? |
| 28 | 3 | 10 | 2: James Chadwick | 2 | high | False | Name the physicist who is credited with the discovery of the Neutron. This 1932 discovery led to his winning the Nobel Prize. |
| 29 | 4 | 10 | 2: Chess | None | high | True | For which of the following sports was Dronavalli Harika, conferred with the prestigious Padma Shri award? |
| 30 | 5 | 10 | 2: Virat Kohli | 4 | high | False | Who is the first and currently the only batsman to score double hundreds in four consecutive test series? |
| 31 | 6 | 10 | 2: Kerala | 4 | high | False | Kolathunadu, Valluvanad and Thekkumkoor were ancient small-time kingdoms in which state of India? |
| 32 | 7 | 10 | 3: Jahangir | None | high | True | Sir Thomas Roe came as an official ambassador from King James I of England to which Mughal emperor's court? |
| 33 | 8 | 11 | 1: Disney | 1 | high | False | Name the media company that purchased the legendary studio of 21st Century Fox. |
| 34 | 9 | 11 | 1: Dry Ice | 1 | high | False | What is the more common name for solid carbon dioxide? |
| 35 | 10 | 11 | 3: Femur | 3 | high | False | Which of these bones is NOT a part of the human ear? |
| 36 | 11 | 11 | 2: An Area of Darkness | 4 | high | False | Which of the following books is NOT written by Salman Rushdie? |
| 37 | 12 | 11 | 3: Rome | 1 | high | False | The World Food Program (WFP) is the food assistance branch of the United Nations. Where is it headquartered? |
| 38 | 13 | 12 | 2: 28 % | 1 | high | False | What is the uniform GST rate that has been fixed up for lottery prizes by the GST Council? |
| 39 | 14 | 12 | 3: Narendra Modi | 1 | high | False | From India, who inaugurated the Kartarpur Corridor and flagged off the first set of pilgrims to the final resting place of Sikhism |
| 40 | 15 | 12 | 3: 1818 | None | high | True | In which year Sanchi was discovered after being abandoned for nearly 600 Years? |
| 41 | 16 | 12 | 2: Cynology | None | high | True | Which of these words refers to the scientific study of domestic dogs? |
| 42 | 17 | 12 | 1: Visakhapatnam | None | high | True | The Araku Valley, a tourist resort, is located near which of these cities of South India? |
| 43 | 18 | 13 | 2: Horses | None | high | True | Prolific Indian painter Maqbool Fida Husain predominantly used which of these animals to depict a lively and free spirit in his pa |
| 44 | 19 | 13 | 4: Karnataka | 1 | high | False | The ruins of the ancient city of Hampi - capital of Vijayanagara - is located in which present day Indian state? |
| 45 | 20 | 13 | 4: Vidya Balan | 4 | high | False | Who among the following played the leading lady in the film 'Mission Mangal' that tells the dramatic true story of the women behin |
| 46 | 21 | 13 | 4: Reserve Bank of India | 4 | high | False | Which of these institutions fixes the Repo Rate and the Reverse Repo Rate in India? |
| 47 | 22 | 13 | 2: Gizzard | 2 | high | False | Red worms have a structure named ______ which helps them in grinding their food. |
| 48 | 23 | 14 | 1: Shashi Tharoor | 4 | high | False | Name the author who won the Sahitya Akademi Award 2019 for his book - An Era of Darkness: The British Empire in India. |
| 49 | 24 | 14 | 3: Maharashtra | 3 | high | False | Veteran freedom fighter, social reformer and feminist Savithribai Phule hailed from which of the following states of India? |
| 50 | 25 | 14 | 4: Oman | None | high | True | Sultan Qaboos bin Said of ________, the Arab world's longest-serving ruler and with a reputation for quiet diplomacy passed away r |
| 51 | 1 | 14 | 2: 11 | 2 | high | False | The area of Δ ABC is 44 cm². If D is the midpoint of BC and E is the midpoint of AB, then the area (in cm²) of ΔBDE is: |
| 52 | 2 | 15 | 1: 0 | 1 | high | False | If the number 1005x4 is completely divisible by 8, then the smallest integer in place of x will be: |
| 53 | 3 | 15 | 3: 1 : 4 | 3 | high | False | If the base radius of 2 cylinders are in the ratio 3 : 4 and their heights are in the ratio 4 : 9, then the ratio of their volumes |
| 54 | 4 | 15 | 2: 18/11 | 2 | high | False | If x, y, z are three integers such that x + y = 8, y + z = 13 and z + x = 17, then the value of x^2 / yz is: |
| 55 | 5 | 15 | 2: A | 2 | high | False | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. |
| 56 | 6 | 16 | 4: D | 4 | high | False | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. |
| 57 | 7 | 16 | 1: 41 | 1 | high | False | If x = 4cosA + 5sinA and y = 4sinA - 5cosA, then the value of x² + y² is: |
| 58 | 8 | 16 | 1: 102 | 1 | high | False | Out of 6 numbers, the sum of the first 5 numbers is 7 times the 6th number. If their average is 136, then the 6th number is: |
| 59 | 9 | 17 | 3: 50% | 3 | high | False | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. |
| 60 | 10 | 17 | 4: 3 | 4 | high | False | If x^2a = y^2b = z^2c != 0 and x^2 = yz, then the value of (ab+bc+ca)/bc is: |
| 61 | 11 | 17 | 2: 604 | 2 | high | False | If x - y = 4 and xy = 45, then the value of x^3 - y^3 is: |
| 62 | 12 | 17 | 3: ₹8,420 | None | high | True | ₹4,300 becomes ₹4,644 in 2 years at simple interest. Find the principle amount that will become ₹10,104 in 5 years at the same rat |
| 63 | 13 | 18 | 4: E | 4 | high | False | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. |
| 64 | 14 | 18 | 3: -15/19 | 4 | high | False | If '+' means '-', '-' means '+', 'x' means '÷' and '÷' means 'x', then the value of (42-12x3+8÷2+15)/(8x2-4+9÷3) is: |
| 65 | 15 | 18 | 4: 996 | None | high | True | A person sells an article at 10% below its cost price. Had he sold it for ₹332 more, he would have made a profit of 20%. What is t |
| 66 | 16 | 19 | 3: 4 | 1 | high | False | If A + B = 45°, then the value of 2(1 + tanA)(1 + tanB) is: |
| 67 | 17 | 19 | 3: 25.5 km/h | None | high | True | A train crosses a pole in 12 sec, and a bridge of length 170 m in 36 sec. Then the speed of the train is: |
| 68 | 18 | 19 | 1: 20 | None | high | True | The ratio of the number of boys to the number of girls in a school of 640 students, is 5 : 3. If 30 more girls are admitted in the |
| 69 | 19 | 19 | 2: 32 cm² | None | high | True | In Δ ABC, MN // BC, the area of quadrilateral MBCN=130 sqcm. If AN : NC=4 : 5, then the area of Δ MAN is: |
| 70 | 20 | 20 | 1: 1 | None | high | True | If A lies in the first quadrant and 6tanA = 5, then the value of (8 sin A - 4 cos A) / (cos A + 2 sin A) is: |
| 71 | 21 | 20 | 4: 12 | 4 | high | False | If the length of a rectangle is increased by 40%, and the breadth is decreased by 20%, then the area of the rectangle increases by |
| 72 | 22 | 20 | 4: ₹144 | None | high | True | A shopkeeper marks the price of the article in such a way that after allowing 28% discount, he wants a gain of 12%. If the marked  |
| 73 | 23 | 20 | 4: 2112 | 4 | high | False | The radius of a circular garden is 42 m. The distance (in m) covered by running 8 rounds around it, is: (Take π = 22/7) |
| 74 | 24 | 21 | 3: 60° | None | high | True | A, B and C are three points on a circle such that the angles subtended by the chord AB and AC at the centre O are 110° and 130°, r |
| 75 | 25 | 21 | 3: 13 1/5 | 3 | high | False | A, B and C can individually complete a piece of work in 24 days, 15 days and 12 days, respectively. B and C started the work and w |
| 76 | 1 | 21 | 1: render | 3 | high | False | Fill in the blank with the most appropriate word. We must ________ help to the homeless and physically disabled people. |
| 77 | 2 | 21 | 3: CBDA | 3 | high | False | Given below are four jumbled sentences. Select the option that gives their correct order A. However, the rate of population increa |
| 78 | 3 | 22 | 3: The work is kept pending by the manager. | 3 | high | False | Select the passive form of the given sentence. The manager keeps the work pending. |
| 79 | 4 | 22 | 1: have been selected | 1 | high | False | In the sentence identify the segment which contains the grammatical error. One of the boys from our school have been selected for  |
| 80 | 5 | 22 | 1: Mandatory | 1 | high | False | Select the correct synonym of the given word. Obligatory |
| 81 | 6 | 22 | 4: agree to the proposal | 4 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, sel |
| 82 | 7 | 23 | 2: vital | 2 | high | False | In the following passage some words have been deleted. Fill in the blanks with the help of the alternatives given. Select the most |
| 83 | 8 | 23 | 4: conscious | 4 | high | False | In the following passage some words have been deleted. Fill in the blanks with the help of the alternatives given. Select the most |
| 84 | 9 | 23 | 3: ability | 3 | high | False | In the following passage some words have been deleted. Fill in the blanks with the help of the alternatives given. Select the most |
| 85 | 10 | 24 | 1: to | 1 | high | False | Select the most appropriate option for blank No. 4 |
| 86 | 11 | 24 | 3: overcome | 3 | high | False | Select the most appropriate option for blank No. 5 |
| 87 | 12 | 24 | 2: Glittering | 2 | high | False | Select the correct synonym of the given word. Scintillating |
| 88 | 13 | 25 | 3: inaudible | 3 | high | False | Select the word, which means the same as the given group of words. Something that cannot be heard |
| 89 | 14 | 25 | 2: The captain as well as the players was | 4 | high | False | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, sel |
| 90 | 15 | 25 | 4: Leave without any intimation | 4 | high | False | Select the appropriate meaning of the given idiom. To take French leave |
| 91 | 16 | 25 | 3: BDCA | 3 | high | False | Given below are four jumbled sentences. Select the option that gives their correct order A. However, they ignore the truth that pr |
| 92 | 17 | 26 | 2: Dirge | 1 | high | False | Select the word, which means the same as the groups of words given. A song sung at a burial |
| 93 | 18 | 26 | 2: A difficult problem | 2 | high | False | Select the appropriate meaning of the given idiom. A hard nut to crack |
| 94 | 19 | 26 | 3: fragile | 3 | high | False | Fill in the blank with the most appropriate word. Handle this glass table with care because it is ______. |
| 95 | 20 | 26 | 3: Sarcasm | 3 | high | False | Select the correctly spelt word. |
| 96 | 21 | 27 | 4: He asked the hotel receptionist if he could t | 3 | high | False | Select the indirect narration of the given sentence. He said to the hotel receptionist, “Can you tell me the tariff of rooms? |
| 97 | 22 | 27 | 1: I can swim | 1 | high | False | In the sentence identify the segment which contains the grammatical error. I can swim very fast when I was only five. |
| 98 | 23 | 27 | 1: exhibit | 1 | high | False | Select the correctly spelt word. |
| 99 | 24 | 27 | 4: Arrival | 4 | high | False | Select the correct antonym of the given word. Exodus |
| 100 | 25 | 28 | 4: Active | None | high | True | Select the correct antonym of the given word. Quiescent |
