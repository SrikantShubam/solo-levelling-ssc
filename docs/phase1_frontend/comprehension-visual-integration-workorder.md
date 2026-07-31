# Phase 1 Baseline: Comprehension, Visual, and Table Integration Workorder

## Context

Manual baseline testing showed the Phase 1 web baseline is not yet valid for final use:

- visual/table questions were present in the corpus but did not render in the browser
- comprehension/cloze questions can depend on a shared passage across 5-6 successive questions
- the current baseline selection treats questions as independent rows

The temporary web-safe baseline filter may keep a score from being corrupted, but it is not the final product behavior. SSC exams include visual, table, graph, cloze, and reading-comprehension items. These must be represented and rendered correctly.

## Non-Negotiable Measurement Constraint

Do not permanently remove or globally exclude visual, table, graph, dice, comprehension, or cloze questions from the baseline. These are real SSC question types. Excluding them would make the baseline easier than the exam and create a false readiness measurement.

The correct behavior is:

- include these question types when their required passage/stimulus/asset is available and readable
- exclude only specific broken rows with explicit reasons, such as `missing_visual_asset` or `missing_passage_stimulus`
- report exclusions in preflight so the operator knows what coverage is still missing

## Current Evidence

Live `data/study.db` has non-holdout visual/table candidates:

- total: 277
- by section: Reasoning 90, Quant/DI 36, English 99, GK/GA 50, Computer Knowledge 2
- by modality: table_di 104, visual_options 74, graph_chart 56, dice 38, visual_stimulus 5

English comprehension-like rows are also present:

- English rows: 671
- comprehension/cloze/passsage-like hits: 133
- examples include Tier-1 cloze rows where some questions carry the full passage and nearby blank-number rows only say `Select the most appropriate option to fill in blank no. X.`

## Problem

The current schema stores each question independently in `questions`. It has no durable concept of:

- a shared passage/stimulus
- a parent-child group for 5-6 successive comprehension questions
- a group-level ordering contract
- a web-renderable asset URL for visual/table questions

This creates two invalid behaviors:

1. A comprehension child can appear without the passage needed to answer it.
2. A baseline can sample one child from a multi-question passage block without keeping the passage context and intended succession.

## Desired Behavior

### Comprehension and Cloze

- Every comprehension/cloze question shown in the web app must include the full readable passage it belongs to.
- If a passage has 5-6 successive questions, the baseline selector should treat that as a block when using that source, preserving internal order.
- The frontend should render the shared passage once, clearly above the child question prompt.
- If a child question does not have a resolved passage, it must be excluded from final baseline eligibility and reported as a quality exclusion.

### Visual and Table Questions

- Visual/table/graph/dice questions must be eligible only when their referenced asset exists and can be served safely by the local web app.
- The frontend should render the image/table asset with readable sizing and a failed-image error state.
- Once renderable, these rows must re-enter baseline eligibility instead of being globally excluded.

### Flagged Questions

- `marked_for_review` from the browser must be persisted, because manual baseline feedback depends on recovering uncomfortable/flagged questions after submit.

## Implementation Plan

### 1. Add Stimulus Data Model

Add a migration for a shared stimulus model:

- `question_stimuli`
  - `stimulus_id`
  - `stimulus_type`: `comprehension`, `cloze`, `visual`, `table`, `graph`, `other`
  - `source_pdf`
  - `source_page_start`
  - `source_page_end`
  - `stimulus_text`
  - `asset_path`
  - `created_at`

- `question_stimulus_links`
  - `question_id`
  - `stimulus_id`
  - `position_in_group`
  - `group_size`

Keep this separate from `questions` so existing question rows and attempts remain stable.

### 2. Backfill Comprehension Groups

Create a deterministic backfill script/module that:

- scans English questions by `pdf_name`, `source_page`, and `global_question_number`
- detects cloze/comprehension markers:
  - `Comprehension:`
  - `In the following passage`
  - `Read the passage carefully`
  - `blank no.`
  - `Select the most appropriate option to fill in blank no.`
- groups contiguous blank-number questions from the same PDF
- extracts the longest/full passage from the group
- links every child row to that passage
- writes an audit report listing unresolved groups

Acceptance rule: no comprehension/cloze child can enter final web baseline eligibility unless it has a linked readable `stimulus_text`.

### 3. Backfill Visual/Table Stimuli

Create a deterministic asset validation step that:

- reads `question_crop_path` and `page_asset_path`
- resolves absolute and repo-relative paths safely
- verifies the file exists and has an allowed image extension
- links the question to a `question_stimuli` row with `asset_path`
- reports missing/unreadable assets

Acceptance rule: visual/table rows can enter baseline eligibility only when their stimulus asset is linkable and renderable.

### 4. Serve Assets Safely

Add a FastAPI route:

- `GET /api/question-assets/{question_id}/{kind}`

Rules:

- serve only paths already recorded in DB stimulus rows
- resolve paths and reject traversal
- return 404 for missing assets
- set a safe image media type

Do not expose arbitrary filesystem paths to the frontend.

### 5. Extend Baseline Payload

Update `_question_to_client()` to include:

- `question_modality`
- `stimulus`: null or object
  - `type`
  - `text`
  - `asset_url`
  - `position_in_group`
  - `group_size`

Do not include correct answers.

### 6. Render Stimuli in UI

Update the exam UI:

- render passage text above the question for comprehension/cloze
- render asset image above the question for visual/table/graph/dice
- keep the question prompt and options below the stimulus
- show image load failure as an explicit error instead of silently hiding it
- keep `Clear Response` and `Mark for Review` behavior unchanged

### 7. Update Baseline Selection

Replace the current temporary `unsupported_visual` exclusion with:

- `missing_visual_asset`
- `missing_passage_stimulus`
- `invalid_stimulus_group`

Selection should:

- preserve the 80/40/40/40 section split
- keep grouped comprehension children successive when selected as a group
- avoid duplicate content
- avoid mojibake
- avoid answer leakage

### 8. Persist Marked-for-Review

Add a persistence path for flagged baseline questions:

- either add `marked_for_review` to `attempts`
- or add `attempt_flags(attempt_id, flag_type, created_at)`

Acceptance rule: after baseline submit, flagged/uncomfortable questions can be queried by session.

## Tests

Add focused tests for:

- comprehension child with no passage is excluded from final baseline
- cloze group backfill links blank no. 1-5 to the same passage
- start response includes passage stimulus but no correct answers
- visual/table row with missing asset is excluded
- visual/table row with valid asset is included and receives an asset URL
- asset route rejects unknown question ids and traversal attempts
- frontend renders passage text
- frontend renders asset image and error fallback
- grouped comprehension selection preserves order
- marked-for-review persists through submit

## Manual QA

Before declaring the baseline ready:

1. Start a full 200-question baseline.
2. Verify exact 80/40/40/40 section split.
3. Confirm at least one comprehension/cloze block renders with the full passage.
4. Confirm visual/table/graph/dice questions render readable assets.
5. Clear a selected answer and submit it as skipped.
6. Mark uncomfortable questions and verify they are recoverable after submit.
7. Confirm no correct-answer fields are present in the start payload or DOM before submit.

## Status

Not implemented yet. This is the next required work before a full manual baseline attempt can be treated as readiness evidence.
