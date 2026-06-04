"""Fix stale practice_ready flags for questions with empty blocking_review_reasons."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status

fixed_all = 0
for mp in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json"):
    data = json.loads(mp.read_text(encoding="utf-8"))
    changed = 0
    for q in data.get("questions", []):
        if not q.get("blocking_review_reasons") and q.get("canonical_correct_option_label") and not q.get("practice_ready"):
            q["practice_ready"] = True
            changed += 1
    if changed:
        _refresh_qc_status(data)
        mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
        fixed_all += changed
        print(f"{mp.parent.name}: fixed {changed} stale, now {pr}/{len(data.get('questions',[]))}")

print(f"\nTotal stale flags fixed: {fixed_all}")
