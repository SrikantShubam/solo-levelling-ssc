# 2026-07-17 Wave 3a: Pool Recovery, Real-Exam Scoring, Session Hardening

You are working in `C:\experiments\ssc`. Read this file fully before changing
anything. Waves 1, 1b, 2a, 2b, 2c are already landed and verified — read
their workorders (`2026-07-17-wave1*`, `2026-07-17-wave2*` in this
directory) for context on the gate architecture in
`src/ssc_study/baseline_web.py`, masking in `src/ssc_study/corpus_assets.py`,
answer verification in `src/ssc_study/answer_verification.py`, and the
scripts convention in `scripts/`.

## Task 1: Stop excluding image-less text questions from leaking sources

`_has_unmaskable_answer_leak` in `baseline_web.py` currently returns True for
ANY question from an `ANSWER_LEAKING_SOURCES` pdf whose `question_crop_path`
is NULL or unmasked. This conflates "cannot display this image safely" with
"cannot serve this question". Verified fact: 181 of the excluded rows from
`2020_tier2_kdcampus_answer_key` + `2024_tier1_appx_answer_key` are
`text_only` with `visual_required=0` and `table_required=0` — they need no
image at all.

Change the rule to:
- If the question does NOT need a visual asset (`_question_needs_visual_asset`
  is False) and its `question_crop_path` is NULL → NOT an answer leak; the
  question may serve with no image. (`_question_asset_urls` already returns
  no crop URL for a NULL path — verify the page-asset URL is also not leaked:
  for leaking sources, `page_asset_path` points at a full page image which
  DOES contain answer marks, so for leaking-source questions the `page`
  asset URL must never be emitted pre-submit regardless of modality. Check
  `_question_asset_urls` and fix if needed.)
- If `question_crop_path` is set but not masked → still exclude (unchanged).
- If the question DOES need a visual asset and has no safe masked crop →
  still exclude (unchanged).

These recovered rows must still pass every other gate (verified answer,
integrity, mojibake, etc.) — many will still be excluded as
`unverified_answer`; that's correct and expected. Report the exact number
recovered into the web-safe pool.

## Task 2: Answer verification round 2 for the two answer-key sources

`answer_verification.py` already has `extract_letter_answer_key_labels` for
compact answer-key tables. The kdcampus and appx PDFs in
`answer_key_candidates_staging/` are answer-key documents — they carry
their own answer tables. Wave 2b resolved some rows this way (e.g.
`2024_tier1_appx_answer_key_q8` from a table showing `Q8 = C`).

Extend coverage: inspect these two PDFs' actual answer-key page formats
directly (open them with fitz, look at the real text) and extend the
extractor to parse whatever format they actually use (e.g. multi-column
`number letter` grids, `number (letter)` styles). Re-run verification for
all still-unverified rows in these two sources. Rules unchanged from Wave
2b: deterministic evidence only, never model reasoning; leave unresolved
rows excluded. Report before/after `unverified_answer` counts.

## Task 3: Real-exam scoring alongside percent

Add SSC CGL marks-based scoring to the baseline result: Tier-1 pattern
+2.0 per correct, -0.5 per wrong, 0 per skipped. The result payload and
result UI must show, per section and overall: correct/wrong/skipped counts,
percent (existing), and marks (new: earned vs maximum). Do not change any
existing threshold logic (55/65/70% tiers act on percent, unchanged) — marks
are additive information. Add a clearly labeled line in the result UI. Keep
the guidance/tier cards exactly as they are.

## Task 4: Exam token survives server restart

`_EXAM_TOKEN_SECRET = secrets.token_bytes(32)` at module level means a
server restart mid-exam makes every in-flight exam unsubmittable. Persist
the secret: on first use, generate and store it (e.g. a `_app_secrets`
table in the study DB, or a file next to the DB — follow whichever pattern
is most consistent with this repo; the DB table is probably cleanest given
`db.py` migrations). Subsequent processes must load the same secret so
tokens issued before a restart still validate. Do not weaken the HMAC
scheme itself.

## Task 5: Automatic DB backup on submit

Before `submit_baseline_exam` persists a full-mode exam (not smoke), copy
`data/study.db` to `data/backups/study-YYYYMMDD-HHMMSS.db` (create the
directory; use sqlite3's backup API or a safe copy — note WAL mode: a naive
file copy of just the .db file can miss WAL contents, so checkpoint or use
`sqlite3.Connection.backup`). Keep the newest 20 backups, delete older
ones. Must never block or fail the submit: wrap in try/except and log a
warning on failure.

## Task 6: Mojibake repair (7 rows)

7 rows are excluded as `mojibake`. Inspect them; they contain cp1252/UTF-8
double-encoding artifacts (chars like Ã, Â, â). Repair them by re-decoding
where the correct text is unambiguous (standard mojibake reversal:
latin1<->utf8 round trip), verifying the repaired text against the source
PDF page text where possible. Any row you cannot repair with confidence
stays excluded. Report per-row outcome.

## Out of scope

- Post-submit review screen, report-question button (Wave 3b, next)
- Archetype/atlas construction
- KaTeX/math rendering changes
- New corpus acquisition

## Verification required before reporting done

- `uv run pytest tests/test_baseline_web.py tests/test_web.py tests/test_phase1_frontend.py -q` and full `uv run pytest -q`, paste exact results.
- Report: web-safe pool per section before/after; rows recovered by Task 1;
  `unverified_answer` before/after Task 2; mojibake rows repaired/remaining.
- Prove Task 4 works: issue a token, simulate a process restart (fresh
  interpreter/import), verify the token still validates. Describe the test.
- Prove Task 5: run a full-mode submit in a test, confirm a backup file
  appears and pruning works.
- Confirm no leaking-source question emits a `page` asset URL pre-submit.

## Report format

Files changed, scripts/migrations added with exact commands, per-task
counts, tests added, exact verification commands and results, residual risk.
