# 2026-07-20 LLM-Solve Verification Smoke Test (Measurement Only, No DB Writes)

You are working in `C:\experiments\ssc`. This is a measurement/proposal task
only — **do not write to `data/study.db`**, do not import/promote anything
yet. The goal is real numbers to decide a follow-up with, same pattern as
the earlier harvest-extraction cost smoke test this session.

## Background

3,113 harvest questions are currently excluded as `unverified_answer`
(section breakdown: Quant/DI 2,054, Reasoning 369, English 690 — verified
via `_web_baseline_rejection_reason` in `src/ssc_study/baseline_web.py`).
GK/GA (574 more unverified rows) is explicitly OUT OF SCOPE for this —
factual-recall questions need grounding an LLM solve can't reliably provide
without search, do not include GK/GA in this smoke test or any follow-up
from it.

The idea: instead of matching against PDF page-position color data (the
approach used earlier, which struggles on compilation PDFs with repeated
local question numbering — see
`docs/agent_workorders/2026-07-20-harvest-answer-verification-recovery-workorder.md`
for that history), have an LLM **independently solve** each question from
its text + options alone (no PDF page context needed), then compare its
answer to the already-extracted `correct_option_label`. Agreement between
two independent methods (original vision-extraction of the visible
checkmark + independent LLM solve) is real evidence; disagreement means
stay excluded — never let the LLM's answer silently override anything.

## Task

1. Randomly sample 30 questions from the `unverified_answer` pool, 10 each
   from Quant/DI, Reasoning, and English (use the same
   `_web_baseline_rejection_reason` check to build this pool — do not
   re-derive it differently).
2. For each sampled question, call OpenRouter (key `SSC_OPENROUTER` in
   `.env`, already wired as first-priority — reuse existing key-lookup
   pattern from `src/ssc_corpus/cli.py`) with the question text and 4
   options, asking the model to solve it and state its final answer label
   clearly (parseable). Run this against **three OpenRouter models**:
   `deepseek/deepseek-r1-0528`, `qwen/qwen3-235b-a22b-thinking-2507`, and
   `tencent/hy3:free` (confirmed genuinely free on OpenRouter — $0
   input/output pricing).
3. **Also run a fourth arm via `gpt-5.4-mini`**, accessed through the
   Codex CLI subscription (not OpenRouter/metered API — the user has this
   covered by an existing subscription, so it is not billed per-token the
   way the other three are). Invoke it with
   `codex exec -m gpt-5.4-mini "<prompt>"` — for efficiency, batch all 30
   questions into a single `codex exec` call (ask it to solve all 30 and
   return a structured, parseable list of answers) rather than 30
   separate CLI invocations. Parse its output into the same per-question
   answer format used for the other three models.
4. For the three OpenRouter models, report: how many of the 30 solved
   answers **agree** with the currently-stored `correct_option_label`,
   broken down by section, and the **real measured cost** (query
   `SSC_OPENROUTER`'s `/api/v1/key` usage before and after, same technique
   as the earlier extraction cost measurement — report the actual dollar
   delta, don't estimate from listed per-token pricing alone; for
   `tencent/hy3:free` confirm the delta is genuinely $0).
5. For the `gpt-5.4-mini` arm, report the same agreement rate/breakdown,
   but note cost honestly as "subscription-covered, not separately
   metered" rather than computing a dollar figure — do not invent a cost
   number for this arm.
6. Extrapolate real per-question cost for the full 3,113-question set from
   the measured per-question cost, for each of the three OpenRouter
   models. For `gpt-5.4-mini`, instead note the practical throughput
   implication of running 3,113 questions through `codex exec` (e.g. batch
   size feasible per call, rough call count needed) since that model's
   constraint is subscription usage/rate limits, not dollar cost.
7. Produce one consolidated **side-by-side table**: all 30 sampled
   questions as rows, with each of the four models' solved answer,
   whether it agrees with the stored `correct_option_label`, and note
   every case where models disagree with each other (not just with the
   stored answer) — this cross-model agreement/disagreement pattern is
   the main signal for how reliable this approach will be at scale, and
   for which model(s) are worth using for the full pass.

## Explicit constraints

- No writes to `data/study.db`. This is measurement only.
- Do not touch GK/GA questions at all.
- Do not build the full verification pipeline yet — that's a follow-up
  workorder after this smoke test's numbers come back. Just measure and
  report.

## Report format

1. The full 30-question side-by-side table (question id/section, stored
   answer, deepseek-r1 answer + agree?, qwen3-235b-thinking answer + agree?,
   tencent/hy3:free answer + agree?, gpt-5.4-mini answer + agree?).
2. Per-model: agreement count/rate overall and per-section; real measured
   cost + extrapolated cost for 3,113 questions for the three OpenRouter
   models; subscription-covered note + throughput estimate for
   gpt-5.4-mini.
3. Cross-model disagreement notes (all four models compared pairwise where
   relevant).
4. A clear recommendation on which model (or combination — e.g.
   subscription-covered gpt-5.4-mini as the primary solver since it's
   effectively free to the user, with a paid/free OpenRouter model only as
   a tie-breaker on disagreements) looks worth using for the full pass,
   with your reasoning.
