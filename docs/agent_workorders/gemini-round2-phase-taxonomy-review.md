# Gemini Round 2 Phase Taxonomy and Boundary Review

This review refines the phase taxonomy and boundaries for the SSC CGL Scoring Machine, correcting previous claims regarding reasoning archetype support, based on the canonical main repository state.

---

## 1. Confirmed

These facts are fully supported by `Plan.md`, the codebase (`gates.py`, `readiness.py`, `phase3.py`, `phase3_eval.py`, `holdout.py`), and spec documentation:

* **Strict Phase 3 Determinism**: The active runtime loops for diagnostic planning, routing, and SM-2 scheduling are entirely deterministic and rule-based. There are no active AI models or classification models processing live user attempts or mutating queues.
* **Read-Only Evaluator Contract**: The evaluator in `phase3_eval.py` runs purely in read-only mode for audit/reporting. It does not write to database tables or alter scheduling queues.
* **Holdout Protection and Mock Cap**: The 25% sealed holdout is fully protected by `holdout.py` and verified by tests. Sealed-holdout mock creation is restricted to a maximum of 2 sessions per calendar month via checks on the `holdout_usage_log` table.
* **Current-Affairs Expiration**: Expired current affairs fact cards are successfully filtered out of the active queues and readiness calculations, retaining historical data only for audits.

---

## 2. Partially Confirmed

These claims from round one are directionally correct but required more precise wording to align with the codebase:

* **Tier-Specific Reasoning Support**:
  * *Previous Claim*: Shared Reasoning archetypes cannot dynamically support different difficulty levels or distinct tier accuracy tracking.
  * *Refinement*: The codebase **does** support tier-specific tracking. In `gates.py`, the helper `get_archetype_accuracy_by_tier()` tracks user attempts separately for `tier1` and `tier2`. In `readiness.py`, `_check_reasoning_tier2()` uses `get_tier2_readiness()` to ensure that all active Reasoning archetypes meet Tier-2 readiness (requiring $\ge 5$ attempts at Tier-2 difficulty at $\ge 80\%$ accuracy).
  * *Limitation*: The predictive route classifier in `phase3_eval.py` (`_predicted_route()`) is simplistic and evaluates only `t1_accuracy` to determine whether an archetype routes to `sm2` or `boss_fight`. It does not evaluate tier-specific difficulty constraints at the route prediction classification level.
* **Phase Drift vs. Phase Progression**:
  * *Previous Claim*: Model-based pattern discovery and pattern registries represent a drift/discrepancy from `Plan.md`.
  * *Refinement*: While no model-based discovery code or pattern registry exists in the current codebase, this is a matter of phase progression (the project is currently at the Phase 2b/3 transition), not design drift. `Plan.md` explicitly reserves paid model integration for later extraction, clustering, and rescue phases.

---

## 3. Unsupported Or Branch-Stale

These claims are unsupported or contradicted by code and plans:

* **Absence of Shared Reasoning Support**: The assertion that the system is entirely unable to track separate tier readiness or that reasoning archetypes cannot have tier-specific accuracy is false. The code in `gates.py` and `readiness.py` explicitly does this.
* **Active Model Integration**: Any claim that runtime scheduling, queues, or mock generation is currently influenced or modified by model-generated pattern reports is incorrect. The pattern intelligence design specs enforce that all pattern reports start strictly read-only and advisory.

---

## 4. Final Taxonomy

The clear boundaries separating the two analytical layers:

| Layer | Phase | Primary Inputs | Primary Outputs | Key Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Exam-Paper Pattern Intelligence** | **Phase 2c** | Non-holdout question corpus (sections, tiers, years, archetype frequencies). | Advisory mock blueprints (expected section/tier/archetype distributions). | Must ignore user attempts and exclude holdout questions. |
| **User-Error Pattern Intelligence** | **Phase 3** | User attempt history (accuracy, timing, student labels, concept tags). | User failure diagnostics (repeated wrong archetypes, concept gaps, decay). | Must ignore attempts on holdout questions and prefer the latest attempt window. |

---

## 5. Overfitting And Independence Risks

* **Holdout Leakage**: If pattern discovery models read the 25% sealed holdout questions or attempts on them, mock blueprints will overfit to the test set, inflating user readiness scores.
* **Self-Confirming Loops**: Mutating queues based on unvalidated model hypotheses creates a feedback loop where the user is drilled on what the model *assumes* they are weak at, artificially confirming the model's predictions.
* **Sparse-Evidence Inflation**: Drawing strong diagnostic conclusions from a tiny window of attempts (e.g. < 5 attempts) leads to scheduling adjustments based on statistical noise.

---

## 6. Promotion Gates

Before a discovered pattern can be promoted from "advisory" to "active" (mutating scheduling, mocks, or archetypes), it must pass:
1. **Minimum Support Gate**: The pattern must have a minimum count of unique non-holdout questions (e.g., 5+) and user attempts (e.g., 10+).
2. **Holdout Validation Gate**: The pattern's predictions must be verified against user performance on independent, sealed holdout mocks before promotion.
3. **Signal Strength Gate**: The pattern signal must reach a `stable` rating.
4. **Deterministic Validation / Gatekeeper Review**: A rule-based controller must verify that the pattern does not violate schema integrity, duplicate existing archetypes, or cause holdout leakage.
