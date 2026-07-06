# Grok Critic — SSC Project Scope Review

Date: 2026-07-06

## Executive Summary

Phase 1 web MVP is **complete for its slice**: local baseline exam (smoke + full),
API contract, exam cockpit UI, persistence, and SM-2 updates on web submit (as of
commit `1e4f35a`). Live verification: smoke test (3/5) and full baseline submit
(200 attempts, mostly skipped) both persisted correctly.

The **whole project** is not a finished study operating system. The backend engine
is substantially ahead of the product surface. The largest gap is the absence of a
unified daily grind that connects baseline → Phase 3 → queues → readiness.

---

## Phase 1 Web MVP — Remaining Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| Daily study has no web UI | High | Web is baseline-only. SM-2 review, boss fights, English/GK blocks are CLI-only. |
| Guardian doesn't execute | High | `guardian plan` prints a schedule; it does not launch sessions or enforce 180 min. |
| Foundation gate workflow | High | Plan expects concept tagging, per-area 70% unlocks, 42-day cap — not implemented as software. |
| Readiness is CLI-only | Medium | No web dashboard for the multi-check readiness model in `Plan.md`. |
| Sealed holdout mocks | Medium | Holdout exists in DB; web/CLI mock cadence (max 2/month) is not a guided flow. |
| Docs drift | Low | `docs/phase1_frontend/README.md` still says frontend isn't built; main `README.md` omits `ssc-study web`. |
| No browser E2E tests | Low | API/route tests are strong; no Playwright smoke for real UX. |

### Phase 1 Non-Goals (Correctly Deferred)

- Accounts / login
- Hosted deployment
- React / build pipeline
- Full analytics dashboard
- Sealed-holdout usage in web MVP

---

## Whole Project — Structural Gaps vs `Plan.md`

### 1. Product split: engine vs product

Backend is rich: queues, Phase 3 orchestrator, pattern intelligence, Guardian
planner v1, embeddings, archetypes, fact cards. The **product** is still mostly
CLI. Phase 1 web is one vertical slice (baseline exam), not daily study.

### 2. Phase 3 doesn't close the loop

`ssc-study phase3` and `phase3-eval` exist and are read-only / advisory. Web
baseline results do not automatically feed unlock, remediation, or boss-fight
routing. The diagnostic engine and the baseline UI are disconnected.

### 3. Atlas incomplete

Plan targets ~160–240 archetypes, tier-specific Reasoning difficulty
(`tier_difficulty`), and foundation concept tagging. Corpus and keyword
classifiers exist; full atlas normalization and concept-level foundation gate
are not done.

### 4. Model layer missing

Plan references local Qwen coach, batched arbitration, DeepSeek rescue, and
model-assisted classification. None of this is in the runtime path today.

### 5. External calibration

`external_mocks` table exists. Recording real mocks and calibrating internal
scores against them is not a first-class user workflow.

### 6. Notification audit

Audit pause/recalibrate behavior is implemented for when SSC CGL 2027 notification
drops. It is infrastructure, not something the user operates day-to-day.

### 7. Final readiness gate

`Plan.md` defines a multi-condition final readiness check: foundation pulse
areas 75%+, top archetype floors, module floors (Math/Reasoning/English/GA/CK),
last 5 mocks above calibrated floor, external/sealed-holdout mocks, 2-option
elimination drills, 7-day trend stability. This is specified, not surfaced as one
actionable "am I exam-ready?" experience.

### 8. Data hygiene and queue enforcement

Partially implemented, not fully enforced end-to-end:

- Expired current-affairs card exclusion from active queues
- CBIC priority recall slots in final 8 weeks
- Skip-list enforcement (temporary/permanent, probe re-entry)
- Holdout policy software enforcement (25% sealed, max 2 mocks/month)

---

## What Works Today (Evidence)

| Capability | Status | Evidence |
|------------|--------|----------|
| Corpus + import | Done | 2355 questions, 19 PDFs |
| CLI quiz + SM-2 | Done | `ssc-study quiz`, regression tests |
| Phase 1 web baseline | Done | Smoke + full live-tested, DB persisted |
| Web SM-2 on submit | Done | `_persist_attempt_with_sm2`, commit `1e4f35a` |
| Phase 3 orchestrator | Done | `ssc-study phase3` |
| Phase 3 evaluation | Done | `ssc-study phase3-eval` (read-only) |
| Pattern intelligence | Advisory | `ssc-study patterns exam/priority` |
| Guardian planner | v1 advisory | `ssc-study guardian plan` |
| Readiness dashboard | CLI | `ssc-study readiness` |

---

## Critic Verdict

**Phase 1 web MVP:** Shipped and verified for local baseline exams.

**Whole project:** Strong study **engine**, weak study **product**. You can take a
baseline in the browser and grind via CLI, but the system does not yet feel like
one coherent daily operating system.

---

## Recommended Next Priorities

1. **Web daily study shell** — SM-2 / boss-fight / English / GK sessions in the
   browser, reusing existing queue loaders.
2. **Baseline → Phase 3 hook** — after full `foundation_pulse`, surface weak
   sections and suggest or auto-queue `phase3` probes.
3. **Guardian execution** — turn plan blocks into launchable quiz sessions, not
   just printed recommendations.
4. **Docs pass** — update `README.md` and `docs/phase1_frontend/README.md` to
   reflect current reality.
5. **Foundation gate software** — concept tagging, per-area unlock thresholds,
   42-day cap tracking (even if manual tagging v1).

---

## Risks If Scope Is Not Addressed

- Users complete baseline in web, then fall back to CLI for everything else —
  fragmented UX, high abandonment risk.
- Phase 3 / Guardian / patterns remain "developer commands" rather than study
  workflows.
- Readiness and final gate criteria in `Plan.md` stay theoretical; user cannot
  see progress toward SSC CGL 2027 target in one place.
- Holdout and mock cadence rules may be violated accidentally without guided
  enforcement.

---

## Files Referenced

- `Plan.md` — master operating system and software build order
- `docs/phase1_frontend/spec.md` — Phase 1 web MVP contract
- `src/ssc_study/baseline_web.py` — backend service
- `src/ssc_study/web.py` — FastAPI routes + UI serving
- `memory.md` — session history and verification notes