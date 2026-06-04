import json

data = json.loads(open("pipeline_output/p2_gemini/2019_tier1_prepp_shift1/merged_questions_global_order.json").read())
print("=== Gemini extraction for page 2 ===")
for q in data["questions"]:
    if q.get("source_page") == 2:
        print(f"Q{q['question_number']}: correct={q.get('correct_option_label')} chosen={q.get('chosen_option_label')} conf={q.get('confidence')} practice_ready={q.get('practice_ready')} evidence={q.get('evidence_status')}")
        print(f"  blocking_reasons={q.get('blocking_review_reasons')}")
        print(f"  canonical_correct={q.get('canonical_correct_option_label')}")
        print(f"  deterministic={q.get('deterministic_correct_option_label')}")
        print(f"  raw_gemini_correct={q.get('raw_gemini_correct_option_label')}")
