"""Apply grok_reason results as we collect them."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

# Map letters to numbers
def norm(v):
    v = str(v).strip().lower()
    return {"a":"1","b":"2","c":"3","d":"4"}.get(v, v)

# Accumulated answers so far
all_answers = {
    "2022_tier1_prepp_shift1": {21: "4", 23: "4", 24: "3"},
    "2023_tier1_prepp_shift1": {11: "3", 15: "4"},
    "2024_tier1_prepp_shift1": {4: "2", 9: "4", 10: "3", 11: "2", 17: "3", 18: "2"},
    "2021_tier1_prepp_shift1": {9: "3", 10: "3", 12: "2", 19: "4", 62: "1", 70: "4", 74: "1", 92: "3"},
    "2019_tier2_prepp_english": {164: "4"},
    "2019_tier2_prepp_quant": {58: "2", 61: "4"},
    "2021_tier2_prepp_english": {138: "3"},
    "2024_tier2_prepp_paper1": {},
    "2019_tier2_prepp_quant": {},
}

# Update all answers into merged JSONs
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
        qn = q.get("question_number")
        if qn not in answers:
            continue
        nc = norm(answers[qn])
        if q.get("canonical_correct_option_label") or nc not in {"1","2","3","4"}:
            continue
        q["canonical_correct_option_label"] = nc
        q["correct_option_label"] = nc
        for o in q.get("options", []):
            if isinstance(o, dict) and str(o.get("label")) == nc:
                q["correct_option_text"] = str(o.get("text", ""))
                break
        q["correct_evidence_source"] = "grok_reason_vision"
        q["evidence_status"] = "PASS_WITH_EVIDENCE"
        q["evidence_reasons"] = ["grok_reason_vision"]
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok_reason"
        fixed += 1
        gnum = q.get("global_question_number")
        ot = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        md = classify_modality(str(q.get("question_text_full", "")), ot)
        rr = review_reasons_for_question(
            modality=md.label, evidence_status="PASS_WITH_EVIDENCE",
            chosen_missing=gnum in ci, option_issue=gnum in oi, low_confidence=gnum in lc,
            has_page_asset=True, has_visual_asset=True, has_question_crop=True)
        q["canonical_review_reasons"] = list(rr)
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    print(f"{pdf_name}: +{fixed} -> PR={pr}/{len(data.get('questions',[]))}")
