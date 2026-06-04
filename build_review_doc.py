"""
Build a unified human-review document from remaining non-practice-ready questions.
Creates:
  1. review_doc.html  — all 48 questions with embedded images, yes/no radio, correction field
  2. review_doc.md    — markdown version (images linked, Y/N blanks)
"""
import io, json, sys, base64
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = Path("pipeline_output/p2_gemini")

# Collect all remaining questions
questions = []
for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf_name = mp.parent.name
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        page = q.get("source_page") or 0
        page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
        questions.append({
            "pdf": pdf_name,
            "page": page,
            "qnum": q.get("question_number"),
            "global_q": q.get("global_question_number"),
            "section": q.get("section", ""),
            "modality": q.get("question_modality", ""),
            "text": q.get("question_text_full", ""),
            "options": [(o.get("label","?"), o.get("text","")) for o in q.get("options", []) if isinstance(o, dict)],
            "current_label": q.get("canonical_correct_option_label", ""),
            "blocking": q.get("blocking_review_reasons") or [],
            "evidence": q.get("correct_evidence_source", ""),
            "page_img_path": str(page_img) if page_img.exists() else None,
        })

print(f"Found {len(questions)} remaining questions")

# Build HTML
html_parts = ["""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SSC Corpus — Human Review</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
  h1 { color: #1a1a1a; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
  .summary { background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .question { background: #fff; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); page-break-inside: avoid; }
  .question h3 { margin-top: 0; color: #2563eb; }
  .meta { color: #666; font-size: 0.85em; margin-bottom: 10px; }
  .meta span { background: #e5e7eb; padding: 2px 8px; border-radius: 4px; margin-right: 6px; }
  .qtext { font-size: 1.05em; margin: 12px 0; line-height: 1.5; }
  .options { margin: 10px 0; }
  .option { padding: 4px 0; }
  .option .label { font-weight: bold; margin-right: 8px; color: #2563eb; }
  .page-img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin: 12px 0; }
  .review-row { display: flex; gap: 20px; align-items: center; margin: 15px 0; padding: 12px; background: #f0fdf4; border-radius: 6px; border: 1px solid #bbf7d0; }
  .review-row label { font-weight: 600; margin-right: 8px; }
  .review-row input[type="radio"] { margin-right: 4px; }
  .review-row .radio-group { display: flex; gap: 15px; }
  .correction { margin: 10px 0; }
  .correction label { font-weight: 600; display: block; margin-bottom: 4px; }
  .correction input { width: 60px; padding: 6px; font-size: 1em; border: 1px solid #d1d5db; border-radius: 4px; }
  .current { font-size: 0.85em; color: #6b7280; margin-left: 12px; }
  .pdf-header { background: #2563eb; color: white; padding: 10px 15px; border-radius: 6px; margin: 30px 0 15px 0; }
  @media print { body { background: white; } .question { box-shadow: none; border: 1px solid #ddd; } }
</style>
</head>
<body>
<h1>SSC Corpus — Human Review (48 Questions)</h1>
<div class="summary">
  <strong>Instructions:</strong> For each question, check <strong>Yes</strong> if the current answer is correct, or <strong>No</strong> and write the correct option number (1/2/3/4).
  The page image shows the original exam page with answer markings where available.
</div>
"""]

current_pdf = None
for i, q in enumerate(questions, 1):
    if q["pdf"] != current_pdf:
        current_pdf = q["pdf"]
        html_parts.append(f'<div class="pdf-header"><h2>{current_pdf}</h2></div>')

    # Encode image as base64 for self-contained HTML
    img_tag = ""
    if q["page_img_path"]:
        img_bytes = Path(q["page_img_path"]).read_bytes()
        img_b64 = base64.b64encode(img_bytes).decode("ascii")
        img_tag = f'<img class="page-img" src="data:image/png;base64,{img_b64}" alt="Page {q["page"]}">'

    options_html = '<div class="options">'
    for label, text in q["options"]:
        options_html += f'<div class="option"><span class="label">({label})</span> {text}</div>'
    options_html += '</div>'

    modality_tags = f'<span>{q["modality"]}</span>'
    if q["blocking"]:
        for b in q["blocking"]:
            modality_tags += f'<span style="background:#fef2f2;color:#dc2626">{b}</span>'

    current_info = f'<span class="current">Current: option {q["current_label"]} (via {q["evidence"]})</span>' if q["current_label"] else ""

    html_parts.append(f"""
<div class="question">
  <h3>#{i} — Q{q["qnum"]} (Global #{q["global_q"]})</h3>
  <div class="meta">{modality_tags} <span>Page {q["page"]}</span> <span>{q["section"]}</span></div>
  <div class="qtext">{q["text"]}</div>
  {options_html}
  {img_tag}
  <div class="review-row">
    <span style="font-weight:600">Correct?</span>
    <div class="radio-group">
      <label><input type="radio" name="q{i}" value="yes"> Yes, option {q["current_label"]} is correct</label>
      <label><input type="radio" name="q{i}" value="no"> No, correct is option:</label>
    </div>
    <input type="text" size="5" placeholder="1-4" style="padding:6px;font-size:1em;border:1px solid #d1d5db;border-radius:4px">
    {current_info}
  </div>
  <div class="correction" style="margin-top:8px">
    <label>Notes:</label>
    <input type="text" style="width:100%;padding:6px;font-size:0.95em;border:1px solid #d1d5db;border-radius:4px" placeholder="Optional note...">
  </div>
</div>
""")

