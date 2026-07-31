Files changed: [scripts/build_atlas_stage1.py](C:/experiments/ssc/scripts/build_atlas_stage1.py), [tests/test_build_atlas_stage1.py](C:/experiments/ssc/tests/test_build_atlas_stage1.py), `data/study.db` updated by the required live script run. No `baseline_web.py`, gates, embeddings, clustering, or taxonomy changes.

Script + exact command: `uv run python scripts/build_atlas_stage1.py --db data/study.db`

Counts:
```text
archetypes_created=48
questions_assigned=1083
assigned_non_holdout=1083
total_non_holdout=1769
coverage_non_holdout=0.612
unassigned_by_section:
  Computer Knowledge=2
  English=310
  GK/GA=234
  Quant/DI=69
  Reasoning=71
```

Tests added: `tests/test_build_atlas_stage1.py` covers idempotent CLI execution, holdout exclusion, and updating stale non-holdout assignments when rule output changes.

Exact verification output:
```text
archetypes_count=48
non_holdout_archetype_non_null=1083
all_archetype_non_null=1083
holdout_archetype_non_null=0
non_holdout_total=1769
```

```text
Phase 3 Orchestrator
  Steps executed: 1
  Stop reason:    max_steps_reached
  Mode:           dry-run

  1. probe (10 q) - Active/Passive Voice
     Unprobed active archetype with enough non-holdout questions.
```

```text
431 passed, 7 warnings in 31.10s
```

Residual risk: the default `uv` cache path hit an access-denied error, so verification used `$env:UV_CACHE_DIR='C:\tmp\uv-cache'`. Pytest warnings are existing dependency/runtime warnings, not Stage 1 failures.

