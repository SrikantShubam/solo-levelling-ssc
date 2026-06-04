import json
from pathlib import Path

pr = 0
ai = 0
total = 0
pdfs = {}

for p in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    pdf_name = p.parent.name
    pdfs[pdf_name] = {"total": 0, "pr": 0}
    for q in data.get("questions", []):
        total += 1
        pdfs[pdf_name]["total"] += 1
        if q.get("practice_ready"):
            pr += 1
            pdfs[pdf_name]["pr"] += 1
        if q.get("ai_reviewed"):
            ai += 1

print(f"TOTAL: {total} questions")
print(f"PRACTICE-READY: {pr}")
print(f"AI-REVIEWED (via Grok): {ai}")
print(f"NEEDS REVIEW: {total - pr}")
print()
print("Per PDF:")
for k, v in sorted(pdfs.items()):
    flag = " <<< GROK FIXED" if v["total"] == v["pr"] and v["total"] > 50 and any(p.parent.name == k for p in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json") if json.loads(p.read_text(encoding="utf-8")).get("questions", [{}])[0].get("ai_reviewed")) else ""
    print(f"  {k}: {v['pr']}/{v['total']}{flag}")