html_parts.append("</body></html>")

html_path = Path("review_doc.html")
html_path.write_text("\n".join(html_parts), encoding="utf-8")
print(f"Created: {html_path} ({html_path.stat().st_size / 1024:.0f} KB)")

# Build Markdown version
md_parts = [
    "# SSC Corpus — Human Review (48 Questions)",
    "",
    "**Instructions:** For each question, mark `[Y]` if correct or `[N]` and write the correct option (1/2/3/4).",
    "",
]

current_pdf = None
for i, q in enumerate(questions, 1):
    if q["pdf"] != current_pdf:
        current_pdf = q["pdf"]
        md_parts.append(f"## {current_pdf}")
        md_parts.append("")

    img_line = f"![Page {q['page']}]({q['page_img_path']})" if q["page_img_path"] else "*(no image)*"
    current_info = f" (current: option {q['current_label']} via {q['evidence']})" if q['current_label'] else ""

    md_parts.append(f"### #{i} — Q{q['qnum']} (Global #{q['global_q']}) — Page {q['page']}")
    md_parts.append(f"**Modality:** {q['modality']} | **Section:** {q['section']} | **Blocking:** {', '.join(q['blocking']) or 'none'}")
    md_parts.append("")
    md_parts.append(f"> {q['text']}")
    md_parts.append("")
    for label, text in q["options"]:
        md_parts.append(f"- ({label}) {text}")
    md_parts.append("")
    md_parts.append(img_line)
    md_parts.append("")
    md_parts.append(f"- [ ] **YES** — option {q['current_label']} is correct{current_info}")
    md_parts.append(f"- [ ] **NO** — correct option is: ___ ")
    md_parts.append(f"  - Notes: ___ ")
    md_parts.append("")
    md_parts.append("---")
    md_parts.append("")

md_path = Path("review_doc.md")
md_path.write_text("\n".join(md_parts), encoding="utf-8")
print(f"Created: {md_path} ({md_path.stat().st_size / 1024:.0f} KB)")

# Also create a simple one-page-per-PDF text summary
txt_parts = []
current_pdf = None
for i, q in enumerate(questions, 1):
    if q["pdf"] != current_pdf:
        current_pdf = q["pdf"]
        txt_parts.append(f"\n{'='*70}")
        txt_parts.append(f"  {current_pdf}")
        txt_parts.append(f"{'='*70}\n")

    txt_parts.append(f"#{i} | Q{q['qnum']} (Global #{q['global_q']}) | Page {q['page']} | {q['modality']}")
    txt_parts.append(f"Blocking: {', '.join(q['blocking']) or 'none'}")
    txt_parts.append(f"Current: option {q['current_label']} (via {q['evidence']})" if q['current_label'] else "Current: NONE")
    txt_parts.append(f"Q: {q['text'][:400]}")
    for label, text in q["options"]:
        txt_parts.append(f"  ({label}) {text[:200]}")
    txt_parts.append(f"  [ ] YES - correct as-is    [ ] NO - correct option: ___")
    txt_parts.append("")

txt_path = Path("review_doc.txt")
txt_path.write_text("\n".join(txt_parts), encoding="utf-8")
print(f"Created: {txt_path} ({txt_path.stat().st_size / 1024:.0f} KB)")
print("\nDone. Open review_doc.html in a browser, or print review_doc.txt.")
