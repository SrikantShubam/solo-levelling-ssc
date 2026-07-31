# Workorder 09: Comprehension and Cloze Stimulus Groups

## Goal

Make comprehension/cloze questions valid by attaching the full passage to every child question and preserving grouped/successive question behavior where required.

## Why This Blocks Another 200Q Attempt

SSC English comprehension and cloze passages often have one shared passage followed by 5-6 questions. The current schema stores each row independently, so a later child question may only say `Select the most appropriate option to fill in blank no. X.` Without the passage, that question is invalid.

## Non-Negotiable

Do not remove comprehension or cloze question types from the corpus or permanently exclude them from baseline selection. They are required SSC English item types. The required fix is to attach the readable passage/stimulus and preserve group coherence.

## Current Evidence

Live `data/study.db` has:

- English rows: 671
- comprehension/cloze/passage-like hits: 133

Observed examples:

- Some rows include the full passage and blank markers.
- Nearby successive rows may only contain `blank no. 2`, `blank no. 3`, etc.
- Current baseline selection can sample those rows independently.

## Files

- Modify: `src/ssc_study/db.py`
- Modify: `src/ssc_study/models.py`
- Modify: `src/ssc_study/baseline_web.py`
- Modify: `src/ssc_study/static/app.js`
- Modify: `src/ssc_study/static/app.css`
- Create: `src/ssc_study/stimuli.py`
- Test: `tests/test_stimuli.py`
- Test: `tests/test_baseline_web.py`
- Test: `tests/test_phase1_frontend.py`

## Data Model

Add tables:

- `question_stimuli`
  - `stimulus_id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `stimulus_type TEXT NOT NULL`
  - `source_pdf TEXT`
  - `source_page_start INTEGER`
  - `source_page_end INTEGER`
  - `stimulus_text TEXT`
  - `asset_path TEXT`
  - `created_at TEXT NOT NULL DEFAULT (datetime('now'))`

- `question_stimulus_links`
  - `question_id TEXT NOT NULL REFERENCES questions(question_id)`
  - `stimulus_id INTEGER NOT NULL REFERENCES question_stimuli(stimulus_id)`
  - `position_in_group INTEGER`
  - `group_size INTEGER`
  - unique pair on `(question_id, stimulus_id)`

## Implementation Steps

- [ ] Add migrations for `question_stimuli` and `question_stimulus_links`.
- [ ] Create `src/ssc_study/stimuli.py`.
- [ ] Implement comprehension marker detection:
  - `Comprehension:`
  - `In the following passage`
  - `Read the passage carefully`
  - `blank no.`
  - `Select the most appropriate option to fill in blank no.`
- [ ] Implement deterministic grouping by:
  - same `pdf_name`
  - English section
  - nearby `global_question_number`
  - contiguous blank numbers where available
- [ ] Extract the longest/full passage text from the group.
- [ ] Link every child question to that passage stimulus.
- [ ] Add an audit report for unresolved comprehension/cloze rows.
- [ ] Update `_question_to_client()` to include `stimulus.text`, `position_in_group`, and `group_size`.
- [ ] Render passage text above each child question in the frontend.
- [ ] Update baseline gating so unresolved comprehension children are excluded with `missing_passage_stimulus`.
- [ ] Update baseline selection so grouped comprehension questions remain successive when selected as a block.

## Required Tests

- [ ] A cloze group with blank no. 1-5 links to one shared passage stimulus.
- [ ] A child row without its own passage receives the shared passage in the start payload.
- [ ] A comprehension child with no resolvable passage is excluded from final baseline eligibility.
- [ ] The browser payload includes passage text but no correct answer fields.
- [ ] Frontend renders passage text before the question prompt.
- [ ] Grouped baseline selection preserves internal order.

## Acceptance Criteria

- No comprehension/cloze question can appear without readable passage context.
- Grouped passage children remain coherent and successive when selected as a group.
- Renderable comprehension/cloze groups are included in baseline eligibility.
- Full relevant tests pass:
  - `uv run pytest tests/test_stimuli.py tests/test_baseline_web.py tests/test_phase1_frontend.py -q`
  - `uv run pytest -q`
