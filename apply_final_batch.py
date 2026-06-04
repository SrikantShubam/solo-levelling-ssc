"""Apply second parallel batch answers."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

all_answers = {
    "2024_tier2_prepp_paper1": {
        48:"1",49:"4",50:"2",51:"3",59:"2",60:"1",61:"4",62:"1",63:"1",64:"2",65:"4",66:"1",67:"4",68:"4",69:"3",
        70:"1",72:"4",73:"2",74:"3",75:"1",76:"2",77:"4",87:"2",88:"1",90:"2",91:"1",92:"3",93:"2",94:"1",96:"2",
        97:"1",98:"1",99:"1",100:"1",101:"3",102:"4",103:"2",104:"2",105:"2",114:"4",115:"3",116:"1",117:"4",118:"2",119:"1",
        120:"1",121:"3",122:"4",123:"3",124:"2",125:"1",126:"4",127:"1",128:"2",129:"1",130:"1",138:"3",139:"2",141:"2",142:"1",
        143:"1",144:"1",146:"3",147:"1",149:"1",
    },
    "2024_tier2_sscportal_jan18_response_sheet": {
        18:"1",19:"2",26:"1",28:"1",6:"1",14:"1",
    },
    "2024_tier2_sscportal_jan20_response_sheet": {
        4:"1",5:"2",10:"2",11:"1",17:"3",20:"2",44:"1",14:"1",15:"1",24:"2",13:"1",
    },
}

total_fixed = 0
for pdf_name, answers in all_answers.items():
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    if not mp.exists():
        continue
    data = json.loads(mp.read_text(encoding="utf-8"))
    oi = set(data.get("option_or_correct_answer_issue_global_questions", []))
    ci = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    lc = set(data.get("low_confidence_global_questions", []))
    fixed = 0
    for q in data.get("questions", []):
        qnum = q.get("question_number")
        if qnum not in answers:
            continue
        new_c = str(answers[qnum])
        if q.get("canonical_correct_option_label") or new_c not in {"1","2","3","4"}:
            continue
        q["canonical_correct_option_label"] = new_c
        q["correct_option_label"] = new_c
        for opt in q.get("options", []):
            if isinstance(opt, dict) and str(opt.get("label")) == new_c:
                q["correct_option_text"] = str(opt.get("text", ""))
                break
        q["correct_evidence_source"] = "grok_massive_answer"
        q["evidence_status"] = "PASS_WITH_EVIDENCE"
        q["evidence_reasons"] = ["grok_massive_batch"]
        q["raw_gemini_correct_option_label"] = q.get("raw_gemini_correct_option_label") or new_c
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok_massive"
        fixed += 1
        gnum = q.get("global_question_number")
        optext = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        modality = classify_modality(str(q.get("question_text_full", "")), optext)
        reasons = review_reasons_for_question(
            modality=modality.label, evidence_status="PASS_WITH_EVIDENCE",
            chosen_missing=gnum in ci, option_issue=gnum in oi, low_confidence=gnum in lc,
            has_page_asset=True, has_visual_asset=True, has_question_crop=True)
        q["canonical_review_reasons"] = list(reasons)
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    total_fixed += fixed
    print(f"{pdf_name}: +{fixed} -> PR={pr}/{len(data.get('questions',[]))}")

print(f"\nTotal new answers: {total_fixed}")
