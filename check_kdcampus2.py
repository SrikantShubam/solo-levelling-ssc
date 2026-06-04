import json; from collections import Counter
d = json.loads(open("pipeline_output/p2_gemini/2020_tier2_kdcampus_answer_key/merged_questions_global_order.json", encoding="utf-8").read())
c = Counter()
for q in d.get("questions", []):
    if not q.get("practice_ready"):
        reasons = tuple(q.get("blocking_review_reasons") or ["(none)"])
        c[reasons] += 1
for reasons, count in c.most_common():
    names = ", ".join(reasons) if reasons else "(none)"
    print(f"  [{names}]: {count}")
print(f"Total not ready: {sum(c.values())}")
# Check what _is_practice_ready says
import sys; sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready
first = [q for q in d.get("questions", []) if not q.get("practice_ready")][0]
print(f"\nFirst Q: computed={_is_practice_ready(first)} stored={first.get('practice_ready')}")
print(f"  canon={first.get('canonical_correct_option_label')}")
print(f"  blocking={first.get('blocking_review_reasons')}")
print(f"  canonical_review={first.get('canonical_review_reasons')}")
print(f"  evidence={first.get('evidence_status')}")
print(f"  option_issues={first.get('global_question_number') in d.get('option_or_correct_answer_issue_global_questions', [])}")
