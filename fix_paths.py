import json, os
from pathlib import Path

pipeline_root = Path("pipeline_output/p2_gemini")
fixed_count = 0

for merged_path in sorted(pipeline_root.rglob("merged_questions_global_order.json")):
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    pdf_dir = merged_path.parent
    updated = False
    for q in data.get("questions", []):
        old_page = q.get("page_asset_path")
        if old_page and not os.path.exists(old_page):
            page_num = q.get("source_page") or 0
            new_page = str(pdf_dir / "page_images" / f"page_{int(page_num):02d}.png")
            q["page_asset_path"] = new_page
            updated = True

        old_qcrop = q.get("question_crop_path")
        if old_qcrop and old_qcrop != new_page and not os.path.exists(old_qcrop):
            page_num = q.get("source_page") or 0
            q["question_crop_path"] = str(pdf_dir / "page_images" / f"page_{int(page_num):02d}.png")
            updated = True

        if os.path.exists(q.get("page_asset_path", "")):
            updated = True

    if updated:
        merged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        fixed_count += 1
        print(f"Fixed paths in {pdf_dir.name}")

print(f"\n{len(list(pipeline_root.rglob('merged_questions_global_order.json')))} PDFs checked, {fixed_count} updated")
