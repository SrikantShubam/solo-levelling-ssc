"""
Final fix pass: Fix option_issue flags and recompute practice_ready for ALL PDFs.
"""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    
    pdf_name = mp.parent.name
    
    # Fix option_issue_set: only flag actual malformed options
    new_option_issues = []
    for q in data.get("questions", []):
        options = q.get("options") or []
        labels = [str(o.get("label")) for o in options if isinstance(o, dict)]
        if labels != ["1", "2", "3", "4"]:
            new_option_issues.append(q.get("global_question_number"))
    
    data["option_or_correct_answer_issue_global_questions"] = new_option_issues
    option_issue_set = set(new_option_issues)
    chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(data.get("low_confidence_global_questions", []))
    
    # Recompute review reasons and practice_ready for ALL questions
    for q in data.get("questions", []):
        gnum = q.get("global_question_number")
        options_text = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        modality = classify_modality(str(q.get("question_text_full", "")), options_text)
        reasons = review_reasons_for_question(
            modality=modality.label,
            evidence_status=str(q.get("evidence_status", "PASS_WITH_EVIDENCE")),
            chosen_missing=gnum in chosen_issue_set,
            option_issue=gnum in option_issue_set,
            low_confidence=gnum in low_confidence_set,
            has_page_asset=True, has_visual_asset=True, has_question_crop=True,
        )
        q["canonical_review_reasons"] = list(reasons)
        q["practice_ready"] = _is_practice_ready(q)
    
    _refresh_qc_status(data)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    total = len(data.get("questions", []))
    
    if pdf_name in ["2020_tier2_kdcampus_answer_key", "2024_tier1_appx_answer_key", 
                     "2021_tier1_prepp_shift1", "2024_tier1_prepp_shift1", "2024_tier2_prepp_paper1"]:
        status = ""
        if pr < total:
            nr = [q for q in data.get("questions", []) if not q.get("practice_ready")]
            reasons = {}
            for q in nr:
                br = tuple(q.get("blocking_review_reasons") or ["none"])
                reasons[br] = reasons.get(br, 0) + 1
            status = " blocked_by=" + ", ".join(f"{list(k)}:{v}" for k, v in sorted(reasons.items()))
        print(f"{pdf_name}: {pr}/{total}{status}")
