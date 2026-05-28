# Extraction Phase Divergence Study

Date: 2026-05-24

## Headline

The real extraction phase diverged materially from the master plan.

The master plan assumed a precision-first extractor that would preserve question recall while routing uncertain answers to review. In the actual P2 batch run over 19 staged PDFs, the dominant failure mode was not "correct answer ambiguity on otherwise complete rows". The dominant failure mode was structural extraction collapse on a large subset of documents.

## What The Plan Expected

- Tier-1 runs should remain structurally complete at 100/100.
- Precision should improve answer trustworthiness by blocking uncertain rows, not by losing large numbers of questions.
- Visual, table, and math questions should retain enough assets to be reviewable.
- Uncertain cases should go to review instead of silently poisoning the dataset.
- The output should be suitable for building a high-precision ground-truth/training corpus.

## What Actually Happened

Batch source: `extraction_reruns/p2_all_pdfs_20260524/batch_summary.json`

- Total PDFs run: 19
- QC statuses:
  - `PASS_WITH_MANUAL_REVIEW`: 1
  - `BLOCKED`: 6
  - `FAIL`: 11
  - `ERROR`: 1
- Tier-1 PDFs in batch: 9
- Tier-1 PDFs with full 100-question extraction: 4
- PDFs with 0 extracted questions: 6
- PDFs with fewer than 10 extracted questions: 9
- One PDF failed due to model copyright refusal:
  - `2020_tier2_kdcampus_answer_key.pdf`

## Main Divergences

1. Structural recall diverged much more than expected.
   - The plan assumed precision-over-recall at the answer level.
   - The real system lost recall at the document/question extraction level on many PDFs.
   - Examples:
     - `2021_tier1_prepp_shift1.pdf`: 91 questions
     - `2023_tier1_prepp_shift1.pdf`: 0 questions
     - `2024_tier1_prepp_shift1.pdf`: 3 questions
     - `2024_tier2_prepp_paper1.pdf`: 7 questions

2. Source heterogeneity is a bigger blocker than expected.
   - The corpus mixes response sheets, coaching reconstructions, answer-key-style PDFs, and at least one non-question notification/notice artifact.
   - The extractor is not robust enough yet across all these layouts to justify one-pass corpus-wide extraction.

3. Modality tagging is still too noisy for downstream trust.
   - Some clearly non-math rows are tagged as `math_formula`.
   - This shows keyword heuristics are still overfitting surface tokens instead of true question type.

4. The pipeline is still reviewable, but not yet production-usable as a corpus generator.
   - On successful documents, P2 does retain assets and route uncertain rows to review.
   - On weak documents, the system fails too early and too broadly for the review workflow to rescue it efficiently.

5. Copyright/model refusal is a real operational constraint.
   - The plan assumed API-based extraction could be budget-limited.
   - In practice, some files also trigger content refusal, which is orthogonal to cost and cannot be solved by prompting alone.

## Interpretation

The project is not ready to move from extraction into downstream corpus-dependent phases such as atlas building, clustering, or training-data freezing across the full corpus.

The extraction phase has proven that:

- the precision logic is directionally correct on good PDFs;
- the corpus is much dirtier and more layout-diverse than the master plan assumed;
- document-class routing now matters more than answer-level arbitration.

## Recommended Next Step

The next step should be an extraction stabilization subphase, not downstream pipeline expansion.

Specifically:

1. Build a document-class triage layer.
   - Separate PDFs into:
     - response-sheet style
     - coaching reconstructed answer-key style
     - section-only booklets
     - likely notice/non-question PDFs
     - refusal-prone PDFs

2. Define a corpus acceptance gate before extraction.
   - Do not run all staged PDFs through the same extraction flow by default.
   - Reject or quarantine obvious non-question artifacts before model spend.

3. Create per-class extraction benchmarks.
   - Pick 2-3 representative PDFs per class.
   - Measure structural question recall first.
   - Only after structural recall is acceptable should precision/QC comparisons matter.

4. Fix the highest-value class first.
   - Response-sheet Tier-1 PDFs are currently the best-behaved class.
   - Stabilize them to a reliable acceptance bar before expanding to noisier Tier-2/coaching artifacts.

5. Delay downstream corpus freeze.
   - Do not treat the current batch as a finalized training dataset.
   - Use it as a failure map for the next extraction iteration.

## Bottom Line

The master plan expected answer-level ambiguity to be the main risk.

The real extraction phase shows document-level structural instability is the bigger risk.

That changes the immediate roadmap:

- next is corpus triage plus extractor stabilization;
- not atlas, not clustering, not large-scale ground-truth freeze.
