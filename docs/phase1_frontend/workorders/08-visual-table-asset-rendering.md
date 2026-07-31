# Workorder 08: Visual and Table Asset Rendering

## Goal

Render visual, table, graph, dice, and visual-option questions in the web baseline using existing crop/page assets.

## Why This Blocks Another 200Q Attempt

SSC includes visual/table questions. The current temporary safety gate excludes these rows from the web baseline because the browser cannot render their assets yet. That prevents bad scoring, but it also makes the baseline less representative.

## Non-Negotiable

Do not remove visual/table/graph/dice question types from the corpus or permanently exclude them from baseline selection. They are required SSC item types. This workorder exists to make them renderable so they can re-enter the baseline pool.

## Current Evidence

Live `data/study.db` has `277` non-holdout visual/table-like rows:

- Reasoning: 90
- Quant/DI: 36
- English: 99
- GK/GA: 50
- Computer Knowledge: 2

Modality counts:

- `table_di`: 104
- `visual_options`: 74
- `graph_chart`: 56
- `dice`: 38
- `visual_stimulus`: 5

Most sampled rows have `question_crop_path` and `page_asset_path` populated, but those paths are local filesystem paths and must not be exposed directly to the browser.

## Files

- Modify: `src/ssc_study/web.py`
- Modify: `src/ssc_study/baseline_web.py`
- Modify: `src/ssc_study/static/app.js`
- Modify: `src/ssc_study/static/app.css`
- Test: `tests/test_web.py`
- Test: `tests/test_baseline_web.py`
- Test: `tests/test_phase1_frontend.py`

## Implementation Steps

- [x] Add a safe asset resolver that accepts `question_id` and `kind`.
- [x] `kind` should support at least:
  - `crop`
  - `page`
- [x] Resolve asset paths only from DB fields:
  - `question_crop_path`
  - `page_asset_path`
- [x] Reject missing paths, non-image extensions, and unknown question IDs.
- [x] Add FastAPI route:
  - `GET /api/question-assets/{question_id}/{kind}`
- [x] Return image bytes with a safe media type.
- [x] Update `_question_to_client()` to include:
  - `question_modality`
  - `visual_required`
  - `table_required`
  - `asset_urls.crop`
  - `asset_urls.page`
- [x] Update the frontend to render an asset block above the question text.
- [x] Add image load error UI: visible message, not silent failure.
- [x] Add CSS for readable asset sizing:
  - max width 100%
  - preserve aspect ratio
  - clear border/background
  - mobile-safe layout

## Required Tests

- [x] Asset endpoint returns 404 for unknown question.
- [x] Asset endpoint returns 404 when the DB path is missing.
- [x] Asset endpoint rejects unsafe/traversal-like existing image paths outside the expected corpus asset roots.
- [x] Asset endpoint serves a valid test PNG for a seeded visual question.
- [x] Start response includes asset URLs for renderable visual/table rows.
- [x] Start response does not include raw filesystem paths.
- [x] Frontend source includes visual asset rendering and image error fallback.

## Acceptance Criteria

- Renderable visual/table questions appear in the browser with images.
- Renderable visual/table rows are included in baseline eligibility.
- Raw local paths are never sent to the client.
- Missing/unreadable asset rows are excluded and reported, not silently rendered broken.
- Full relevant tests pass:
  - `uv run pytest tests/test_web.py tests/test_baseline_web.py tests/test_phase1_frontend.py -q`
  - `uv run pytest -q`
