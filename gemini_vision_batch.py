"""
Process remaining non-practice-ready questions using Gemini vision.
Uses google-genai SDK (not deprecated generativeai) with gemini-3.1-flash-lite.
Sends page images 10 at a time with retry and quota handling.
"""
import io
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "src")

from ssc_corpus.extraction import _refresh_qc_status
from google import genai
from google.genai import types

OUTPUT_DIR = Path("pipeline_output/p2_gemini")
BATCH_SIZE = 10
MODEL_NAME = "models/gemini-3.1-flash-lite"


def load_api_key():
    env_text = Path(".env").read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env_text)
    if not match:
        raise ValueError("No API key found in .env")
    return match.group(1).strip()


def get_remaining_questions():
    """Collect all non-practice-ready questions with their page images."""
    remaining = []
    for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
        data = json.loads(mp.read_text(encoding="utf-8"))
        pdf_name = mp.parent.name
        for q in data.get("questions", []):
            if q.get("practice_ready"):
                continue
            page = q.get("source_page") or 0
            page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
            if not page_img.exists():
                continue
            remaining.append({
                "pdf_name": pdf_name,
                "merged_path": str(mp),
                "page": page,
                "page_img": str(page_img),
                "question_number": q.get("question_number"),
                "global_question_number": q.get("global_question_number"),
                "question_text": q.get("question_text_full", ""),
                "options": q.get("options", []),
                "modality": q.get("question_modality", ""),
            })
    return remaining


def build_page_prompt(questions_on_page):
    """Build a prompt for Gemini to identify correct answers for specific questions on a page."""
    lines = [
        "Look at this SSC exam page image. For each question listed below, determine the correct answer.",
        "If the page shows green tick marks or answer indicators, use those as evidence.",
        "If a question involves a figure, chart, table, diagram, or dice, analyze the visual to determine the answer.",
        "Return STRICT JSON only. No markdown fences. Schema:",
        '{"answers":[{"question_number":<int>,"correct_option_label":"1"|"2"|"3"|"4","reasoning":"<brief>"}]}',
        "",
        "Questions to answer on this page:",
    ]
    for q in questions_on_page:
        opts = ""
        for o in q["options"]:
            if isinstance(o, dict):
                label = o.get("label", "?")
                text = str(o.get("text", ""))[:200]
                opts += f"  ({label}) {text}\n"
        lines.append(f"Q{q['question_number']} [{q.get('modality','')}]")
        qtext = str(q.get("question_text", ""))[:500]
        lines.append(f"  Text: {qtext}")
        lines.append(f"  Options:\n{opts}")
    lines.append("")
    return "\n".join(lines)


def parse_response_text(text):
    """Robust JSON parsing of model response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Remove control characters that break JSON
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # Trim trailing noise after closing brace
    brace_idx = text.rfind("}")
    if brace_idx != -1:
        text = text[:brace_idx + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[^{}]*"answers"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def call_gemini_vision(client, page_img_path, prompt):
    """Call Gemini with an inline image using google-genai SDK."""
    image_bytes = Path(page_img_path).read_bytes()

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                ],
                config=types.GenerateContentConfig(temperature=0),
            )
            break
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                # Extract retry delay or default to exponential backoff
                delay = 2 ** attempt * 5
                retry_match = re.search(r'retryDelay["\']?\s*:\s*["\']?(\d+)s', err_str)
                if retry_match:
                    delay = max(delay, int(retry_match.group(1)) + 2)
                print(f"(quota limit, waiting {delay}s)...", end=" ", flush=True)
                time.sleep(delay)
                if attempt == 2:
                    raise
            elif attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise

    text = response.text or ""
    return parse_response_text(text)


def apply_answers(merged_path_str, page, answers):
    """Apply Gemini-determined answers to the merged JSON."""
    mp = Path(merged_path_str)
    data = json.loads(mp.read_text(encoding="utf-8"))
    changed = 0
    for q in data.get("questions", []):
        q_page = q.get("source_page") or 0
        q_num = q.get("question_number")
        if q_page != page:
            continue
        for ans in answers:
            if ans.get("question_number") == q_num:
                label = str(ans.get("correct_option_label", ""))
                if label in ("1", "2", "3", "4"):
                    q["canonical_correct_option_label"] = label
                    q["correct_evidence_source"] = "gemini_vision_review"
                    q["ai_reviewed"] = True
                    q["ai_review_source"] = MODEL_NAME
                    reasons = q.get("canonical_review_reasons") or []
                    q["canonical_review_reasons"] = [
                        r for r in reasons
                        if r not in ("correct_option_unresolved_or_conflict", "missing_correct_option_label")
                    ]
                    changed += 1
                break

    if changed:
        _refresh_qc_status(data)
        for q in data.get("questions", []):
            if not q.get("blocking_review_reasons") and q.get("canonical_correct_option_label"):
                q["practice_ready"] = True
        mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
        pdf_name = mp.parent.name
        print(f"  -> {pdf_name}: applied {changed} answers, now {pr}/{len(data.get('questions',[]))} practice-ready")
    return changed


def main():
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    remaining = get_remaining_questions()
    print(f"Found {len(remaining)} remaining questions across all PDFs")

    # Group by (pdf_name, page, merged_path)
    by_page = defaultdict(list)
    for q in remaining:
        key = (q["pdf_name"], q["page"], q["merged_path"])
        by_page[key].append(q)

    pages = list(by_page.items())
    print(f"Across {len(pages)} unique pages")
    total_batches = (len(pages) + BATCH_SIZE - 1) // BATCH_SIZE

    total_applied = 0
    errors = []

    for batch_start in range(0, len(pages), BATCH_SIZE):
        batch = pages[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        print(f"\n--- Batch {batch_num}/{total_batches} ({len(batch)} pages) ---")

        for (pdf_name, page, merged_path), questions in batch:
            page_img = questions[0]["page_img"]
            q_nums = [q["question_number"] for q in questions]
            print(f"  {pdf_name}/p{page:02d} Q{q_nums} ({len(questions)} q)...", end=" ", flush=True)

            try:
                prompt = build_page_prompt(questions)
                result = call_gemini_vision(client, page_img, prompt)
                answers = result.get("answers", [])
                changed = apply_answers(merged_path, page, answers)
                total_applied += changed
                print(f"OK ({changed} applied)")
                time.sleep(1.0)
            except Exception as e:
                print(f"ERROR: {type(e).__name__}: {e}")
                errors.append({
                    "pdf_name": pdf_name,
                    "page": page,
                    "question_numbers": q_nums,
                    "error": str(e)[:300],
                })

    print(f"\n{'='*60}")
    print(f"DONE: Applied {total_applied} answers total")
    print(f"Model: {MODEL_NAME}")
    if errors:
        print(f"Errors: {len(errors)} pages failed")
        err_path = Path("gemini_vision_errors.json")
        err_path.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Error details saved to {err_path}")


if __name__ == "__main__":
    main()
