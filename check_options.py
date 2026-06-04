import json
d = json.loads(open("pipeline_output/p2_gemini/2020_tier2_kdcampus_answer_key/merged_questions_global_order.json", encoding="utf-8").read())
for q in d.get("questions", [])[:3]:
    print(f"Q{q.get('global_question_number')}:")
    print(f"  question_text: {q.get('question_text_full')[:80]}")
    print(f"  options: {q.get('options')}")
    print(f"  option_issue_global: {q.get('global_question_number') in d.get('option_or_correct_answer_issue_global_questions', [])}")
    print()
