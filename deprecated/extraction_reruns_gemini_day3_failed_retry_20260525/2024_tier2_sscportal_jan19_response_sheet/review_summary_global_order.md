# Full PDF Visual Extraction

- Source PDF: `C:\experiments\ssc\answer_key_candidates_staging\2024_tier2_sscportal_jan19_response_sheet.pdf`
- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order
- Questions extracted: 97 / None
- Overall status: INFRA_FAILURE
- Structural QC passed: False
- Load errors: [{'page': 13, 'warnings': ["ERROR JSONDecodeError: Expecting ':' delimiter: line 80 column 9 (char 1892)", '{\n  "page": 13,\n  "questions": [\n    {\n      "question_number": 34,\n      "section": null,\n      "question_text_full": "Level of significance is:",\n      "options": [\n        {\n          "label": "1",\n          "text": "Probability of Type I Error"\n        },\n        {\n          "label": "2",\n          "text": "1 - Probability of Type I Error"\n        },\n        {\n          "label": "3",\n          "text": "1 - Probability of Type II Error"\n        },\n        {\n          "label": "4",\n          "text": "Probability of Type II Error"\n        }\n      ],\n      "question_id": "6306801307996",\n      "chosen_option_label": "3",\n      "correct_option_label": "1",\n      "correct_option_text": "Probability of Type I Error",\n      "is_complete_on_page": true,\n      "confidence": "high",\n      "notes": ""\n    },\n    {\n      "question_number": 35,\n      "section": null,\n      "question_text_full": "Let X follow Poisson distribution with mean λ. If P(X = 2) = 1/2 P(X = 3), then the value of λ is:",\n      "options": [\n        {\n          "label": "1",\n          "text": "4"\n        },\n        {\n          "label": "2",\n          "text": "6"\n        },\n        {\n          "label": "3",\n          "text": "7"\n        },\n        {\n          "label": "4",\n          "text": "2"\n        }\n      ],\n      "question_id": "6306801352881",\n      "chosen_option_label": "2",\n      "correct_option_label": "2",\n      "correct_option_text": "6",\n      "is_complete_on_page": true,\n      "confidence": "high",\n      "notes": ""\n    },\n    {\n      "question_number": 36,\n      "section": null,\n      "question_text_full": "Which of the following is the relative measure of skewness?",\n      "options": [\n        {\n          "label": "1",\n          "text": "β2"\n        },\n        {\n          "label": "2",\n          "text": "β1"\n        },\n        {\n          "label": "3",\n          "(X - μ)/σ"\n        },\n        {\n          "label": "4",\n          "(Q3 - 2Q2 + Q1) / (Q3 - Q1)"\n        }\n      ],\n      "quest'], 'failure_type': 'json_or_schema_failure', 'retryable': True}]
- Option/correct-answer issue global questions: []
- Missing/invalid chosen-option global questions: [30, 48, 70, 92]
- Low-confidence global questions: []
- Manual review count: 4
- Canonical review count: 11

## Gate Summary

| Check | Status | Count/Detail |
|---|---|---|
| Page JSON parse | FAIL | 1 failures |
| Expected question count | PASS | 97 / None |
| Four options and correct answer | PASS | [] |
| Chosen answer present/valid | WARN | [30, 48, 70, 92] |
| Confidence/manual-review flags | PASS | [] |
| Canonical review routing | WARN | 11 questions |

## Page Counts

| Page | Questions |
|---:|---:|
| 1 | 2 |
| 2 | 0 |
| 3 | 3 |
| 4 | 4 |
| 5 | 3 |
| 6 | 3 |
| 7 | 3 |
| 8 | 3 |
| 9 | 3 |
| 10 | 3 |
| 11 | 3 |
| 12 | 3 |
| 13 | 0 |
| 14 | 0 |
| 15 | 3 |
| 16 | 3 |
| 17 | 3 |
| 18 | 3 |
| 19 | 3 |
| 20 | 3 |
| 21 | 3 |
| 22 | 3 |
| 23 | 3 |
| 24 | 3 |
| 25 | 3 |
| 26 | 3 |
| 27 | 4 |
| 28 | 2 |
| 29 | 3 |
| 30 | 3 |
| 31 | 3 |
| 32 | 3 |
| 33 | 3 |
| 34 | 4 |
| 35 | 0 |
| 36 | 3 |

