"""
Targeted Gemini pass for orphan questions (qnum=None).
Matches by page position instead of question_number.
"""
import io, json, re, sys, time
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, "src")

from ssc_corpus.extraction import _refresh_qc_status
from google import genai
from google.genai import types
from PIL import Image

OUTPUT_DIR = Path("pipeline_output/p2_gemini")
MODEL_NAME = "models/gemini-3.1-flash-lite"

def load_api_key():
    env_text = Path(".env").read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env_text)
    return match.group(1).strip()

def resize_image(img_path):
    img = Image.open(img_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    ratio = 768 / max(w, h)
    if ratio < 1.0:
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70, optimize=True)
    return buf.getvalue()

def build_orphan_prompt(orphans_on_page):
    lines = [
        "Look at this SSC exam page image. The page may have green tick marks or answer indicators.",
        "For each question described below, find the correct answer option (1/2/3/4).",
        "Return STRICT JSON only — no markdown:",
        '{"answers":[{"index":<int starting at 0>,"correct_option_label":"1"|"2"|"3"|"4","reasoning":"<brief>"}]}',
        "",
    ]
    for idx, q in enumerate(orphans_on_page):
        opts_str = ""
        for o in q["options"]:
            if isinstance(o, dict):
                opts_str += f"({o['label']}) {o.get('text','')[:150]}\n"
        qtext = q.get("question_text_full", "") or q.get("text", "")
        lines.append(f"Question index={idx}: {qtext[:500]}")
        lines.append(f"Options:\n{opts_str}")
    return "\n".join(lines)

def call_gemini(client, img_bytes, prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")],
                config=types.GenerateContentConfig(temperature=0),
            )
            break
        except Exception as exc:
            err_str = str(exc)
            if any(s in err_str for s in ("429", "RESOURCE_EXHAUSTED", "quota")):
                delay = 2 ** attempt * 10
                m = re.search(r'retryDelay["\']?\s*:\s*["\']?(\d+)s', err_str)
                if m: delay = max(delay, int(m.group(1)) + 3)
                print(f"(quota {delay}s)...", end=" ", flush=True)
                time.sleep(delay)
                if attempt == 2: raise
            elif attempt < 2:
                time.sleep(3)
            else:
                raise
    text = (response.text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    idx = text.rfind("}")
    if idx != -1: text = text[:idx + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[^{}]*"answers"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
        if match: return json.loads(match.group())
        raise

# Collect orphans grouped by page
orphans_by_page = {}
for mp in sorted(OUTPUT_DIR.rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    pdf = mp.parent.name
    non_pr = [q for q in data.get("questions", []) if not q.get("practice_ready")]
    for q in non_pr:
        page = q.get("source_page") or 0
        page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
        if not page_img.exists():
            continue
        key = (pdf, page, str(mp), str(page_img))
        orphans_by_page.setdefault(key, []).append(q)

print(f"Orphan pages: {len(orphans_by_page)}")
for (pdf, page, mp, img), qs in orphans_by_page.items():
    print(f"  {pdf} p{page:02d}: {len(qs)} orphans")

api_key = load_api_key()
client = genai.Client(api_key=api_key)
applied = 0

for (pdf_name, page, merged_path, img_path), orphans in orphans_by_page.items():
    print(f"\n{pdf_name} p{page:02d} ({len(orphans)} orphans)...", end=" ", flush=True)

    try:
        img_bytes = resize_image(img_path)
        prompt = build_orphan_prompt(orphans)
        result = call_gemini(client, img_bytes, prompt)
        answers = result.get("answers", [])

        # Apply by index within page's orphan list
        mp = Path(merged_path)
        data = json.loads(mp.read_text(encoding="utf-8"))
        changed = 0
        orphan_indices = [
            i for i, q in enumerate(data["questions"])
            if not q.get("practice_ready") and (q.get("source_page") or 0) == page
        ]

        for ans in answers:
            ans_idx = ans.get("index", -1)
            label = str(ans.get("correct_option_label", ""))
            if ans_idx < 0 or ans_idx >= len(orphan_indices) or label not in ("1","2","3","4"):
                continue
            q_idx = orphan_indices[ans_idx]
            q = data["questions"][q_idx]
            q["canonical_correct_option_label"] = label
            q["correct_evidence_source"] = "gemini_vision_review"
            q["ai_reviewed"] = True
            q["ai_review_source"] = MODEL_NAME
            reasons = q.get("canonical_review_reasons") or []
            q["canonical_review_reasons"] = [
                r for r in reasons if r not in ("correct_option_unresolved_or_conflict", "missing_correct_option_label", "low_confidence")
            ]
            changed += 1

        if changed:
            _refresh_qc_status(data)
            for q in data["questions"]:
                if not q.get("practice_ready") and not q.get("blocking_review_reasons") and q.get("canonical_correct_option_label"):
                    q["practice_ready"] = True
            mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            applied += changed

        a_str = ", ".join(f"idx{a.get('index')}={a.get('correct_option_label')}" for a in answers)
        print(f"OK [{a_str}] -> {changed} applied")
        time.sleep(0.8)
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")

# Final count
total = sum(1 for mp in OUTPUT_DIR.rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions",[]))
pr = sum(1 for mp in OUTPUT_DIR.rglob("merged_questions_global_order.json") for q in json.loads(mp.read_text(encoding="utf-8")).get("questions",[]) if q.get("practice_ready"))
print(f"\nApplied {applied} answers")
print(f"Final: {pr}/{total} practice-ready ({pr*100//total}%) — {total-pr} remaining")
