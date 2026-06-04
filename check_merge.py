import json
d = json.loads(open("pipeline_output/p2_gemini/2020_tier1_prepp_shift1/merged_questions_global_order.json", encoding="utf-8").read())
print("Practice-ready:", sum(1 for q in d.get("questions",[]) if q.get("practice_ready")))
print("AI-reviewed:", sum(1 for q in d.get("questions",[]) if q.get("ai_reviewed")))
print("Still needs review:", sum(1 for q in d.get("questions",[]) if not q.get("practice_ready")))
ready = [q for q in d.get("questions",[]) if q.get("practice_ready") and q.get("ai_reviewed")]
print("Became ready via AI:", len(ready))
not_ready = [q for q in d.get("questions",[]) if not q.get("practice_ready") and q.get("ai_reviewed")]
print("AI reviewed but still blocked:", len(not_ready))
if not_ready:
    q = not_ready[0]
    print("Example blocked question:", q.get("global_question_number"), "blocking_reasons:", q.get("blocking_review_reasons"), "qc:", q.get("evidence_status"))
