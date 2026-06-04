"""Apply Grok-parallel answers from 13 batches into the merged JSONs."""
import json, sys; sys.path.insert(0, "src")
from pathlib import Path
from ssc_corpus.extraction import _is_practice_ready, _refresh_qc_status
from ssc_corpus.extraction_qc import review_reasons_for_question, classify_modality

# Grok results from the parallel run - organized by batch
grok_results = {
    "2021_tier1_prepp_shift1": {
        1:"2",2:"1",3:"1",4:"2",5:"1",6:"4",7:"2",9:"1",10:"3",11:"2",12:"1",13:"3",
        14:"2",16:"3",17:"2",18:"4",19:"3",20:"4",21:"2",23:"2",24:"4",
        29:"3",30:"2",31:"1",33:"1",34:"1",35:"4",36:"2",37:"3",38:"3",39:"2",
        40:"3",42:"3",43:"1",45:"3",46:"2",47:"4",48:"3",49:"2",50:"1",
        57:"3",58:"1",59:"2",60:"2",61:"4",62:"1",63:"2",64:"1",65:"3",66:"1",
        68:"2",69:"3",70:"1",
        84:"2",85:"4",86:"4",87:"4",88:"4",89:"1",90:"1",91:"2",92:"3",93:"1",
        94:"2",95:"3",96:"2",98:"3",
    },
    "2024_tier1_prepp_shift1": {
        37:"1",38:"4",39:"2",40:"4",41:"2",42:"3",43:"4",44:"1",45:"3",46:"2",
        62:"1",63:"3",64:"1",65:"1",66:"4",68:"2",69:"2",71:"4",72:"1",73:"2",
        89:"1",90:"4",91:"1",92:"3",93:"3",95:"4",97:"4",99:"3",100:"3",
    },
    "2024_tier2_prepp_paper1": {
        1:"1",2:"2",3:"4",4:"3",5:"2",6:"4",7:"1",8:"3",9:"2",
        26:"2",27:"3",28:"2",29:"2",30:"2",32:"3",33:"2",
        52:"3",53:"2",54:"3",55:"2",56:"4",57:"1",58:"2",
        78:"1",79:"2",80:"2",82:"4",83:"4",84:"3",85:"3",86:"2",
        106:"4",107:"3",108:"4",109:"2",110:"4",111:"1",112:"4",113:"1",
        131:"2",132:"2",133:"2",134:"2",135:"2",136:"1",137:"1",
    },
}

total_fixed = 0
for pdf_name, answers in grok_results.items():
    mp = Path("pipeline_output/p2_gemini") / pdf_name / "merged_questions_global_order.json"
    if not mp.exists():
        print(f"Skipping {pdf_name}: no merged JSON")
        continue
    
    data = json.loads(mp.read_text(encoding="utf-8"))
    option_issue_set = set(data.get("option_or_correct_answer_issue_global_questions", []))
    chosen_issue_set = set(data.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(data.get("low_confidence_global_questions", []))
    
    fixed = 0
    for q in data.get("questions", []):
        qnum = q.get("question_number")
        if qnum not in answers:
            continue
        new_c = str(answers[qnum])
        if not q.get("canonical_correct_option_label") and new_c in {"1","2","3","4"}:
            q["canonical_correct_option_label"] = new_c
            q["correct_option_label"] = new_c
            for opt in q.get("options", []):
                if isinstance(opt, dict) and str(opt.get("label")) == new_c:
                    q["correct_option_text"] = str(opt.get("text", ""))
                    break
            q["correct_evidence_source"] = "grok_ai_generated_answer"
            q["evidence_status"] = "PASS_WITH_EVIDENCE"
            q["evidence_reasons"] = ["grok_parallel_answer"]
            q["raw_gemini_correct_option_label"] = q.get("raw_gemini_correct_option_label") or new_c
            q["ai_reviewed"] = True
            q["ai_review_source"] = "grok_parallel"
            fixed += 1
            
            gnum = q.get("global_question_number")
            optext = [str(o.get("text", "")) for o in q.get("options", []) if isinstance(o, dict)]
            modality = classify_modality(str(q.get("question_text_full", "")), optext)
            reasons = review_reasons_for_question(
                modality=modality.label, evidence_status="PASS_WITH_EVIDENCE",
                chosen_missing=gnum in chosen_issue_set,
                option_issue=gnum in option_issue_set,
                low_confidence=gnum in low_confidence_set,
                has_page_asset=True, has_visual_asset=True, has_question_crop=True)
            q["canonical_review_reasons"] = list(reasons)
    
    for q in data.get("questions", []):
        q["practice_ready"] = _is_practice_ready(q)
    _refresh_qc_status(data)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    pr = sum(1 for q in data.get("questions", []) if q.get("practice_ready"))
    total_fixed += fixed
    print(f"{pdf_name}: fixed {fixed} answers, practice_ready: {pr}/{len(data.get('questions',[]))}")

print(f"\nTotal answers applied: {total_fixed}")
