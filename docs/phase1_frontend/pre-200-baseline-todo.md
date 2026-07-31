# Pre-200-Question Baseline Todo

Do not treat another full 200-question run as final baseline evidence until every required item below is checked.

## Non-Negotiable Baseline Validity Rule

- [x] Visual, table, graph, and dice questions are not globally excluded by the web baseline gate.
- [ ] Comprehension and cloze questions are not globally excluded once passage stimulus grouping exists.
- [x] Visual/table item types are included whenever their image assets are renderable.
- [ ] Comprehension/cloze item types are included whenever their passages are renderable.
- [x] Only individually broken visual/table rows are excluded, and each exclusion has a reported reason.

## User-Visible Smoke Check

These are quick checks the user can do after implementation:

- [ ] Start a smoke exam.
- [ ] Select an answer, then use `Clear Response`, and confirm the nav dot returns to unanswered.
- [ ] Mark at least one question for review.
- [ ] Submit the smoke exam.
- [ ] Confirm the marked question is recoverable after submit.
- [ ] Confirm skipped/unattempted questions are counted as skipped.

## Required Engineering Completion Before Full Attempt

- [x] Flagged/marked baseline questions persist after submit.
- [x] Visual/table/graph/dice assets render in the web exam when the DB points to an existing image file.
- [x] Missing visual assets are reported as quality exclusions.
- [x] Visual/table rows with valid assets re-enter the baseline pool.
- [ ] Restore or regenerate the missing local visual/table asset files for `data/study.db`.
- [ ] Comprehension/cloze rows have linked readable passage text.
- [ ] Comprehension/cloze passage text renders with every child question that needs it.
- [ ] Grouped comprehension/cloze children preserve internal order when selected as a block.
- [x] Baseline start payload contains no correct-answer fields.
- [x] Full baseline preflight reports quality exclusions clearly.

## Final Automated Validation Before User Attempts 200Q

Run and paste/save the output:

```powershell
uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q
uv run pytest -q
```

Run a representative baseline-start audit and verify it reports:

- [x] `question_count = 200`
- [x] Quant/DI = 80
- [x] Reasoning = 40
- [x] English = 40
- [x] GK/GA = 40
- [x] duplicate IDs = 0
- [x] duplicate fingerprints = 0
- [x] mojibake rows = 0
- [x] invalid option rows = 0
- [ ] visual/table rows included and renderable
- [ ] comprehension/cloze rows included only with passage stimulus
- [x] correct-answer fields = 0

Latest validation note: `data/study.db` currently has 277 non-holdout visual/table-like rows that need assets, but 0 have valid local image files available. The code can include renderable visual/table rows, but this DB cannot produce them until the asset files exist.

## User Should Attempt Full 200Q Only When

- [ ] The engineering checklist is complete.
- [ ] The automated validation is green.
- [ ] At least one visual/table question has been manually seen rendering correctly.
- [ ] At least one comprehension/cloze group has been manually seen with the passage visible.
- [ ] Marked-for-review recovery has been manually checked.

If any item above is unchecked, do a smoke/manual QA pass only. Do not spend another two-hour baseline attempt yet.
