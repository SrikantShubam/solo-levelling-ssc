import json
data = json.loads(open("pipeline_output/p2_gemini/2019_tier1_prepp_shift1/merged_questions_global_order.json").read())
for q in data["questions"]:
    if q.get("source_page") == 2 and q["question_number"] == 3:
        print(f"practice_ready: {q.get('practice_ready')}")
        print(f"visual_required: {q.get('visual_required')}")
        print(f"math_required: {q.get('math_required')}")
        print(f"question_modality: {q.get('question_modality')}")
        print(f"question_crop_path: {q.get('question_crop_path')}")
        print(f"stimulus_crop_path: {q.get('stimulus_crop_path')}")
        print(f"option_crop_paths count: {len(q.get('option_crop_paths') or [])}")
        print(f"blocking_review_reasons: {q.get('blocking_review_reasons')}")
        print(f"canonical_correct_option_label: {q.get('canonical_correct_option_label')}")
