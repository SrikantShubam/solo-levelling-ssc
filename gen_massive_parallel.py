"""Generate maximum-parallelism task batch for ALL remaining unanswered questions."""
import json
from pathlib import Path

all_unanswered = []

for mp in sorted(Path("pipeline_output/p2_gemini").rglob("merged_questions_global_order.json")):
    pdf_name = mp.parent.name
    data = json.loads(mp.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("canonical_correct_option_label"):
            continue
        opts_text = {}
        for opt in q.get("options", []):
            if isinstance(opt, dict):
                opts_text[opt.get("label")] = opt.get("text", "")
        qt = q.get("question_text_full", "")
        all_unanswered.append({
            "pdf_name": pdf_name,
            "question_number": q.get("question_number"),
            "global_question_number": q.get("global_question_number"),
            "question_text_full": qt[:250],
            "options": {l: opts_text.get(l, "") for l in ["1","2","3","4"]},
            "merged_path": str(mp),
        })

print(f"Total unanswered questions: {len(all_unanswered)}")
print()

# Group by PDF
by_pdf = {}
for q in all_unanswered:
    by_pdf.setdefault(q["pdf_name"], []).append(q)

for pdf, qs in sorted(by_pdf.items()):
    print(f"  {pdf}: {len(qs)} unanswered")
print()

# Create tasks - 15 questions per task for maximum parallelism
TASKS_PER_BATCH = 15
tasks = []
task_id = 0
for pdf_name, questions in sorted(by_pdf.items()):
    for i in range(0, len(questions), TASKS_PER_BATCH):
        batch = questions[i:i+TASKS_PER_BATCH]
        question_texts = []
        for q in batch:
            opts = " | ".join(f"{k}. {v[:60]}" for k, v in q["options"].items() if v)
            qt = q["question_text_full"][:150]
            question_texts.append(
                f"Q{q['question_number']}: {qt}\n{opts}"
            )
        
        task_body = "\n\n".join(question_texts)
        tasks.append({
            "id": f"task_{task_id:03d}",
            "pdf_name": pdf_name,
            "question_count": len(batch),
            "task": f"Answer these {len(batch)} SSC CGL questions from '{pdf_name}':\n\n{task_body}\n\nReturn ONLY a JSON array: [{{\"question_number\": INTEGER, \"correct_option_label\": \"1\"|\"2\"|\"3\"|\"4\"}}]"
        })
        task_id += 1

print(f"Generated {len(tasks)} parallel tasks ({TASKS_PER_BATCH} questions each)")

# Save manifest
Path("grok_batches/massive_batch_manifest.json").write_text(json.dumps({
    "total_unanswered": len(all_unanswered),
    "total_tasks": len(tasks),
    "tasks": tasks,
}, indent=2), encoding="utf-8")

print(f"Tasks: {len(tasks)}")
print(f"Max grok_run_parallel_tasks can handle: {min(20, len(tasks))}")
