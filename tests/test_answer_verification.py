from __future__ import annotations

import json
from pathlib import Path

import fitz

from ssc_study.answer_verification import (
    extract_green_answer_labels,
    extract_letter_answer_key_labels,
    reverify_answers,
)


def _insert_question(
    conn,
    qid: str,
    *,
    pdf_name: str,
    global_question_number: int,
    correct_label: str = "1",
    correct_text: str | None = "Old",
    evidence_status: str = "PASS_LLM_ONLY",
) -> None:
    options = [
        {"label": "1", "text": "Alpha"},
        {"label": "2", "text": "Beta"},
        {"label": "3", "text": "Gamma"},
        {"label": "4", "text": "Delta"},
    ]
    conn.execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, evidence_status)
           VALUES (?, ?, 1, ?, 'Reasoning', 2024, 'tier1', 'Question?', ?, ?, ?, ?)""",
        (
            qid,
            pdf_name,
            global_question_number,
            json.dumps(options),
            correct_label,
            correct_text,
            evidence_status,
        ),
    )


def test_extract_green_answer_labels_from_response_sheet_pdf() -> None:
    labels = extract_green_answer_labels(
        Path("answer_key_candidates_staging/2024_tier2_sscportal_jan20_response_sheet.pdf")
    )

    assert labels[1].label == "3"
    assert labels[1].text == "1330"
    assert labels[2].label == "4"
    assert labels[2].text == "47 hours"


def test_reverify_answers_promotes_rows_using_staging_green_spans(study_db, tmp_path: Path) -> None:
    pdf_path = tmp_path / "green_answers.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Q.1", color=(0, 0, 0))
    page.insert_text((50, 70), "Ans", color=(0, 0, 0))
    page.insert_text((90, 70), "1. Alpha", color=(0.9, 0.1, 0.1))
    page.insert_text((90, 90), "2. Beta", color=(0.1, 0.6, 0.1))
    page.insert_text((90, 110), "3. Gamma", color=(0.9, 0.1, 0.1))
    page.insert_text((90, 130), "4. Delta", color=(0.9, 0.1, 0.1))
    doc.save(pdf_path)
    doc.close()

    conn = study_db.connect()
    _insert_question(
        conn,
        "needs_verify",
        pdf_name="green_answers",
        global_question_number=1,
    )
    conn.commit()

    stats = reverify_answers(conn, staging_dir=tmp_path)

    row = conn.execute(
        "SELECT correct_option_label, correct_option_text, evidence_status FROM questions WHERE question_id = ?",
        ("needs_verify",),
    ).fetchone()
    assert stats.resolved_from_staging == 1
    assert stats.resolved_from_crop_ground_truth == 0
    assert row["correct_option_label"] == "2"
    assert row["correct_option_text"] == "Beta"
    assert row["evidence_status"] == "PASS_WITH_EVIDENCE"


def test_extract_letter_answer_key_labels_parses_numeric_parenthesized_answers(tmp_path: Path) -> None:
    pdf_path = tmp_path / "numeric_key.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "ANSWER KEY")
    page.insert_text((50, 80), "1. (2) 2. (4) 3. (1)")
    doc.save(pdf_path)
    doc.close()

    labels = extract_letter_answer_key_labels(pdf_path)

    assert labels[1].label == "2"
    assert labels[2].label == "4"
    assert labels[3].label == "1"


def test_extract_letter_answer_key_labels_parses_worked_solution_option_lines(tmp_path: Path) -> None:
    pdf_path = tmp_path / "worked_solutions.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Q8- Logic text. Hence Option C is the correct answer.")
    page.insert_text((50, 80), "Q9- More text. Hence Option B is the right answer.")
    doc.save(pdf_path)
    doc.close()

    labels = extract_letter_answer_key_labels(pdf_path)

    assert labels[8].label == "3"
    assert labels[9].label == "2"
