import json, os
data = json.loads(open("pipeline_output/p2_gemini/2019_tier1_prepp_shift1/merged_questions_global_order.json").read())
for q in data["questions"]:
    if q.get("source_page") == 2 and q["question_number"] == 3:
        crops = q.get("option_crop_paths") or []
        for c in crops:
            print(f"  crop exists: {os.path.exists(c)} -> {c}")
        print(f"  question_crop exists: {os.path.exists(q.get('question_crop_path', ''))}")
        print(f"  stimulus_crop exists: {os.path.exists(q.get('stimulus_crop_path', ''))}")
        break
