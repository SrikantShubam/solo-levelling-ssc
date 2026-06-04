# SSC CGL Scoring Machine Plan v9 Final

## Summary
Target is true readiness for SSC CGL 2027. This is the build-from version: pattern subjects use boss fights, memory subjects use recall systems, shared subjects use one archetype pool with tier-specific difficulty, and readiness is multi-sourced.

Refresh the system against the official SSC CGL 2027 notification when it drops. Current structure is based on the recent official SSC CGL pattern.

## Operating System
### Phase 1: Foundation Gate, 42-Day Hard Cap

- Run 200-question baseline: 80 Quant/DI, 40 Reasoning, 40 English, 40 GK.
- Manually tag every Phase 1 question by foundation concept.
- Unlock boss fights per area at 70%+ timed accuracy.
- 65-69% enters boss fights with paired remediation.
- Below 55% stays remediation-first and is excluded from readiness scoring until 65%.
- Phase 1 ends after 42 days regardless; weak areas become active remediation.

### Phase 2: Corpus, Holdout, Atlas

- Extract PYQs and solution booklets into SQLite.
- Reserve 25% sealed holdout before clustering.
- Use sealed holdout max 2 full mocks/month.
- Normalize atlas to roughly 160-240 archetypes.
- Build one shared Reasoning archetype pool with `tier_difficulty`.
- Build separate pattern archetypes and memory fact cards.

### Phase 3: Diagnostic Grinding

- Probe each unlocked archetype with 10 timed questions.
- Failure cause = student label + rule inference + manual arbitration.
- After local Qwen exists, arbitration can be batched to the model.
- Routes: 80%+ to SM-2, 50-79% to boss fights, below 50% with concept gap to remediation, below 50% without concept gap to high-priority boss fights.

### Phase 4: Main Grind, Exactly 180 Min/Day

- 25 min SM-2 review.
- 35 min Tier-1 boss fights.
- 60 min Tier-2 module queue.
- 20 min GK/GA memory queue.
- 30 min English.
- 10 min analysis.

After Tier-1 calibrated floor clears 135 twice: shift to 25 min Tier-1 and 70 min Tier-2, total still 180.

## Queue Rules
### English

- Daily 30-minute English block covers Tier-1 grammar, vocabulary, cloze, spotting errors, sentence improvement, and short RC.
- Tier-2 English sessions inside the Tier-2 block are separate and cover long RC, inference, para-jumbles, passage stamina, and deeper comprehension.
- Tier-2 English questions are not pre-exposed through the daily Tier-1 English block.

### Reasoning

- Reasoning archetypes are shared between Tier-1 and Tier-2.
- Accuracy is tracked separately for `tier1` and `tier2`.
- For shared Reasoning archetypes, Tier-2 readiness requires 80%+ accuracy at Tier-2 difficulty specifically, not Tier-1 accuracy on the same archetype.

### GK/GA

- GK and GA use one memory queue with `tier_scope` and `depth_level`.
- `tier1_basic` cards cover direct static facts and standard PYQ-style recall.
- `tier2_deep` cards cover deeper GA: economy terms, base years, indices, schemes, trade/customs relevance, current figures, and comparison facts.
- CBIC-relevant economy, trade policy, taxation, customs, schemes, and indices receive explicit tags.
- Daily 20-minute GK/GA block trains the unified queue; weekly Tier-2 GA filters to `tier2_deep` and `both`.

### Computer Knowledge

- CK is flashcard and recall only, not boss fights.
- Maintain 25-35 high-repeat CK topics.
- Minimum 10 minutes/week direct CK recall.
- Monthly 20-question CK pulse test.

### Skip List

- Temporary skip after 2 failed unlock gates.
- Temporary skip lasts 14 days or until monthly audit, whichever comes first.
- Re-entry requires one 5-question recognition probe at 60%+.
- Permanent skip after 3 failed unlock gates with JIT rescue.
- Permanent skip can be challenged only during monthly audit.

## Weekly Tier-2 Budget
The 60-minute Tier-2 block equals 360 minutes/week.

- Math/DI: 2 x 60 min = 120 min.
- English/RC: 2 x 45 min = 90 min.
- Reasoning: 1 x 45 min = 45 min.
- GA deep recall: 1 x 30 min = 30 min.
- Computer Knowledge: 1 x 15 min = 15 min.
- Mixed Tier-2 sectional: 1 x 60 min = 60 min.

Total: 360 minutes/week.

## Mocks, Pulses, And Notification Audit
### Mock Cadence

- First 8 weeks of Phase 4: 1 full mock/week.
- Months 3-5: 1 full mock every 5 days.
- After Tier-1 floor crosses 125: 1 full mock every 3 days.
- Mock day replaces boss-fight blocks, not SM-2.

