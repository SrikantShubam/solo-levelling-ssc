# Worker Round 2 Scoring Rubric

Use this rubric when ranking Gemini, DeepSeek, and Mimo after the second pass.

## Scoring Categories

- Evidence accuracy: `0-40`
  - Are claims supported by `Plan.md`, README, canonical docs, or code?
  - Did the worker separate confirmed facts from branch-stale guesses?

- Scope discipline: `0-20`
  - Did the worker stay inside assigned files and task boundaries?
  - Did it avoid runtime changes, schema changes, and dependency churn?

- Merge quality: `0-20`
  - Is the output close to canonical-main quality?
  - If tests were written, do they collect and fail for meaningful reasons?

- Signal density: `0-10`
  - Does the output surface the highest-value findings without filler?

- Branch hygiene: `0-10`
  - Did the worker commit only intended files and push cleanly?
  - Did it report context gaps instead of inventing local replacements?

## Automatic Penalties

- `-20`
  - Claims a file or test is missing without checking the canonical main path when instructed.

- `-20`
  - Uses top-level import failure as the main red-test strategy.

- `-15`
  - Includes tautological assertions, placeholder checks, or obviously meaningless tests.

- `-15`
  - Overstates a partial truth as a repo-wide fact.

- `-10`
  - Leaves branch junk or unrelated files in the final diff.

## Rating Bands

- `90-100`: strong orchestrator-grade output
- `75-89`: useful with small corrections
- `60-74`: mixed quality, needs non-trivial rewrite
- `40-59`: partial value, weak mergeability
- `<40`: mostly reject
