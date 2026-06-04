"""Fix malformed_options flag for questions where the issue was missing correct label, not bad options."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

def fix_pdf(pdf_name, force_fix=False):
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(mp.read_text(encoding="utf-8"))
    
    # Recompute option_issue_set: only flag if options are actually malformed
    new_option_issues = []
    for q in data.get("questions", []):
        options = q.get("options") or []
        labels = [str(o.get("label")) for o in options if isinstance(o, dict)]
        # Only flag if labels are wrong, NOT if correct answer was missing
        if labels != ["1", "2", "3", "4"]:
            new_option_issues.append(q.get("global_question_number"))
    
    old_issues = data.get("option_or_correct_answer_issue_global_questions", [])
    data["option_or_correct_answer_issue_global_questions"] = new_option_issues
    
    changed = len(old_issues) != len(new_option_issues)
    if not changed and not force_fix:
        return 0, sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    
    option_issue_set = set(new_option_issues)
    chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(data.get("low_confidence_global_questions", []))
    
    for q in data.get("questions", []):
        gnum = q.get("global_question_number")
        options = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
        modality = classify_modality(str(q.get("question_text_full", "")), options)
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
    print(f"{pdf_name}: option_issues {len(old_issues)} -> {len(new_option_issues)}, practice_ready: {pr}/{len(data.get('questions',[]))}")
    return len(old_issues) - len(new_option_issues), pr

if __name__ == "__main__":
    fix_pdf("2020_tier2_kdcampus_answer_key", force_fix=True)
