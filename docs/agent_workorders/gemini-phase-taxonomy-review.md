# Phase Taxonomy and Pattern Intelligence Review

This document reviews the phase taxonomy and boundaries for integrating exam-paper and user-error pattern intelligence into the SSC CGL Scoring Machine, as directed by the [gemini-3.5-flash-high-workorder.md](file:///C:/experiments/ssc/docs/agent_workorders/gemini-3.5-flash-high-workorder.md).

---

## 1. Phase Placement of Pattern Intelligence

### Phase 2c: Exam-Paper Pattern Intelligence
* **Placement Verdict**: **Correct and logical.**
* **Rationale**: Phase 2 is designated for the corpus, holdout, and atlas primitives. Exam-paper pattern intelligence analyzes the structural distributions (sections, tiers, years, archetype frequency) of the question corpus to produce advisory mock blueprints. Because this analysis is completely independent of user performance and attempts, it belongs alongside the corpus ingestion and atlas normalization phases (as Phase 2c) rather than diagnostic execution.

### Phase 3: User-Error Pattern Intelligence
* **Placement Verdict**: **Correct and logical.**
* **Rationale**: Phase 3 is the diagnostic grinding phase. User-error pattern intelligence analyzes attempts, wrong answers, concept gaps, and timing failures to diagnose why and where a user is failing. Since it consumes live user performance metrics to determine mastery and remediation routes, it is intrinsically tied to Phase 3 diagnostics.

---

## 2. Exact Phase Drift Analysis

There is noticeable drift between the core system specifications (`Plan.md`), the `README.md`, developer documentation, and the actual code:

| Area / Concept | `Plan.md` Target | `README.md` / Spec Docs | Current Code Status | Drift Details |
| :--- | :--- | :--- | :--- | :--- |
| **Phase Definition** | Only defines Phases 1, 2, 3, and 4. No subphases. | Introduces Phase 2b (primitives), Phase 2c (exam patterns), and Phase 3b (pattern discovery). | Primitives are in `src/ssc_study/`. Diagnostic loop and eval are in `phase3.py` & `phase3_eval.py`. | Subphases are introduced to separate runtime primitives from analytical/model-driven logic. |
| **Model-Based Discovery** | Focuses on rule-based classifiers and Qwen-based manual arbitration. | Mentions model-based paper pattern discovery and registries. | Fully deterministic; no model layer or pattern registry exists in the code. | The codebase relies entirely on deterministic regular expressions and accuracy ratios. |
| **Reasoning Tier Difficulty** | A shared pool with tier-specific difficulty constraints. | Shared Reasoning tier readiness requires separate accuracy tracking. | `ArchetypeDef` has static difficulty and tier fields. `t1_accuracy` is hardcoded in routing. | Shared archetypes cannot dynamically support different difficulty levels or distinct tier accuracy tracking. |
| **Holdout Mocks** | Reserve 25% sealed holdout; max 2 full mocks/month. | Specifies monthly cap and holdout-backed session types. | `holdout.py` implements the SQLite log and monthly cap checks. | Aligned, but the policy is only recently fully integrated. |

### Evidence from `Plan.md` and Current Code
1. **Model Absence**: `Plan.md` lines 122–125 list "local Qwen coach, DeepSeek-R1 rescue, Gemini extraction support". No AI pattern discovery is written in the codebase.
2. **Reasoning Difficulty Staticity**: `Plan.md` line 167 specifies: *"For shared Reasoning, Tier-2 accuracy must be Tier-2 difficulty accuracy."* In `src/ssc_study/archetypes.py` line 27:
   ```python
   class ArchetypeDef:
       name: str
       section: str
       tier: str  # 'tier1' | 'tier2' | 'both'
       difficulty: str  # 'easy' | 'medium' | 'hard'
   ```
   This schema forces each archetype to have a single static difficulty, and `src/ssc_study/phase3_eval.py` line 116 only checks `row["t1_accuracy"]` to predict routing.

---

## 3. Minimal Read-Only Design Critique

1. **Static Keyword Archetypes**: Pre-defining archetypes via regex in `archetypes.py` is brittle and fails when question phrasing changes. Model-assisted pattern mining would improve flexibility, but it must be kept advisory.
2. **Hardcoded Eval Window**: `phase3_eval.py` utilizes a fixed window of the latest 10 attempts. It does not account for forgetting curves or decay over time, making predictions stale if the user hasn't attempted an archetype recently.
3. **Absence of Shared Difficulty Logic**: Tracking tier-specific accuracy is planned but missing in the evaluator and routing code. Currently, `t1_accuracy` dominates routing.

---

## 4. Risks of Overfitting and Self-Confirming Evaluation

* **Holdout Leakage**: If the pattern discovery engine reads holdout questions, it will design mock blueprints that mimic the holdout set, inflating mock scores.
* **Feedback Loops**: Feeding model-discovered patterns directly into scheduler queues without validation causes self-confirming bias. The model creates a hypothesis, changes the queues to expose the user to more of those questions, and "confirms" its hypothesis on the biased data.
* **Sparse Evidence Bias**: Evaluating signal strength as `stable` with fewer than 10 attempts runs the risk of classification on statistical noise (careless errors or lucky guesses).

---

## 5. Forbidden Integration Points

To preserve execution safety, the pattern intelligence layer must never:
1. **Mutate Core Tables**: Direct writes to `questions`, `archetypes`, `attempts`, `sessions`, `sm2_state`, or `fact_cards` by model-assisted classifiers are strictly banned.
2. **Schedule Core Queues**: The scheduling logic in `scheduler.py` and `queues.py` must remain independent of raw pattern report outputs.
3. **Access Holdout Data**: Any question marked `is_holdout = 1` or attempts linked to them must be fully filtered out of pattern mining inputs.

---

## 6. Recommended Promotion Gates

Before a discovered pattern is promoted to affect scheduling, mocks, or archetypes, it must pass:
1. **Minimum Support Gate**: At least 5 unique non-holdout questions and 10 attempts showing the pattern.
2. **Holdout Validation Gate**: Cross-validate the model-hypothesized weakness against user performance on sealed holdout mocks to verify predictive accuracy.
3. **Signal Strength Gate**: The pattern signal must be flagged as `stable` (10+ attempts in the active window).
4. **Deterministic Collision Gate**: Ensure the pattern does not overlap or conflict with existing core database archetypes.
