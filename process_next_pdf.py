import json
from pathlib import Path

# Find which PDFs still need processing
pipeline_root = Path("pipeline_output/p2_gemini")
results = []
for d in sorted(pipeline_root.iterdir()):
    if not d.is_dir():
        continue
    mp = d / "merged_questions_global_order.json"
    if not mp.exists():
        continue
    data = json.loads(mp.read_text(encoding="utf-8"))
    total = len(data.get("questions", []))
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    missing_correct = sum(1 for q in data.get("questions", []) if not q.get("canonical_correct_option_label"))
    
    if missing_correct > 0:
        pages_needed = {}
        for q in data.get("questions", []):
            if not q.get("canonical_correct_option_label"):
                page = q.get("source_page") or 0
                image = d / "page_images" / f"page_{page:02d}.png"
                if image.exists():
                    pages_needed.setdefault(page, []).append(q.get("question_number"))
        
        results.append({
            "pdf_name": d.name,
            "total": total,
            "practice_ready": pr,
            "missing_correct": missing_correct,
            "pages": len(pages_needed),
            "page_details": pages_needed,
        })

# Sort by most missing correct labels
results.sort(key=lambda r: -r["missing_correct"])

print("PDFs needing Grok review (sorted by most missing):")
for r in results[:10]:
    print(f"  {r['pdf_name']}: {r['missing_correct']} missing correct, {r['pages']} pages, practice_ready={r['practice_ready']}/{r['total']}")

if results:
    next_pdf = results[0]
    print(f"\nNext to process: {next_pdf['pdf_name']}")
    print(f"  Pages: {sorted(next_pdf['page_details'].keys())}")
