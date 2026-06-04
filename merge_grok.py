import json, os
from pathlib import Path

# Grok results for 2020_tier1_prepp_shift1
grok_results = {
    2: {"questions": [{"question_number": 3, "correct_option_label": "3", "chosen_option_label": None}, {"question_number": 4, "correct_option_label": "2", "chosen_option_label": "2"}]},
    4: {"questions": [{"question_number": 9, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 10, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 11, "correct_option_label": "1", "chosen_option_label": "1"}]},
    6: {"questions": [{"question_number": 14, "correct_option_label": "1", "chosen_option_label": None}, {"question_number": 15, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 16, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 17, "correct_option_label": "4", "chosen_option_label": "4"}]},
    8: {"questions": [{"question_number": 21, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 22, "correct_option_label": "4", "chosen_option_label": None}, {"question_number": 23, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 24, "correct_option_label": "3", "chosen_option_label": "3"}]},
    9: {"questions": [{"question_number": 25, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 1, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 2, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 3, "correct_option_label": "1", "chosen_option_label": "4"}, {"question_number": 4, "correct_option_label": "3", "chosen_option_label": "3"}]},
    10: {"questions": [{"question_number": 5, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 6, "correct_option_label": "1", "chosen_option_label": "4"}, {"question_number": 7, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 8, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 9, "correct_option_label": "3", "chosen_option_label": "3"}]},
    11: {"questions": [{"question_number": 10, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 11, "correct_option_label": "2", "chosen_option_label": "4"}, {"question_number": 12, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 13, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 14, "correct_option_label": "3", "chosen_option_label": "3"}]},
    12: {"questions": [{"question_number": 15, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 16, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 17, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 18, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 19, "correct_option_label": "4", "chosen_option_label": "1"}]},
    13: {"questions": [{"question_number": 20, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 21, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 22, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 23, "correct_option_label": "3", "chosen_option_label": None}, {"question_number": 24, "correct_option_label": "2", "chosen_option_label": "2"}]},
    14: {"questions": [{"question_number": 25, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 1, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 2, "correct_option_label": "3", "chosen_option_label": "1"}]},
    21: {"questions": [{"question_number": 25, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 1, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 2, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 3, "correct_option_label": "1", "chosen_option_label": "4"}]},
    22: {"questions": [{"question_number": 4, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 5, "correct_option_label": "1", "chosen_option_label": "3"}, {"question_number": 6, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 7, "correct_option_label": "4", "chosen_option_label": "3"}]},
    23: {"questions": [{"question_number": 8, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 9, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 10, "correct_option_label": "1", "chosen_option_label": "2"}, {"question_number": 11, "correct_option_label": "2", "chosen_option_label": "2"}]},
    24: {"questions": [{"question_number": 12, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 13, "correct_option_label": "4", "chosen_option_label": "2"}, {"question_number": 14, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 15, "correct_option_label": "4", "chosen_option_label": "4"}]},
    25: {"questions": [{"question_number": 16, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 17, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 18, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 19, "correct_option_label": "4", "chosen_option_label": "4"}]},
    26: {"questions": [{"question_number": 20, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 21, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 22, "correct_option_label": "1", "chosen_option_label": "1"}]},
    27: {"questions": [{"question_number": 23, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 24, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 25, "correct_option_label": "1", "chosen_option_label": "1"}]},
}

merged_path = Path("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json")
data = json.loads(merged_path.read_text(encoding="utf-8"))

updated = 0
correct_fixed = 0
chosen_fixed = 0
already_correct = 0
conflict = 0

for q in data.get("questions", []):
    page = q.get("source_page")
    qnum = q.get("question_number")
    
    if page not in grok_results:
        continue
    
    grok_qs = grok_results[page].get("questions", [])
    grok_q = None
    for gq in grok_qs:
        if gq.get("question_number") == qnum:
            grok_q = gq
            break
    
    if not grok_q:
        continue
    
    existing_correct = q.get("canonical_correct_option_label")
    new_correct = grok_q.get("correct_option_label")
    new_chosen = grok_q.get("chosen_option_label")
    
    if not existing_correct and new_correct and new_correct in {"1", "2", "3", "4"}:
        q["canonical_correct_option_label"] = new_correct
        q["correct_option_label"] = new_correct
        q["correct_option_text"] = ""
        for opt in q.get("options", []):
            if str(opt.get("label")) == new_correct:
                q["correct_option_text"] = str(opt.get("text", ""))
                break
        q["correct_evidence_source"] = "grok_ai_review"
        q["evidence_status"] = "PASS_WITH_EVIDENCE"
        q["evidence_reasons"] = ["grok_ai_review"]
        q["raw_gemini_correct_option_label"] = q.get("raw_gemini_correct_option_label") or new_correct
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok"
        correct_fixed += 1
        updated = True
    elif existing_correct and new_correct and existing_correct != new_correct:
        conflict += 1
    elif existing_correct and new_correct and existing_correct == new_correct:
        already_correct += 1
    
    existing_chosen = q.get("chosen_option_label")
    if (not existing_chosen or str(existing_chosen).strip() not in {"1", "2", "3", "4"}) and new_chosen and new_chosen in {"1", "2", "3", "4"}:
        q["chosen_option_label"] = new_chosen
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok"
        chosen_fixed += 1
        updated = True

if updated:
    # Recompute practice_ready
    from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    merged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    practice_ready = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    print(f"Updated {merged_path.parent.name}")
    print(f"  Correct labels fixed: {correct_fixed}")
    print(f"  Chosen labels fixed: {chosen_fixed}")
    print(f"  Already correct (no change): {already_correct}")
    print(f"  Conflicts (different from existing): {conflict}")
    print(f"  Practice-ready now: {practice_ready}")
