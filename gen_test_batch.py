import json
from pathlib import Path

data = json.loads(Path("work_manifest.json").read_text(encoding="utf-8"))
pages = [p for p in data["pages"] if p["pdf_name"] == "2019_tier1_prepp_shift1"][:6]

tasks = []
for p in pages:
    merged_path = str(Path(p["page_image_path"]).parent.parent / "merged_questions_global_order.json")
    tasks.append({
        "task_id": f'{p["pdf_name"]}/p{p["page_number"]:02d}',
        "pdf_name": p["pdf_name"],
        "page_number": p["page_number"],
        "page_image_path": p["page_image_path"],
        "merged_path": merged_path,
    })

Path("test_batch.json").write_text(json.dumps({"results": tasks}, indent=2), encoding="utf-8")
print(f"Wrote {len(tasks)} tasks to test_batch.json")
for t in tasks:
    print(f"  {t['task_id']}")
