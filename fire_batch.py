"""Helper to prepare tasks for grok_run_parallel_tasks call."""
import json

tasks = json.loads(open("grok_batches/massive_batch_manifest.json").read())["tasks"]

# Print first batch as formatted Python for the grok call
first_batch = tasks[:20]
print(json.dumps([{"id": t["id"], "task": t["task"]} for t in first_batch], indent=2))
