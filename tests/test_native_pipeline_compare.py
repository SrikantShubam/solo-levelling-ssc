import json
from pathlib import Path

from ssc_corpus.native_pipeline_compare import generate_native_two_pipeline_comparison


def test_generate_native_two_pipeline_comparison_for_2019_batch() -> None:
    run_dir = Path("extraction_batch/tier1_gemini/2019_tier1_prepp_shift1")
    outputs = generate_native_two_pipeline_comparison(run_dir)

    pipeline_1 = json.loads(outputs.pipeline_1_path.read_text(encoding="utf-8"))
    pipeline_2 = json.loads(outputs.pipeline_2_path.read_text(encoding="utf-8"))
    audit = outputs.audit_path.read_text(encoding="utf-8")

    assert pipeline_1["question_count"] == 100
    assert pipeline_2["question_count"] == 100
    assert pipeline_1["status"] == "deprecated"

    for global_q in (13, 21):
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


def _find_q(questions: list[dict], global_q: int) -> dict:
    for q in questions:
        if q.get("global_question_number") == global_q:
            return q
    raise AssertionError(f"Question {global_q} not found")
