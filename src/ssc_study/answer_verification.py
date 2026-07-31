"""Answer re-verification helpers for staged answer-key evidence."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz

from .baseline_web import _web_baseline_rejection_reason
from .corpus_assets import ANSWER_LEAKING_SOURCES
from .models import Question

VERIFIED_EVIDENCE_STATUS = "PASS_WITH_EVIDENCE"


@dataclass(frozen=True)
class VerifiedAnswer:
    label: str
    text: str | None
    source: str


@dataclass
class ReverificationStats:
    before_reasons: Counter[str] = field(default_factory=Counter)
    after_reasons: Counter[str] = field(default_factory=Counter)
    resolved_from_crop_ground_truth: int = 0
    resolved_from_staging: int = 0
    unresolved_by_reason: Counter[str] = field(default_factory=Counter)
    updated_question_ids: list[str] = field(default_factory=list)


def extract_green_answer_labels(pdf_path: str | Path) -> dict[int, VerifiedAnswer]:
    """Return question-number to green-marked correct option from a response sheet PDF."""
    path = Path(pdf_path)
    answers: dict[int, VerifiedAnswer] = {}
    if not path.is_file():
        return answers

    doc = fitz.open(path)
    try:
        for page in doc:
            current_q: int | None = None
            for line in _iter_lines(page):
                text = line["text"].strip()
                match = re.match(r"^Q\.(\d+)\b", text)
                if match:
                    current_q = int(match.group(1))
                    continue
                if current_q is None or current_q in answers:
                    continue

                option = _line_green_option(line)
                if option is not None:
                    label, option_text = option
                    answers[current_q] = VerifiedAnswer(
                        label=label,
                        text=option_text,
                        source=f"{path.name}:green_option_span",
                    )
    finally:
        doc.close()
    return answers


def extract_letter_answer_key_labels(pdf_path: str | Path) -> dict[int, VerifiedAnswer]:
    """Parse compact answer-key pages and worked-solution pages with explicit answer labels."""
    path = Path(pdf_path)
    answers: dict[int, VerifiedAnswer] = {}
    if not path.is_file():
        return answers

    letter_to_label = {"A": "1", "B": "2", "C": "3", "D": "4"}
    doc = fitz.open(path)
    try:
        for page in doc:
            text = page.get_text("text")
            upper_text = text.upper()
            if "ANSWER KEY" in upper_text:
                for match in re.finditer(r"(?<!\d)(\d{1,3})\s*[\.\-:]?\s*(?:\(\s*([1-4])\s*\)|([A-D]))", text):
                    number = int(match.group(1))
                    label = match.group(2) or letter_to_label.get((match.group(3) or "").upper())
                    if label and number not in answers:
                        answers[number] = VerifiedAnswer(
                            label=label,
                            text=None,
                            source=f"{path.name}:answer_key_table",
                        )

            for line in text.splitlines():
                match = re.search(
                    r"\bQ(?:uestion)?\s*(\d{1,3})\s*[-:.].*?Option\s*([A-D])\b.*?(?:correct|right)\s+answer",
                    line,
                    flags=re.IGNORECASE,
                )
                if not match:
                    continue
                number = int(match.group(1))
                label = letter_to_label[match.group(2).upper()]
                if number not in answers:
                    answers[number] = VerifiedAnswer(
                        label=label,
                        text=None,
                        source=f"{path.name}:worked_solution",
                    )
    finally:
        doc.close()
    return answers


def reverify_answers(conn: Any, *, staging_dir: str | Path = "answer_key_candidates_staging") -> ReverificationStats:
    """Promote rows whose answer can be verified from staged row-level evidence."""
    staging = Path(staging_dir)
    stats = ReverificationStats()
    rows = conn.execute(
        """SELECT q.*, p.passage_text
           FROM questions q
           LEFT JOIN passages p ON p.passage_id = q.passage_id
           WHERE q.is_holdout = 0
           ORDER BY q.pdf_name, q.global_question_number, q.question_id"""
    ).fetchall()
    questions = [Question.from_row(row) for row in rows]
    target_questions: list[Question] = []
    for question in questions:
        reason = _web_baseline_rejection_reason(question)
        if reason in {"unverified_answer", "answer_integrity_failure"}:
            stats.before_reasons[reason] += 1
            target_questions.append(question)

    answer_cache: dict[str, dict[int, VerifiedAnswer]] = {}
    for question in target_questions:
        answer = _answer_for_question(question, staging, answer_cache)
        if answer is None:
            stats.unresolved_by_reason[_web_baseline_rejection_reason(question) or "unknown"] += 1
            continue

        option_text = _option_text_for_label(question, answer.label)
        if option_text is None:
            stats.unresolved_by_reason["verified_label_missing_from_options"] += 1
            continue

        conn.execute(
            """UPDATE questions
               SET correct_option_label = ?,
                   correct_option_text = ?,
                   evidence_status = ?
               WHERE question_id = ?""",
            (answer.label, option_text, VERIFIED_EVIDENCE_STATUS, question.question_id),
        )
        stats.updated_question_ids.append(question.question_id)
        if question.pdf_name in ANSWER_LEAKING_SOURCES:
            stats.resolved_from_crop_ground_truth += 1
        else:
            stats.resolved_from_staging += 1

    conn.commit()

    refreshed = conn.execute(
        """SELECT q.*, p.passage_text
           FROM questions q
           LEFT JOIN passages p ON p.passage_id = q.passage_id
           WHERE q.is_holdout = 0
           ORDER BY q.question_id"""
    ).fetchall()
    for row in refreshed:
        reason = _web_baseline_rejection_reason(Question.from_row(row))
        if reason in {"unverified_answer", "answer_integrity_failure"}:
            stats.after_reasons[reason] += 1
    return stats


def _answer_for_question(
    question: Question,
    staging_dir: Path,
    answer_cache: dict[str, dict[int, VerifiedAnswer]],
) -> VerifiedAnswer | None:
    pdf_path = staging_dir / f"{question.pdf_name}.pdf"
    if not pdf_path.is_file():
        return None
    if question.pdf_name not in answer_cache:
        answers = extract_green_answer_labels(pdf_path)
        answers.update({k: v for k, v in extract_letter_answer_key_labels(pdf_path).items() if k not in answers})
        answer_cache[question.pdf_name] = answers
    return answer_cache[question.pdf_name].get(question.global_question_number)


def _option_text_for_label(question: Question, label: str) -> str | None:
    for option in question.options:
        if option.label == label:
            return option.text
    return None


def _iter_lines(page: fitz.Page) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(str(span.get("text", "")) for span in spans)
            if text.strip():
                lines.append({"text": text, "spans": spans})
    return lines


def _line_green_option(line: dict[str, Any]) -> tuple[str, str] | None:
    text = str(line["text"]).strip()
    match = re.match(r"^([1-4])\.\s*(.+)$", text)
    if not match:
        return None
    green_chars = 0
    red_chars = 0
    for span in line["spans"]:
        span_text = str(span.get("text", ""))
        rgb = _int_color_to_rgb(int(span.get("color", 0)))
        if _is_green(rgb):
            green_chars += max(1, len(span_text.strip()))
        elif _is_red(rgb):
            red_chars += max(1, len(span_text.strip()))
    if green_chars > red_chars and green_chars > 0:
        return match.group(1), match.group(2).strip()
    return None


def _int_color_to_rgb(color: int) -> tuple[int, int, int]:
    return (color >> 16) & 255, (color >> 8) & 255, color & 255


def _is_green(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return green >= 90 and green > red * 1.25 and green > blue * 1.25


def _is_red(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return red >= 120 and red > green * 1.25 and red > blue * 1.25
