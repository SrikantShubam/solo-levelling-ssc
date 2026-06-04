"""
Category A: Process response sheets and coaching PDFs via Grok.
Generates prompts for Grok subagents and provides merge functionality.
"""
import json, sys, os
from pathlib import Path

sys.path.insert(0, "src")
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

def generate_grok_prompt(pdf_name, pages_with_qnums):
    lines = [
        f"You are processing PDF: {pdf_name}",
        f"You need to read {len(pages_with_qnums)} page images and extract the correct option label for each question.",
        "",
        "For EACH page image, read it and determine:",
        "1. Which questions are on that page",
        "2. Which option (1/2/3/4) has the GREEN tick mark (this is the correct answer)",
        "3. Which option has the CHOSEN/response-sheet mark (if visible)",
        "",
        'Return a JSON object with this structure:',
        '{',
        '  "pages": [',
        '    {',
        '      "page": INTEGER,',
        '      "questions": [',
        '        {',
        '          "question_number": INTEGER,',
        '          "correct_option_label": "1"|"2"|"3"|"4"|null,',
        '          "chosen_option_label": "1"|"2"|"3"|"4"|null,',
        '          "confidence": "high"|"medium"|"low"',
        '        }',
        '      ]',
        '    }',
        '  ]',
        '}',
        "",
        "CRITICAL: Each question must have correct_option_label set to the GREEN-ticked option.",
        "Rules:",
        "- Correct option is the GREEN tick/check-marked option",
        "- Red cross is NOT correct",
        "- Chosen Option is the response-sheet field (may not exist on all pages)",
        "- Return ONLY the raw JSON object",
        "- Read ALL images listed below. Do not skip any.",
        "",
        "Page images to process:",
    ]
    for page, qnums in sorted(pages_with_qnums.items()):
        image_path = f"C:\\experiments\\ssc\\pipeline_output\\p2_gemini\\{pdf_name}\\page_images\\page_{page:02d}.png"
        qlist = ",".join(str(q) for q in qnums)
        lines.append(f"- Page {page:02d} (questions {qlist}): {image_path}")
    return "\n".join(lines)

def merge_grok_into_pdf(pdf_name, grok_page_data):
    """Merge Grok subagent output into a PDF's merged JSON.
    
    grok_page_data: dict mapping page_number -> list of {question_number, correct_option_label, chosen_option_label, confidence}
    """
    merged_path = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    
    option_issue_set = set(data.get("option_or_correct_answer_issue_global_questions", []))
    chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(data.get("low_confidence_global_questions", []))
    
    correct_fixed = 0
    chosen_fixed = 0
    
    for q in data.get("questions", []):
        page = q.get("source_page")
        qnum = q.get("question_number")
        if page not in grok_page_data:
            continue
        grok_qs = grok_page_data[page]
        grok_q = None
        for gq in grok_qs:
            if gq.get("question_number") == qnum:
                grok_q = gq
                break
        if not grok_q:
            continue
        
        existing = q.get("canonical_correct_option_label")
        new_correct = grok_q.get("correct_option_label")
        new_chosen = grok_q.get("chosen_option_label")
        
        if not existing and new_correct and new_correct in {"1", "2", "3", "4"}:
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
        
        existing_chosen = q.get("chosen_option_label")
        if (not existing_chosen or str(existing_chosen).strip() not in {"1", "2", "3", "4"}) and new_chosen and new_chosen in {"1", "2", "3", "4"}:
            q["chosen_option_label"] = new_chosen
            q["ai_reviewed"] = True
            q["ai_review_source"] = "grok"
            chosen_fixed += 1
        
        # Recompute canonical review reasons
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
    
    # Recompute practice_ready for ALL questions
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    
    merged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    return {"correct_fixed": correct_fixed, "chosen_fixed": chosen_fixed, "practice_ready": pr, "total": len(data.get("questions", []))}

def parse_grok_output(raw_text):
    """Parse Grok subagent output JSON from text that may contain handoff blocks."""
    import re
    text = raw_text
    # Strip handoff markers
    for marker in ["---SUBAGENT-HANDOFF---", "---END-HANDOFF---"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None

def scan_pdf(pdf_name):
    """Find all pages with missing correct labels in a PDF."""
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(mp.read_text(encoding="utf-8"))
    pages = {}
    for q in data.get("questions", []):
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            image = mp.parent / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                pages.setdefault(page, []).append(q.get("question_number"))
    return pages

def pdf_report(pdf_name):
    """Get current status for a PDF."""
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(mp.read_text(encoding="utf-8"))
    total = len(data.get("questions", []))
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    mc = sum(1 for q in data.get("questions", []) if not q.get("canonical_correct_option_label"))
    return {"total": total, "practice_ready": pr, "missing_correct": mc}


if __name__ == "__main__":
    # Generate prompts for all PDFs needing processing
    pdfs_to_process = [
        # Response sheets (green ticks visible)
        "2024_tier2_sscportal_jan18_response_sheet",
        "2024_tier2_sscportal_jan19_response_sheet",
        "2024_tier2_sscportal_jan20_response_sheet",
        "2024_tier1_sscportal_sep09_shift1_response_sheet",
        # Coaching PDFs that need green tick review
        "2019_tier1_prepp_shift1",
        "2019_tier2_prepp_english",
        "2019_tier2_prepp_quant",
        "2021_tier1_sscportal_shift1_response_sheet",
        "2021_tier2_prepp_english",
        "2022_tier1_prepp_shift1",
        "2022_tier2_prepp_paper1",
        "2023_tier1_prepp_shift1",
        "2023_tier2_prepp_paper1",
    ]
    
    print("PDF status and prompt info:")
    print("=" * 80)
    for pdf in pdfs_to_process:
        pages = scan_pdf(pdf)
        report = pdf_report(pdf)
        flag = ""
        if not pages:
            flag = " (DONE - no missing correct labels)"
        print(f"{pdf}: {report['practice_ready']}/{report['total']} PR, {len(pages)} pages with {sum(len(v) for v in pages.values())} missing correct labels{flag}")
