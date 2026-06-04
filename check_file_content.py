import json
d = json.loads(open("pipeline_output/p2_gemini/2020_tier2_kdcampus_answer_key/merged_questions_global_order.json", encoding="utf-8").read())
q = [qq for qq in d.get("questions", []) if qq.get("global_question_number") == 1][0]
print(f"practice_ready field value: {q.get('practice_ready')}")
print(f"type: {type(q.get('practice_ready'))}")
print(f"exact repr: {repr(q.get('practice_ready'))}")
print(f"bool: {bool(q.get('practice_ready'))}")
print(f"q['practice_ready'] is False: {q.get('practice_ready') is False}")
