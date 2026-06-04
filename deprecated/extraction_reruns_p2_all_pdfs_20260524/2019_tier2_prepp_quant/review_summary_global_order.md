# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2019_tier2_prepp_quant.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 100 / None
- Overall status: BLOCKED
- Structural QC passed: True
- Load errors: []
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [2, 3, 4, 12, 13, 20, 23, 26, 41, 45, 48, 51, 53, 61, 66, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
- Low-confidence global questions: []
- Manual review count: 45
- Canonical review count: 57

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | PASS | 0 failures |
| Expected question count | PASS | 100 / None |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [2, 3, 4, 12, 13, 20, 23, 26, 41, 45, 48, 51, 53, 61, 66, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 57 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 3 |
| 2 | 3 |
| 3 | 3 |
| 4 | 4 |
| 5 | 4 |
| 6 | 4 |
| 7 | 4 |
| 8 | 4 |
| 9 | 3 |
| 10 | 4 |
| 11 | 3 |
| 12 | 3 |
| 13 | 4 |
| 14 | 4 |
| 15 | 3 |
| 16 | 4 |
| 17 | 2 |
| 18 | 3 |
| 19 | 4 |
| 20 | 4 |
| 21 | 5 |
| 22 | 4 |
| 23 | 4 |
| 24 | 4 |
| 25 | 4 |
| 26 | 4 |
| 27 | 4 |
| 28 | 1 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 3: 47/6 | 3 | high | False | The value of 3 ÷ 18 of 3 × 6 + 21 × 6 ÷ 18 - 3 ÷ 2 + 3 - 3 ÷ 9 of 3 × 9 is: |
| 2 | 2 | 1 |  | None | high | True | In ΔABC, D and E are the mid points of sides BC and AC, respectively. If AD = 10.8 cm, BE = 14.4 cm and AD and BE intersect at G a |
| 3 | 3 | 1 | 3: 20 | None | high | True | Rishu saves x% of her income. If her income increases by 26% and the expenditure increases by 20%, then her savings increase by 50 |
| 4 | 4 | 2 | 4: 5 | None | high | True | If 45/53 = 1/(a + 1/(b + 1/(c - 2/5))), where a, b and c are positive integers, then what is the value of (4a - b + 3c)? |
| 5 | 5 | 2 | 3: 6,768 | 3 | high | False | कोई व्यक्ति किसी निश्चित राशि को अपने तीन बेटों के बीच 3 : 4 : 5 के अनुपात में विभाजित करता है। यदि उसने इस राशि को 1/3 : 1/4 : 1/ |
| 6 | 6 | 2 | 3: -1 | 3 | high | False | The value of (sec^2 θ(2+tan^2 θ+cot^2 θ)÷(sin^2 θ-tan^2 θ))/(cosec^2 θ+sec^2 θ)(1+cot^2 θ)^2 is: |
| 7 | None | 3 | 1: 27.5 | 1 | high | False | Study the given graph and answer the question that follows. The number of patients aged 10 or more years but below 40 years is wha |
| 8 | 8 | 3 | 1: 16 2/3 | 1 | high | False | If (x + 20)% of 250 is 25% more than x% of 220, then 10% of (x + 50) is what per cent less than 15% of x? |
| 9 | 9 | 3 |  | 4 | high | False | Remi earns a profit of 20% on selling an article at a certain price. If she sells the articles for ₹8 more, she will gain 30%. Wha |
| 10 | 10 | 4 |  | 2 | high | False | PQR में, O अन्तःकेंद्र है और ∠P = 42° है। तो ∠QOR का माप ज्ञात कीजिए। |
| 11 | 11 | 4 | 2: 1 : 3 | 2 | high | False | The sum of the present ages of a father and son is 52 years. Four years hence, the son's age will be 1/4 that of the father. What  |
| 12 | 12 | 4 |  | None | high | True | (1/cosθ - 1/sinθ) + 1/(cosecθ - cotθ) - 1/(secθ + tanθ) = ? |
| 13 | 13 | 4 | 3: 1 1/8 hours | None | high | True | A takes 2 hours more than B to cover a distance of 40 km. If A doubles his speed, he takes 1 1/2 hours more than B to cover 80 km. |
| 14 | 14 | 5 |  | 1 | high | False | On selling an article for ₹123.40, the gain is 20% more than the amount of loss incurred on selling it for ₹108. If the article is |
| 15 | 15 | 5 |  | 4 | high | False | In ΔPQR, ∠Q = 84°, ∠R = 48°, PS ⊥ QR at S and the bisector of ∠P meets QR at T. What is the measure of ∠SPT? |
| 16 | 16 | 5 | 2: 6 | 2 | high | False | In ΔABC, ∠A = 90°, AD is the bisector of ∠A meeting BC at D, and DE ⊥ AC at E. If AB = 10 cm and AC = 15 cm, then the length of DE |
| 17 | 17 | 5 | 2: 100√5 | 3 | high | False | The base of a right pyramid is a square of side 10 cm. If its height is 10 cm, then the area (in cm²) of its lateral surface is: |
| 18 | 18 | 6 | 1: ₹1,820.50 | 1 | high | False | The compound interest on a sum of ₹5,500 at 15% p.a. for 2 years, when the interest is compounded 8 monthly, is: |
| 19 | 19 | 6 | 3: 1.1̅ | 3 | high | False | The value of (2.4̅ × 0.6̅ × 3 × 0.16̅) ÷ [0.27̅ × (0.83̅ ÷ 0.16̅)] is: |
| 20 | 20 | 6 | 1: ₹702 | None | high | True | A sold a watch to B at a profit of 20%. B sold it to C at 30% profit. C sold it to D at 10% loss. If B's profit is ₹80 more than t |
| 21 | 21 | 6 | 1: 10 | 1 | high | False | The value of [4/7 of 2 4/5 × 1 2/3 - (3 1/2 - 2 1/6)] ÷ (3 1/5 ÷ 4 1/2 of 5 1/3) is: |
| 22 | 22 | 7 | 3: 54 | 3 | high | False | The average score in Mathematics of 90 students of section A and B of class IX was 63. The number of students in A were 10 more th |
| 23 | 23 | 7 | 3: 25.872 | None | high | True | The curved surface area of a right cylinder is 3696 cm². Its height is three times its radius. What is the capacity (in litres) of |
| 24 | 24 | 7 | 3: 36° | 3 | high | False | The sides BA and DE of a regular pentagon are produced to meet at F. What is the measure of ∠EFA? |
| 25 | 25 | 7 | 1: 5(3 + 2√2) | 1 | high | False | The expression 15(√10+√5) / (√10+√20+√40-√5-√80) is equal to: |
| 26 | 26 | 8 |  | None | high | True | A person has to cover a distance of 160 km in 15 hours. If he covers 4/5 of the distance in 2/3 of the time, then what should be h |
| 27 | 27 | 8 | 1: 430 π | 1 | high | False | The height of a solid cylinder is 30 cm and the diameter of its base is 10 cm. Two identical conical holes each of radius 5 cm and |
| 28 | 28 | 8 |  | 4 | high | False | If 9x² + y² = 37 and xy = 2, x, y > 0, then the value of (27x³ + y³) is: |
| 29 | 29 | 8 | 1: -3(2 + √3) | 1 | high | False | The value of (cosec² 30° sin² 45° + sec² 60°) / (tan 60° cosec² 45° - sec² 60° tan 45°) is: |
| 30 | 30 | 9 | 4: 7√3/5 cm | 4 | high | False | Given that ΔDEF~ΔABC. If the area of ΔABC is 9 cm² and that of ΔDEF = 12 cm² and BC = 2.1 cm, then the length of EF is: |
| 31 | 31 | 9 | 3: -7 | 3 | high | False | If a + b + c = 6, a³ + b³ + c³ - 3abc = 342, then what is the value of ab + bc + ca? |
| 32 | 32 | 9 | 3: 2 1/9 | 3 | high | False | If 3x² - 5x + 1 = 0, then the value of (x² + 1/9x²) is: |
| 33 | 33 | 10 | 1: 2 cm | 1 | high | False | A spherical metallic shell with 6 cm external radius weighs 6688 g. What is the thickness of the shell if the density of metal is  |
| 34 | 34 | 10 | 4: 1485 | 4 | high | False | Two positive numbers differ by 1280. When the greater number is divided by the smaller number, the quotient is 7 and the remainder |
| 35 | 35 | 10 | 4: 3 days | 4 | high | False | A can do a piece of work in 15 days. B is 25% more efficient than A, and C is 40% more efficient than B. A and C work together for |
| 36 | 36 | 10 |  | 3 | high | False | The base of a right prism is a regular hexagon of side 5 cm. If its height is 12√3 cm, then its volume (in cm³) is: |
| 37 | 37 | 11 | 3: 5/12 | 3 | high | False | Let x = (sqrt(1875)/sqrt(3888) / sqrt(1200)/sqrt(768)) * sqrt(175)/sqrt(1792). Then sqrt(x) is equal to: |
| 38 | 38 | 11 | 4: 135 π | 2 | high | False | The area of the base of a right circular cone is 81π cm² and its height is 12 cm. What is the curved surface area (in cm²) of the  |
| 39 | 39 | 11 | 4: -3/2 | 1 | high | False | The value of (2 sin² 38° sec² 52° + cos 64° sin 26° + sin² 64°) / (tan² 23° + cot² 23° - sec² 67° - cosec² 67°) is: |
| 40 | 40 | 12 | 2: 88.2 | 1 | high | False | Study the given graph and answer the question that follows. The total revenue in 2015 and 2017 is what per cent of the total expen |
| 41 | 41 | 12 | 4: 13/9 | None | high | True | In ΔABC, ∠C = 90°. Points P and Q are on the sides AC and BC, respectively, such that AP : PC = BQ : QC = 1 : 2. Then, (AQ^2 + BP^ |
| 42 | 42 | 12 | 4: 2.9% | 3 | high | False | The marked price of an article is 40% above its cost price. If its selling price is 73 1/2% of the marked price, then the profit p |
| 43 | 43 | 13 | 2: 103° | 3 | high | False | ABCD is a cyclic quadrilateral. Diagonals BD and AC intersect each other at E. If ∠BEC = 128° and ∠ECD = 25°, then what is the mea |
| 44 | 44 | 13 | 1: ₹14,470 | 4 | high | False | A certain sum amounts to ₹15,500 in 2 years at 12% p.a. simple interest. The same sum will amount to what in 1 1/2 years at 10% p. |
| 45 | 45 | 13 | 4: 5 | None | high | True | A and B start moving towards each other from places X and Y, respectively, at the same time on the same day. The speed of A is 20% |
| 46 | 46 | 13 | 3: (a²(2b² - a²))/(b²(a² + b²)) | 3 | high | False | If secθ = a/b, b ≠ 0, then (1-tan²θ)/(2-sin²θ) = ? |
| 47 | 47 | 14 | 3: 4 | 3 | high | False | If sin 3A = cos(A+10°), where 3A is an acute angle, then what is the value of 2cosec 3A/2 + 6sin² 3A - 3/2 tan² 3A? |
| 48 | 48 | 14 | 3: 35 | None | high | True | When x is added to each of 9, 15, 21 and 31, the numbers so obtained are in proportion. What is the mean proportional between the  |
| 49 | 49 | 14 | 3: -2/7 | 2 | high | False | In Δ PQR, ∠Q = 90°. If cot R = 1/3, then what is the value of secP (cosR + sinP) / cosec R (sinR - cosec P)? |
| 50 | 50 | 14 |  | 4 | high | False | अमित, अंकित मूल्य पर 12% छूट देने के बाद किसी वस्तु को ₹369.60 में बेचता है। यदि उसने कोई छूट नहीं दी होती तो उसे 20% का लाभ होता। |
| 51 | 51 | 15 | 1: 8 | None | high | True | When positive numbers x, y and z are divided by 31, the remainders are 17, 24 and 27, respectively. When (4x - 2y + 3z) is divided |
| 52 | 52 | 15 | 3: 240 m | 3 | high | False | As observed from the top of a light house, 120√3 m above the sea level, the angle of depression of a ship sailing towards it chang |
| 53 | 53 | 15 | 3: 2018 | None | high | True | Study the given graph and answer the question that follows. In which year was the revenue 33 1/3% more than the average expenditur |
| 54 | None | 16 | 1: 1/2 | 1 | high | False | The value of \frac{\cos^6\theta + \sin^6\theta + 3\sin^2\theta \cos^2\theta}{\text{cosec}\theta\sec\theta(\sin\theta + \cos\theta  |
| 55 | 55 | 16 | 2: 30,000 | 2 | high | False | A certain sum is lent at 4% p.a. for 3 years, 8% p.a. for the next 4 years, and 12% p.a. beyond 7 years. If for a period of 11 yea |
| 56 | 56 | 16 |  | 3 | high | False | The areas of three adjacent faces of a cuboidal tank are 3 m² , 12 m² and 16 m² . The capacity of the tank, in litres, is: |
| 57 | 57 | 16 |  | 3 | high | False | A train of length 287 m, running at 80 km/h, crosses another train moving in the opposite direction at 37 km/h in 18 seconds. What |
| 58 | 58 | 17 |  | 2 | high | False | Study the given graph and answer the question that follows. Break up for distribution (degree wise) of the employees working in fi |
| 59 | 59 | 17 | 4: 54 | 4 | high | False | Study the given graph and answer the question that follows. Break up for distribution (degree wise) of the employees working in fi |
| 60 | None | 18 | 3: 98 1/2 | 1 | high | False | If 1/(4-√8) + (3+2√2)/(3-2√2) - (3-2√2)/(3+2√2) = a + b√2, then what is the value of (3a + 4b)? |
| 61 | 61 | 18 |  | None | high | True | Study the given graph and answer the question that follows. In how many years was the profit (Revenue - Expenditure) as a percenta |
| 62 | 62 | 18 |  | 3 | high | False | A and B are solutions of acid and water. The ratios of water and acid in A and B are 4 : 5 and 1 : 2, respectively. If x litres of |
| 63 | 63 | 19 | 4: 1/4 | 4 | high | False | The numerator of a fraction is 3 more than the denominator. When 5 is added to the numerator and 2 is subtracted from the denomina |
| 64 | 64 | 19 | 1: 8 cm | 1 | high | False | In ΔABC, the bisector of ∠A intersects side BC at D. If AB = 12 cm, AC = 15 cm and BC = 18 cm, then the length of BD is: |
| 65 | 65 | 19 | 1: 218 cm² | 1 | high | False | The lengths of two sides of a parallelogram are 3 cm and 10 cm. What is the sum of the squares of the diagonals of the parallelogr |
| 66 | 66 | 19 | 1: 8 : 15 | None | high | True | The monthly incomes of A and B are in the ratio 3 : 5 and the ratio of their savings is 2 : 3. If the income of B is equal to thre |
| 67 | 67 | 20 |  | 2 | high | False | X and Y enter into a partnership with capital in the ratio 3 : 5. After 5 months X adds 50% of his capital, while Y withdraws 60%  |
| 68 | 68 | 20 | 4: 40 | 4 | high | False | The average of three numbers a, b and c is 2 more than c. The average of a and b is 48. If d is 10 less than c, then the average o |
| 69 | 69 | 20 | 2: 768 π | 4 | high | False | The radius and height of a right circular cone are in the ratio 3 : 4. If its curved surface area (in cm²) is 240 π, then its volu |
| 70 | 70 | 20 |  | None | high | True | Anuja owns 66 2/3% of a property. If 30% of the property that she owns is worth ₹1,25,000, then 45% of the value (in ₹) of the pro |
| 71 | 71 | 21 | 1: 64 : 27 | None | high | True | The sum of the radii of spheres A and B is 14 cm, the radius of A being larger than that of B. The difference between their surfac |
| 72 | 72 | 21 | 1: 18 cm | 1 | high | False | The perimeters of ΔABC and ΔDEF are 43.2 cm and 28.8 cm, respectively, and ΔABC~ΔDEF. If DE = 12 cm, then the length of AB is: |
| 73 | 73 | 21 | 2: 16 | None | high | True | If 27(x + y)³ - 8(x - y)³ = (x + 5y)(Ax² + By² + Cxy) , then what is the value of (A + B - C)? |
| 74 | 74 | 21 | 3: 18 | None | high | True | When 1062, 1134 and 1182 are divided by the greatest number x, the remainder in each case is y. What is the value of (x - y)? |
| 75 | 75 | 21 |  | None | high | True | Pipes A and B can fill a tank in 43.2 minutes and 108 minutes, respectively. Pipe C can empty it at 3 litres/minute. When all the  |
| 76 | 76 | 22 | 2: 5√8 | None | high | True | Given that x^8 - 34x^4 + 1 = 0, x > 0. What is the value of (x^3 + x^-3)? |
| 77 | 77 | 22 |  | None | high | True | A solid metallic sphere of radius 15 cm is melted and recast into spherical balls of radius 3 cm each. What is the ratio of the su |
| 78 | 78 | 22 | 1: 0.05 | None | high | True | The value of (0.0203 * 2.92) / (0.7 * 0.0365 * 2.9) ÷ ((12.12)^2 - (8.12)^2) / ((0.25)^2 + (0.25)(19.99)) is: |
| 79 | 79 | 22 | 1: tan A | None | high | True | cosA(sec A - cos A)(cotA + tan A) = ? |
| 80 | 80 | 23 | 4: 49.2 | None | high | True | Study the given graph and answer the question that follows. Break up for distribution (degree wise) of the employees working in fi |
| 81 | 81 | 23 | 3: 95 | None | high | True | If the 5-digit number 535ab is divisible by 3, 7 and 11, then what is the value of ( a^2 - b^2 + ab )? |
| 82 | 82 | 23 |  | None | high | True | If the radius of the base of a right circular cylinder is increased by 20% and the height is decreased by 30%, then what is the pe |
| 83 | 83 | 23 | 2: 28 | None | high | True | The area (in sq. units) of the triangle formed by the graphs of 8x + 3y = 24, 2x + 8 = y and the x-axis is: |
| 84 | 84 | 24 | 2: 20 | None | high | True | A is 80% more than B and C is 48 4/7% less than the sum of A and B. By what per cent is C less than A? |
| 85 | 85 | 24 | 4: 300 | None | high | True | In a school, 3/8 of the number of students are girls and the rest are boys. One-third of the number of boys are below 10 years and |
| 86 | 86 | 24 | 2: 16 | None | high | True | A certain number of students from school X appeared in an examination and 30% students failed. 150% more students than those from  |
| 87 | 87 | 24 | 3: 3 : 4 | None | high | True | The radii of two right circular cylinders are in the ratio 3 : 2 and the ratio of their volumes is 27 : 16. What is the ratio of t |
| 88 | 88 | 25 | 1: 11 1/9% | None | high | True | An article is marked 35% above its cost. If a profit of 20% is earned by selling the article, then the discount per cent offered o |
| 89 | 89 | 25 | 1: 12 1/2 | None | high | True | How many kg of rice costing ₹42 per kg should be mixed with 7 1/2 kg rice costing ₹50 per kg so that by selling the mixture at ₹53 |
| 90 | 90 | 25 | 1: 5 | None | high | True | A, B and C started a business. Twice the investment of A is equal to thrice the investment of B and also five times the investment |
| 91 | 91 | 25 | 1: 112° | None | high | True | In a circle with centre O, BC is a chord. Points D and A are on the circle, on the opposite side of BC, such that ∠DBC = 28° and B |
| 92 | 92 | 26 | 3: 10 days | None | high | True | A can do 20% of a work in 4 days, B can do 33 1/3% of the same work in 10 days. They worked together for 9 days. C completed the r |
| 93 | 93 | 26 | 2: 25% | None | high | True | Shashi sells two articles for ₹5,000 each with no loss and no profit in the overall transaction. If one article is sold at 16 2/3% |
| 94 | 94 | 26 |  | None | high | True | sinθ[(1-tanθ)tanθ+sec^2θ] / ((1-sinθ)tanθ(1+tanθ)(secθ+tanθ)) is equal to: |
| 95 | 95 | 26 | 1: 27° | None | high | True | In a circle with centre O, a diameter AB is produced to a point P lying outside the circle and PT is a tangent to the circle at th |
| 96 | 96 | 27 |  | None | high | True | Surekha borrowed a sum of money and returned it in two equal annual instalments of ₹5,547 each. If the rate of interest was 7 1/2  |
| 97 | 97 | 27 | 2: 31/41 | None | high | True | The graphs of the equations 3x - 20y - 2 = 0 and 11x - 5y + 61 = 0 intersect at P(a,b). What is the value of (a² + b² - ab)/(a² -  |
| 98 | 98 | 27 | 2: 10 : 13 | None | high | True | If (10 a³ + 4b³) : (11a³ - 15b³) = 7 : 5, then (3a + 5b) : (9a - 2b) = ? |
| 99 | 99 | 27 | 3: 125° | None | high | True | In ΔABC, ∠A - ∠B = 33°, ∠B - ∠C = 18°. What is the sum of the smallest and the largest angles of the triangle? |
| 100 | 100 | 28 | 3: 10 days | None | high | True | Three men and 4 women can do a piece of work in 7 days, whereas 2 men and 1 woman can do it in 14 days. Seven women will complete  |
