"""Quick test with new google-genai SDK."""
import io, json, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google import genai
from google.genai import types

env = Path(".env").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env)
client = genai.Client(api_key=m.group(1).strip())

# Find first remaining question
for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(mp.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready"):
            continue
        page = q.get("source_page") or 0
        page_img = mp.parent / "page_images" / f"page_{page:02d}.png"
        if page_img.exists():
            name = mp.parent.name
            qnum = q.get("question_number")
            opts = " ".join(str(o.get("text",""))[:100] for o in q.get("options",[]) if isinstance(o, dict))
            print(f"Test: {name}/p{page:02d} Q{qnum}")

            prompt = f"Look at this SSC exam page. What is the correct answer for question {qnum}? Options: {opts}. Answer with just the option number (1/2/3/4)."
            img_bytes = page_img.read_bytes()

            response = client.models.generate_content(
                model="models/gemini-3.1-flash-lite",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                ],
                config=types.GenerateContentConfig(temperature=0),
            )
            print(f"Response: {response.text[:200]}")
            print("SUCCESS: new SDK + gemini-2.0-flash works!")
            raise SystemExit(0)
print("No remaining questions")
