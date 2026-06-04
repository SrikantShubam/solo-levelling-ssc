"""Merge Grok results from response sheets into the pipeline output."""
import json, sys; sys.path.insert(0, "src")
from process_category_a import merge_grok_into_pdf, parse_grok_output

def run(pdf_name, grok_raw):
    parsed = parse_grok_output(grok_raw)
    if not parsed or "pages" not in parsed:
        print(f"Failed to parse Grok output for {pdf_name}")
        return
    page_data = {}
    for p in parsed["pages"]:
        page_data[p["page"]] = p["questions"]
    result = merge_grok_into_pdf(pdf_name, page_data)
    print(f"{pdf_name}: {result}")

# Paste Grok output for each PDF here
if __name__ == "__main__":
    PDF = sys.argv[1] if len(sys.argv) > 1 else ""
    print("Usage: python merge_response.py <pdf_name>")
    print("Then paste the Grok JSON output and press Ctrl+Z then Enter")
    if PDF:
        print(f"Reading grok_results/{PDF}.json")
        raw = open(f"grok_results/{PDF}.json", encoding="utf-8").read()
        run(PDF, raw)
