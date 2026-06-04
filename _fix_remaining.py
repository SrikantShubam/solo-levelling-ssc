"""
Fix the last 12 remaining non-practice-ready questions:
  1. The 1 stuck low_confidence (filtered wrong)
  2. The 11 qnum=None that couldn't be matched by Gemini
"""
import io, json, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, "src")

from ssc_corpus.extraction import _refresh_qc_status

OUTPUT_DIR = Path("pipeline_output/p2_gemini")
SOFT_FLAGS = {"low_confidence", "math_parse_lossy", "malformed_options"}

fixed = 0
for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf = mp.parent.name
    changed = False

    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue

        has_label = bool(q.get("canonical_correct_option_label"))
        blocking = q.get("blocking_review_reasons") or []

        # Case 1: Has a label and only soft flags — promote
        if has_label and all(r in SOFT_FLAGS for r in blocking):
            q["canonical_review_reasons"] = [
                r for r in (q.get("canonical_review_reasons") or [])
                if r not in SOFT_FLAGS
            ]
            fixed += 1
            changed = True

        # Case 2: qnum=None (couldn't match Gemini response) —
        # check if Gemini actually returned an answer for it
        # (These need the answer applied from the Gemini response)
        # For now, skip — need manual or secondary pass

    if changed:
        _refresh_qc_status(data)
        for q in data.get("questions", []):
            if not q.get("practice_ready"):
                if not q.get("blocking_review_reasons") and q.get("canonical_correct_option_label"):
                    q["practice_ready"] = True
                    fixed += 1
        mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Fixed: {fixed}")

# Now for the qnum=None ones — re-run Gemini focusing on just those pages
# Collect them
orphans = []
for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf = mp.parent.name
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        # Remaining are all qnum=None with correct_option_unresolved_or_conflict
        page = q.get("source_page") or 0
        page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
        if not page_img.exists():
            continue
        orphans.append({
            "pdf": pdf,
            "merged_path": str(mp),
            "page": page,
            "page_img": str(page_img),
            "text": q.get("question_text_full", ""),
            "options": q.get("options", []),
            "modality": q.get("question_modality", ""),
        })

print(f"\nOrphan questions (qnum=None, need targeted Gemini pass): {len(orphans)}")
for o in orphans:
    print(f"  {o['pdf']} p{o['page']:02d} mod={o['modality']} text={o['text'][:120]}...")

# Write orphans to JSON for a targeted pass
Path("orphan_questions.json").write_text(
    json.dumps(orphans, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("\nSaved to orphan_questions.json")
