"""Generate parallel tasks for Grok to answer question-only PDFs."""
import json
from pathlib import Path

targets = ["2021_tier1_prepp_shift1", "2024_tier1_prepp_shift1", "2024_tier2_prepp_paper1"]
all_pdf_questions = {}

for pdf_name in targets:
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    data = json.loads(mp.read_text(encoding="utf-8"))
    questions = []
    for q in data.get("questions", []):
        if not q.get("canonical_correct_option_label"):
            opts_text = {}
            for opt in q.get("options", []):
                if isinstance(opt, dict):
                    opts_text[opt.get("label")] = opt.get("text", "")
            qt = q.get("question_text_full", "")
            questions.append({
                "global_question_number": q.get("global_question_number"),
                "question_number": q.get("question_number"),
                "source_page": q.get("source_page"),
                "question_text_full": qt,
                "options": {l: opts_text.get(l, "") for l in ["1","2","3","4"]},
                "merged_path": str(mp),
                "pdf_name": pdf_name,
            })
    all_pdf_questions[pdf_name] = questions
    print(f"{pdf_name}: {len(questions)} unanswered questions")

# Create batches of ~25 questions each
tasks = []
task_id = 0
for pdf_name, questions in all_pdf_questions.items():
    for i in range(0, len(questions), 25):
        batch = questions[i:i+25]
        task_data = {
            "pdf_name": pdf_name,
            "batch_start": i+1,
            "batch_end": min(i+25, len(questions)),
            "questions": batch,
        }
        path = Path(f"grok_batches/question_batches/{pdf_name}_batch_{task_id}.json")
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"task_id": task_id, "data": task_data}, indent=2), encoding="utf-8")
        
        # Build a task string for Grok
        qlist = []
        for q in batch:
            opts = "\n".join(f"  {k}. {v}" for k, v in q["options"].items() if v)
            qlist.append(f"Q{q['question_number']} (p{q['source_page']}): {q['question_text_full'][:120]}\n{opts}")
        
        question_texts = []
        for i, q in enumerate(batch):
            question_texts.append(f"--- Q{i+1} ---")
            question_texts.append(qlist[i])
        questions_block = "\n".join(question_texts)
        
        task_prompt = f"""Answer {len(batch)} SSC CGL questions from PDF: {pdf_name}

For each question, determine which option (1/2/3/4) is the CORRECT answer.
Return a JSON object:
{{"answers": [{{"question_number": INTEGER, "correct_option_label": "1"|"2"|"3"|"4", "confidence": "high"|"medium"|"low"}}]}}

Questions to answer:
{questions_block}
"""
        
        tasks.append({
            "id": f"batch_{task_id}",
            "task": task_prompt,
        })
        print(f"  task_{task_id}: {pdf_name} Q{questions[i]['question_number']}-Q{min(i+25, len(questions))}")
        task_id += 1

Path("grok_batches/question_batches/tasks_manifest.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")
print(f"\nTotal tasks: {len(tasks)}")
