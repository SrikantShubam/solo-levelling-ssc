# Pipeline 1 vs Pipeline 2 Comparison: 2019 Tier-1 Shift 1

Pipeline 1 is raw Gemini LLM-only extraction from `raw_gemini_record`.
Pipeline 2 is precision-first canonical output after option-crop HSV evidence and QC.

## Headline Metrics

- Questions retained: 100 / 100 = 100.0%
- Pipeline 1 auto-answer coverage: 100 / 100 = 100.0%
- Pipeline 2 auto-canonical coverage: 98 / 100 = 98.0%
- Precision blocked-for-review rate: 2 / 100 = 2.0%
- Pipeline 1 vs Pipeline 2 same accepted answers: 98 / 100 = 98.0%
- Rows where Pipeline 1 gave an answer but Pipeline 2 refused to canonicalize: 2 / 100 = 2.0%
- True answer error rate: not knowable until manual gold verification is added. The measurable rate here is disagreement/block risk.

## Evidence Status Counts

| Evidence status | Count |
|---|---:|
| PASS_WITH_EVIDENCE | 98 |
| PASS_WITH_MANUAL_REVIEW | 2 |

## Modality Counts

| Modality | Count |
|---|---:|
| dice | 2 |
| math_formula | 22 |
| table_di | 7 |
| text_only | 63 |
| visual_options | 5 |
| visual_stimulus | 1 |

## Blocking Rows For Manual Check

| Q | Page | Modality | LLM correct | Precision correct | Deterministic | Reason | Crop |
|---:|---:|---|---|---|---|---|---|
| 13 | 5 | text_only | 4 | None | AMBIGUOUS | correct_option_unresolved_or_conflict | `C:\experiments\ssc\extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\assets\question_crops\2019_tier1_prepp_shift1_p05_q013_question.png` |
| 21 | 7 | text_only | 4 | None | AMBIGUOUS | correct_option_unresolved_or_conflict | `C:\experiments\ssc\extraction_batch\tier1_gemini\2019_tier1_prepp_shift1\assets\question_crops\2019_tier1_prepp_shift1_p07_q021_question.png` |

## One-By-One Comparison

