# Updated Worker Assignments

Round two goal:
- rerun the three-worker split with stricter evidence rules
- preserve the useful separation of concerns
- reduce stale-branch drift and low-quality contract tests

## Mimo v2.5 Mini

Task:
- Inventory phase drift and existing pattern-related code/tests.

Output:
- `docs/agent_workorders/mimo-pattern-system-inventory.md`

Allowed:
- Documentation only.
- Commit and push branch `codex/phase3b-mimo-inventory` when done.

Focus:
- `Plan.md`
- `README.md`
- `src/ssc_study/archetypes.py`
- `src/ssc_study/queues.py`
- `src/ssc_study/gates.py`
- `src/ssc_study/readiness.py`
- `tests/test_phase3.py`
- `tests/test_phase3_eval.py`
- existing tests

## Gemini 3.5 Flash High

Task:
- Review and refine the Phase 2c / Phase 3 boundary and pattern-intelligence design.

Output:
- `docs/agent_workorders/gemini-phase-taxonomy-review.md`

Allowed:
- Documentation only.
- Commit and push branch `codex/phase3b-gemini-scope` when done.

Focus:
- phase taxonomy
- exact distinction between Phase 2c and Phase 3 pattern recognition
- overfitting risks
- mock blueprint rules
- promotion gates
- read-only boundaries
- branch-staleness caveats

## DeepSeek v4 Flash

Task:
- Draft failing tests or a precise test specification for pattern intelligence.

Output:
- Preferred: `docs/agent_workorders/deepseek-pattern-test-spec.md`
- Optional: `tests/test_pattern_intelligence_contract.py`

Allowed:
- Test/spec work only.
- No production code.
- Commit and push branch `codex/phase3b-deepseek-tests` when done.

Focus:
- holdout exclusion
- latest-window user attempts
- signal strength
- read-only guarantees
- Phase 3 planner independence
- collection-safe contract-test design
- spec-quality vs merge-quality recommendations

## Main Orchestrator

Task:
- Review worker outputs.
- Reject scope violations.
- Integrate only accepted docs/tests.
- Write production implementation only after specs and tests are approved.
