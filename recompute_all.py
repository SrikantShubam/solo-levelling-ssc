"""
Recompute practice_ready for ALL questions across all PDFs.
Fixes the stale practice_ready flag issue.
"""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status

total_fixed = 0
for p in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    changed = 0
    for q in data.get("questions", []):
        computed = _is_practice_ready(q)
        if computed != q.get("practice_ready"):
            q["practice_ready"] = computed
            changed += 1
    if changed:
        _refresh_qc_status(data)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        total_fixed += changed
        pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
        print(f"{p.parent.name}: fixed {changed} flags, now {pr}/{len(data.get('questions',[]))} practice-ready")

print(f"\nTotal flags fixed: {total_fixed}")
