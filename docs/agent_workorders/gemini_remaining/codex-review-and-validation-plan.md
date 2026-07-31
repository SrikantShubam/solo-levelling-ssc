# Codex Review And Validation Plan

Use this after Gemini finishes a workorder.

## Inputs Required From Gemini

Gemini must provide:

- completed workorder path
- changed files
- commit SHA if committed
- exact test commands and results
- any blockers
- any deferred behavior

## Review Steps

1. Inspect status:

```powershell
git status --short
git log --oneline -5
```

2. Inspect the Gemini diff:

```powershell
git show --stat --oneline HEAD
git show --name-only --oneline HEAD
git diff HEAD~1..HEAD -- src tests docs README.md memory.md
```

If Gemini did not commit, inspect the working tree diff instead:

```powershell
git diff -- src tests docs README.md memory.md
```

3. Check scope:

- changed files are allowed by the workorder
- no secrets or generated data changed
- no extraction outputs changed
- no broad rewrites
- no runtime mutation added to read-only features
- no Phase 3 coupling to Phase 2c pattern output

4. Check tests:

- tests collect normally
- tests fail for meaningful reasons before implementation if reviewing staged TDD output
- tests assert behavior, not implementation trivia
- tests include negative cases and non-mutation checks
- tests do not depend on network or local secrets

5. Run focused verification:

For Phase 2c:

```powershell
uv run pytest tests/test_pattern_intelligence_contract.py tests/test_phase3.py tests/test_phase3_eval.py tests/test_cli.py -q
```

For Phase 4:

```powershell
uv run pytest tests/test_guardian.py tests/test_audit.py tests/test_readiness.py tests/test_cli.py -q
```

For docs-only work:

```powershell
rg -n "Phase 2b is MVP-complete|Missing for full Phase 2b approval|Current Verdict|Phase 2c|Phase 3b|Phase 4" README.md docs
```

6. Add missing validation tests if needed:

- If Gemini omitted non-mutation tests, add them before accepting.
- If Gemini's CLI tests only check exit code, add output assertions.
- If signal strength thresholds are not boundary-tested, add boundary tests.
- If Guardian scheduling lacks date-injection tests, add deterministic date tests.

7. Run full verification:

```powershell
uv run pytest -q
```

## Acceptance Bar

Accept Gemini work only if:

- focused tests pass
- full suite passes or any failure is clearly pre-existing and documented
- changed files match allowed scope
- behavior is backed by tests
- docs do not overstate completion
- advisory systems stay read-only until explicitly promoted

## Rejection Reasons

Reject or request rework if:

- Gemini edits forbidden files
- Gemini uses network/model calls
- Gemini mutates runtime state from Phase 2c reports
- Gemini couples Phase 3 planning to pattern-priority output
- tests are tautological or import-failure red tests
- README claims implementation that tests do not prove