## Review Table

| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |
|---:|---:|---:|---|---|---|---|---|
| 1 | 1 | 1 | 4: 3(2x + 3) / 4(1 + x)^4 | 3 | high | False | For the bivariate random variable (X,Y), let the joint probability density function be f(x,y) = 9(1 + x + y) / 2(1 + x)^4(1 + y)^4 |
| 2 | 2 | 1 | 3: 1.0 | 3 | high | False | Monthly sales data (in units) shows the following trend-adjusted ratios for three months: January (1.1), February (0.9), and March |
| 3 | 3 | 3 | 3: Range Statistic (R) | 3 | high | False | Duncan's Multiple Range Test makes use of which statistical measure? |
| 4 | 4 | 3 | 3: (1 - r)(1 + 2r) / (1 + r) | 4 | high | False | For three random variables X1, X2 and X3, the correlation coefficients between pairs of random variables are r12 = r13 = r23 = r ≠ |
| 5 | 5 | 3 | 2: It is subjective and may lead to inconsistent | 2 | high | False | What is the primary challenge in using the free-hand curve method for trend estimation? |
| 6 | 6 | 4 | 4: Two tailed | 4 | high | False | If the critical region is evenly distributed, then the test is referred to as: |
| 7 | 7 | 4 |  | 3 | high | False | Which of the following is NOT true for seasonal variation? |
| 8 | 8 | 4 | 1: Three | 1 | high | False | In a two-way ANOVA, how many hypotheses are tested? |
| 9 | 9 | 4 | 1: The results of ANCOVA may be biased. | 1 | high | False | In ANCOVA, what happens when the covariate is not linearly related to the dependent variable? |
| 10 | 10 | 5 | 2: 5 | 3 | high | False | Let X and Y be two independent Poisson variates with rate 5 and 10, respectively, then the E(XY=2) is equal to: |
| 11 | 11 | 5 | 2: 0 | 2 | high | False | The mean of a residual error in a one way classified data analysis is: |
| 12 | 12 | 5 | 3: 0 | 3 | high | False | If the angle between two lines of regression is 90°, then correlation coefficient is: |
| 13 | 13 | 6 |  | 4 | high | False | For a monthly data, the link relative for any month is given by: |
| 14 | 14 | 6 | 1: b/12 | 1 | high | False | On fitting of a trend line Y = a + bt on a time series (with year as a unit of time), the monthly increment/decrement is given by |
| 15 | 15 | 6 | 2: M - Md | 4 | high | False | If M: Mean, Md: Median, Mo: Mode, Q1: First Quartile and Q3: Third Quartile, then which of the following is an absolute measure of |
| 16 | 16 | 7 | 2: Histograms are constructed using cumulative f | 2 | high | False | Which of the following is NOT true? |
| 17 | 17 | 7 | 3: pq (r-1) and pqr-1 | 1 | high | False | For a two-way classification with p treatments, q blocks and r observations per cell, the degrees of freedom for error and total,  |
| 18 | 18 | 7 | 1: Poisson distribution with rate 15 | 1 | high | False | Let X and Y be two independent Poisson variates with rate 5 and 10, respectively, then the distribution of Z=X+Y is: |
| 19 | 19 | 8 | 2: 1/4 | 1 | high | False | The second central moment of the Binomial distribution B(1, 1/2) is: |
| 20 | 20 | 8 | 2: 13 | 2 | high | False | 10-15 is the model class with 25 as its frequency. Also if the frequency of the class preceding and succeeding the model class is  |
| 21 | 21 | 8 | 4: Used when number of observations in data set  | 2 | high | False | Which of the following is NOT true about ungrouped frequency distribution? |
| 22 | 22 | 9 | 3: Skewness | 3 | high | False | What does the third moment measure? |
| 23 | 23 | 9 |  | 3 | high | False | For testing whether two independent Normal populations (with unknown and equal variances) have same mean, one uses: |
| 24 | 24 | 9 | 1: First-Order: 20, Second-Order: -30 | 3 | high | False | The following data represents a time series. Period : 1 2 3 4 5 Observed values : 150 140 160 170 180 Compute the first-order and  |
| 25 | 25 | 10 | 4: frequency of the class divided by total frequ | 4 | high | False | The relative frequency of a class is: |
| 26 | 26 | 10 | 3: 1/4 | 2 | high | False | Let (X, Y) have the probability density function (pdf) as f(x, y) = [c(x + 2y) if 0 < x < 2, 0 < y < 1 0 , otherwise. The value of |
| 27 | 27 | 10 | 4: displays random pattern | 1 | high | False | A model being fitted is said to be adequate if the residual plot: |
| 28 | 28 | 11 | 2: median | 4 | high | False | For a normal distribution, the mean deviation is minimum when deviations are taken from: |
| 29 | 29 | 11 | 3: Classical definition | 1 | high | False | Which definition of probability is NOT applicable if the events of a random experiment are not equally likely? |
| 30 | 30 | 11 | 1: 3/8 | None | high | True | If the joint distribution of two random variables X1 and X2 is f(x1,x2) = {x1 + x2; 0 < x1,x2 < 1 {0, otherwise , then P(0 < X2 <  |
| 31 | 31 | 12 | 1: 2/7 | 1 | high | False | Find the probability that there may be 53 Sundays in a leap year. |
| 32 | 32 | 12 | 3: 2 | 3 | high | False | For two random variables X and Y, how many lines of regression are possible? |
| 33 | 33 | 12 | 3: 5.3 | 3 | high | False | Out of 100 numbers, 20 are 4's, 40 are 5's, 30 are 6's and the remaining are 7's. The arithmetic mean of the numbers is: |
| 34 | 37 | 15 | 2: 4.88 | 3 | high | False | The mean absolute deviation of 25, 30, 27, 40 and 35 is: |
| 35 | 38 | 15 | 3: expenditure involved at time of collection of | 3 | high | False | Before using secondary data, one need NOT verify: |
| 36 | 39 | 15 | 2: 2/25 | 3 | high | False | 25 books are placed at random on a shelf. The probability that a particular pair of books shall be always together is: |
| 37 | 40 | 16 | 1: Negative Perfect Correlation | 1 | high | False | Scatter diagram for the following data shows _________. X 1 2 3 4 5 Y 9 8 7 6 5 |
| 38 | 41 | 16 | 1: (p1 - p2) ± 1.96 √(p1q1/n1 + p2q2/n2) | 1 | high | False | With usual notations, the 95% confidence limits for the difference of two proportions is: |
| 39 | 42 | 16 | 3: 3/4 | 3 | high | False | Find the coefficient of skewness from the following information: Mode = 11, median = 8, Q3-Q1 = 8, Q3+Q1 = 22. |
| 40 | 43 | 17 | 4: mutually exclusive and exhaustive | 4 | high | False | On rolling of a die, the events E1 (getting an even number) and E2 (getting an odd number) are: |
| 41 | 44 | 17 | 3: 1/4 | 3 | high | False | If Y = x/2 + 2 and X = y/8 - 1 are regression lines of Y on X and X on Y, then correlation coefficient between X and Y is equal to |
| 42 | 45 | 17 | 3: 3 | 3 | high | False | The coefficient of kurtosis ( β2 ) of standard normal distribution is equal to: |
| 43 | 46 | 18 | 1: x̄ ± 1.96(σ/√n) | 1 | high | False | If a large sample of size n is taken from a normal population with mean μ and standard deviation σ, the 95% confidence interval fo |
| 44 | 47 | 18 | 4: mean | 4 | high | False | O-gives are NOT useful for locating: |
| 45 | 48 | 18 | 3: Irving Fisher Index | 3 | high | False | Which of the following index numbers is the geometric mean of Laspeyre's and Paasche's Index number? |
| 46 | 49 | 19 | 1: Seasonal component | 4 | high | False | Which component of a time series represents short-term fluctuations due to seasonal factors? |
| 47 | 50 | 19 |  | 3 | high | False | Type I error occurs when: |
| 48 | 51 | 19 | 2: The hypothesis for testing mu < mu0 is two si | None | high | True | Which of the following statements is FALSE? |
| 49 | 52 | 20 | 4: μ | 4 | high | False | The median of the normal distribution with mean and variance μ and σ² is: |
| 50 | 53 | 20 | 1: -1 or 1 | 1 | high | False | When two judges rank only two individuals, then value of Spearman's rank correlation coefficient is: |
| 51 | 54 | 20 | 3: (Σ pij) / Σ p0j * 100 | 3 | high | False | The formula used for finding the simple aggregate index numbers is: |
| 52 | 55 | 21 | 2: (n - 1) s² = n S² | 2 | high | False | If S² is the sample variance of a sample of size n and s² is an unbiased estimator of population variance, then which of the follo |
| 53 | 56 | 21 | 1: tanθ - 1 | 1 | high | False | For three random variables X₁, X₂ and X₃, correlation coefficients between pairs of random variables are r₁₂ = sin²θ, r₁₃ = cosθ a |
| 54 | 57 | 21 | 2: Alternative hypothesis accepted if set points | 1 | high | False | Which of the following statements is NOT true about a critical region w? |
| 55 | 58 | 22 | 1: 13.2 | 1 | high | False | For the set of numbers 2, 3, 7, 8 and 10, the second order moment about the origin 4 is: |
| 56 | 59 | 22 | 2: 11.25 | 2 | high | False | In a data set, let the first and third quartiles be 268.25 and 290.75, respectively. The quartile deviation is equal to: |
| 57 | 60 | 22 | 1: 0.0764 | 1 | high | False | It has been found that 2% of the tools produced by a certain machine are defective. What is the probability that in a shipment of  |
| 58 | 61 | 23 | 4: 25/4 | 4 | high | False | If the values of Bowley's coefficient of skewness, third quartile and first quartile are 0.5, 10 and 5, respectively, then the val |
| 59 | 62 | 23 | 1: Trend | 4 | high | False | Which of the following components of time series reflect the general tendency of the data to increase or decrease during a long pe |
| 60 | 63 | 23 | 2: 12.11 | 3 | high | False | In a completely randomized design, with 4 treatments replicated 5 times, the following information is obtained. SST=26234.95, SSE= |
| 61 | 64 | 24 | 2: 1/36 | 2 | high | False | If a fair six-sided die is tossed twice and the tosses are independent, then probability of getting a 5 on both tosses is: |
| 62 | 65 | 24 |  | 1 | high | False | The primary purpose of constructing index numbers is to: |
| 63 | 66 | 24 | 4: quartile deviation | 4 | high | False | Half of the difference between the 75th percentile and 25th percentile is called: |
| 64 | 67 | 25 | 3: tend to have heavy outliers | 3 | high | False | Data sets with high kurtosis: |
| 65 | 68 | 25 | 4: 1 | 2 | high | False | Let a continuous random variable X have pdf f(x) = { -0.75 x^2 + 1.5x for 0 < x < 2 0 , otherwise The mode of X is: |
| 66 | 69 | 25 | 2: 1 | 3 | high | False | At what value of R_1.23 are all regression residuals zero? |
| 67 | 70 | 26 | 1: 10 | 3 | high | False | If the standard deviation of a population is 100, then based on a sample of size 100, the standard deviation of sample mean is equ |
| 68 | 71 | 26 | 2: 10 | 2 | high | False | If for the given distribution, the arithmetic mean is 9.41, then which of the following values will replace the question mark (?)  |
| 69 | 72 | 26 | 3: class intervals are of equal width | 2 | high | False | For a frequency polygon: |
| 70 | 73 | 27 | 1: 26 | None | high | True | The first four moments of a distribution about X=2 are -2, 12, -20 and 100, then μ3 equals: |
| 71 | 74 | 27 | 4: 1/2 | 4 | high | False | Die I has 4 red and 2 white faces and die II has 2 red and 4 white faces. A coin is flipped once. If head appears, the game contin |
| 72 | 75 | 27 | 4: 16 | 4 | high | False | The mean and variance of a Binomial distribution are 8 and 4 respectively, then the value of n is: |
| 73 | 76 | 27 | 2: 0 | 1 | high | False | Let X follows normal distribution with mean μ and median μ̃, then P(μ < X < μ̃) is equal to: |
| 74 | 77 | 28 | 3: Σ_{j=1}^k Σ_{i=1}^{n_j}(x_ij - x_bar_j)^2 | 4 | high | False | For a completely randomised design with k treatments, let x_ij = i^th observation corresponding to j^th treatment, i = 1,2,...,n_j |
| 75 | 78 | 28 | 2: Uncorrelated | 4 | high | False | If (X, Y) has a bivariate normal distribution, then X, Y are independent if and only if X, Y are: |
| 76 | 79 | 29 | 4: 1/8 | 4 | high | False | What is the geometric mean of 1/4, 1/8 and 1/16? |
| 77 | 80 | 29 |  | 2 | high | False | Let X1, X2, . . . , X10 be 10 independent and identically distributed (i.i.d) random variables taking the values 0, 1 with corresp |
| 78 | 81 | 29 |  | 1 | high | False | In using one way analysis of variance for testing whether treatments are equally effective for a certain experimental data, if Fca |
| 79 | 82 | 30 | 2: 7/2^5 | 1 | high | False | The mean and variance of a binomially distributed random variable X are 4 and 2, respectively. P(X = 2)is equal to: |
| 80 | 83 | 30 | 4: approaches the true probability of an event | 4 | high | False | As the sample size increases, empirical probability: |
| 81 | 84 | 30 | 4: The sequence of asked questions can be change | 2 | high | False | Which of the following is NOT true about collecting data through structured interviews? |
| 82 | 85 | 31 | 4: Correlation | 4 | high | False | Which of the following is NOT considered as a property of a good estimator? |
| 83 | 86 | 31 | 3: 5/6 | 3 | high | False | Suppose a sample of size 36 is drawn from a population with mean 2 and variance 25 using simple random sampling with replacement.  |
| 84 | 87 | 31 | 2: 1/n [ 1 - (1-p)n ] | 2 | high | False | 'p' is the probability that a man aged x years will die in a year. If there are n men aged x, A1 will die in a year and will be th |
| 85 | 88 | 32 | 2: Residuals showing a skewed distribution | 1 | high | False | In a one-way ANOVA, which of the following would indicate a violation of the normality assumption? |
| 86 | 89 | 32 | 4: The seasonal component is additive. | 4 | high | False | What is the main assumption of the ratio-to-moving-averages method? |
| 87 | 90 | 32 | 4: Ui Ai = S and Ai ∩ Aj = Ø for i ≠ j | 4 | high | False | For an experiment with sample space S, the events Ai, i = 1, 2, 3, .... are mutually exclusive and exhaustive if: |
| 88 | 91 | 33 | 3: Autobiography | 2 | high | False | Which of the following is NOT a secondary source of data? |
| 89 | 92 | 33 | 4: 4, 6 | 4 | high | False | The points of inflection of a normal distribution N (5, 1) that exist at x is equal to: |
| 90 | 93 | 33 | 4: 100 | 2 | high | False | From a population of a large number of workers with a standard deviation 5, a sample is drawn and the standard error is found to b |
| 91 | 94 | 34 | 2: 9 | 2 | high | False | If the arithmetic mean is 25 and geometric mean is 15, then the value of the Harmonic mean is equal to: |
| 92 | 95 | 34 | 4: x̄ | None | high | True | If x̄ is the mean of a sample from N(μ, 1), then the maximum likelihood estimator of μ is: |
| 93 | 96 | 34 | 3: Personal and intimate questions should be put | 3 | high | False | Which of the following is NOT a good characteristic of a questionnaire? |
| 94 | 97 | 34 | 4: 47.826 | 4 | high | False | The coefficient of variation and standard deviation for a dataset are 23 and 11, then the mean is approximately equal to: |
| 95 | 98 | 36 | 2: N-n / N-1 | 2 | high | False | Let N be the size of a population and n be the size of the sample. Then the efficiency of SRSWOR with respect to SRSWR is: |
| 96 | 99 | 36 | 1: Product moment correlation coefficient | 3 | high | False | Karl Pearson's correlation coefficient is also called: |
| 97 | 100 | 36 | 3: 1 + 3.322 × log10 N | 2 | high | False | Usually the formula to determine the number of classes is given by: |
