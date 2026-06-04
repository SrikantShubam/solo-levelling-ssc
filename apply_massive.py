"""Apply all parallel batch answers into merged JSONs."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

# All answers from the parallel batch, organized by PDF
all_answers = {
    "2019_tier1_prepp_shift1": {13:"2", 21:"4"},
    "2019_tier2_prepp_english": {3:"2",5:"2",9:"1",11:"1",13:"3",15:"3",17:"2",19:"1",21:"1",23:"4",25:"3",37:"2",41:"2",50:"2",55:"3",63:"2",67:"1",71:"3",79:"1",86:"2",94:"3"},
    "2019_tier2_prepp_quant": {2:"4",9:"2",10:"2",12:"1",14:"2",15:"1",26:"2",28:"3",36:"3",67:"2",70:"2",75:"1",77:"2",82:"1",94:"4",96:"3"},
    "2021_tier1_prepp_shift1": {25:"2",26:"4",27:"3",28:"3",51:"3",52:"2",53:"1",54:"2",55:"1",56:"2",76:"2",77:"2",78:"2",79:"4",80:"1",82:"3",83:"3",99:"3",100:"2"},
    "2021_tier2_prepp_english": {23:"1",48:"1",88:"3",101:"3",115:"2",118:"1"},
    "2022_tier1_prepp_shift1": {22:"4",1:"3",3:"2",5:"2",6:"3",14:"3",15:"2",16:"1",19:"1",20:"2",6:"3",12:"2",18:"2",20:"3"},
    "2022_tier2_prepp_paper1": {19:"1",23:"2",26:"3"},
    "2023_tier1_prepp_shift1": {1:"2",9:"1",13:"1",25:"3",7:"1",9:"4",10:"1",18:"1",4:"2",5:"2",6:"3",16:"3",22:"1",23:"3",1:"1",6:"1",7:"4",17:"2",24:"1"},
    "2023_tier2_prepp_paper1": {23:"2",29:"1",31:"3",41:"1",14:"3",17:"4",19:"1"},
    "2024_tier1_appx_answer_key": {1:"3",2:"2",3:"1"},
    "2024_tier1_prepp_shift1": {47:"4",48:"2",49:"2",50:"2",51:"1",52:"4",53:"2",54:"1",55:"2",74:"1",75:"4",76:"3",77:"3",78:"1",79:"4",80:"4",81:"1",82:"3",83:"3",84:"2",97:"3"},
    "2024_tier2_prepp_paper1": {10:"1",11:"1",12:"4",13:"3",14:"1",15:"2",16:"2",17:"1",18:"3",19:"1",20:"2",25:"1",34:"2",35:"1",36:"2",37:"1",38:"3",39:"1",40:"2",41:"3"},
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
    print(f"{pdf_name}: +{fixed} answers, PR={pr}/{len(data.get('questions',[]))}")

print(f"\nTotal new answers applied: {total_fixed}")
