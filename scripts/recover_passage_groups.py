"""Recover passage text for passage-dependent baseline questions.

The recovery is intentionally conservative: it only links questions when the
source PDF page exposes a clear ``Comprehension:`` passage block. Unmatched rows
are reported and remain excluded by the web baseline gate.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ssc_study.db import Database


PASSAGE_SOURCE_DIR = Path("answer_key_candidates_staging")
WHOLE_PAGE_ONLY_SOURCES = {
    "2020_tier2_kdcampus_answer_key",
    "2024_tier1_appx_answer_key",
}
DEPENDENT_RE = re.compile(
    r"\b(?:fill in (?:the )?blank|blank)\s*(?:no\.?|number)\s*\d+\b|"
    r"\b(?:according to|as per|from|in|above|the)\s+(?:the\s+)?(?:above\s+)?passage\b|"
    r"\bpassage\s+(?:mainly|suggests|is about|talks about)\b",
    re.IGNORECASE,
)
QUESTION_START_RE = re.compile(
    r"\nSubQuestion No\s*:\s*\d+\b|"
    r"\n(?:SubQuestion No\s*:\s*\d+\s*)?(?:Q\.?\s*)?\d+[\.)]?\s+Select\b|"
    r"\nQ\.?\s*\d+\b|\n\d+\.\s+",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Candidate:
    question_id: str
    pdf_name: str
    source_page: int
    global_question_number: int
    question_text: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _source_pdf(pdf_name: str, source_dir: Path) -> Path:
    return source_dir / f"{pdf_name}.pdf"


def _page_text(pdf_path: Path, page_number: int) -> str:
    try:
        import fitz
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required for passage recovery") from exc

    with fitz.open(pdf_path) as doc:
        if page_number < 1 or page_number > len(doc):
            return ""
        return doc[page_number - 1].get_text("text")


def _extract_passage_from_page(text: str) -> str | None:
    match = re.search(r"Comprehension\s*:\s*", text, re.IGNORECASE)
    if match:
        tail = text[match.end() :]
    else:
        match = re.search(
            r"In the following passage,?\s+some words have been deleted\.\s*"
            r"Read the passage carefully and select the most appropriate option to fill in each blank\.\s*",
            text,
            re.IGNORECASE,
        )
        if not match:
            return None
        tail = text[match.end() :]
    stop = QUESTION_START_RE.search(tail)
    passage = tail[: stop.start()] if stop else tail
    select_stop = re.search(
        r"\bSelect the most appropriate option to fill in blank number\s+\d+\b",
        passage,
        re.IGNORECASE,
    )
    if select_stop:
        passage = passage[: select_stop.start()]
    passage = re.sub(
        r"^In the following passage,?\s+some words have been deleted\.\s*",
        "",
        passage,
        flags=re.IGNORECASE,
    )
    passage = re.sub(
        r"^(?:Read the passage carefully and\s+)?(?:Fill in the blanks?|select the most appropriate option).*?\.\s*",
        "",
        passage,
        flags=re.IGNORECASE,
    )
    passage = _normalize_text(passage)
    if len(passage.split()) < 20:
        return None
    return passage


def _load_candidates(conn: sqlite3.Connection) -> list[Candidate]:
    rows = conn.execute(
        """SELECT question_id, pdf_name, source_page, global_question_number, question_text
           FROM questions
           WHERE is_holdout = 0
             AND passage_id IS NULL
           ORDER BY pdf_name, global_question_number"""
    ).fetchall()
    candidates: list[Candidate] = []
    for row in rows:
        text = str(row["question_text"] or "")
        if DEPENDENT_RE.search(text):
            candidates.append(
                Candidate(
                    question_id=str(row["question_id"]),
                    pdf_name=str(row["pdf_name"]),
                    source_page=int(row["source_page"]),
                    global_question_number=int(row["global_question_number"]),
                    question_text=text,
                )
            )
    return candidates


def recover_passages(db_path: Path, source_dir: Path) -> dict[str, object]:
    db = Database(db_path)
    conn = db.connect()
    candidates = _load_candidates(conn)
    passage_cache: dict[tuple[str, str], int] = {}
    active_by_pdf: dict[str, str] = {}
    linked: list[str] = []
    skipped: list[dict[str, object]] = []

    with db.transaction() as tx:
        for candidate in candidates:
            if candidate.pdf_name in WHOLE_PAGE_ONLY_SOURCES:
                skipped.append({**candidate.__dict__, "reason": "whole_page_only_source_out_of_scope"})
                continue
            pdf_path = _source_pdf(candidate.pdf_name, source_dir)
            if not pdf_path.is_file():
                skipped.append({**candidate.__dict__, "reason": "source_pdf_missing"})
                continue

            text = _page_text(pdf_path, candidate.source_page)
            passage = _extract_passage_from_page(text)
            if passage:
                active_by_pdf[candidate.pdf_name] = passage
            else:
                passage = active_by_pdf.get(candidate.pdf_name)
            if not passage:
                skipped.append({**candidate.__dict__, "reason": "passage_not_confidently_locatable"})
                continue

            cache_key = (candidate.pdf_name, passage)
            passage_id = passage_cache.get(cache_key)
            if passage_id is None:
                existing = tx.execute(
                    """SELECT passage_id FROM passages
                       WHERE pdf_name = ? AND passage_text = ?""",
                    (candidate.pdf_name, passage),
                ).fetchone()
                if existing:
                    passage_id = int(existing["passage_id"])
                else:
                    cursor = tx.execute(
                        """INSERT INTO passages (pdf_name, source_page, passage_text)
                           VALUES (?, ?, ?)""",
                        (candidate.pdf_name, candidate.source_page, passage),
                    )
                    passage_id = int(cursor.lastrowid)
                passage_cache[cache_key] = passage_id

            tx.execute(
                "UPDATE questions SET passage_id = ? WHERE question_id = ?",
                (passage_id, candidate.question_id),
            )
            linked.append(candidate.question_id)

    passages_created = conn.execute("SELECT COUNT(*) AS c FROM passages").fetchone()["c"]
    still_excluded = conn.execute(
        """SELECT q.question_id, q.pdf_name, q.source_page, q.global_question_number, q.question_text
           FROM questions q
           WHERE q.passage_id IS NULL
           ORDER BY q.pdf_name, q.global_question_number"""
    ).fetchall()
    still_excluded = [
        dict(row)
        for row in still_excluded
        if DEPENDENT_RE.search(str(row["question_text"] or ""))
    ]
    db.close()
    return {
        "candidate_count": len(candidates),
        "passages_created": int(passages_created),
        "questions_linked": len(linked),
        "linked_question_ids": linked,
        "skipped": skipped,
        "still_dependent_unlinked": still_excluded,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/study.db"))
    parser.add_argument("--source-dir", type=Path, default=PASSAGE_SOURCE_DIR)
    args = parser.parse_args()
    result = recover_passages(args.db, args.source_dir)
    print(f"candidate_count={result['candidate_count']}")
    print(f"passages_created={result['passages_created']}")
    print(f"questions_linked={result['questions_linked']}")
    print(f"still_dependent_unlinked={len(result['still_dependent_unlinked'])}")
    for row in result["skipped"]:
        print(
            "skipped {question_id} {pdf_name} p{source_page} q{global_question_number}: {reason}".format(
                **row
            )
        )


if __name__ == "__main__":
    main()
