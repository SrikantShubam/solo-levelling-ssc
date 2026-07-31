# Worker Guardrails

These rules apply to all worker agents on the pattern-intelligence review and planning pass.

Canonical coordination docs live only in:
- `C:\experiments\ssc\docs\agent_workorders`
- `C:\experiments\ssc\docs\superpowers\specs`
- `C:\experiments\ssc\docs\superpowers\plans`

Worker workspaces must read those canonical files by absolute path. Do not copy or maintain local duplicates inside `gm`, `ds`, or `mm`.

## Branches And Worktrees

Main workspace:
- Path: `C:\experiments\ssc`
- Branch: `main`
- Status: dirty workspace with recent Phase 3 and hardening changes.

Worker branches:
- Gemini scope branch: `codex/phase3b-gemini-scope`
- DeepSeek tests branch: `codex/phase3b-deepseek-tests`
- Mimo inventory branch: `codex/phase3b-mimo-inventory`

Worker worktrees:
- Gemini: `C:\experiments\ssc\gm`
- DeepSeek: `C:\experiments\ssc\ds`
- Mimo: `C:\experiments\ssc\mm`

Important:
- Worker branches were created from `HEAD` commit `61b1490`.
- They may not include uncommitted main-workspace Phase 3 and hardening files.
- Workers must read canonical docs from `C:\experiments\ssc\docs\...` by absolute path when branch context is stale.
- Workers must report missing files as context gaps instead of inventing replacements.
- Workers must distinguish:
  - `spec-quality`: useful ideas or contracts that still need orchestrator rewrite
  - `merge-quality`: ready to copy into main with minimal edits

## Hard Bans

Workers must not:
- edit `.env`, `.env.txt`, or any secret-bearing file
- add, remove, or rename database tables
- change migrations
- delete tests
- delete corpus data
- run network-dependent tests
- change extraction outputs under `pipeline_output/`, `deprecated/`, `raw/`, or `wiki/`
- rewrite large files wholesale
- modify runtime Phase 3 orchestration to consume evaluation output
- make evaluator output mutate queues, readiness, gates, archetypes, attempts, or SM-2 state
- rename existing public functions unless the workorder explicitly allows it
- commit generated caches, logs, or binary artifacts

## Test Quality Rules

If a worker is writing tests or test specs, it must not:
- make the whole test module fail at import time just to force a red test
- hardcode a production module name unless the canonical spec already fixes that name
- add tautological assertions or `or True`-style placeholders
- overconstrain future dataclass field names beyond the canonical spec
- confuse `expected failure because feature is missing` with `low-quality test design`

Acceptable red tests:
- collect successfully
- fail at assertion time or with a narrow runtime error caused by missing behavior
- prove one contract at a time

## Required Behavior

Every worker must:
- read `Plan.md`
- read `README.md` if the workorder mentions phase drift or current status
- read `C:\experiments\ssc\docs\agent_workorders\phase3-scope-breakdown.md`
- read this guardrail file
- inspect only files needed for its workorder
- keep changes inside allowed files
- provide exact changed files
- provide exact test commands run
- provide blockers instead of guessing
- cite repo evidence for claims about scope or missing behavior

## Completion Protocol

When finished, every worker must:
- run `git status --short`
- review `git diff`
- run the workorder's verification command
- commit only allowed files
- push its branch with `git push -u origin <branch-name>`
- if push fails, report the exact error and leave the commit local

Commit message format:
- Gemini: `docs: review phase taxonomy and pattern scope`
- DeepSeek: `test: specify pattern intelligence contract`
- Mimo: `docs: inventory pattern system`

Final worker response must include:
- commit SHA
- push status
- changed files
- verification command and result
- blockers or context gaps

## Review Gate

No worker output is accepted until the main orchestrator reviews:
- diff scope
- forbidden-file violations
- test coverage
- branch-staleness effects on findings
- whether the work changes runtime behavior
- whether any model-generated claim lacks code or plan evidence
- whether proposed tests are merge-quality or only spec-quality

## Token-Saving Rule

Workers should return compact findings:
- one-line status
- changed files
- commands run
- blockers
- evidence list

Do not return long prose unless the workorder asks for a design memo.
