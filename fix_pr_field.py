import json, sys; sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status

d = json.loads(open("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())

changed = 0
for q in d.get("questions", []):
    recomputed = _is_practice_ready(q)
    stored = q.get("practice_ready")
    if recomputed != stored:
        print(f"Q{q.get('global_question_number')}: stored={stored}, recomputed={recomputed}")
        q["practice_ready"] = recomputed
        changed += 1

_refresh_qc_status(d)

open("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))

pr = sum(1 for q in d.get("questions", []) if q.get("practice_ready"))
print(f"\nFixed {changed} practice_ready flags")
print(f"Practice-ready now: {pr}")
