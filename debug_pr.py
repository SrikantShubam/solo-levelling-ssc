import json, sys; sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

d = json.loads(open("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())

for q in d.get("questions", []):
    if not q.get("practice_ready") and q.get("ai_reviewed"):
        pr = _is_practice_ready(q)
        reasons = q.get("blocking_review_reasons") or []
        print(f"Q{q.get('global_question_number')}:")
        print(f"  _is_practice_ready={pr}")
        print(f"  blocking_reasons={list(reasons)}")
        print(f"  canonical_correct={q.get('canonical_correct_option_label')}")
        print(f"  visual_required={q.get('visual_required')}")
        print(f"  modality={q.get('question_modality')}")
        print(f"  question_crop_path={bool(q.get('question_crop_path'))}")
        print(f"  stimulus_crop_path={bool(q.get('stimulus_crop_path'))}")
        print(f"  option_crop_paths={len(q.get('option_crop_paths') or [])}")
        break
