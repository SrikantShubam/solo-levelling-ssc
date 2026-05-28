from pathlib import Path

from ssc_corpus.extraction import (
    _classify_failure_type,
    _extract_page,
    merge_page_results,
    write_review_summary,
)


def test_merge_preserves_page_order_and_assigns_global_question_numbers(tmp_path: Path) -> None:
    page_results = [
        {
            "page": 1,
            "questions": [
                _question(1, "A", "4"),
                _question(2, "B", "3"),
            ],
            "warnings": [],
        },
        {
            "page": 2,
            "questions": [
                _question(1, "C", "2"),
                _question(2, "D", "1"),
            ],
            "warnings": [],
        },
    ]

    merged = merge_page_results(Path("paper.pdf"), page_results, expected_questions=4)

    assert merged["qc_passed"] is True
    assert merged["question_count"] == 4
    assert [q["global_question_number"] for q in merged["questions"]] == [1, 2, 3, 4]
    assert [q["section_local_question_number"] for q in merged["questions"]] == [1, 2, 1, 2]
    assert [q["source_page"] for q in merged["questions"]] == [1, 1, 2, 2]


def test_merge_fails_qc_when_expected_count_or_options_are_wrong() -> None:
    page_results = [
        {
            "page": 1,
            "questions": [
                {
                    **_question(1, "A", "4"),
                    "options": [{"label": "1", "text": "only one"}],
                }
            ],
            "warnings": [],
        }
    ]

    merged = merge_page_results(Path("paper.pdf"), page_results, expected_questions=100)

    assert merged["qc_passed"] is False
    assert merged["question_count"] == 1
    assert merged["option_or_correct_answer_issue_global_questions"] == [1]


def test_write_review_summary_includes_qc_and_counts(tmp_path: Path) -> None:
    merged = merge_page_results(
        Path("paper.pdf"),
        [{"page": 1, "questions": [_question(1, "A", "4")], "warnings": []}],
        expected_questions=1,
    )
    summary_path = tmp_path / "summary.md"

    write_review_summary(merged, summary_path)

    summary = summary_path.read_text(encoding="utf-8")
    assert "Overall status: PASS_LLM_ONLY" in summary
    assert "| 1 | 1 | 1 | 4: option 4 | 4 | high | False | A |" in summary


def test_missing_chosen_answer_sets_manual_review_without_structural_failure() -> None:
    question = _question(1, "A", "4")
    question["chosen_option_label"] = None

    merged = merge_page_results(
        Path("paper.pdf"),
        [{"page": 1, "questions": [question], "warnings": []}],
        expected_questions=1,
    )

    assert merged["qc_passed"] is True
    assert merged["qc_status"] == "PASS_WITH_MANUAL_REVIEW"
    assert merged["missing_or_invalid_chosen_option_global_questions"] == [1]
    assert merged["questions"][0]["manual_review"] is True


def test_raw_gemini_record_survives_canonical_failure() -> None:
    question = _question(1, "Choose the figure shown below", "2")

    merged = merge_page_results(
        Path("paper.pdf"),
        [{"page": 1, "questions": [question], "warnings": []}],
        expected_questions=1,
    )

    row = merged["questions"][0]
    assert row["raw_gemini_record"]["correct_option_label"] == "2"
    assert row["raw_gemini_correct_option_label"] == "2"
    assert row["canonical_correct_option_label"] is None
    assert row["correct_option_label"] is None
    assert "correct_option_unresolved_or_conflict" in row["canonical_review_reasons"]


def test_merge_marks_quota_error_as_infra_failure_not_empty_extraction() -> None:
    merged = merge_page_results(
        Path("paper.pdf"),
        [
            {
                "page": 1,
                "questions": [],
                "warnings": ["ERROR API: ResourceExhausted: 429 quota exceeded"],
            }
        ],
        expected_questions=100,
    )

    assert merged["qc_passed"] is False
    assert merged["qc_status"] == "INFRA_FAILURE"
    assert merged["structural_status"] == "INFRA_FAILURE"
    assert "api_quota_or_rate_limit" in merged["structural_failure_reasons"]
    assert merged["page_counts"][0]["page_status"] == "ERROR"
    assert merged["page_counts"][0]["failure_type"] == "api_quota_or_rate_limit"


