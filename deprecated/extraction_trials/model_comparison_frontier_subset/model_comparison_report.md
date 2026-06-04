# Model Comparison Report

- Pages tested: [1, 5, 17, 28]

| Provider | Model | Status | Correct Acc | Chosen Acc | Fills Missing Chosen | Option Shape | Text Similarity | Reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| nvidia_nim | mistralai/mistral-medium-3.5-128b | PASS | 1.00 | 0.75 | 0 | 1.00 | 0.98 |  |
| nvidia_nim | meta/llama-4-maverick-17b-128e-instruct | PASS | 1.00 | 0.75 | 1 | 1.00 | 0.98 |  |
| nvidia_nim | mistralai/mistral-large-3-675b-instruct-2512 | FAIL | 0.75 | 0.50 | 0 | 0.75 | 0.73 |  |
