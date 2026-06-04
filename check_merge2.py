import json
d = json.loads(open("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())
pr = [q for q in d.get("questions",[]) if q.get("practice_ready")]
nr = [q for q in d.get("questions",[]) if not q.get("practice_ready")]
print(f"Total: {len(d.get('questions',[]))}")
print(f"Practice-ready: {len(pr)}")
print(f"Not practice-ready: {len(nr)}")
print(f"AI-reviewed: {sum(1 for q in d.get('questions',[]) if q.get('ai_reviewed'))}")
print()
print("Blocked reasons for not-ready questions:")
from collections import Counter
c = Counter()
for q in nr:
    c[tuple(q.get("blocking_review_reasons") or ["(none)"])] += 1
for reasons, count in c.most_common():
    print(f"  {list(reasons)}: {count}")
print()
if nr:
    q = nr[0]
    print(f"Example: Q{q.get('global_question_number')} page={q.get('source_page')}")
    print(f"  canonical_correct={q.get('canonical_correct_option_label')}")
    print(f"  blocking_reasons={q.get('blocking_review_reasons')}")
    print(f"  evidence_status={q.get('evidence_status')}")
    print(f"  canonical_review_reasons={q.get('canonical_review_reasons')}")
    print(f"  visual_required={q.get('visual_required')}")
    print(f"  math_required={q.get('math_required')}")
    print(f"  option_crop_paths_count={len(q.get('option_crop_paths') or [])}")
