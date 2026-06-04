# Model Comparison Report

- Pages tested: [1, 5, 17, 28]

| Provider | Model | Status | Correct Acc | Chosen Acc | Fills Missing Chosen | Option Shape | Text Similarity | Reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| nvidia_nim | mistralai/mistral-medium-3.5-128b | FAIL | 0.12 | 0.50 | 0 | 0.50 | 0.50 |  |
| nvidia_nim | meta/llama-4-maverick-17b-128e-instruct | FAIL | 0.50 | 1.00 | 1 | 1.00 | 0.99 |  |
| nvidia_nim | google/gemma-3n-e4b-it | FAIL | 0.12 | 0.50 | 0 | 0.12 | 0.35 |  |
