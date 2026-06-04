"""Apply figure batch answers."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

answers = {"2019_tier2_prepp_english": {164: "4"}, "2021_tier1_prepp_shift1": {12: "2", 70: "4", 74: "1"}, "2021_tier2_prepp_english": {138: "3"}, "2023_tier1_prepp_shift1": {15: "4"}, "2024_tier1_prepp_shift1": {4: "2"}}

for pdf_name, ans in answers.items():
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(mp.read_text(encoding="utf-8"))
    oi = set(data.get("option_or_correct_answer_issue_global_questions", []))
    ci = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    lc = set(data.get("low_confidence_global_questions", []))
    fixed = 0
    for q in data.get("questions", []):
        qn = q.get("question_number")
        if qn not in ans or q.get("canonical_correct_option_label"):
            continue
        nc = str(ans[qn])
        q["canonical_correct_option_label"] = nc
        q["correct_option_label"] = nc
        for o in q.get("options", []):
            if isinstance(o, dict) and str(o.get("label")) == nc:
                q["correct_option_text"] = str(o.get("text", ""))
                break
        q["correct_evidence_source"] = "grok_figure_batch"
        q["evidence_status"] = "PASS_WITH_EVIDENCE"
        q["evidence_reasons"] = ["grok_figure_vision"]
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok_figure"
        fixed += 1
        gnum = q.get("global_question_number")
        ot = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        md = classify_modality(str(q.get("question_text_full", "")), ot)
        rr = review_reasons_for_question(modality=md.label, evidence_status="PASS_WITH_EVIDENCE",
            chosen_missing=gnum in ci, option_issue=gnum in oi, low_confidence=gnum in lc,
            has_page_asset=True, has_visual_asset=True, has_question_crop=True)
        q["canonical_review_reasons"] = list(rr)
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    print(f"{pdf_name}: +{fixed} -> PR={pr}/{len(data.get('questions',[]))}")
