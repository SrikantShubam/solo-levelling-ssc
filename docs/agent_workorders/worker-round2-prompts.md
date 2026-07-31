# Worker Round 2 Prompts

Use these prompts as the exact dispatch text for the next worker run.

## Gemini Prompt

```text
Work on branch `codex/phase3b-gemini-scope` in worktree `C:\experiments\ssc\gm`.

Read these canonical files by absolute path first:
- C:\experiments\ssc\docs\agent_workorders\gemini-round2-workorder.md
- C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md

Then execute only that workorder.

Hard rules:
- docs only
- no source edits
- no test edits
- no network
- if local branch files are stale, prefer canonical-main evidence from C:\experiments\ssc\...
- push when done

Return only:
- status
- changed file
- three corrected claims from round one
- five strongest conclusions
- commit SHA
- push status
```

## DeepSeek Prompt

```text
Work on branch `codex/phase3b-deepseek-tests` in worktree `C:\experiments\ssc\ds`.

Read these canonical files by absolute path first:
- C:\experiments\ssc\docs\agent_workorders\deepseek-round2-workorder.md
- C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-test-cases.md
- C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md

Then execute only that workorder.

Critical correction from round one:
- do not create a test file that fails collection through top-level import of a missing module
- do not use tautological assertions
- docs-only is acceptable if tests are not merge-quality

Hard rules:
- no production code edits
- no schema or dependency changes
- no network
- push when done

Return only:
- status
- changed files
- whether the result is spec-quality or merge-quality
- verification command and result
- remaining production API assumptions
- commit SHA
- push status
```

## Mimo Prompt

```text
Work on branch `codex/phase3b-mimo-inventory` in worktree `C:\experiments\ssc\mm`.

Read these canonical files by absolute path first:
- C:\experiments\ssc\docs\agent_workorders\mimo-round2-workorder.md
- C:\experiments\ssc\docs\agent_workorders\worker-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\pattern-intelligence-guardrails.md
- C:\experiments\ssc\docs\agent_workorders\worker-round2-scoring-rubric.md

Then execute only that workorder.

Critical correction from round one:
- do not claim files or tests are missing without checking canonical-main paths in C:\experiments\ssc

Hard rules:
- docs only
- no code edits
- no test edits
- no network
- push when done

Return only:
- status
- changed file
- top ten findings
- three corrected claims from round one
- commit SHA
- push status
```
