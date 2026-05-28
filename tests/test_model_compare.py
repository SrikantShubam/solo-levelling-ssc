from pathlib import Path

from ssc_corpus.model_compare import (
    DEFAULT_MODEL_SPECS,
    compare_models,
    score_page_result,
)


def test_score_page_result_compares_answer_options_and_text() -> None:
    reference = [_question("What is 2+2?", "4", "1")]
    candidate = {
        "page": 1,
        "questions": [_question("What is 2+2?", "4", "1")],
        "warnings": [],
    }

    score = score_page_result(candidate, reference, page=1)

    assert score["status"] == "PASS"
    assert score["correct_accuracy"] == 1
    assert score["chosen_accuracy"] == 1
    assert score["option_shape_accuracy"] == 1


def test_compare_models_skips_when_keys_missing_and_text_only_model(tmp_path: Path) -> None:
    reference = {
        "questions": [
            {
                **_question("What is 2+2?", "4", "1"),
                "source_page": 1,
            }
        ]
    }
    reference_path = tmp_path / "reference.json"
    reference_path.write_text(__import__("json").dumps(reference), encoding="utf-8")
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "page_01.png").write_bytes(b"not used because models are skipped")
    env_file = tmp_path / ".env.txt"
    env_file.write_text("api='gemini-only'\n", encoding="utf-8")

    report = compare_models(
        env_file=env_file,
        reference_path=reference_path,
        image_dir=image_dir,
        output_dir=tmp_path / "out",
        pages=[1],
        model_specs=DEFAULT_MODEL_SPECS[:2],
    )

    statuses = [row["status"] for row in report["results"]]
    assert statuses == ["SKIPPED", "SKIPPED"]
    assert (tmp_path / "out" / "model_comparison_report.md").exists()


def _question(text: str, correct: str, chosen: str | None) -> dict:
    return {
        "question_text_full": text,
        "options": [
            {"label": "1", "text": "one"},
            {"label": "2", "text": "two"},
            {"label": "3", "text": "three"},
            {"label": "4", "text": "four"},
        ],
        "correct_option_label": correct,
        "chosen_option_label": chosen,
    }
