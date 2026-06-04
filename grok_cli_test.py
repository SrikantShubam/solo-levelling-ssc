"""Test calling grok CLI directly with longer timeout."""
import subprocess, json, sys

cmd = [
    "C:\\Users\\srika\\.grok\\bin\\grok.exe",
    "--no-auto-update", "-p",
    "Read the image file at this path and tell me what you see. Keep it under 2 sentences: "
    "C:\\experiments\\ssc\\pipeline_output\\p2_gemini\\2019_tier2_prepp_quant\\page_images\\page_17.png",
    "-m", "grok-build",
    "--output-format", "json",
]

print("Running grok CLI with 120s timeout...")
try:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            text = data.get("text", result.stdout)[:500]
        except json.JSONDecodeError:
            text = result.stdout[:500]
        print(f"Output: {text}")
    else:
        print(f"Stderr: {result.stderr[:500]}")
except subprocess.TimeoutExpired:
    print("Timed out after 120s")
except Exception as e:
    print(f"Error: {e}")
