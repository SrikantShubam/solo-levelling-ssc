from __future__ import annotations

import json
from pathlib import Path

from ssc_corpus.ai_review import compute_delta, merge_grok_results


def test_compute_delta_counts_ai_reviewed_and_practice_ready(tmp_path: Path) -> None:
    merged_path = tmp_path / "sample" / "merged_questions_global_order.json"
    merged_path.parent.mkdir(parents=True)
    merged_path.write_text(
        json.dumps(
            {
                "questions": [
                    {"practice_ready": True, "ai_reviewed": True},
                    {"practice_ready": False, "ai_reviewed": False},
                    {"practice_ready": True, "ai_reviewed": False},
                ]
            }
        ),
        encoding="utf-8",
    )

    delta = compute_delta(tmp_path)

    assert delta == {
        "total_questions": 3,
        "practice_ready": 2,
        "ai_reviewed": 1,
        "needs_review": 1,
    }


def test_merge_grok_results_preserves_option_order(tmp_path: Path) -> None:
    merged_dir = tmp_path / "paper"
    merged_dir.mkdir()
    merged_path = merged_dir / "merged_questions_global_order.json"
    merged_path.write_text(
        json.dumps(
            {
                "questions": [
                    {
                        "question_number": 1,
                        "global_question_number": 1,
                        "source_page": 1,
                        "question_text_full": "Test question",
                        "options": [
                            {"label": "1", "text": ""},
                            {"label": "2", "text": ""},
                            {"label": "3", "text": ""},
                            {"label": "4", "text": ""},
                        ],
                        "confidence": "high",
                        "practice_ready": False,
                        "canonical_correct_option_label": None,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    results_path = tmp_path / "results.json"
    results_path.write_text(
        json.dumps(
            [
                {
                    "pdf_name": "paper",
                    "page_number": 1,
                    "merged_path": str(merged_path),
                    "grok_output": json.dumps(
                        {
                            "questions": [
                                {
                                    "question_number": 1,
                                    "correct_option_label": "2",
                                    "chosen_option_label": "3",
                                    "confidence": "high",
                                    "options": [
                                        {"label": "4", "text": "four"},
                                        {"label": "2", "text": "two"},
                                        {"label": "1", "text": "one"},
                                        {"label": "3", "text": "three"},
                                    ],
                                }
                            ]
                        }
                    ),
                }
            ]
        ),
        encoding="utf-8",
    )

    merge_grok_results(results_path)
    merged = json.loads(merged_path.read_text(encoding="utf-8"))

    assert [option["label"] for option in merged["questions"][0]["options"]] == ["1", "2", "3", "4"]
