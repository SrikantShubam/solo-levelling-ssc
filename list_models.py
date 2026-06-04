import re
from pathlib import Path
import google.generativeai as genai

env = Path(".env").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env)
genai.configure(api_key=m.group(1).strip())

models = genai.list_models()
for model in models:
    if 'generateContent' in model.supported_generation_methods:
        print(f"{model.name:50s} | input: {model.input_token_limit:8d} | output: {model.output_token_limit:8d}")
