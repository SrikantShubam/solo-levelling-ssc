"""Generate a single massive prompt for grok_reason with ALL remaining figure pages."""
import json
from pathlib import Path

# Find ALL remaining unanswered questions
entries = []
for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    pdf_name = mp.parent.name
    data = json.loads(mp.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        if q.get("canonical_correct_option_label"):
            continue
        page = q.get("source_page") or 0
        image = mp.parent / "page_images" / f"page_{page:02d}.png"
        if not image.exists():
            continue
        qnum = q.get("question_number")
        text = q.get("question_text_full", "")[:200]
        options = {}
        for opt in q.get("options", []):
            if isinstance(opt, dict):
                options[opt.get("label")] = opt.get("text", "")
        entries.append((pdf_name, page, qnum, text, options, str(image)))

print(f"Total remaining unanswered: {len(entries)}")
print()

# Group by PDF for the prompt
by_pdf = {}
for pdf_name, page, qnum, text, options, img in entries:
    by_pdf.setdefault(pdf_name, []).append((page, qnum, text, options, img))

# Build prompt
prompt_parts = [
    "You are an SSC CGL exam expert. I need you to read the following page images and determine the CORRECT answer option (1/2/3/4) for each question.",
    "",
    "For each page image listed below, open the file, look at the questions on that page, and determine which option is marked as correct (GREEN tick mark or answer indicator).",
    "",
    "Return a JSON array with ALL answers like this:",
    '[{"pdf_name": "PDF_NAME", "page": NUMBER, "question_number": NUMBER, "correct_option_label": "1"|"2"|"3"|"4"}, ...]',
    "",
    "IMPORTANT: Return the EXACT JSON array with every single question answered. Do not skip any question. Even if uncertain, give your best answer.",
    "",
    "Here are the pages to process:",
]

for pdf_name, items in sorted(by_pdf.items()):
    prompt_parts.append(f"\n=== PDF: {pdf_name} ===")
    for page, qnum, text, options, img in items:
        opts_str = " | ".join(f"{k}. {v[:80]}" for k, v in sorted(options.items()) if v)
        prompt_parts.append(f"\nPage {page:02d} (Q{qnum}): {img}")
        prompt_parts.append(f"  Question: {text[:150]}")
        prompt_parts.append(f"  Options: {opts_str}")

full_prompt = "\n".join(prompt_parts)
Path("grok_batches/single_massive_prompt.txt").write_text(full_prompt, encoding="utf-8")
print(f"Prompt generated: {len(full_prompt)} chars, {len(entries)} questions")
print(f"\nFirst 200 chars: {full_prompt[:200]}...")
