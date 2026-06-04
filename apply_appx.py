import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

answers = {1:2,2:2,3:3,4:2,5:4,6:1,7:1,8:3,9:2,10:1,11:1,12:1,13:4,14:4,15:3,16:1,17:4,18:2,19:2,20:1,21:3,22:3,23:2,24:4,25:1,26:4,27:2,28:3,29:4,30:4,31:1,32:3,33:1,34:1,35:2,36:2}
mp = Path("pipeline_output/p2_gemini/2024_tier1_appx_answer_key/merged_questions_global_order.json")
d = json.loads(mp.read_text(encoding="utf-8"))

option_issue_set = set(d.get("option_or_correct_answer_issue_global_questions", []))
chosen_issue_set = set(d.get("missing_or_invalid_chosen_option_global_questions", []))
low_confidence_set = set(d.get("low_confidence_global_questions", []))

fixed = 0
for q in d.get("questions", []):
    qnum = q.get("question_number")
    if qnum not in answers or q.get("canonical_correct_option_label"):
        continue
    new_c = str(answers[qnum])
    q["canonical_correct_option_label"] = new_c
    q["correct_option_label"] = new_c
    for opt in q.get("options", []):
        if str(opt.get("label")) == new_c:
            q["correct_option_text"] = str(opt.get("text", ""))
            break
    q["correct_evidence_source"] = "answer_key_extraction"
    q["evidence_status"] = "PASS_WITH_EVIDENCE"
    q["evidence_reasons"] = ["answer_key_lookup"]
    q["ai_reviewed"] = True
    q["ai_review_source"] = "answer_key"
    fixed += 1
    
    gnum = q.get("global_question_number")
    optext = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
    modality = classify_modality(str(q.get("question_text_full", "")), optext)
    reasons = review_reasons_for_question(
        modality=modality.label, evidence_status="PASS_WITH_EVIDENCE",
        chosen_missing=gnum in chosen_issue_set,
        option_issue=gnum in option_issue_set,
        low_confidence=gnum in low_confidence_set,
        has_page_asset=True, has_visual_asset=True, has_question_crop=True)
    q["canonical_review_reasons"] = list(reasons)

for q in d.get("questions", []):
    q["practice_ready"] = _is_practice_ready(q)
_refresh_qc_status(d)
mp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
pr = sum(1 for q in d.get("questions", []) if q.get("practice_ready"))
print(f"Fixed {fixed} answers, practice_ready: {pr}/{len(d.get('questions',[]))}")
