import json
from pathlib import Path

page_counts = {}
for merged_path in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    pdf_name = merged_path.parent.name
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready", True):
            continue
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            image = merged_path.parent / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                key = f"{pdf_name}/p{page:02d}"
                page_counts[key] = page_counts.get(key, 0) + 1

# Sort by count descending
sorted_pages = sorted(page_counts.items(), key=lambda x: -x[1])
print(f"Total high-value pages (need correct label): {len(sorted_pages)}")
print()
print("Top 50 pages by question count:")
for key, count in sorted_pages[:50]:
    print(f"  {key}: {count} questions")
print()
print(f"Top 50 pages cover: {sum(c for _, c in sorted_pages[:50])} of {sum(c for _, c in sorted_pages)} questions")
print(f"Bottom {len(sorted_pages)-50} pages: {sum(c for _, c in sorted_pages[50:])} questions")
