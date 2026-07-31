"""Tests for the Phase 1 baseline web service."""

from __future__ import annotations

import json
import importlib
from collections import Counter
from typing import Any

import pytest
from PIL import Image

from ssc_study.baseline_web import (
    ANSWER_LEAKING_SOURCES,
    SMOKE_REQUIREMENTS,
    BaselineWebError,
    _encode_exam_token,
    _question_asset_urls,
    get_baseline_preflight,
    get_baseline_result,
    start_baseline_exam,
    submit_baseline_exam,
)
from ssc_study.corpus_assets import mask_answer_leaking_crop, remap_question_assets
from ssc_study.db import Database
from ssc_study.models import Question
from ssc_study.quiz import FOUNDATION_PULSE_REQUIREMENTS


def _insert_question(
    conn,
    qid: str,
    section: str,
    *,
    correct_label: str = "1",
    is_holdout: int = 0,
    question_text: str | None = None,
    options: list[dict[str, str]] | None = None,
    question_modality: str = "text_only",
    visual_required: int = 0,
    table_required: int = 0,
    question_crop_path: str | None = None,
    page_asset_path: str | None = None,
    evidence_status: str | None = "PASS",
    correct_option_text: str | None = "A",
    pdf_name: str = "test_pdf",
) -> None:
    options = options or [
        {"label": "1", "text": "A"},
        {"label": "2", "text": "B"},
        {"label": "3", "text": "C"},
        {"label": "4", "text": "D"},
    ]
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout,
            question_modality, visual_required, table_required,
            question_crop_path, page_asset_path, evidence_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            qid,
            pdf_name,
            1,
            1,
            section,
            2021,
            "tier1",
            question_text if question_text is not None else f"Question {qid}?",
            json.dumps(options),
            correct_label,
            correct_option_text,
            is_holdout,
            question_modality,
            visual_required,
            table_required,
            question_crop_path,
            page_asset_path,
            evidence_status,
        ),
    )


def _seed_section_counts(conn, counts: dict[str, int], *, holdout_extra: int = 0) -> None:
    counter = 0
    for section, count in counts.items():
        for index in range(count):
            counter += 1
            _insert_question(conn, f"{section.replace('/', '_')}_{index}", section)
        for index in range(holdout_extra):
            counter += 1
            _insert_question(
                conn,
                f"{section.replace('/', '_')}_holdout_{index}",
                section,
                is_holdout=1,
            )
    conn.commit()


@pytest.fixture
def smoke_eligible_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(conn, {"Quant/DI": 2, "Reasoning": 1, "English": 1, "GK/GA": 1})
    return study_db


@pytest.fixture
def full_eligible_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(
        conn,
        {
            "Quant/DI": 80,
            "Reasoning": 40,
            "English": 40,
            "GK/GA": 40,
        },
        holdout_extra=2,
    )
    return study_db


@pytest.fixture
def underfilled_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(conn, {"Quant/DI": 10, "Reasoning": 40, "English": 40, "GK/GA": 40})
    return study_db


def _build_submit_payload(
    exam_id: str,
    mode: str,
    questions: list[dict],
    *,
    exam_token: str | None = None,
    answers: dict[str, str | None] | None = None,
) -> dict:
    answer_map = answers or {}
    payload = {
        "exam_id": exam_id,
        "mode": mode,
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": [
            {
                "question_id": question["question_id"],
                "user_answer": answer_map.get(question["question_id"]),
                "time_spent_seconds": 30,
                "marked_for_review": False,
            }
            for question in questions
        ],
    }
    if exam_token is not None:
        payload["exam_token"] = exam_token
    return payload


def _build_section_accuracy_answers(
    db: Database,
    questions: list[dict[str, Any]],
    section_correct_counts: dict[str, int],
) -> dict[str, str]:
    conn = db.connect()
    answers: dict[str, str] = {}
    section_seen: Counter[str] = Counter()

    for question in questions:
        section = question["section"]
        question_id = question["question_id"]
        correct_label = conn.execute(
            "SELECT correct_option_label FROM questions WHERE question_id = ?",
            (question_id,),
        ).fetchone()["correct_option_label"]
        wrong_label = next(label for label in ("1", "2", "3", "4") if label != correct_label)

        if section_seen[section] < section_correct_counts.get(section, 0):
            answers[question_id] = str(correct_label)
        else:
            answers[question_id] = wrong_label
        section_seen[section] += 1

    return answers


