"""Find pages with figure-based questions that need Grok vision."""
import json
from pathlib import Path

figure_pages = {}
text_unresolved = {}

for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf_name = mp.parent.name
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        page = q.get("source_page") or 0
        image = mp.parent / "page_images" / f"page_{page:02d}.png"
        modality = q.get("question_modality", "")
        visual = modality in {"visual_options", "visual_stimulus", "table_di", "graph_chart", "dice"}
        has_text = bool(q.get("question_text_full", "").strip())
        key = f"{pdf_name}/p{page:02d}"
        
        if visual and image.exists():
            figure_pages.setdefault(key, {"pdf_name": pdf_name, "page": page, "image": str(image), "qnums": []})
            figure_pages[key]["qnums"].append(q.get("question_number"))
        elif has_text and image.exists():
            text_unresolved.setdefault(key, {"pdf_name": pdf_name, "page": page, "image": str(image), "qnums": []})
            text_unresolved[key]["qnums"].append(q.get("question_number"))

print(f"Figure-based pages: {len(figure_pages)} pages, {sum(len(v['qnums']) for v in figure_pages.values())} questions")
print(f"Text-unresolved pages: {len(text_unresolved)} pages, {sum(len(v['qnums']) for v in text_unresolved.values())} questions")
print()
print("Figure pages:")
for k, v in sorted(figure_pages.items()):
    print(f"  {k}: Q{v['qnums']}")

# Generate a prompt for a single batch of figure pages
batch = list(figure_pages.values())[:5]  # First 5
if batch:
    prompt_lines = ["You are processing figure-based SSC CGL questions.",
        "Read EACH page image. For each question on the page, determine which option (1/2/3/4) is CORRECT.",
        "Look carefully at the figures, diagrams, dice, paper folds, etc.",
        "Return JSON: {\"pages\":[{\"page\":INTEGER,\"questions\":[{\"question_number\":INTEGER,\"correct_option_label\":\"1\"|\"2\"|\"3\"|\"4\"}]}]}",
        "Return ONLY raw JSON.",
        "Pages to process:"]
    for p in batch:
        prompt_lines.append(f"- Page {p['page']:02d} (questions {p['qnums']}): {p['image']}")
    print()
    print("Sample prompt for first 5:")
    print("\n".join(prompt_lines))
