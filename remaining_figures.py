"""List all remaining figure-based questions that Grok hasn't answered yet."""
import json
from pathlib import Path

remaining = []
for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf = mp.parent.name
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        modality = q.get("question_modality", "")
        page = q.get("source_page") or 0
        image = mp.parent / "page_images" / f"page_{page:02d}.png"
        is_figure = modality in {"visual_options", "visual_stimulus", "table_di", "graph_chart", "dice"}
        if is_figure and image.exists():
            remaining.append((pdf, page, q.get("question_number"), image))
        elif not q.get("canonical_correct_option_label") and image.exists():
            remaining.append((pdf, page, q.get("question_number"), image))

print(f"Total remaining unanswered: {len(remaining)}")
print()
print("FIGURE-BASED (need vision):")
for pdf, page, qnum, img in remaining:
    mod = ""
    # check modality
    for mp2 in Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json"):
        if pdf in str(mp2):
            data = json.loads(mp2.read_text(encoding="utf-8"))
            for q in data.get("questions", []):
                if q.get("question_number") == qnum and q.get("source_page") == page:
                    mod = q.get("question_modality", "")
                    break
    is_fig = mod in {"visual_options", "visual_stimulus", "table_di", "graph_chart", "dice"}
    tag = "FIGURE" if is_fig else "TEXT"
    print(f"  {tag} {pdf}/p{page:02d} Q{qnum} ({mod})")
