import json
from pathlib import Path

pages_needing_correct_label = {}
pages_grok_processed = {}

for merged_path in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    pdf_name = merged_path.parent.name
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready", True):
            continue
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            key = f"{pdf_name}/p{page:02d}"
            image = merged_path.parent / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                qnum = q.get("global_question_number") or q.get("question_number")
                if key not in pages_needing_correct_label:
                    pages_needing_correct_label[key] = {
                        "pdf_name": pdf_name,
                        "page_number": page,
                        "pdf_dir": str(merged_path.parent),
                        "merged_path": str(merged_path),
                        "page_image_path": str(image),
                        "question_numbers": [],
                    }
                pages_needing_correct_label[key]["question_numbers"].append(qnum)

print(f"Unique pages needing correct label: {len(pages_needing_correct_label)}")
page_list = sorted(pages_needing_correct_label.keys(), key=lambda k: (-pages_needing_correct_label[k]["pdf_name"], k))
for key in page_list[:10]:
    info = pages_needing_correct_label[key]
    print(f"  {key}: {len(info['question_numbers'])} questions needing correct label")
