import json, sys; sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready

d = json.loads(open("pipeline_output/p2_gemini/2022_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())
for q in d.get("questions", []):
    if not q.get("blocking_review_reasons") and not q.get("practice_ready"):
        pr = _is_practice_ready(q)
        print("Q{}: computed={} stored={} canon={} visual={} modality={}".format(
            q.get("global_question_number"), pr, q.get("practice_ready"),
            q.get("canonical_correct_option_label"), q.get("visual_required"),
            q.get("question_modality")))
        break
