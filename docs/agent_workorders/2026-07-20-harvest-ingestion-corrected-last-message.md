**ID-namespacing fix and re-verified collision-safety proof:** Applied deterministic IDs in all 64 harvest JSONs: `harvest_<pdf_name>_q<global_question_number>`, writing both `question_id` and `resolved_question_id`. Before fix: `236` collisions with existing DB IDs and `218` duplicate harvest IDs. After fix: `6,180` insertable rows, `0` DB collisions, `0` harvest duplicates. Re-ran the collision gate immediately before import: still `0/0`.

**Masking counts + manual verification:** Used existing `remap_question_assets` / `mask_answer_leaking_crop`. Harvest results: `1,110` masked crop rows, `5,070` harvest crop paths nulled as shared/whole-page unsafe crops, `0` raw unmasked harvest crop rows remaining. Manual sample checked 8 masked crops across 4 sources: all had answer marker/status area removed and visible stem content intact; no masked harvest rows were visual/table-dependent.

**Import collision-safety proof:** Import added `6,180` questions from 64 PDFs. DB went from `2,355` to `8,535` questions. Existing 2,355 question row hashes: `0` changed, `0` missing. Protected tables unchanged: `attempts=410`, `sessions=4`, `sm2_state=204`.

**Modality spot-check outcome:** 20-row spot-check across sections/evidence states was clean. Classifier comparison found `0` harvest modality mismatches. I did find and repair `158` noncanonical harvest section labels using existing section inference: final harvest sections are only `Quant/DI`, `Reasoning`, `English`, `GK/GA`.

**Atlas backfill counts:** `archetypes_created=0`, `questions_assigned=2444`. Harvest non-holdout assigned: `2,444 / 4,637`. Harvest holdout assigned: `0 / 1,543`.

**Full before/after preflight numbers:** Headline: net new web-safe questions added = `749`.

Before `available`: Quant/DI `331`, Reasoning `274`, English `631`, GK/GA `331`.  
After `available`: Quant/DI `655`, Reasoning `384`, English `794`, GK/GA `483`.

Before `raw_available`: Quant/DI `372`, Reasoning `332`, English `671`, GK/GA `389`.  
After `raw_available`: Quant/DI `2775`, Reasoning `828`, English `1664`, GK/GA `1134`.

After `quality_exclusions`: `answer_integrity_failure=13`, `unverified_answer=3936`, `duplicate_content=111`, `passage_dependent=7`, `unmaskable_answer_leak=6`, `invalid_options=12`.

**Test suite results:** `uv run pytest -q` passed: `436 passed, 7 warnings in 75.01s`.

**Residual risk:** Most imported harvest rows are safe but not web-servable yet because they remain `PASS_LLM_ONLY` or duplicate/passage-dependent. The usable gain is therefore `749`, not `6,180`. The 5,070 unsafe shared/whole-page crop references were removed, so those answer-leaking images are not exposed.

