import json
from pathlib import Path

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

# Find pages missing correct labels for 2024_tier2_prepp_paper1
pipeline_root = Path("pipeline_output/p2_gemini")
mp = pipeline_root / "2024_tier2_prepp_paper1" / "merged_questions_global_order.json"
data = json.loads(mp.read_text(encoding="utf-8"))

pages_needed = {}
for q in data.get("questions", []):
    if not q.get("canonical_correct_option_label"):
        page = q.get("source_page") or 0
        image = pipeline_root / "2024_tier2_prepp_paper1" / "page_images" / f"page_{page:02d}.png"
        if image.exists():
            pages_needed.setdefault(page, []).append(q.get("question_number"))

# Split into batches of ~15 pages
page_list = sorted(pages_needed.items())
batch_size = 15
batches = []
for i in range(0, len(page_list), batch_size):
    batch_pages = dict(page_list[i:i+batch_size])
    batches.append(batch_pages)
    prompt = generate_grok_prompt("2024_tier2_prepp_paper1", batch_pages)
    output_path = Path(f"grok_batches/2024_tier2_prepp_paper1_batch_{i//batch_size}.txt")
    output_path.write_text(prompt, encoding="utf-8")
    total_qs = sum(len(qns) for qns in batch_pages.values())
    print(f"Batch {i//batch_size}: {len(batch_pages)} pages, {total_qs} questions -> {output_path}")

print(f"\nTotal batches: {len(batches)}")
print(f"Total pages: {len(page_list)}")
print(f"Total questions: {sum(len(qns) for _, qns in page_list)}")

# Save metadata
meta = {"pdf_name": "2024_tier2_prepp_paper1", "batches": []}
for i, batch_pages in enumerate(batches):
    meta["batches"].append({
        "batch_num": i,
        "pages": list(batch_pages.keys()),
        "question_count": sum(len(qns) for qns in batch_pages.values()),
    })
Path("grok_batches/2024_tier2_prepp_paper1_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
