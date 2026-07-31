**Snapshot before**

Questions: `8,535` total, `6,180` harvest imported. Harvest statuses: `5,070 PASS_LLM_ONLY`, `1,110 PASS_WITH_EVIDENCE`.

Protected tables before: `attempts=410`, `sessions=4`, `sm2_state=204`.

**Part A results**

Promoted: `156 / 5,070` harvest `PASS_LLM_ONLY` rows to `PASS_WITH_EVIDENCE`.

Corrected stored answers: `0`.

Unresolved remaining: `4,914`.

I added a text-alignment guard after finding repeated local numbering in compilation PDFs: deterministic green label was only accepted when the PDF option text matched or was a normalized prefix/containment match for the DB option text. Mismatched hits were left as `PASS_LLM_ONLY`.

**Part B results**

Previously unimported conflict rows scanned: `5,653`.

Resolved and newly imported: `47`.

Still excluded: `5,606`, reason bucket: `correct_option_unresolved_or_conflict_or_text_mismatch`.

I ran `ssc-study import`; it initially used `INSERT OR REPLACE` across all harvest rows, so I restored the pre-existing `6,180` harvest rows from `data/backups/study-pre-harvest-verification-20260720-013713.db`, then reapplied only the verified Part A updates and kept the `47` validated new rows.

**Collision/protected-table safety proof**

Final questions: `8,582`, exactly `+47`.

Harvest imported total: `6,227`.

Duplicate question IDs: `0`.

Non-harvest collision count: `0`.

Previously imported harvest IDs missing: `0`.

Sample per-PDF question ID sets unchanged: `true`.

Protected tables after: `attempts=410`, `sessions=4`, `sm2_state=204`; unchanged from before.

**Manual verification samples**

1. `2020_tier2_prepp_2022-02-03_english` Q2: extracted `3`; before `3 / without / PASS_LLM_ONLY`; after `3 / without / PASS_WITH_EVIDENCE`.
2. `2020_tier2_prepp_2022-02-03_english` Q3: extracted `3`; before `3 / recently / PASS_LLM_ONLY`; after `3 / recently / PASS_WITH_EVIDENCE`.
3. `2020_tier2_prepp_2022-02-03_english` Q4: extracted `1`; before `1 / property / PASS_LLM_ONLY`; after `1 / property / PASS_WITH_EVIDENCE`.
4. `2020_tier2_prepp_2022-02-03_english` Q5: extracted `2`; before `2 / written / PASS_LLM_ONLY`; after `2 / written / PASS_WITH_EVIDENCE`.
5. `2020_tier2_prepp_2022-02-03_english` Q6: extracted `1`; before `1 / the / PASS_LLM_ONLY`; after `1 / the / PASS_WITH_EVIDENCE`.

**Full before/after preflight numbers**

Headline web-safe count: `2,316 -> 2,432`, delta `+116`.

Available by section:
Before: `English=794`, `GK/GA=483`, `Quant/DI=655`, `Reasoning=384`.
After: `English=906`, `GK/GA=483`, `Quant/DI=655`, `Reasoning=388`.

Raw available:
Before: `English=1664`, `GK/GA=1134`, `Quant/DI=2775`, `Reasoning=828`.
After: `English=1696`, `GK/GA=1134`, `Quant/DI=2775`, `Reasoning=835`.

Quality exclusions:
Before: `unverified_answer=3936`, `unmaskable_answer_leak=6`, `duplicate_content=111`, `invalid_options=12`, `passage_dependent=7`, `answer_integrity_failure=13`.
After: `unverified_answer=3820`, `unmaskable_answer_leak=45`, `duplicate_content=111`, `invalid_options=12`, `passage_dependent=7`, `answer_integrity_failure=13`.

Full and smoke readiness remain `true`.

**Test suite results**

`$env:UV_CACHE_DIR='C:\experiments\ssc\.uv-cache'; uv run pytest -q`

Result: `436 passed, 7 warnings`.

**Residual risk**

The deterministic extractor is reliable when the PDF question number maps cleanly to the row and the option text aligns. Some compilation PDFs repeat local question numbering, so I rejected those mismatched hits instead of forcing them through. Full details are in `reports/harvest_answer_verification_recovery_report.json`; the reusable recovery script is `scripts/recover_harvest_answer_verification.py`.

