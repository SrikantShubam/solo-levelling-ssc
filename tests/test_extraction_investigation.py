import json
from pathlib import Path

from ssc_corpus.extraction_investigation import build_extraction_investigation


def test_investigation_separates_quota_failure_from_layout_failure(tmp_path: Path) -> None:
    batch_dir = tmp_path / "batch"
    quota_run = batch_dir / "quota_pdf"
    layout_run = batch_dir / "layout_pdf"
    quota_page_json = quota_run / "page_json"
    layout_page_json = layout_run / "page_json"
    quota_page_json.mkdir(parents=True)
    layout_page_json.mkdir(parents=True)

    (quota_page_json / "page_01.json").write_text(
        json.dumps(
            {
                "page": 1,
                "questions": [],
                "warnings": ["ERROR API: ResourceExhausted: 429 quota exceeded"],
            }
        ),
        encoding="utf-8",
    )
    (layout_page_json / "page_01.json").write_text(
        json.dumps({"page": 1, "questions": [], "warnings": []}),
        encoding="utf-8",
    )
    batch_summary = [
        {
            "pdf": "2023_tier1_prepp_shift1.pdf",
            "expected_questions": 100,
            "question_count": 0,
            "qc_status": "FAIL",
            "output_dir": str(quota_run),
            "error": None,
        },
        {
            "pdf": "2024_tier1_appx_answer_key.pdf",
            "expected_questions": 100,
            "question_count": 0,
            "qc_status": "FAIL",
            "output_dir": str(layout_run),
            "error": None,
        },
    ]
    summary_path = batch_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(batch_summary), encoding="utf-8")

    report = build_extraction_investigation(summary_path)

    by_pdf = {row["pdf"]: row for row in report["rows"]}
    assert by_pdf["2023_tier1_prepp_shift1.pdf"]["primary_failure_type"] == "api_quota_or_rate_limit"
    assert by_pdf["2023_tier1_prepp_shift1.pdf"]["recommended_action"] == "rerun_needed"
    assert by_pdf["2024_tier1_appx_answer_key.pdf"]["document_class"] == "answer_key_notice_or_non_question"
    assert by_pdf["2024_tier1_appx_answer_key.pdf"]["recommended_action"] == "quarantine"


def test_investigation_marks_complete_blocked_pdf_as_usable_with_review(tmp_path: Path) -> None:
    batch_dir = tmp_path / "batch"
    run_dir = batch_dir / "complete_pdf"
    page_json = run_dir / "page_json"
    page_json.mkdir(parents=True)
    (page_json / "page_01.json").write_text(
        json.dumps({"page": 1, "questions": [{"question_number": 1}], "warnings": []}),
        encoding="utf-8",
    )
    summary_path = batch_dir / "batch_summary.json"
    summary_path.write_text(
        json.dumps(
            [
                {
                    "pdf": "2019_tier1_prepp_shift1.pdf",
                    "expected_questions": 1,
                    "question_count": 1,
                    "qc_status": "BLOCKED",
                    "output_dir": str(run_dir),
                    "error": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    report = build_extraction_investigation(summary_path)

    assert report["rows"][0]["recommended_action"] == "usable_with_review"
    assert report["summary"]["usable_with_review"] == 1


def test_investigation_marks_non_expected_positive_blocked_pdf_as_usable_with_review(tmp_path: Path) -> None:
    batch_dir = tmp_path / "batch"
    run_dir = batch_dir / "tier2_pdf"
    page_json = run_dir / "page_json"
    page_json.mkdir(parents=True)
    (page_json / "page_01.json").write_text(
        json.dumps({"page": 1, "questions": [{"question_number": 1}], "warnings": []}),
        encoding="utf-8",
    )
    summary_path = batch_dir / "batch_summary.json"
    summary_path.write_text(
        json.dumps(
            [
                {
                    "pdf": "2019_tier2_prepp_english.pdf",
                    "expected_questions": None,
                    "question_count": 200,
                    "qc_status": "BLOCKED",
                    "output_dir": str(run_dir),
                    "error": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    report = build_extraction_investigation(summary_path)

    assert report["rows"][0]["recommended_action"] == "usable_with_review"
