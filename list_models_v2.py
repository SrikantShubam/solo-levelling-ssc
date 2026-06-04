"""List available models with the new google-genai SDK."""
import re
from pathlib import Path
from google import genai
from google.genai import types

env = Path(".env").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'api\s*=\s*["\']?([^"\'\r\n]+)', env)
client = genai.Client(api_key=m.group(1).strip())

models = client.models.list()
for model in models:
    methods = getattr(model, 'supported_actions', [])
    if methods:
        print(f"{model.name:50s} | methods: {methods}")
