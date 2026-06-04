import json
d = json.loads(open("pipeline_output/p2_gemini/2022_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())
pr_count = sum(1 for q in d.get("questions", []) if q.get("practice_ready"))
print("Practice ready in file:", pr_count)

# Find first question without blocking reasons that isn't practice_ready
for q in d.get("questions", []):
    if not q.get("blocking_review_reasons") and not q.get("practice_ready"):
        print("Q{}: practice_ready={} canon={} visual={} modality={}".format(
            q.get("global_question_number"), q.get("practice_ready"),
            q.get("canonical_correct_option_label"), q.get("visual_required"),
            q.get("question_modality")))

# Count
count = sum(1 for q in d.get("questions", []) if not q.get("blocking_review_reasons") and not q.get("practice_ready"))
print("No blocking but not practice_ready:", count)