### Monthly Pulses

- Foundation pulse and CK pulse run on the first Monday of each month.
- They replace that day's boss-fight blocks.
- SM-2, GK/GA, English, and analysis still run.
- If a full mock lands on pulse day, move the mock to the next grind day.

### Notification Audit

- When SSC CGL 2027 notification drops, pause new boss-fight advancement for up to 48 hours.
- Continue only SM-2, GK/GA recall, English recall, and due pulses.
- Compare section counts, marks, timing, negative marking, syllabus, module structure, eligibility, and skill-test rules.
- Audit complete means ROI weights updated, changed modules flagged, readiness thresholds adjusted, and affected queues regenerated.
- Major change triggers a 7-day recalibration block; minor/no change resumes normal grind immediately.
- Major change means altered section weights, new/removed module, changed negative marking, or changed qualifying rule.

## Software Build Plan
Build order:

- MVP: SQLite, question loader, CLI quiz loop, timer, attempt logging, basic reports.
- Scheduler: unlocks, SM-2, active queue, remediation queue, skip list.
- Rule-based classifier: student label, timing inference, concept tags, manual arbitration.
- Retrieval: sentence-transformer embeddings and persistent FAISS.
- Model layer: local Qwen coach, DeepSeek-R1 rescue, Gemini extraction support.
- Model-assisted classifier: batched Qwen arbitration.
- Readiness dashboard: internal, holdout, external mock, fatigue, coverage, module floors.

Core tables: `questions`, `archetypes`, `attempts`, `sessions`, `external_mocks`, `fact_cards`, `notification_audits`.

## Checkpoints And Readiness
### Month 2

- Foundation gate and diagnostic complete.
- At least 30 archetypes probed.
- Probed archetypes average 65%+ accuracy.
- Probed-only Tier-1 floor above 90 with coverage shown.
- If missed: pause new archetype unlocks for 2 weeks and run remediation-heavy mode.

### Month 5

- Tier-1 floor above 125.
- Top 50 ROI archetypes unlocked or in SM-2.
- Minimum 20 full mocks completed.
- External calibration started.
- If Quant/DI is weakest: pull 10 min/day from GK/GA for 4 weeks.
- If Tier-2 overall is weakest: pull 10 min/day from Tier-1 for 4 weeks.
- If English is weakest: protect daily English and add one extra Tier-2 English session by replacing one mixed sectional per week for 4 weeks.
- If GA is weakest: do not pull from GK/GA; convert one weekly mixed Tier-2 sectional into deep GA recall for 4 weeks.
- If multiple sections are equally weakest, apply priority order: Quant/DI, Tier-2 overall, English, GA.

### Month 8

- Tier-1 floor above 140.
- Tier-2 floor above 110 with top60 coverage shown.
- At least 2 external mocks in last 30 days.
- No section consistently below 15 correct.
- If missed: run atlas audit, skip-list audit, and rebalance daily split toward weakest section.

### Final Readiness

Final readiness fires only when all are true:

- All foundation pulse areas are 75%+ within the last 14 days.
- Top 100 Tier-1 archetypes are 80%+.
- Top 60 Tier-2 pattern archetypes are 80%+.
- Module floors: Math 80%, Reasoning 80%, English 80%, GA 75%, CK 70% across at least 15 CK topics.
- For shared Reasoning, Tier-2 accuracy must be Tier-2 difficulty accuracy.
- CBIC-relevant cards are 80%+ specifically.
- Last 5 full mocks are above calibrated 145 floor.
- At least 2 of those 5 are external or sealed-holdout mocks.
- No section below 17 correct in last 3 mocks.
- 2-option elimination success above 85% across last 100 drills.
- 7-day readiness trend stable or improving.

## Data Rules
### fact_cards

`fact_cards` include:

- `tier_scope`: `tier1`, `tier2`, or `both`.
- `depth_level`: `basic` or `deep`.
- `cbic_relevance`: boolean.
- `source`.
- `expires_on` for current affairs.

Expired current-affairs cards are automatically removed from active SM-2, drill, and readiness queues. They remain in the database for audit, mock review, and historical analysis, but no longer count toward active GA accuracy.

### CBIC Priority

In the final 8 weeks before the attempt, `cbic_relevant=true` cards get a daily 5-minute priority recall slot inside the GK/GA block. Final readiness requires 80%+ accuracy on CBIC-relevant cards specifically, separate from the aggregate GA 75% floor.

## Assumptions

- Baseline is near zero.
- SSC CGL 2027 is the serious target.
- Daily capacity is exactly 3 hours, 6 days/week.
- Tier-2 English and Tier-2 GA require deeper treatment than Tier-1 equivalents.
- Paid model use remains limited to extraction, clustering, and limited rescue.
