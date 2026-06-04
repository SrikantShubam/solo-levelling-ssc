import json, os
from pathlib import Path

total_review = 0
only_blocked_by_path = 0
blocked_by_data = 0
low_conf = 0
missing_correct = 0
malformed = 0

for merged_path in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready", True):
            continue
        total_review += 1
        br = q.get("blocking_review_reasons") or []
        canonical = q.get("canonical_correct_option_label")

        if not canonical:
            missing_correct += 1
        if "malformed_options" in br:
            malformed += 1
        if q.get("confidence") == "low":
            low_conf += 1

        crop_paths = q.get("option_crop_paths") or []
        crops_missing = not all(os.path.exists(p) for p in crop_paths) if crop_paths else True

        has_correct = canonical and canonical in {"1","2","3","4"}
        has_options = len(q.get("options") or []) >= 4
        no_blocking = not br or br == ["malformed_options"]

        if has_correct and has_options and no_blocking and crops_missing:
            only_blocked_by_path += 1
        elif has_correct and has_options:
            blocked_by_data += 1
        else:
            blocked_by_data += 1

print(f"Total review questions: {total_review}")
print(f"  Only blocked by stale crop paths: {only_blocked_by_path}")
print(f"  Actually blocked by data issues: {blocked_by_data}")
print()
print(f"Missing canonical correct label: {missing_correct}")
print(f"Malformed options: {malformed}")
print(f"Low confidence: {low_conf}")

# Now check questions that have blocking_review_reasons with actual data issues
data_blockers = {"missing_correct_no_options": 0, "has_options_no_correct": 0, "other": 0}
for merged_path in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    data = json.loads(merged_path.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("practice_ready", True):
            continue
        br = q.get("blocking_review_reasons") or []
        canonical = q.get("canonical_correct_option_label")
        opts = len(q.get("options") or [])

        if not canonical and opts < 4:
            data_blockers["missing_correct_no_options"] += 1
        elif not canonical and opts >= 4:
            data_blockers["has_options_no_correct"] += 1
        else:
            data_blockers["other"] += 1

print(f"\nData issue breakdown:")
for k, v in data_blockers.items():
    print(f"  {k}: {v}")
