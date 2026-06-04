import json
from collections import Counter
d = json.loads(open("pipeline_output/p2_gemini/2020_tier2_kdcampus_answer_key/merged_questions_global_order.json", encoding="utf-8").read())
c = Counter()
for q in d.get("questions", []):
    if not q.get("practice_ready"):
        c[tuple(q.get("blocking_review_reasons") or ["(none)"])] += 1
for reasons, count in c.most_common():
    print(f"{list(reasons)}: {count}")
print(f"Total not ready: {sum(c.values())}")
# Check first one
for q in d.get("questions", []):
    if not q.get("practice_ready"):
        print(f"First: Q{q.get('global_question_number')} canon={q.get('canonical_correct_option_label')} blocking={q.get('blocking_review_reasons')}")
        break
