"""Retry the 1 failed page from gemini_vision_batch.py."""
import io, json, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, "src")

from ssc_corpus.extraction import _refresh_qc_status
from google import genai
from google.genai import types

MODEL_NAME = "models/gemini-3.1-flash-lite"

# Load API key
env = Path(".env").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env)
client = genai.Client(api_key=m.group(1).strip())

# Find questions on 2024_tier1_prepp_shift1 page 6
mp = Path("pipeline_output/p2_gemini/2024_tier1_prepp_shift1/merged_questions_global_order.json")
data = json.loads(mp.read_text(encoding="utf-8"))
questions = [q for q in data["questions"] if q.get("source_page") == 6 and not q.get("practice_ready")]
print(f"Found {len(questions)} non-practice-ready questions on page 6")

page_img = mp.parent / "page_images" / "page_06.png"
print(f"Page image: {page_img}, exists={page_img.exists()}")

# Build simple prompt
lines = [
    "Look at this SSC exam page image. For each question listed below, determine the correct answer.",
    "If the page shows green tick marks, use those as evidence.",
    "Return STRICT JSON only. No markdown fences. Schema:",
    '{"answers":[{"question_number":<int>,"correct_option_label":"1"|"2"|"3"|"4","reasoning":"<brief>"}]}',
    "",
    "Questions:",
]
for q in questions:
    lines.append(f"Q{q['question_number']}: {q.get('question_text_full','')[:300]}")
    for o in q.get("options", []):
        if isinstance(o, dict):
            lines.append(f"  ({o['label']}) {o.get('text','')[:200]}")

prompt = "\n".join(lines)
print(f"Prompt preview:\n{prompt[:500]}...")
print()

# Call Gemini
img_bytes = page_img.read_bytes()
response = client.models.generate_content(
    model=MODEL_NAME,
    contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type="image/png")],
    config=types.GenerateContentConfig(temperature=0),
)

text = response.text or ""
text = re.sub(r"^```(?:json)?\s*", "", text.strip())
text = re.sub(r"\s*```$", "", text)
text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
brace_idx = text.rfind("}")
if brace_idx != -1:
    text = text[:brace_idx + 1]

print(f"Raw response: {text[:500]}")

try:
    result = json.loads(text)
except json.JSONDecodeError:
    match = re.search(r'\{[^{}]*"answers"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
    if match:
        result = json.loads(match.group())
    else:
        print("FAILED to parse JSON")
        raise SystemExit(1)

answers = result.get("answers", [])
print(f"Parsed answers: {answers}")

# Apply
changed = 0
for q in data["questions"]:
    if q.get("source_page") != 6:
        continue
    for ans in answers:
        if ans.get("question_number") == q.get("question_number"):
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
    for q in data["questions"]:
        if not q.get("blocking_review_reasons") and q.get("canonical_correct_option_label"):
            q["practice_ready"] = True
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data["questions"] if q.get("practice_ready"))
    print(f"Applied {changed} answers, now {pr}/{len(data['questions'])} practice-ready")
else:
    print("No answers applied")
