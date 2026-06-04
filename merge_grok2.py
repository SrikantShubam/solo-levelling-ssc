import json, sys, os
from pathlib import Path

sys.path.insert(0, "src")

from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

grok_results = {
    2: [{"question_number": 3, "correct_option_label": "3", "chosen_option_label": None}, {"question_number": 4, "correct_option_label": "2", "chosen_option_label": "2"}],
    4: [{"question_number": 9, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 10, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 11, "correct_option_label": "1", "chosen_option_label": "1"}],
    6: [{"question_number": 14, "correct_option_label": "1", "chosen_option_label": None}, {"question_number": 15, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 16, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 17, "correct_option_label": "4", "chosen_option_label": "4"}],
    8: [{"question_number": 21, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 22, "correct_option_label": "4", "chosen_option_label": None}, {"question_number": 23, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 24, "correct_option_label": "3", "chosen_option_label": "3"}],
    9: [{"question_number": 25, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 1, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 2, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 3, "correct_option_label": "1", "chosen_option_label": "4"}, {"question_number": 4, "correct_option_label": "3", "chosen_option_label": "3"}],
    10: [{"question_number": 5, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 6, "correct_option_label": "1", "chosen_option_label": "4"}, {"question_number": 7, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 8, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 9, "correct_option_label": "3", "chosen_option_label": "3"}],
    11: [{"question_number": 10, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 11, "correct_option_label": "2", "chosen_option_label": "4"}, {"question_number": 12, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 13, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 14, "correct_option_label": "3", "chosen_option_label": "3"}],
    12: [{"question_number": 15, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 16, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 17, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 18, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 19, "correct_option_label": "4", "chosen_option_label": "1"}],
    13: [{"question_number": 20, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 21, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 22, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 23, "correct_option_label": "3", "chosen_option_label": None}, {"question_number": 24, "correct_option_label": "2", "chosen_option_label": "2"}],
    14: [{"question_number": 25, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 1, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 2, "correct_option_label": "3", "chosen_option_label": "1"}],
    21: [{"question_number": 25, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 1, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 2, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 3, "correct_option_label": "1", "chosen_option_label": "4"}],
    22: [{"question_number": 4, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 5, "correct_option_label": "1", "chosen_option_label": "3"}, {"question_number": 6, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 7, "correct_option_label": "4", "chosen_option_label": "3"}],
    23: [{"question_number": 8, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 9, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 10, "correct_option_label": "1", "chosen_option_label": "2"}, {"question_number": 11, "correct_option_label": "2", "chosen_option_label": "2"}],
    24: [{"question_number": 12, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 13, "correct_option_label": "4", "chosen_option_label": "2"}, {"question_number": 14, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 15, "correct_option_label": "4", "chosen_option_label": "4"}],
    25: [{"question_number": 16, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 17, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 18, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 19, "correct_option_label": "4", "chosen_option_label": "4"}],
    26: [{"question_number": 20, "correct_option_label": "2", "chosen_option_label": "2"}, {"question_number": 21, "correct_option_label": "4", "chosen_option_label": "4"}, {"question_number": 22, "correct_option_label": "1", "chosen_option_label": "1"}],
    27: [{"question_number": 23, "correct_option_label": "1", "chosen_option_label": "1"}, {"question_number": 24, "correct_option_label": "3", "chosen_option_label": "3"}, {"question_number": 25, "correct_option_label": "1", "chosen_option_label": "1"}],
}

merged_path = Path("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json")
data = json.loads(merged_path.read_text(encoding="utf-8"))

option_issue_set = set(data.get("option_or_correct_answer_issue_global_questions", []))
chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
low_confidence_set = set(data.get("low_confidence_global_questions", []))

correct_fixed = 0
chosen_fixed = 0

for q in data.get("questions", []):
    page = q.get("source_page")
    qnum = q.get("question_number")
    if page not in grok_results:
        continue
    grok_qs = grok_results[page]
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

    if (not q.get("chosen_option_label") or str(q.get("chosen_option_label")).strip() not in {"1", "2", "3", "4"}) and new_chosen and new_chosen in {"1", "2", "3", "4"}:
        q["chosen_option_label"] = new_chosen
        q["ai_reviewed"] = True
        q["ai_review_source"] = "grok"
        chosen_fixed += 1

    # Recompute canonical_review_reasons
    gnum = q.get("global_question_number")
    options = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
    modality = classify_modality(str(q.get("question_text_full", "")), options)
    reasons = review_reasons_for_question(
        modality=modality.label,
        evidence_status=str(q.get("evidence_status", "PASS_WITH_EVIDENCE")),
        chosen_missing=gnum in chosen_issue_set,
        option_issue=gnum in option_issue_set,
        low_confidence=gnum in low_confidence_set,
        has_page_asset=True,
        has_visual_asset=True,
        has_question_crop=True,
    )
    q["canonical_review_reasons"] = list(reasons)

# Recompute question-wide stats
for q in data.get("questions", []):
    q["practice_ready"] = _is_practice_ready(q)
_refresh_qc_status(data)

merged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

practice_ready = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
print(f"Correct labels fixed: {correct_fixed}")
print(f"Chosen labels fixed: {chosen_fixed}")
print(f"Practice-ready now: {practice_ready}")
