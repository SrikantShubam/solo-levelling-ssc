# Main Orchestrator Review Plan

## Purpose

This file defines how worker outputs will be accepted or rejected.

## Review Order

1. Review Mimo inventory first.
2. Review Gemini scope report second.
3. Review DeepSeek tests last.

Reason:
- inventory gives file facts
- scope report gives design boundaries
- tests should be judged against both

## Acceptance Criteria

Worker output is acceptable only if:
- it stays inside allowed files
- it cites `Plan.md` or code evidence for scope claims
- it distinguishes local-worktree evidence from canonical-main evidence when they differ
- it does not mutate runtime behavior
- it does not add schema or dependency changes
- it treats missing files as context gaps
- it keeps holdout data excluded from hypothesis creation
- it keeps evaluation read-only
- if it writes tests, those tests collect successfully and fail for a meaningful contract reason

## Rejection Criteria

Reject output immediately if it:
- changes source code outside the workorder
- deletes or rewrites existing tests
- invents a new phase status without plan evidence
- makes Phase 3 runtime consume evaluator or hypothesis output
- proposes using holdout data for hypothesis generation
- changes migrations or schema without explicit approval
- claims a file or test is missing without checking the canonical main path when instructed
- uses top-level import failure as the main red-test strategy
- contains tautological assertions or placeholder checks

## Integration Path

After worker outputs are reviewed:
- copy only accepted docs/tests into the main workspace
- rewrite spec-quality output before integration if needed
- run focused tests
- design the minimal production API if tests are approved
- keep Phase 3b disabled from runtime until evaluation proves value

## Current Setup Caveat

The main workspace has uncommitted changes beyond `HEAD`.

Worker branches were created from `HEAD` commit `61b1490`, so they may not contain:
- recent Phase 3 orchestrator files
- recent Phase 3 evaluation files
- recent hardening changes
- these workorder docs unless copied into the worktree

Workers must report missing files instead of creating replacements.

## Current Worker Locations

- Gemini: `C:\experiments\ssc\gm`
- DeepSeek: `C:\experiments\ssc\ds`
- Mimo: `C:\experiments\ssc\mm`

Workers are expected to commit and push their own branches. If a push fails because credentials or remotes are unavailable, the worker must report the exact error and local commit SHA.
