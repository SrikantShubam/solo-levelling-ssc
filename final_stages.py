"""Full stage-by-stage breakdown of corpus status."""
import json
from pathlib import Path

# Stage 1: Raw extraction
total = 0
# Stage 2: Baseline practice-ready (original pipeline)
baseline = 1073
# Stage 3: Current state
current_pr = 0
current_ai = 0

by_pdf = {}
for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    name = mp.parent.name
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    ai = sum(1 for q in data.get("questions", []) if q.get("ai_reviewed"))
    total_here = len(data.get("questions", []))
    total += total_here
    current_pr += pr
    current_ai += ai
    by_pdf[name] = {"total": total_here, "pr": pr, "ai": ai}

figures = sum(1 for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions", []) if not q.get("practice_ready") and q.get("question_modality") in {"visual_options", "visual_stimulus", "table_di", "graph_chart", "dice"})
stale = sum(1 for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions", []) if not q.get("practice_ready") and not q.get("blocking_review_reasons"))
low_conf = sum(1 for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions", []) if not q.get("practice_ready") and "low_confidence" in (q.get("blocking_review_reasons") or []))
unresolved = sum(1 for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions", []) if not q.get("practice_ready") and "correct_option_unresolved_or_conflict" in (q.get("blocking_review_reasons") or []))
malformed = sum(1 for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions", []) if not q.get("practice_ready") and "malformed_options" in (q.get("blocking_review_reasons") or []))

print("=" * 72)
print("SSC CORPUS STATUS - FINAL STAGE BREAKDOWN")
print("=" * 72)
print()
print(f"Total corpus:              {total} questions across 19 PDFs")
print(f"Stage 1 - Raw extraction:  {total} (Gemini pipeline)")
print(f"Stage 2 - Pipeline QC:     {baseline} practice-ready (original CV evidence)")
print(f"Stage 3 - Grok AI Review:  +{current_pr - baseline} (green-tick pages + parallel answer batches)")
print(f"Stage 4 - Answer Keys:     2 dedicated keys (191 + 36 answers extracted)")
print(f"Stage 5 - Final state:     {current_pr} practice-ready ({current_pr/total*100:.1f}%)")
print()
print("BREAKDOWN OF REMAINING 146:")
print(f"  Figure-based (vision required):  {figures}")
print(f"  Low confidence:                  {low_conf}")
print(f"  Unresolved correct options:      {unresolved}")
print(f"  Stale flags (fixable):           {stale}")
print(f"  Malformed options:               {malformed}")
print()
print("PDFs AT 100%:")
done = [n for n, d in by_pdf.items() if d["pr"] == d["total"]]
for n in sorted(done):
    print(f"  {n}")
print()
print("PDFs WITH GAPS:")
for n, d in sorted(by_pdf.items()):
    if d["pr"] < d["total"]:
        print(f"  {n}: {d['pr']}/{d['total']} ({d['total']-d['pr']} remaining)")
