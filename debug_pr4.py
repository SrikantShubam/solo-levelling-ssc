import json, sys; sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready

d = json.loads(open("pipeline_output/p2_gemini/2022_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())
# Debug Q1
q = [qq for qq in d.get("questions", []) if qq.get("global_question_number") == 1][0]
print("Q1:")
print("  blocking_review_reasons:", q.get("blocking_review_reasons"))
print("  canonical_correct_option_label:", q.get("canonical_correct_option_label"))
print("  visual_required:", q.get("visual_required"))
print("  math_required:", q.get("math_required"))
print("  question_modality:", q.get("question_modality"))
print("  question_crop_path:", bool(q.get("question_crop_path")))
print("  stimulus_crop_path:", bool(q.get("stimulus_crop_path")))
print("  option_crop_paths:", len(q.get("option_crop_paths") or []))
print("  computed _is_practice_ready:", _is_practice_ready(q))

# Also debug Q5 (visual_options)
q5 = [qq for qq in d.get("questions", []) if qq.get("global_question_number") == 5][0]
print("\nQ5 (visual_options):")
print("  blocking_review_reasons:", q5.get("blocking_review_reasons"))
print("  canonical_correct_option_label:", q5.get("canonical_correct_option_label"))
print("  visual_required:", q5.get("visual_required"))
print("  math_required:", q5.get("math_required"))
print("  question_modality:", q5.get("question_modality"))
print("  option_crop_paths count:", len(q5.get("option_crop_paths") or []))
print("  computed _is_practice_ready:", _is_practice_ready(q5))
