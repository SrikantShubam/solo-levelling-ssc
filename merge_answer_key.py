"""Merge answer key data into PDF's merged JSON."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

def apply_answer_key(pdf_name, answer_map):
    merged_path = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    
    option_issue_set = set(data.get("option_or_correct_answer_issue_global_questions", []))
    chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(data.get("low_confidence_global_questions", []))
    
    correct_fixed = 0
    for q in data.get("questions", []):
        qnum = q.get("question_number")
        if qnum not in answer_map:
            continue
        new_correct = str(answer_map[qnum])
        if new_correct not in {"1", "2", "3", "4"}:
            continue
        if q.get("canonical_correct_option_label"):
            continue
        
        q["canonical_correct_option_label"] = new_correct
        q["correct_option_label"] = new_correct
        for opt in q.get("options", []):
            if str(opt.get("label")) == new_correct:
                q["correct_option_text"] = str(opt.get("text", ""))
                break
        q["correct_evidence_source"] = "answer_key_extraction"
        q["evidence_status"] = "PASS_WITH_EVIDENCE"
        q["evidence_reasons"] = ["answer_key_lookup"]
        q["raw_gemini_correct_option_label"] = q.get("raw_gemini_correct_option_label") or new_correct
        q["ai_reviewed"] = True
        q["ai_review_source"] = "answer_key"
        correct_fixed += 1
        
        gnum = q.get("global_question_number")
        options = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        modality = classify_modality(str(q.get("question_text_full", "")), options)
        reasons = review_reasons_for_question(
            modality=modality.label,
            evidence_status="PASS_WITH_EVIDENCE",
            chosen_missing=gnum in chosen_issue_set,
            option_issue=gnum in option_issue_set,
            low_confidence=gnum in low_confidence_set,
            has_page_asset=True, has_visual_asset=True, has_question_crop=True,
        )
        q["canonical_review_reasons"] = list(reasons)
    
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    merged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    print(f"{pdf_name}: {correct_fixed} answers applied, practice_ready: {pr}/{len(data.get('questions',[]))}")
    return correct_fixed

if __name__ == "__main__":
    # KD Campus answer key
    kdcampus_answers = {i: v for i, v in enumerate([
        2,4,4,3,2,4,4,3,1,3,2,1,1,1,3,2,4,2,2,1,3,1,3,1,2,3,1,1,4,3,3,3,1,4,4,4,2,4,3,2,
        2,4,4,4,1,1,2,2,3,3,2,2,2,3,1,4,4,1,2,3,2,1,3,2,3,2,1,4,1,2,1,1,1,1,4,3,2,2,2,1,
        2,4,3,1,4,1,4,1,3,3,1,3,4,1,2,1,3,1,1,2,1,1,2,1,1,4,2,2,3,4,2,1,3,2,3,1,1,2,4,2,
        2,1,2,2,2,2,4,4,1,4,2,4,1,1,4,1,3,4,4,3,4,2,1,3,1,4,2,3,2,4,3,2,4,2,2,2,4,3,3,2,
        3,3,3,1,1,2,2,2,3,3,4,4,3,3,1,2,1,2,1,1,3,4,2,3,2,1,3,1,4,2,4,3,3,3,3,3,1,3,2,2,
    ], start=1)}
    apply_answer_key("2020_tier2_kdcampus_answer_key", kdcampus_answers)
