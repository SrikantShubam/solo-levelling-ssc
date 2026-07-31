import json
from pathlib import Path

from ssc_corpus.native_pipeline_compare import generate_native_two_pipeline_comparison


def test_generate_native_two_pipeline_comparison_from_cached_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "2019_tier1_prepp_shift1"
    page_json_dir = run_dir / "page_json"
    page_json_dir.mkdir(parents=True)
    questions = [_question_payload(13), _question_payload(21)]
    (page_json_dir / "page_01.json").write_text(
        json.dumps({"page": 1, "questions": questions}),
        encoding="utf-8",
    )
    (run_dir / "merged_questions_global_order.json").write_text(
        json.dumps({"questions": [_merged_payload(1, 13), _merged_payload(2, 21)]}),
        encoding="utf-8",
    )

    outputs = generate_native_two_pipeline_comparison(run_dir)

    pipeline_1 = json.loads(outputs.pipeline_1_path.read_text(encoding="utf-8"))
    pipeline_2 = json.loads(outputs.pipeline_2_path.read_text(encoding="utf-8"))
    audit = outputs.audit_path.read_text(encoding="utf-8")

    assert pipeline_1["question_count"] == 2
    assert pipeline_2["question_count"] == 2
    assert pipeline_1["status"] == "deprecated"

    for global_q in (1, 2):
        p1_row = _find_q(pipeline_1["questions"], global_q)
        assert p1_row["source"] == "page_json_cached_native"
        assert "native_extraction" in p1_row
        assert "question" not in p1_row
        assert p1_row["native_extraction"]["correct_option_label"] == "4"
        assert p1_row["native_capabilities"] == {
            "uses_deterministic_green_detection": False,
            "uses_option_crops": False,
            "uses_visual_asset_validation": False,
            "uses_precision_qc": False,
        }
        assert "manual_review_assets_added_posthoc" in p1_row
        assert "question_crop_path" not in p1_row
        assert "option_crop_paths" not in p1_row

        p2_row = _find_q(pipeline_2["questions"], global_q)
        assert p2_row["answer"]["deterministic_correct_option_label"] == "AMBIGUOUS"
        assert p2_row["answer"]["evidence_status"] == "PASS_WITH_MANUAL_REVIEW"
        assert p2_row["answer"]["canonical_correct_option_label"] is None
        assert "correct_option_unresolved_or_conflict" in p2_row["review"]["blocking_review_reasons"]
        assert "page_asset_path" in p2_row["native_assets"]
        assert "question_crop_path" in p2_row["native_assets"]
        assert "stimulus_crop_path" in p2_row["native_assets"]
        assert len(p2_row["native_assets"]["option_crop_paths"]) == 4
        assert "1" in p2_row["answer"]["deterministic_option_evidence"]

    assert "cached" in audit
    assert "cached existing merged artifact" in audit
    assert "Fallback model used: no" in audit
    assert "Pipeline 1 is deprecated" in audit


def _question_payload(question_number: int) -> dict:
    return {
        "question_number": question_number,
        "section": "Quant/DI",
        "question_id": f"q{question_number}",
        "question_text_full": f"Question {question_number}?",
        "options": [
            {"label": "1", "text": "A"},
            {"label": "2", "text": "B"},
            {"label": "3", "text": "C"},
            {"label": "4", "text": "D"},
        ],
        "chosen_option_label": "1",
        "correct_option_label": "4",
        "correct_option_text": "D",
        "is_complete_on_page": True,
        "confidence": "high",
        "notes": "",
    }


def _merged_payload(global_q: int, question_number: int) -> dict:
    return {
        **_question_payload(question_number),
        "global_question_number": global_q,
        "source_page": 1,
        "section_local_question_number": question_number,
        "raw_gemini_correct_option_label": "4",
        "raw_gemini_correct_option_text": "D",
        "canonical_correct_option_label": None,
        "deterministic_correct_option_label": "AMBIGUOUS",
        "correct_evidence_source": "manual_review_required",
        "evidence_status": "PASS_WITH_MANUAL_REVIEW",
        "evidence_reasons": [],
        "deterministic_option_evidence": {"1": "green pixels ambiguous"},
        "manual_review_reasons": [],
        "canonical_review_reasons": [],
        "blocking_review_reasons": ["correct_option_unresolved_or_conflict"],
        "page_asset_path": f"page_{global_q}.png",
        "question_crop_path": f"question_{global_q}.png",
        "stimulus_crop_path": f"stimulus_{global_q}.png",
        "option_crop_paths": [
            f"q{global_q}_opt_1.png",
            f"q{global_q}_opt_2.png",
            f"q{global_q}_opt_3.png",
            f"q{global_q}_opt_4.png",
        ],
    }


def _find_q(questions: list[dict], global_q: int) -> dict:
    for q in questions:
        if q.get("global_question_number") == global_q:
            return q
    raise AssertionError(f"Question {global_q} not found")
