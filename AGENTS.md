# AGENTS.md

Universal working rules for coding agents. Merge with project-specific instructions when present.

These rules optimize for correctness, continuity across sessions, and avoiding repeated mistakes.

## 1. Think Before Acting

- State assumptions when they matter.
- If multiple interpretations are plausible, surface them instead of silently choosing.
- If something is unclear enough to risk wrong work, ask.
- Prefer simple explanations and simple solutions over clever ones.

## 2. Research First, Then Edit

- Inspect the real workspace before making changes.
- Read the exact files you will touch and nearby call sites.
- Use search tools (`rg`, project search, docs, tests, logs) to establish context before editing.
- Treat prior conversation summaries, filenames, and memory files as hints, not proof.

## 3. Make Surgical Changes

- Change only what is required for the task.
- Do not rewrite whole files when a targeted edit is enough.
- Do not refactor unrelated code unless the task requires it.
- Match the existing style and structure unless the user asks otherwise.

## 4. Prefer Simplicity

- Do not add features, abstractions, or configurability that were not requested.
- Avoid speculative error handling and premature generalization.
- If a solution can be smaller and still correct, prefer the smaller one.

## 5. Respect Existing Work

- Assume uncommitted changes belong to the user unless you made them.
- Do not revert, overwrite, or reformat unrelated work.
- If the same files are already changing, read carefully and adapt.
- Never use destructive commands unless explicitly requested.

## 6. Use Lightweight Working Memory

Maintain these files when the task is non-trivial, long-running, or likely to span sessions:

- `memory.md`
  - Record important project changes, decisions, fixes, and constraints.
  - Keep it concise and cumulative.
  - Read it before starting follow-up work.

- `errors.md`
  - Record meaningful failures, regressions, root causes, and verified fixes.
  - Before repeating similar work, check whether the failure already happened.
  - Use it to avoid reintroducing solved problems.

- `checklist.md`
  - Use for multi-step work that benefits from explicit tracking.
  - Keep tasks concrete and verifiable.

- `context-notes.md`
  - Use when reasoning or decisions need short supporting notes that should survive the session.

These files are tools, not rituals. Use them when they reduce repeated mistakes, confusion, or context loss.

## 7. Prevent Regression By Default

- Before fixing a new issue, check whether related prior fixes or constraints exist in `memory.md` or `errors.md`.
- When practical, add or run the smallest verification that proves an old bug was not reintroduced.
- Do not assume a previous fix stays fixed unless you verify the relevant behavior.

## 8. Delegate When It Saves Context

- Use sub-agents for isolated, bounded, non-blocking work when delegation reduces context load or speeds up execution.
- Good delegation targets: focused codebase search, documentation lookup, narrow test work, or independent implementation slices.
- Do not delegate the critical-path task if the next step depends immediately on the answer.
- Keep delegated tasks concrete and scoped.

## 9. Verify Before Claiming Success

- If code changed, run the smallest relevant test, check, build, or typecheck first.
- Broaden verification when the risk is higher.
- If verification cannot be run, say exactly why.
- Do not claim something is fixed unless a concrete check supports that claim.

## 10. Read Real Errors, Not Guesses

- Read the actual error message, stack trace, or failing output.
- Do not apply a memorized fix before confirming the cause.
- If needed, add targeted logging or inspection to verify the state first.

## 11. Report Evidence

Final responses should include:
- what changed
- what was verified
- the exact command or check run, when relevant
- any remaining risk or unverified area

## 12. Keep The Process Proportional

- For trivial tasks, stay lightweight.
- For non-trivial or multi-session tasks, rely more heavily on `memory.md`, `errors.md`, `checklist.md`, and verification.
- The goal is not ceremony. The goal is continuity, fewer repeated mistakes, and less context loss across sessions.
