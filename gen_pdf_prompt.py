import json
from pathlib import Path

def gen_prompt(pdf_name):
    merged_path = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    if not merged_path.exists():
        return None, None
    
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    
    pages_needed = {}
    for q in data.get("questions", []):
        if q.get("practice_ready", True):
            continue
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            image = merged_path.parent / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                pages_needed.setdefault(page, []).append(q.get("question_number"))
    
    if not pages_needed:
        return None, None
    
    pages_sorted = sorted(pages_needed.items())
    
    lines = [
        f"You are processing PDF: {pdf_name}",
        f"You need to read {len(pages_sorted)} page images and extract the correct option label for each question.",
        "",
        "For EACH page image, read it and determine:",
        "1. Which questions are on that page",
        "2. Which option (1/2/3/4) has the GREEN tick mark (this is the correct answer)",
        "3. Which option has the CHOSEN/response-sheet mark (if visible)",
        "",
        "Return a JSON object with this structure:",
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
        "",
        "Page images to process:",
    ]
    
    for page, qnums in pages_sorted:
        image_path = merged_path.parent / "page_images" / f"page_{page:02d}.png"
        qnums_str = ",".join(str(q) for q in qnums)
        lines.append(f"- Page {page:02d} (questions {qnums_str}): {image_path}")
    
    return "\n".join(lines), {
        "pdf_name": pdf_name,
        "pages": [p for p, _ in pages_sorted],
        "question_count": sum(len(qns) for _, qns in pages_sorted),
    }

# Generate for first PDF
prompt, meta = gen_prompt("2020_tier1_prepp_shift1")
if prompt:
    print(f"Prompt for {meta['pdf_name']}:")
    print(f"  Pages: {len(meta['pages'])}")
    print(f"  Questions: {meta['question_count']}")
    print()
    print(prompt[:1000])
    print("...")
    Path("grok_batches/pdf_prompt.txt").write_text(prompt, encoding="utf-8")
    Path("grok_batches/pdf_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
