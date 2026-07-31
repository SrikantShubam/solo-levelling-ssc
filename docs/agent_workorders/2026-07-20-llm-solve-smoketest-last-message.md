I could not complete the four-model measurement because both required remote execution paths are blocked by the sandbox at socket creation.

1. The full 30-question side-by-side table

| # | question id / section | stored | deepseek-r1 | qwen3-thinking | tencent/hy3:free | gpt-5.4-mini |
|---:|---|---:|---|---|---|---|
| 1 | `harvest_2016_tier1_testbook_compilation_q724` / Quant/DI | 1 | not run | not run | not run | not run |
| 2 | `harvest_2017_tier1_testbook_compilation_q2515` / Quant/DI | 2 | not run | not run | not run | not run |
| 3 | `harvest_2017_tier1_testbook_compilation_q2444` / Quant/DI | 1 | not run | not run | not run | not run |
| 4 | `harvest_2017_tier1_testbook_compilation_q2086` / Quant/DI | 3 | not run | not run | not run | not run |
| 5 | `harvest_2017_tier1_testbook_compilation_q2017` / Quant/DI | 2 | not run | not run | not run | not run |
| 6 | `harvest_2017_tier1_testbook_compilation_q308` / Quant/DI | 3 | not run | not run | not run | not run |
| 7 | `harvest_2022_tier1_prepp_2022-12-12_shift4_q187` / Quant/DI | 1 | not run | not run | not run | not run |
| 8 | `harvest_2017_tier1_testbook_compilation_q2183` / Quant/DI | 3 | not run | not run | not run | not run |
| 9 | `harvest_2016_tier1_testbook_compilation_q233` / Quant/DI | 1 | not run | not run | not run | not run |
| 10 | `harvest_2018_tier1_prepp_2019-06-07_shift1_q61` / Quant/DI | 3 | not run | not run | not run | not run |
| 11 | `harvest_2022_tier1_prepp_2022-12-02_shift2_q22` / Reasoning | 4 | not run | not run | not run | not run |
| 12 | `harvest_2017_tier1_prepp_2017-08-12_shift1_q1` / Reasoning | 1 | not run | not run | not run | not run |
| 13 | `harvest_2017_tier1_testbook_compilation_q539` / Reasoning | 4 | not run | not run | not run | not run |
| 14 | `harvest_2016_tier1_prepp_2016-09-11_shift1_q6` / Reasoning | 4 | not run | not run | not run | not run |
| 15 | `harvest_2022_tier1_prepp_2022-12-13_shift3_q21` / Reasoning | 2 | not run | not run | not run | not run |
| 16 | `harvest_2022_tier1_prepp_2022-12-08_shift4_q4` / Reasoning | 1 | not run | not run | not run | not run |
| 17 | `2024_tier1_prepp_shift1_q13` / Reasoning | 1 | not run | not run | not run | not run |
| 18 | `harvest_2023_tier1_prepp_2023-07-17_shift4_q18` / Reasoning | 1 | not run | not run | not run | not run |
| 19 | `harvest_2022_tier1_prepp_2022-12-06_shift3_q16` / Reasoning | 4 | not run | not run | not run | not run |
| 20 | `harvest_2017_tier1_testbook_compilation_q2143` / Reasoning | 2 | not run | not run | not run | not run |
| 21 | `harvest_2020_tier2_prepp_2022-02-03_english_akey_q276` / English | 1 | not run | not run | not run | not run |
| 22 | `harvest_2023_tier1_prepp_2023-07-24_shift4_q90` / English | 3 | not run | not run | not run | not run |
| 23 | `harvest_2022_tier1_prepp_2022-12-02_shift2_q95` / English | 3 | not run | not run | not run | not run |
| 24 | `harvest_2022_tier1_prepp_2022-12-01_shift1_q94` / English | 3 | not run | not run | not run | not run |
| 25 | `harvest_2023_tier1_prepp_2023-07-21_shift1_alt_q87` / English | 3 | not run | not run | not run | not run |
| 26 | `26433059713` / English | 3 | not run | not run | not run | not run |
| 27 | `81616113413` / English | 4 | not run | not run | not run | not run |
| 28 | `harvest_2023_tier1_prepp_2023-07-18_shift1_q82` / English | 1 | not run | not run | not run | not run |
| 29 | `harvest_2022_tier1_prepp_2022-12-12_shift4_q86` / English | 4 | not run | not run | not run | not run |
| 30 | `harvest_2017_tier1_prepp_2017-08-10_shift1_q87` / English | 2 | not run | not run | not run | not run |

2. Per-model results

No agreement counts, rates, measured costs, or extrapolated costs are available because no model calls completed.

Blocked checks:
- OpenRouter `/api/v1/key`: failed with `PermissionError: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`.
- `codex.cmd exec -m gpt-5.4-mini "Return exactly: OK"`: failed connecting to `wss://api.openai.com/v1/responses`, then HTTPS fallback also failed with socket error `10013`.

3. Cross-model disagreement notes

Unavailable. Since no model returned answers, there is no pairwise disagreement data.

4. Recommendation

No model recommendation can be made from this run. The measurement is blocked by network restrictions, not by repo logic or missing credentials. I did create the exact sampled set at [reports/llm_solve_smoketest_sample_20260720.json](/C:/experiments/ssc/reports/llm_solve_smoketest_sample_20260720.json), using seed `20260720`, current `_web_baseline_rejection_reason`, and excluding GK/GA.

Verification:
- DB opened read-only via `file:data/study.db?mode=ro`.
- Current in-scope unverified pools: Quant/DI `2747`, Reasoning `548`, English `972`.
- `data/study.db` last write time remained `2026-07-19 21:10:58 UTC`.
- No database writes were attempted.