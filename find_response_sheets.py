import json
from pathlib import Path
from collections import Counter

pipeline_root = Path("pipeline_output/p2_gemini")

# Focus on response_sheet_green_answer type PDFs
targets = [
    "2024_tier2_sscportal_jan18_response_sheet",
    "2024_tier2_sscportal_jan19_response_sheet",
    "2024_tier2_sscportal_jan20_response_sheet",
    "2024_tier1_sscportal_sep09_shift1_response_sheet",
    "2021_tier1_sscportal_shift1_response_sheet",
]

for pdf_name in targets:
    mp = pipeline_root / pdf_name / "merged_questions_global_order.json"
    if not mp.exists():
        print(f"{pdf_name}: no merged JSON")
        continue
    data = json.loads(mp.read_text(encoding="utf-8"))
    total = len(data.get("questions", []))
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    missing_correct = sum(1 for q in data.get("questions", []) if not q.get("canonical_correct_option_label"))
    
    pages_needed = {}
    for q in data.get("questions", []):
        if not q.get("canonical_correct_option_label"):
            page = q.get("source_page") or 0
            image = pipeline_root / pdf_name / "page_images" / f"page_{page:02d}.png"
            if image.exists():
                pages_needed.setdefault(page, []).append(q.get("question_number"))
    
    print(f"\n{pdf_name}:")
    print(f"  Total: {total}, Practice-ready: {pr}, Missing correct: {missing_correct}")
    print(f"  Pages needing review: {len(pages_needed)}")
    if pages_needed:
        pages_sorted = sorted(pages_needed.items())
        for page, qnums in pages_sorted[:8]:
            print(f"    p{page:02d}: questions {qnums}")
        if len(pages_sorted) > 8:
            print(f"    ... and {len(pages_sorted)-8} more pages")