def test_merge_marks_zero_question_expected_pdf_as_quarantine() -> None:
    merged = merge_page_results(
        Path("notice.pdf"),
        [{"page": 1, "questions": [], "warnings": []}],
        expected_questions=100,
    )

    assert merged["qc_passed"] is False
    assert merged["qc_status"] == "QUARANTINE"
    assert merged["structural_status"] == "QUARANTINE"
    assert "true_empty_or_non_question_pdf" in merged["structural_failure_reasons"]


def test_extract_page_classifies_response_text_refusal() -> None:
    class Response:
        @property
        def text(self) -> str:
            raise ValueError("finish_reason is 4 reciting from copyrighted material")

    class Model:
        def generate_content(self, *_args, **_kwargs):
            return Response()

    result = _extract_page(
        Model(),
        Path("page.png"),
        1,
        uploader=lambda _path: object(),
        file_getter=lambda uploaded: uploaded,
        sleep=lambda _seconds: None,
    )

    assert result["questions"] == []
    assert result["page_status"] == "ERROR"
    assert result["failure_type"] == "model_refusal"
    assert result["retryable"] is False


def test_extract_page_uses_fallback_only_after_primary_failure() -> None:
    class Model:
        def generate_content(self, *_args, **_kwargs):
            raise RuntimeError("ResourceExhausted: 429 quota exceeded")

    def fallback(_image_path: Path, page_number: int, failure: dict) -> dict:
        return {
            "page": page_number,
            "questions": [_question(1, "Recovered", "1")],
            "warnings": ["fallback used"],
            "provider": "test_fallback",
            "model": "test_model",
            "fallback_parent_failure_type": failure["failure_type"],
        }

    result = _extract_page(
        Model(),
        Path("page.png"),
        1,
        uploader=lambda _path: object(),
        file_getter=lambda uploaded: uploaded,
        sleep=lambda _seconds: None,
        fallback_extractor=fallback,
    )

    assert result["page_status"] == "OK"
    assert result["fallback_attempted"] is True
    assert result["fallback_used"] is True
    assert result["provider"] == "test_fallback"
    assert result["fallback_parent_failure_type"] == "api_quota_or_rate_limit"


def test_extract_page_classifies_failed_fallback_result() -> None:
    class Model:
        def generate_content(self, *_args, **_kwargs):
            raise RuntimeError("ResourceExhausted: 429 quota exceeded")

    def fallback(_image_path: Path, page_number: int, _failure: dict) -> dict:
        return {
            "page": page_number,
            "questions": [],
            "warnings": ["ERROR HTTP 400: DEGRADED function cannot be invoked"],
            "page_status": "ERROR",
            "provider": "nvidia_nim",
            "model": "bad_model",
        }

    result = _extract_page(
        Model(),
        Path("page.png"),
        1,
        uploader=lambda _path: object(),
        file_getter=lambda uploaded: uploaded,
        sleep=lambda _seconds: None,
        fallback_extractor=fallback,
    )

    assert result["page_status"] == "ERROR"
    assert result["failure_type"] == "fallback_provider_unavailable"
    assert result["fallback_attempted"] is True
    assert result["fallback_used"] is False


def test_timeout_warning_classifies_as_provider_timeout() -> None:
    assert _classify_failure_type("ERROR TimeoutError: The read operation timed out") == "provider_timeout"


def test_deterministic_conflict_clears_canonical_correct_answer() -> None:
    question = _question(1, "Choose the figure shown below", "2")
    question["deterministic_correct_option_label"] = "3"

    merged = merge_page_results(
        Path("paper.pdf"),
        [{"page": 1, "questions": [question], "warnings": []}],
        expected_questions=1,
    )

    row = merged["questions"][0]
    assert row["evidence_status"] == "PASS_WITH_MANUAL_REVIEW"
    assert row["canonical_correct_option_label"] is None
    assert row["correct_option_label"] is None
    assert row["raw_gemini_correct_option_label"] == "2"


def _question(number: int, text: str, correct: str) -> dict:
    return {
        "question_number": number,
        "section": "Reasoning",
        "question_text_full": text,
        "options": [
            {"label": "1", "text": "option 1"},
            {"label": "2", "text": "option 2"},
            {"label": "3", "text": "option 3"},
            {"label": "4", "text": "option 4"},
        ],
        "question_id": str(number),
        "chosen_option_label": correct,
        "correct_option_label": correct,
        "correct_option_text": f"option {correct}",
        "is_complete_on_page": True,
        "confidence": "high",
        "notes": "",
    }