| Q | Page | Modality | LLM | Precision | Evidence | Comparison | Short text |
|---:|---:|---|---|---|---|---|---|
| 1 | 1 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the set of letters that when sequentially placed in the blanks of the given letter series will complete the series. k_lmml_mk_mmk_lkkl_m |
| 2 | 1 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Arrange the following words in the order in which they appear in an English dictionary. 1. Rightly 2. Rigidly 3. Righteous 4. Rigour 5. Rights |
| 3 | 2 | visual_options | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the figure that can replace the question mark (?) in the following series. |
| 4 | 2 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Study the given pattern carefully and select the number that can replace the question mark (?) in it. 6 21 14 40 500 ? 8 25 7 |
| 5 | 2 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Four words have been given, out of which three are alike in some manner, while one is different. Select the odd word. |
| 6 | 3 | visual_options | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | The sequence of folding a piece of paper and the manner in which the folded paper has been cut is shown in the following figures. How would this paper look when unfolded? |
| 7 | 3 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the option that is related to the third number in the same way as the second number is related to the first number and the sixth number is related to the fifth number. 12 :  |
| 8 | 4 | visual_stimulus | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | The given Venn diagram represents employees in an organisation: The triangle represents executives, the circle represents females, the rectangle represents MBAs and the square repr |
| 9 | 4 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Which two numbers should be interchanged to make the given equation correct? 9 + 7 × 5 - 18 ÷ 2 = 3 × 4 - 10 + 45 ÷ 5 |
| 10 | 4 | visual_options | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Which of the option figures is the exact mirror image of the given figure when the mirror is held at the right side? RST2PK9LOX |
| 11 | 5 | dice | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Two positions of the same dice are shown. Select the number that will be on the face opposite to the one showing 6. |
| 12 | 5 | math_formula | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | The ratio of the present ages of Asha and Lata is 5 : 6. If the difference between their ages is 6 years, then what will be Lata's age will be after 5 years? |
| 13 | 5 | text_only | 4 | None | PASS_WITH_MANUAL_REVIEW | llm_answer_blocked_for_review | Read the given statements and conclusions carefully. Assuming that the information given in the statements is true, even if it appears to be at variance with commonly known facts,  |
| 14 | 5 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | In a certain code language, 'HARVEST' is coded as '22-21-7-24-20-3-10'. How will 'FARMER' be coded as in that language? |
| 15 | 6 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | In the following equations, if '+' is interchanged with '-' and '6' is interchanged with '7', then which equation would be correct? |
| 16 | 6 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the number that can replace the question mark (?) in the following series. 17, 21, 30, 46, 71, ? |
| 17 | 6 | visual_options | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | How many rectangles are there in the given figure? |
| 18 | 7 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the option in which the numbers are related in the same way as are the numbers in the given set. (269, 278, 296) |
| 19 | 7 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the option that is related to the third word in the same way as the second word is related to the first word. Medicine : Disease :: Food : ? |
| 20 | 7 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Amit is the brother of Sonia. Jyoti is the sister of Nikita. Sonia is the daughter of Satish's father. Nikita is the daughter of Kavinder. Jyoti is the mother of Amit. Mukesh is Ni |
| 21 | 7 | text_only | 4 | None | PASS_WITH_MANUAL_REVIEW | llm_answer_blocked_for_review | Select the option in which the words share the same relationship as that shared by the given pair of words. Clock : Time |
| 22 | 8 | visual_options | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the option figure in which the given figure is embedded (rotation is NOT allowed). |
| 23 | 8 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Four letter-clusters have been given, out of which three are alike in some manner, while one is different. Select the odd letter-cluster. |
| 24 | 9 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | In a certain code language, WARDROBE is written as YXVYXHJV. How will ACCURATE be written as in that language? |
| 25 | 9 | table_di | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the letter-cluster that can replace the question mark (?) in the following series. CXB, HUI, MRP, ROW, ? |
| 26 | 9 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | As of February 2020, who is the President of Sri Lanka? |
| 27 | 9 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | As on January 2020, Shri Bhupesh Baghel is the Chief Minister of which of the following states? |
| 28 | 10 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Name the physicist who is credited with the discovery of the Neutron. This 1932 discovery led to his winning the Nobel Prize. |
| 29 | 10 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | For which of the following sports was Dronavalli Harika, conferred with the prestigious Padma Shri award? |
| 30 | 10 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Who is the first and currently the only batsman to score double hundreds in four consecutive test series? |
| 31 | 10 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Kolathunadu, Valluvanad and Thekkumkoor were ancient small-time kingdoms in which state of India? |
| 32 | 10 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Sir Thomas Roe came as an official ambassador from King James I of England to which Mughal emperor's court? |
| 33 | 11 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Name the media company that purchased the legendary studio of 21st Century Fox. |
| 34 | 11 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | What is the more common name for solid carbon dioxide? |
| 35 | 11 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Which of these bones is NOT a part of the human ear? |
| 36 | 11 | dice | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Which of the following books is NOT written by Salman Rushdie? |
| 37 | 11 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | The World Food Program (WFP) is the food assistance branch of the United Nations. Where is it headquartered? |
| 38 | 12 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | What is the uniform GST rate that has been fixed up for lottery prizes by the GST Council? |
| 39 | 12 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | From India, who inaugurated the Kartarpur Corridor and flagged off the first set of pilgrims to the final resting place of Sikhism founder Guru Nanak Dev? |
| 40 | 12 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | In which year Sanchi was discovered after being abandoned for nearly 600 Years? |
| 41 | 12 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Which of these words refers to the scientific study of domestic dogs? |
| 42 | 12 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | The Araku Valley, a tourist resort, is located near which of these cities of South India? |
| 43 | 13 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Prolific Indian painter Maqbool Fida Husain predominantly used which of these animals to depict a lively and free spirit in his paintings? |
| 44 | 13 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | The ruins of the ancient city of Hampi - capital of Vijayanagara - is located in which present day Indian state? |
| 45 | 13 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Who among the following played the leading lady in the film 'Mission Mangal' that tells the dramatic true story of the women behind India's first mission to Mars? |
| 46 | 13 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Which of these institutions fixes the Repo Rate and the Reverse Repo Rate in India? |
| 47 | 13 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Red worms have a structure named ______ which helps them in grinding their food. |
| 48 | 14 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Name the author who won the Sahitya Akademi Award 2019 for his book - An Era of Darkness: The British Empire in India. |
| 49 | 14 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Veteran freedom fighter, social reformer and feminist Savithribai Phule hailed from which of the following states of India? |
| 50 | 14 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Sultan Qaboos bin Said of ________, the Arab world's longest-serving ruler and with a reputation for quiet diplomacy passed away recently (2020). |
| 51 | 14 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | The area of Δ ABC is 44 cm². If D is the midpoint of BC and E is the midpoint of AB, then the area (in cm²) of ΔBDE is: |
| 52 | 15 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | If the number 1005x4 is completely divisible by 8, then the smallest integer in place of x will be: |
| 53 | 15 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | If the base radius of 2 cylinders are in the ratio 3 : 4 and their heights are in the ratio 4 : 9, then the ratio of their volumes is: |
| 54 | 15 | math_formula | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | If x, y, z are three integers such that x + y = 8, y + z = 13 and z + x = 17, then the value of x²/yz is: |
| 55 | 15 | table_di | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. Study the table and answer the question that foll |
| 56 | 16 | table_di | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. Study the table and answer the question that foll |
| 57 | 16 | math_formula | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | If x = 4cosA + 5sinA and y = 4sinA - 5cosA, then the value of x² + y² is: |
| 58 | 16 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Out of 6 numbers, the sum of the first 5 numbers is 7 times the 6th number. If their average is 136, then the 6th number is: |
| 59 | 17 | table_di | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. Study the table and answer the question that foll |
| 60 | 17 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | If x^2a = y^2b = z^2c ≠ 0 and x^2 = yz, then the value of (ab+bc+ca)/bc is: |
| 61 | 17 | math_formula | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | If x - y = 4 and xy = 45, then the value of x^3 - y^3 is: |
| 62 | 17 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | ₹4,300 becomes ₹4,644 in 2 years at simple interest. Find the principle amount that will become ₹10,104 in 5 years at the same rate of interest. |
| 63 | 18 | table_di | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | The given table shows the number (in thousands) of cars of five different models A, B, C, D and E produced during Years 2012-2017. Study the table and answer the question that foll |
| 64 | 18 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | If '+' means '-', '-' means '+', 'x' means '÷' and '÷' means 'x', then the value of 42-12x3+8÷2+15 / 8x2-4+9÷3 is: |
| 65 | 18 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | A person sells an article at 10% below its cost price. Had he sold it for ₹332 more, he would have made a profit of 20%. What is the original selling price (in ₹) of the article? |
| 66 | 19 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | If A + B = 45°, then the value of 2(1 + tanA)(1 + tanB) is: |
| 67 | 19 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | A train crosses a pole in 12 sec, and a bridge of length 170 m in 36 sec. Then the speed of the train is: |
| 68 | 19 | math_formula | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | The ratio of the number of boys to the number of girls in a school of 640 students, is 5 : 3. If 30 more girls are admitted in the school, then how many more boys should be admitte |
| 69 | 19 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | In Δ ABC, MN // BC, the area of quadrilateral MBCN=130 sqcm. If AN : NC=4 : 5, then the area of Δ MAN is: |
| 70 | 20 | math_formula | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | If A lies in the first quadrant and 6tanA = 5, then the value of (8 sin A - 4 cos A) / (cos A + 2 sin A) is: |
| 71 | 20 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | If the length of a rectangle is increased by 40%, and the breadth is decreased by 20%, then the area of the rectangle increases by x%. Then the value of x is: |
| 72 | 20 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | A shopkeeper marks the price of the article in such a way that after allowing 28% discount, he wants a gain of 12%. If the marked price is ₹224, then the cost price of the article  |
| 73 | 20 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | The radius of a circular garden is 42 m. The distance (in m) covered by running 8 rounds around it, is: (Take π = 22/7) |
| 74 | 21 | math_formula | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | A, B and C are three points on a circle such that the angles subtended by the chord AB and AC at the centre O are 110° and 130°, respectively. Then the value of ∠BAC is: |
| 75 | 21 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | A, B and C can individually complete a piece of work in 24 days, 15 days and 12 days, respectively. B and C started the work and worked for 3 days and left. The number of days requ |
| 76 | 21 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Fill in the blank with the most appropriate word. We must ________ help to the homeless and physically disabled people. |
| 77 | 21 | table_di | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Given below are four jumbled sentences. Select the option that gives their correct order A. However, the rate of population increase is another important factor to consider. B. Thi |
| 78 | 22 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the passive form of the given sentence. The manager keeps the work pending. |
| 79 | 22 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | In the sentence identify the segment which contains the grammatical error. One of the boys from our school have been selected for National Badminton Championship. |
| 80 | 22 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correct synonym of the given word. Obligatory |
| 81 | 22 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, select No improvement The Director will agree with th |
| 82 | 23 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option for blank No. 1 |
| 83 | 23 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option for blank No. 2 |
| 84 | 23 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option for blank No. 3 |
| 85 | 24 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option for blank No. 4 |
| 86 | 24 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option for blank No. 5 |
| 87 | 24 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correct synonym of the given word. Scintillating |
| 88 | 25 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the word, which means the same as the given group of words. Something that cannot be heard |
| 89 | 25 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the most appropriate option to substitute the underlined segment in the given sentence. If no substitution is required, select No improvement The captain as well the players |
| 90 | 25 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the appropriate meaning of the given idiom. To take French leave |
| 91 | 25 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Given below are four jumbled sentences. Select the option that gives their correct order A. However, they ignore the truth that progress and success are proportional to the labor t |
| 92 | 26 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the word, which means the same as the groups of words given. A song sung at a burial |
| 93 | 26 | text_only | 2 | 2 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the appropriate meaning of the given idiom. A hard nut to crack |
| 94 | 26 | table_di | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Fill in the blank with the most appropriate word. Handle this glass table with care because it is ______. |
| 95 | 26 | text_only | 3 | 3 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correctly spelt word. |
| 96 | 27 | math_formula | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the indirect narration of the given sentence. He said to the hotel receptionist, “Can you tell me the tariff of rooms? |
| 97 | 27 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | In the sentence identify the segment which contains the grammatical error. I can swim very fast when I was only five. |
| 98 | 27 | text_only | 1 | 1 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correctly spelt word. |
| 99 | 27 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correct antonym of the given word. Exodus |
| 100 | 28 | text_only | 4 | 4 | PASS_WITH_EVIDENCE | same_auto_accepted | Select the correct antonym of the given word. Quiescent |
