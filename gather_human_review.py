"""
Step 3: Gather all remaining non-practice-ready questions into a single folder
for human review. Copies page images and creates text summaries.

Step 4: Generate final precision/recall breakdown.
"""
import io
import json
import shutil
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUTPUT_DIR = Path("pipeline_output/p2_gemini")
REVIEW_DIR = Path("human_review_pending")
REVIEW_DIR.mkdir(exist_ok=True)

# Track evidence sources for precision analysis
evidence_counts = {}
total = 0
practice_ready = 0
remaining_details = []

for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf_name = mp.parent.name
    questions = data.get("questions", [])
    total += len(questions)

    for q in questions:
        # Count evidence sources
        src = q.get("correct_evidence_source", "unknown")
        evidence_counts[src] = evidence_counts.get(src, 0) + 1

        if q.get("practice_ready"):
            practice_ready += 1
        else:
            page = q.get("source_page") or 0
            qnum = q.get("question_number")
            modality = q.get("question_modality", "")
            reasons = q.get("blocking_review_reasons") or []
            has_label = bool(q.get("canonical_correct_option_label"))

            remaining_details.append({
                "pdf": pdf_name,
                "page": page,
                "question_number": qnum,
                "global_question_number": q.get("global_question_number"),
                "modality": modality,
                "has_correct_label": has_label,
                "blocking_reasons": reasons,
                "section": q.get("section", ""),
                "evidence_source": q.get("correct_evidence_source", ""),
            })

            # Copy page image to review folder
            page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
            if page_img.exists():
                dest_name = f"{pdf_name}_p{page:02d}_Q{qnum}.png"
                shutil.copy2(page_img, REVIEW_DIR / dest_name)

            # Write text summary
            txt_name = f"{pdf_name}_p{page:02d}_Q{qnum}.txt"
            txt_path = REVIEW_DIR / txt_name
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"PDF: {pdf_name}\n")
                f.write(f"Page: {page}\n")
                f.write(f"Question Number: {qnum}\n")
                f.write(f"Global Q#: {q.get('global_question_number')}\n")
                f.write(f"Section: {q.get('section', '')}\n")
                f.write(f"Modality: {modality}\n")
                f.write(f"Blocking Reasons: {reasons}\n")
                f.write(f"Has Correct Label: {has_label}\n")
                if has_label:
                    f.write(f"Current Label: {q.get('canonical_correct_option_label')}\n")
                f.write(f"Evidence Source: {q.get('correct_evidence_source', '')}\n")
                f.write(f"\n--- Question Text ---\n")
                f.write(str(q.get("question_text_full", "")))
                f.write(f"\n\n--- Options ---\n")
                for o in q.get("options", []):
                    if isinstance(o, dict):
                        f.write(f"  ({o.get('label','?')}) {o.get('text','')}\n")

print("=" * 72)
print("FINAL CORPUS PRECISION & RECALL BREAKDOWN")
print("=" * 72)
print()
print(f"Total questions extracted:  {total}")
print(f"Practice-ready:            {practice_ready} ({practice_ready/total*100:.1f}%)")
print(f"Still pending:             {total - practice_ready} ({(total-practice_ready)/total*100:.1f}%)")
print()

# Precision analysis
print("EVIDENCE SOURCES (Precision Indicators):")
print("-" * 60)
# Define confidence tiers
high_confidence = {"rgb_hsv_option_crop", "answer_key_extraction"}
medium_confidence = {"grok_ai_review", "grok_reason_vision", "grok_vision_figures",
                      "grok_massive_answer", "grok_figure_batch", "grok_parallel_answer",
                      "grok_ai_generated_answer", "gemini_vision_review"}
low_confidence = {"llm_only", "ambiguous_rgb_hsv_option_crop"}

high_count = sum(v for k, v in evidence_counts.items() if k in high_confidence)
med_count = sum(v for k, v in evidence_counts.items() if k in medium_confidence)
low_count = sum(v for k, v in evidence_counts.items() if k in low_confidence)

print(f"  HIGH confidence (green-tick, answer keys):  {high_count} ({high_count/total*100:.1f}%)")
for k in sorted(high_confidence):
    if k in evidence_counts:
        print(f"    - {k}: {evidence_counts[k]}")
print(f"  MEDIUM confidence (AI review):              {med_count} ({med_count/total*100:.1f}%)")
for k in sorted(medium_confidence):
    if k in evidence_counts:
        print(f"    - {k}: {evidence_counts[k]}")
print(f"  LOW confidence (LLM-only):                  {low_count} ({low_count/total*100:.1f}%)")
for k in sorted(low_confidence):
    if k in evidence_counts:
        print(f"    - {k}: {evidence_counts[k]}")
print()

# Per-PDF breakdown
print("PER-PDF BREAKDOWN:")
print("-" * 60)
by_pdf = {}
for d in remaining_details:
    by_pdf.setdefault(d["pdf"], []).append(d)

for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    name = mp.parent.name
    t = len(data.get("questions", []))
    p = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    r = t - p
    pct = p/t*100
    bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
    print(f"  {name}")
    print(f"    [{bar}] {p}/{t} ({pct:.1f}%)", end="")
    if r > 0:
        print(f" — {r} remaining")
        # Show reasons for this PDF
        reason_counts = {}
        for d in by_pdf.get(name, []):
            for reason in d["blocking_reasons"]:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            if not d["blocking_reasons"] and not d["has_correct_label"]:
                reason_counts["missing_correct_label"] = reason_counts.get("missing_correct_label", 0) + 1
            if not d["blocking_reasons"] and d["has_correct_label"]:
                reason_counts["stale_flag"] = reason_counts.get("stale_flag", 0) + 1
        for reason, count in sorted(reason_counts.items()):
            print(f"      - {reason}: {count}")
    else:
        print(" ✓")

print()
print(f"Human review files saved to: {REVIEW_DIR}/")
print(f"  {len(list(REVIEW_DIR.glob('*.png')))} page images")
print(f"  {len(list(REVIEW_DIR.glob('*.txt')))} text summaries")

# Write CSV for easy triage
csv_path = REVIEW_DIR / "review_manifest.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("pdf,page,question_number,modality,has_correct_label,blocking_reasons,evidence_source\n")
    for d in sorted(remaining_details, key=lambda x: (x["pdf"], x["page"])):
        f.write(f"{d['pdf']},{d['page']},{d['question_number']},{d['modality']},"
                f"{d['has_correct_label']},{'|'.join(d['blocking_reasons'])},{d['evidence_source']}\n")
print(f"  CSV manifest: {csv_path}")
