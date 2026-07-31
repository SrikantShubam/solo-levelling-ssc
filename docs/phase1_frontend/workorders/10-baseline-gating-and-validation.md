# Workorder 10: Baseline Gating and Representative Validation

## Goal

Replace the temporary text-only safety gate with a final readiness gate that allows all valid SSC question types while excluding only genuinely invalid or unrenderable rows.

## Why This Blocks Another 200Q Attempt

The baseline must be representative. It should include text, math, visual/table, and comprehension questions when each row has the context/assets needed to answer it.

## Non-Negotiable

The final baseline gate must not become a text-only shortcut. Visual, table, graph, dice, comprehension, and cloze questions must be eligible when renderable. Excluding whole categories would create a false readiness score.

## Files

- Modify: `src/ssc_study/baseline_web.py`
- Modify: `src/ssc_study/web.py`
- Modify: `tests/test_baseline_web.py`
- Modify: `tests/test_web.py`
- Modify: `tests/test_phase1_frontend.py`
- Optional: add `scripts/audit_baseline_readiness.py` if a CLI audit is useful

## Final Gating Rules

Rows should be excluded only for concrete reasons:

- `duplicate_content`
- `mojibake`
- `invalid_options`
- `blank_content`
- `missing_visual_asset`
- `missing_passage_stimulus`
- `invalid_stimulus_group`

Rows should not be excluded merely because they are visual/table/comprehension rows.

## Implementation Steps

- [x] Replace `unsupported_visual` with asset-specific visual/table exclusions.
- [x] Include renderable visual/table rows in the eligible pool.
- [ ] Include comprehension/cloze rows only when linked to readable passage context.
- [x] Keep full baseline split exactly:
  - Quant/DI: 80
  - Reasoning: 40
  - English: 40
  - GK/GA: 40
- [x] Keep smoke mode available for quick UI testing.
- [x] Ensure `raw_available`, `available`, `missing`, and `quality_exclusions` remain visible in preflight.
- [ ] Add a representative validation script or test helper that starts a full baseline and reports:
  - section split
  - duplicate IDs
  - duplicate fingerprints
  - mojibake count
  - visual/table count
  - comprehension/stimulus count
  - missing asset/stimulus count
  - correct-answer field leakage

## Required Tests

- [x] Renderable visual/table rows are included in the pool.
- [x] Visual/table rows with missing assets are excluded.
- [ ] Comprehension rows with passage stimulus are included.
- [ ] Comprehension rows without passage stimulus are excluded.
- [x] Full baseline preserves 80/40/40/40.
- [x] Start payload has no correct answers.
- [x] Preflight reports quality exclusions.

## Acceptance Criteria

- A full baseline start can include all valid question types.
- It still has no duplicates, mojibake, invalid options, or answer leakage.
- Full test suite passes:
  - `uv run pytest -q`