def _load_question(conn, qid: str) -> Question:
    row = conn.execute("SELECT * FROM questions WHERE question_id = ?", (qid,)).fetchone()
    assert row is not None
    return Question.from_row(row)


class TestPreflight:
    def test_preflight_ready_on_full_eligible_db(self, full_eligible_db):
        result = get_baseline_preflight(full_eligible_db)

        assert result["full_ready"] is True
        assert result["smoke_ready"] is True
        assert result["required"] == FOUNDATION_PULSE_REQUIREMENTS
        assert result["available"]["Quant/DI"] == 80
        assert result["missing"] == {}

    def test_preflight_underfilled_full(self, underfilled_db):
        result = get_baseline_preflight(underfilled_db)

        assert result["full_ready"] is False
        assert result["missing"]["Quant/DI"] == 70
        assert result["smoke_ready"] is True

    def test_preflight_smoke_not_ready_when_section_short(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Quant/DI": 1, "Reasoning": 1, "English": 1, "GK/GA": 1})

        result = get_baseline_preflight(study_db)

        assert result["smoke_ready"] is False
        assert result["full_ready"] is False

    def test_preflight_uses_web_safe_unique_question_pool(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Reasoning": 40, "English": 40, "GK/GA": 40})
        for index in range(77):
            _insert_question(conn, f"quant_clean_{index}", "Quant/DI")
        _insert_question(conn, "quant_dup_a", "Quant/DI", question_text="Duplicate stem?")
        _insert_question(conn, "quant_dup_b", "Quant/DI", question_text="Duplicate stem?")
        _insert_question(
            conn,
            "quant_visual",
            "Quant/DI",
            question_text="Use the missing chart to answer.",
            question_modality="graph_chart",
            visual_required=1,
        )
        _insert_question(
            conn,
            "quant_mojibake",
            "Quant/DI",
            question_text="Find the value of âˆš16.",
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["raw_available"]["Quant/DI"] == 81
        assert result["available"]["Quant/DI"] == 78
        assert result["missing"]["Quant/DI"] == 2
        assert result["full_ready"] is False
        assert result["quality_exclusions"]["duplicate_content"] == 1
        assert result["quality_exclusions"]["missing_visual_asset"] == 1
        assert result["quality_exclusions"]["mojibake"] == 1

    def test_visual_question_with_existing_asset_is_available(self, study_db, tmp_path, monkeypatch):
        monkeypatch.setenv("SSC_QUESTION_ASSET_ROOTS", str(tmp_path))
        conn = study_db.connect()
        asset = tmp_path / "chart.png"
        asset.write_bytes(b"\x89PNG\r\n\x1a\n")
        _insert_question(
            conn,
            "visual_ok",
            "Quant/DI",
            question_text="Use the chart to answer.",
            question_modality="graph_chart",
            visual_required=1,
            question_crop_path=str(asset),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Quant/DI"] == 1
        assert result["quality_exclusions"].get("missing_visual_asset", 0) == 0

    def test_visual_question_with_missing_asset_is_excluded(self, study_db, tmp_path):
        conn = study_db.connect()
        _insert_question(
            conn,
            "visual_missing",
            "Quant/DI",
            question_text="Use the chart to answer.",
            question_modality="graph_chart",
            visual_required=1,
            question_crop_path=str(tmp_path / "missing.png"),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Quant/DI"] == 0
        assert result["quality_exclusions"]["missing_asset"] == 1

    def test_incomplete_continuation_stem_is_excluded(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "fragment_stem",
            "Reasoning",
            question_text=(
                "pair does not belong to that group? (NOTE: Operations should be "
                "performed on the whole numbers.) (23/09/2024 SHIFT-3)"
            ),
            question_modality="math_formula",
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Reasoning"] == 0
        assert result["quality_exclusions"]["incomplete_stem"] == 1

    def test_symbol_blank_and_currency_starts_are_not_incomplete_stems(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "blank_start",
            "GK/GA",
            question_text="________ is the structural and functional unit of kidney.",
        )
        _insert_question(
            conn,
            "formula_start",
            "Quant/DI",
            question_text="(1/cos theta - 1/sin theta) is equal to:",
        )
        _insert_question(
            conn,
            "currency_start",
            "Quant/DI",
            question_text="Rs. 4,300 becomes Rs. 4,644 in 2 years at simple interest.",
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["GK/GA"] == 1
        assert result["available"]["Quant/DI"] == 2
        assert result["quality_exclusions"].get("incomplete_stem", 0) == 0

    def test_blank_option_text_is_invalid_options(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "blank_options",
            "Reasoning",
            options=[
                {"label": "1", "text": "13 - 8 - 109"},
                {"label": "2", "text": "21 - 4 - 89"},
                {"label": "3", "text": ""},
                {"label": "4", "text": ""},
            ],
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Reasoning"] == 0
        assert result["quality_exclusions"]["invalid_options"] == 1

    @pytest.mark.parametrize("status", ["PASS_LLM_ONLY", "BLOCKED"])
    def test_unverified_answer_status_is_excluded(self, study_db, status):
        conn = study_db.connect()
        _insert_question(conn, f"unverified_{status}", "Reasoning", evidence_status=status)
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Reasoning"] == 0
        assert result["quality_exclusions"]["unverified_answer"] == 1

    def test_correct_label_missing_from_options_is_answer_integrity_failure(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "missing_label",
            "Reasoning",
            correct_label="4",
            options=[
                {"label": "1", "text": "A"},
                {"label": "2", "text": "B"},
                {"label": "3", "text": "C"},
                {"label": "5", "text": "D"},
            ],
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Reasoning"] == 0
        assert result["quality_exclusions"]["answer_integrity_failure"] == 1

    def test_correct_option_text_mismatch_is_answer_integrity_failure(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "text_mismatch",
            "Reasoning",
            correct_label="2",
            correct_option_text="Expected answer text",
            options=[
                {"label": "1", "text": "A"},
                {"label": "2", "text": "Different parsed text"},
                {"label": "3", "text": "C"},
                {"label": "4", "text": "D"},
            ],
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Reasoning"] == 0
        assert result["quality_exclusions"]["answer_integrity_failure"] == 1

    def test_passage_dependent_orphan_stem_is_excluded(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "orphan_blank",
            "English",
            question_text="Select the most appropriate option to fill in blank number 1.",
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["English"] == 0
        assert result["quality_exclusions"]["passage_dependent"] == 1

    def test_sentence_split_stem_is_not_passage_dependent(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "sentence_split",
            "English",
            question_text=(
                "The following sentence has been split into four segments. "
                "Identify the segment that contains a grammatical error.\n"
                "Had you / not reached in time, / we will have / lost our lives."
            ),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["English"] == 1
        assert result["quality_exclusions"].get("passage_dependent", 0) == 0

    def test_linked_passage_dependent_stem_is_available(self, study_db):
        conn = study_db.connect()
        cursor = conn.execute(
            """INSERT INTO passages (pdf_name, source_page, passage_text)
               VALUES ('test_pdf', 1, 'Recovered cloze passage with (1)______ context.')"""
        )
        passage_id = cursor.lastrowid
        _insert_question(
            conn,
            "linked_blank",
            "English",
            question_text="Select the most appropriate option to fill in blank number 1.",
        )
        conn.execute(
            "UPDATE questions SET passage_id = ? WHERE question_id = 'linked_blank'",
            (passage_id,),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["English"] == 1
        assert result["quality_exclusions"].get("passage_dependent", 0) == 0

    def test_self_contained_cloze_passage_is_available(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "self_contained_cloze",
            "English",
            question_text=(
                "In the following passage, some words have been deleted. Read the passage "
                "carefully and select the most appropriate option to fill in each blank. "
                "Climate change (1) _____ an imminent threat to our planet. "
                "Select the most appropriate option to fill in blank number 1."
            ),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["English"] == 1
        assert result["quality_exclusions"].get("passage_dependent", 0) == 0

    def test_missing_existing_asset_path_is_missing_asset_even_for_text_question(self, study_db, tmp_path):
        conn = study_db.connect()
        _insert_question(
            conn,
            "drifted_crop",
            "Quant/DI",
            question_crop_path=str(tmp_path / "gone.png"),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Quant/DI"] == 0
        assert result["quality_exclusions"]["missing_asset"] == 1

    def test_asset_urls_do_not_include_drifted_paths(self, study_db, tmp_path):
        conn = study_db.connect()
        _insert_question(
            conn,
            "drifted_url",
            "Quant/DI",
            question_crop_path=str(tmp_path / "gone.png"),
        )
        conn.commit()

        assert _question_asset_urls(_load_question(conn, "drifted_url")) == {}

    def test_unmaskable_answer_leaking_source_is_excluded(self, study_db, tmp_path, monkeypatch):
        monkeypatch.setenv("SSC_QUESTION_ASSET_ROOTS", str(tmp_path))
        image_path = tmp_path / "plain.png"
        Image.new("RGB", (240, 120), "white").save(image_path)
        conn = study_db.connect()
        _insert_question(
            conn,
            "leak_without_marker",
            "Quant/DI",
            pdf_name=next(iter(ANSWER_LEAKING_SOURCES)),
            question_crop_path=str(image_path),
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Quant/DI"] == 0
        assert result["quality_exclusions"]["unmaskable_answer_leak"] == 1

    def test_text_only_answer_leaking_source_without_crop_is_allowed(self, study_db):
        conn = study_db.connect()
        _insert_question(
            conn,
            "leak_text_only",
            "Quant/DI",
            pdf_name=next(iter(ANSWER_LEAKING_SOURCES)),
            question_crop_path=None,
        )
        conn.commit()

        result = get_baseline_preflight(study_db)

        assert result["available"]["Quant/DI"] == 1
        assert result["quality_exclusions"].get("unmaskable_answer_leak", 0) == 0

    def test_leaking_source_page_asset_url_is_never_emitted(self, study_db, tmp_path, monkeypatch):
        monkeypatch.setenv("SSC_QUESTION_ASSET_ROOTS", str(tmp_path))
        crop = tmp_path / "question_crops_masked" / "masked.png"
        crop.parent.mkdir(parents=True)
        crop.write_bytes(b"\x89PNG\r\n\x1a\n")
        page = tmp_path / "page.png"
        page.write_bytes(b"\x89PNG\r\n\x1a\n")
        conn = study_db.connect()
        _insert_question(
            conn,
            "leak_masked",
            "Quant/DI",
            pdf_name=next(iter(ANSWER_LEAKING_SOURCES)),
            question_crop_path=str(crop),
            page_asset_path=str(page),
        )
        conn.commit()

        urls = _question_asset_urls(_load_question(conn, "leak_masked"))

        assert urls == {"crop": "/api/question-assets/leak_masked/crop"}


class TestStart:
    def test_smoke_start_exact_split(self, smoke_eligible_db):
        result = start_baseline_exam(smoke_eligible_db, "smoke")

        assert result["mode"] == "smoke"
        assert result["question_count"] == 5
        assert len(result["exam_id"]) == 36
        assert result["exam_token"]

        sections = [question["section"] for question in result["questions"]]
        assert sections.count("Quant/DI") == 2
        assert sections.count("Reasoning") == 1
        assert sections.count("English") == 1
        assert sections.count("GK/GA") == 1

    def test_full_start_exact_split(self, full_eligible_db):
        result = start_baseline_exam(full_eligible_db, "full")

        assert result["mode"] == "full"
        assert result["question_count"] == 200

        sections = [question["section"] for question in result["questions"]]
        for section, required in FOUNDATION_PULSE_REQUIREMENTS.items():
            assert sections.count(section) == required

    def test_start_rejects_raw_ready_but_web_unsafe_pool(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Reasoning": 40, "English": 40, "GK/GA": 40})
        for index in range(79):
            _insert_question(conn, f"quant_clean_{index}", "Quant/DI")
        _insert_question(
            conn,
            "quant_visual_only_extra",
            "Quant/DI",
            question_text="Use the missing graph to answer.",
            question_modality="graph_chart",
            visual_required=1,
        )
        conn.commit()

        with pytest.raises(BaselineWebError, match="web-safe"):
            start_baseline_exam(study_db, "full")

    def test_start_excludes_holdout_questions(self, full_eligible_db):
        result = start_baseline_exam(full_eligible_db, "full")
        question_ids = {question["question_id"] for question in result["questions"]}

        conn = full_eligible_db.connect()
        holdout_rows = conn.execute(
            "SELECT question_id FROM questions WHERE is_holdout = 1"
        ).fetchall()
        holdout_ids = {row["question_id"] for row in holdout_rows}
        assert question_ids.isdisjoint(holdout_ids)

    def test_start_response_has_no_correct_answers(self, smoke_eligible_db):
        result = start_baseline_exam(smoke_eligible_db, "smoke")

        for question in result["questions"]:
            assert "correct_option_label" not in question
            assert "correct_option_text" not in question
            for option in question["options"]:
                assert set(option.keys()) == {"label", "text"}

    def test_start_response_includes_linked_passage_text(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Quant/DI": 2, "Reasoning": 1, "GK/GA": 1})
        cursor = conn.execute(
            """INSERT INTO passages (pdf_name, source_page, passage_text)
               VALUES ('test_pdf', 1, 'Recovered cloze passage with (1)______ context.')"""
        )
        _insert_question(
            conn,
            "linked_blank",
            "English",
            question_text="Select the most appropriate option to fill in blank number 1.",
        )
        conn.execute(
            "UPDATE questions SET passage_id = ? WHERE question_id = 'linked_blank'",
            (cursor.lastrowid,),
        )
        conn.commit()

        result = start_baseline_exam(study_db, "smoke")
        linked = next(q for q in result["questions"] if q["question_id"] == "linked_blank")

        assert linked["passage_text"] == "Recovered cloze passage with (1)______ context."

    def test_start_response_includes_visual_asset_metadata_without_raw_paths(self, study_db, tmp_path, monkeypatch):
        monkeypatch.setenv("SSC_QUESTION_ASSET_ROOTS", str(tmp_path))
        conn = study_db.connect()
        asset = tmp_path / "chart.png"
        asset.write_bytes(b"\x89PNG\r\n\x1a\n")
        _seed_section_counts(conn, {"Quant/DI": 1, "Reasoning": 1, "English": 1, "GK/GA": 1})
        _insert_question(
            conn,
            "visual_ok",
            "Quant/DI",
            question_text="Use the chart to answer.",
            question_modality="graph_chart",
            visual_required=1,
            question_crop_path=str(asset),
        )
        conn.commit()

        result = start_baseline_exam(study_db, "smoke")
        visual = next(q for q in result["questions"] if q["question_id"] == "visual_ok")

        assert visual["question_modality"] == "graph_chart"
        assert visual["visual_required"] is True
        assert visual["asset_urls"]["crop"] == "/api/question-assets/visual_ok/crop"
        assert str(asset) not in json.dumps(visual)

    def test_start_refuses_answer_integrity_excluded_rows(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Quant/DI": 1, "English": 1, "GK/GA": 1})
        _insert_question(
            conn,
            "bad_reasoning",
            "Reasoning",
            correct_label="2",
            correct_option_text="Expected",
        )
        conn.commit()

        with pytest.raises(BaselineWebError, match="web-safe"):
            start_baseline_exam(study_db, "smoke")


class TestAnswerLeakMasking:
    def test_remap_question_assets_rewrites_only_verified_current_files(self, study_db, tmp_path):
        root = tmp_path
        pdf_name = "test_pdf"
        current = root / "pipeline_output" / "p2_gemini" / pdf_name / "assets" / "question_crops"
        current.mkdir(parents=True)
        current_crop = current / "test_pdf_p01_q001_question.png"
        Image.new("RGB", (20, 20), "white").save(current_crop)
        stale_crop = (
            root / "extraction_reruns" / "p2_all_pdfs_20260524" / pdf_name
            / "assets" / "question_crops" / current_crop.name
        )
        stale_page = (
            root / "extraction_reruns" / "p2_all_pdfs_20260524" / pdf_name
            / "page_images" / "page_01.png"
        )
        conn = study_db.connect()
        _insert_question(
            conn,
            "stale_asset",
            "Quant/DI",
            pdf_name=pdf_name,
            question_crop_path=str(stale_crop),
            page_asset_path=str(stale_page),
        )
        conn.commit()

        stats = remap_question_assets(conn, repo_root=root)

        row = conn.execute(
            "SELECT question_crop_path, page_asset_path FROM questions WHERE question_id = ?",
            ("stale_asset",),
        ).fetchone()
        assert stats.rows_remapped == 1
        assert row["question_crop_path"] == str(current_crop.resolve())
        assert row["page_asset_path"] is None

    def test_mask_answer_leaking_crop_removes_answer_marker_region(self, tmp_path):
        source = (
            "pipeline_output/p2_gemini/2021_tier1_sscportal_shift1_response_sheet/"
            "assets/question_crops/"
            "2021_tier1_sscportal_shift1_response_sheet_p01_q003_question.png"
        )
        output = tmp_path / "masked.png"

        result = mask_answer_leaking_crop(source, output)

        assert result.masked_path == output
        assert result.cut_y is not None
        assert output.is_file()
        with Image.open(source) as original, Image.open(output) as masked:
            assert masked.height < original.height
            assert masked.height <= result.cut_y
            assert masked.width == original.width
            assert masked.height > 40

    def test_mask_answer_leaking_crop_reports_unmaskable_image(self, tmp_path):
        source = tmp_path / "plain.png"
        Image.new("RGB", (240, 120), "white").save(source)
        output = tmp_path / "masked.png"

        result = mask_answer_leaking_crop(source, output)

        assert result.masked_path is None
        assert result.reason == "answer_marker_not_found"
        assert not output.exists()

    def test_remap_question_assets_excludes_shared_page_images_without_masking(self, study_db, tmp_path):
        root = tmp_path
        pdf_name = "2020_tier2_kdcampus_answer_key"
        page_dir = root / "pipeline_output" / "p2_gemini" / pdf_name / "page_images"
        page_dir.mkdir(parents=True)
        shared_page = page_dir / "page_02.png"
        image = Image.new("RGB", (240, 120), "white")
        for x in range(0, 12):
            image.putpixel((x, 35), (220, 30, 30))
        image.save(shared_page)
        stale_page = (
            root / "extraction_reruns" / "p2_all_pdfs_20260524" / pdf_name
            / "page_images" / shared_page.name
        )
        conn = study_db.connect()
        _insert_question(
            conn,
            "shared_page_q1",
            "Quant/DI",
            pdf_name=pdf_name,
            question_crop_path=str(stale_page),
        )
        _insert_question(
            conn,
            "shared_page_q2",
            "Quant/DI",
            pdf_name=pdf_name,
            question_crop_path=str(stale_page),
        )
        conn.commit()

        stats = remap_question_assets(conn, repo_root=root)

        rows = conn.execute(
            """SELECT question_crop_path FROM questions
               WHERE question_id IN ('shared_page_q1', 'shared_page_q2')
               ORDER BY question_id"""
        ).fetchall()
        assert stats.masked_rows == 0
        assert stats.unmaskable_answer_leak_rows == 2
        assert [row["question_crop_path"] for row in rows] == [None, None]
        assert not (page_dir.parent / "question_crops_masked").exists()
        result = get_baseline_preflight(study_db)
        assert result["available"]["Quant/DI"] == 2
        assert result["quality_exclusions"].get("unmaskable_answer_leak", 0) == 0

    def test_start_invalid_mode_raises(self, smoke_eligible_db):
        with pytest.raises(BaselineWebError, match="Invalid mode"):
            start_baseline_exam(smoke_eligible_db, "turbo")

    def test_start_full_underfilled_raises(self, underfilled_db):
        with pytest.raises(BaselineWebError, match="requires 80"):
            start_baseline_exam(underfilled_db, "full")


class TestSubmit:
    def test_submit_persists_session_and_attempts(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )

        result = submit_baseline_exam(smoke_eligible_db, payload)

        assert result["mode"] == "smoke"
        assert result["question_count"] == 5
        assert result["session_id"] is not None

        conn = smoke_eligible_db.connect()
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert session["session_type"] == "analysis"
        assert session["notes"] == f"phase1_web_smoke:{started['exam_id']}"

        attempts = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert attempts["c"] == 5

    def test_submit_requires_exam_token(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])

        with pytest.raises(BaselineWebError, match="exam_token"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_invalid_exam_token(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])
        payload["exam_token"] = "not-a-valid-token"

        with pytest.raises(BaselineWebError, match="exam_token"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_malformed_answer_entry(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])
        payload["exam_token"] = started["exam_token"]
        payload["answers"][0] = None

        with pytest.raises(BaselineWebError, match="answer entry"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_full_uses_foundation_pulse_session_type(self, full_eligible_db):
        started = start_baseline_exam(full_eligible_db, "full")
        payload = _build_submit_payload(
            started["exam_id"],
            "full",
            started["questions"],
            exam_token=started["exam_token"],
        )

        result = submit_baseline_exam(full_eligible_db, payload)

        conn = full_eligible_db.connect()
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert session["session_type"] == "foundation_pulse"
        assert session["notes"] == f"phase1_web_full:{started['exam_id']}"
        assert result["question_count"] == 200

    def test_submit_computes_correctness_server_side(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        first_id = started["questions"][0]["question_id"]

        conn = smoke_eligible_db.connect()
        correct_label = conn.execute(
            "SELECT correct_option_label FROM questions WHERE question_id = ?",
            (first_id,),
        ).fetchone()["correct_option_label"]
        wrong_label = "2" if correct_label != "2" else "3"

        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={
                first_id: correct_label,
                started["questions"][1]["question_id"]: wrong_label,
            },
        )

        result = submit_baseline_exam(smoke_eligible_db, payload)

        assert result["correct_count"] == 1
        assert result["wrong_count"] == 1
        assert result["skipped_count"] == 3
        assert result["accuracy"] == pytest.approx(0.2)
        assert result["marks_earned"] == pytest.approx(1.5)
        assert result["by_section"][started["questions"][0]["section"]]["correct"] == 1

    def test_submit_updates_sm2_state(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        first_id = started["questions"][0]["question_id"]

        conn = smoke_eligible_db.connect()
        before = conn.execute(
            "SELECT COUNT(*) as c FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
            (first_id,),
        ).fetchone()["c"]
        assert before == 0

        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={first_id: "1"},
        )
        submit_baseline_exam(smoke_eligible_db, payload)

        row = conn.execute(
            "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
            (first_id,),
        ).fetchone()
        assert row is not None
        assert row["last_review"] is not None
        assert row["last_quality"] is not None

    def test_submit_treats_missing_answers_as_skipped(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
        )

        submit_baseline_exam(smoke_eligible_db, payload)

        conn = smoke_eligible_db.connect()
        skipped = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE student_label = 'skipped'"
        ).fetchone()
        assert skipped["c"] == 5

    def test_submit_persists_marked_for_review(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        marked_id = started["questions"][0]["question_id"]
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
        )
        payload["answers"][0]["marked_for_review"] = True
        payload["answers"][0]["user_answer"] = None

        result = submit_baseline_exam(smoke_eligible_db, payload)

        conn = smoke_eligible_db.connect()
        row = conn.execute(
            """SELECT marked_for_review, student_label
               FROM attempts
               WHERE session_id = ? AND question_id = ?""",
            (result["session_id"], marked_id),
        ).fetchone()
        assert row["marked_for_review"] == 1
        assert row["student_label"] == "skipped"

    def test_duplicate_submit_is_idempotent(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )

        first = submit_baseline_exam(smoke_eligible_db, payload)
        second = submit_baseline_exam(smoke_eligible_db, payload)

        assert second == first

        conn = smoke_eligible_db.connect()
        sessions = conn.execute(
            "SELECT COUNT(*) as c FROM sessions WHERE notes = ?",
            (f"phase1_web_smoke:{started['exam_id']}",),
        ).fetchone()
        attempts = conn.execute("SELECT COUNT(*) as c FROM attempts").fetchone()
        assert sessions["c"] == 1
        assert attempts["c"] == 5

    def test_submit_rejects_holdout_question(self, smoke_eligible_db):
        conn = smoke_eligible_db.connect()
        _insert_question(conn, "holdout_trap", "Quant/DI", is_holdout=1)
        conn.commit()

        started = start_baseline_exam(smoke_eligible_db, "smoke")
        questions = list(started["questions"])
        questions[0] = {
            **questions[0],
            "question_id": "holdout_trap",
        }
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                smoke_eligible_db,
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="Holdout question not allowed"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_unknown_question(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        questions = list(started["questions"])
        questions[0] = {**questions[0], "question_id": "missing_q"}
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                smoke_eligible_db,
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="Unknown question_id"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_wrong_smoke_distribution(self, smoke_eligible_db):
        conn = smoke_eligible_db.connect()
        _insert_question(conn, "quant_extra", "Quant/DI")
        conn.commit()

        started = start_baseline_exam(smoke_eligible_db, "smoke")
        used_ids = {question["question_id"] for question in started["questions"]}
        extra = conn.execute(
            """SELECT question_id FROM questions
               WHERE section = 'Quant/DI' AND is_holdout = 0
                 AND question_id NOT IN ({})
               LIMIT 1""".format(",".join("?" for _ in used_ids)),
            tuple(used_ids),
        ).fetchone()["question_id"]

        questions = list(started["questions"])
        reasoning_index = next(
            index for index, question in enumerate(questions) if question["section"] == "Reasoning"
        )
        questions[reasoning_index] = {**questions[reasoning_index], "question_id": extra}
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                smoke_eligible_db,
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="smoke submit requires"):
            submit_baseline_exam(smoke_eligible_db, payload)


class TestResult:
    def test_get_baseline_result_returns_persisted_score(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )
        submitted = submit_baseline_exam(smoke_eligible_db, payload)

        result = get_baseline_result(smoke_eligible_db, submitted["session_id"])

        assert result == submitted
        assert set(result["by_section"]) <= set(SMOKE_REQUIREMENTS)

    def test_full_submit_creates_and_prunes_backups_and_marks(self, tmp_path):
        db_path = tmp_path / "data" / "study.db"
        db = Database(db_path)
        conn = db.connect()
        _seed_section_counts(
            conn,
            {
                "Quant/DI": 80,
                "Reasoning": 40,
                "English": 40,
                "GK/GA": 40,
            },
        )
        backups_dir = db_path.parent / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        for index in range(25):
            (backups_dir / f"study-20260101-0000{index:02d}.db").write_bytes(b"old")

        started = start_baseline_exam(db, "full")
        payload = _build_submit_payload(
            started["exam_id"],
            "full",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )

        result = submit_baseline_exam(db, payload)
        backup_files = sorted(backups_dir.glob("study-*.db"))

        assert len(backup_files) == 20
        assert any(path.stat().st_size > 3 for path in backup_files)
        assert result["marks_max"] == 400.0
        assert result["correct_count"] + result["wrong_count"] + result["skipped_count"] == 200

    def test_exam_token_survives_database_reopen(self, tmp_path):
        db_path = tmp_path / "study.db"
        db = Database(db_path)
        conn = db.connect()
        _seed_section_counts(conn, {"Quant/DI": 2, "Reasoning": 1, "English": 1, "GK/GA": 1})

        started = start_baseline_exam(db, "smoke")
        db.close()

        from ssc_study import baseline_web as baseline_web_module
        baseline_web_reloaded = importlib.reload(baseline_web_module)
        reopened = Database(db_path)
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
        )

        result = baseline_web_reloaded.submit_baseline_exam(reopened, payload)

        assert result["session_id"] is not None

    def test_get_baseline_result_missing_session_raises(self, smoke_eligible_db):
        from ssc_study import baseline_web as baseline_web_module

        with pytest.raises(baseline_web_module.BaselineWebError, match="Session not found"):
            get_baseline_result(smoke_eligible_db, 9999)

    def test_get_baseline_result_rejects_non_web_session(self, smoke_eligible_db):
        from ssc_study import baseline_web as baseline_web_module

        conn = smoke_eligible_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at, ended_at, notes) "
            "VALUES ('mock', '2026-01-01', '2026-01-01', 'cli session')"
        )
        conn.commit()
        session_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]

        with pytest.raises(baseline_web_module.BaselineWebError, match="Session not found"):
            get_baseline_result(smoke_eligible_db, session_id)

    def test_smoke_next_steps_do_not_expose_phase3_guidance(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
        )

        result = submit_baseline_exam(smoke_eligible_db, payload)

        assert result["next_steps"]["mode"] == "smoke"
        assert result["next_steps"]["weak_sections"] == []
        assert result["next_steps"]["overall_action"]["action_type"] == "smoke_warning"
        assert result["next_steps"]["guardian_plan"] is None

    def test_full_next_steps_classify_threshold_tiers(self, full_eligible_db):
        started = start_baseline_exam(full_eligible_db, "full")
        answers = _build_section_accuracy_answers(
            full_eligible_db,
            started["questions"],
            {
                "Quant/DI": 44,
                "Reasoning": 26,
                "English": 28,
                "GK/GA": 21,
            },
        )
        payload = _build_submit_payload(
            started["exam_id"],
            "full",
            started["questions"],
            exam_token=started["exam_token"],
            answers=answers,
        )

        result = submit_baseline_exam(full_eligible_db, payload)
        weak_sections = {
            row["section"]: row
            for row in result["next_steps"]["weak_sections"]
        }

        assert result["next_steps"]["overall_action"]["action_type"] == "remediation_excluded"
        assert weak_sections["GK/GA"]["tier"] == "remediation_excluded"
        assert weak_sections["Quant/DI"]["tier"] == "remediation_priority"
        assert weak_sections["Reasoning"]["tier"] == "paired_remediation"
        assert "English" not in weak_sections

    def test_full_next_steps_unlock_guardian_when_all_sections_clear_gate(self, full_eligible_db):
        started = start_baseline_exam(full_eligible_db, "full")
        answers = _build_section_accuracy_answers(
            full_eligible_db,
            started["questions"],
            {
                "Quant/DI": 56,
                "Reasoning": 28,
                "English": 28,
                "GK/GA": 28,
            },
        )
        payload = _build_submit_payload(
            started["exam_id"],
            "full",
            started["questions"],
            exam_token=started["exam_token"],
            answers=answers,
        )

        result = submit_baseline_exam(full_eligible_db, payload)

        assert result["next_steps"]["weak_sections"] == []
        assert result["next_steps"]["overall_action"]["action_type"] == "guardian_main_grind"
        assert result["next_steps"]["guardian_plan"] is not None
        assert result["next_steps"]["guardian_plan"]["total_minutes"] == 180
