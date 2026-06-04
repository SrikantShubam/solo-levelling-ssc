import json
from pathlib import Path

total_pr = 0
total_all = 0
total_ai = 0
pdfs = []

for p in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    name = p.parent.name
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    ai = sum(1 for q in data.get("questions", []) if q.get("ai_reviewed"))
    total_all += len(data.get("questions", []))
    total_pr += pr
    total_ai += ai
    pdfs.append((name, pr, ai, len(data.get("questions", []))))

print(f"TOTAL: {total_all} questions")
print(f"PRACTICE-READY: {total_pr}")
print(f"AI-REVIEWED (Grok): {total_ai}")
print(f"NEEDS REVIEW: {total_all - total_pr}")
print(f"\nDELTA FROM BASELINE (1,073): +{total_pr - 1073}")
print()

for name, pr, ai, total in sorted(pdfs):
    flag = " OK" if pr == total else ""
    print(f"  {name}: {pr}/{total} (ai={ai}){flag}")
