"""Quick test that inline image API works with Gemini."""
import json, re, time, sys, io
from pathlib import Path
import google.generativeai as genai

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load API key
env = Path(".env").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env)
api_key = m.group(1).strip()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

# Find first remaining question
remaining = []
for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        page = q.get("source_page") or 0
        page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
        if page_img.exists():
            remaining.append((mp.parent.name, page, str(page_img), q.get("question_text_full", "")[:200]))
            break
    if remaining:
        break

if remaining:
    name, page, img, text = remaining[0]
    print(f"Test: {name}/p{page:02d}")
    print(f"Image: {img}, exists={Path(img).exists()}, size={Path(img).stat().st_size}")
    text_ascii = text.encode('ascii', errors='replace').decode('ascii')
    print(f"Question: {text_ascii[:100]}...")

    prompt = "Describe what you see on this SSC exam page in 2-3 sentences."
    img_bytes = Path(img).read_bytes()
    print("Calling Gemini with inline image...")
    response = model.generate_content(
        [prompt, {"mime_type": "image/png", "data": img_bytes}],
        generation_config={"temperature": 0},
    )
    print(f"Response: {response.text[:300]}")
    print("SUCCESS: Inline image API works!")
else:
    print("No remaining questions found")
