Files changed: `src/ssc_study/db.py`, `src/ssc_study/models.py`, `src/ssc_study/baseline_web.py`, `src/ssc_study/static/app.js`, `src/ssc_study/static/app.css`, `tests/test_db.py`, `tests/test_baseline_web.py`, `tests/test_phase1_frontend.py`, `scripts/recover_passage_groups.py`, `data/study.db`.

Migration added: migration `16`, adding `passages` and nullable `questions.passage_id`.

Counts: `42` passages created, `100` questions linked, `0` questions still excluded as `passage_dependent`. Current remaining quality exclusions are unrelated: `unmaskable_answer_leak=183`, `answer_integrity_failure=8`, `unverified_answer=155`, `mojibake=7`, `duplicate_content=39`, `invalid_options=3`.

Tests added: passage schema/link test, linked-passage gate test, self-contained cloze gate test, sentence-split false-positive regression test, client payload passage test, frontend passage-render static test.

Exact verification commands and results:
`uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q` -> `138 passed in 5.72s`.
`uv run pytest -q` -> `415 passed, 2 warnings in 59.73s`.
`git diff --check -- ...` -> no whitespace errors; only Git CRLF warnings.

Manual render confirmation: verified two linked passage payloads render through the new `baseline-passage` block. `12356883` shows the full Communication cloze passage above “Select the most appropriate option for blank No. 1”; `8161615507` shows the full Australia bushfire RC passage above “The passage is mainly about:”. Both passage texts match source-PDF extracted text and end cleanly without truncation.

Residual risk for later waves: answer verification, modality reclassification, and whole-page-only source cleanup remain out of scope for Wave 2b/2c.