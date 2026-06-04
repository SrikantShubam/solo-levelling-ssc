import json
from pathlib import Path

data = json.loads(Path("work_manifest.json").read_text(encoding="utf-8"))

# Get pages needing correct label
pages_needing_correct_label = {}
for merged_path in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    pdf_name = merged_path.parent.name
    mdata = json.loads(merged_path.read_text(encoding="utf-8"))
    for q in mdata.get("questions", []):
        if q.get("practice_ready", True):
            continue
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            image = merged_path.parent / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                key = f"{pdf_name}/p{page:02d}"
                if key not in pages_needing_correct_label:
                    pages_needing_correct_label[key] = {
                        "pdf_name": pdf_name,
                        "page_number": page,
                        "merged_path": str(merged_path),
                        "page_image_path": str(image),
                    }

pages = list(pages_needing_correct_label.values())

# Generate batch files
batch_size = 4
batches = []
for i in range(0, len(pages), batch_size):
    batch = pages[i:i+batch_size]
    batch_num = i // batch_size
    path = Path(f"grok_batches/batch_{batch_num:04d}.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"batch": batch_num, "pages": batch}, indent=2), encoding="utf-8")
    batches.append(path)
    names = []
    for p in batch:
        parts = p["page_image_path"].replace("\\", "/").split("/")
        pdf_name = parts[-3] if len(parts) >= 3 else "?"
        names.append(f"{pdf_name}/p{p['page_number']:02d}")
    print(f"batch_{batch_num:04d}: {len(batch)} pages - {' '.join(names)}")

print(f"\nTotal: {len(batches)} batches, {len(pages)} pages")
