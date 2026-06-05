"""Corpus loader — one-shot ETL from 19 merged JSONs into SQLite."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._normalize import get_pdf_year_tier, infer_section_from_qnum, normalize_section
from .db import Database, get_connection
from .models import Question


@dataclass
class ImportResult:
    question_count: int
    skipped_count: int
    holdout_count: int
    pdf_count: int
    import_hash: str
    errors: list[str]


def compute_import_hash(pipeline_root: str | Path) -> str:
    """SHA-256 hash of all merged JSONs concatenated — for import idempotency."""
    pipeline = Path(pipeline_root)
    hasher = hashlib.sha256()
    for mp in sorted(pipeline.rglob("merged_questions_global_order.json")):
        hasher.update(mp.read_bytes())
    return hasher.hexdigest()


def import_corpus(
    pipeline_root: str | Path,
    db_path: str | Path,
    holdout_ratio: float = 0.25,
    seed: int = 2027,
) -> ImportResult:
    """Import all 19 merged JSONs into the SQLite database.

    Args:
        pipeline_root: Path to pipeline_output/p2_gemini/
        db_path: Path to the SQLite database file.
        holdout_ratio: Fraction of questions to seal as holdout (per section).
        seed: Random seed for reproducible holdout assignment.

    Returns:
        ImportResult with counts and any errors encountered.
    """
    pipeline = Path(pipeline_root)
    db = Database(db_path)

    import_hash = compute_import_hash(pipeline)

    # Check if already imported
    conn = db.connect()
    existing = conn.execute(
        "SELECT question_count FROM _corpus_import_log WHERE import_hash = ?",
        (import_hash,),
    ).fetchone()
    if existing:
        return ImportResult(
            question_count=existing["question_count"],
            skipped_count=0,
            holdout_count=0,
            pdf_count=0,
            import_hash=import_hash,
            errors=["Already imported — hash matches existing import"],
        )

    questions: list[Question] = []
    errors: list[str] = []
    pdf_count = 0

    for mp in sorted(pipeline.rglob("merged_questions_global_order.json")):
        data = json.loads(mp.read_text(encoding="utf-8"))
        pdf_name = mp.parent.name
        year, tier = get_pdf_year_tier(pdf_name)
        pdf_count += 1

        for q in data.get("questions", []):
            if not q.get("practice_ready"):
                continue
            if not q.get("canonical_correct_option_label"):
                errors.append(
                    f"{pdf_name} Q{q.get('question_number')}: missing correct_option_label"
                )
                continue

            raw_section = q.get("section", "")
            section = normalize_section(raw_section)
            # If section is unknown/None, infer from question number
            if not raw_section or not raw_section.strip():
                gqn = q.get("global_question_number") or 0
                section = infer_section_from_qnum(int(gqn), tier, pdf_name)

            # Generate stable unique ID from pdf_name + global_question_number
            qid = str(q.get("question_id") or "")
            gqn = q.get("global_question_number") or 0
            if not qid or qid == "None":
                qid = f"{pdf_name}_q{gqn}"

            q["pdf_name"] = pdf_name
            q["resolved_question_id"] = qid
            question = Question.from_merged_json(q, section, year, tier)
            questions.append(question)

    # Assign holdout deterministically per section
    rng = random.Random(seed)
    by_section: dict[str, list[Question]] = {}
    for q in questions:
        by_section.setdefault(q.section, []).append(q)

    holdout_count = 0
    holdout_ids: set[str] = set()
    for section_qs in by_section.values():
        rng.shuffle(section_qs)
        n_holdout = max(1, int(len(section_qs) * holdout_ratio))
        for q in section_qs[:n_holdout]:
            holdout_ids.add(q.question_id)

    # Apply holdout flags to all questions at once
    for i, q in enumerate(questions):
        if q.question_id in holdout_ids:
            questions[i] = Question(
                question_id=q.question_id,
                pdf_name=q.pdf_name,
                source_page=q.source_page,
                global_question_number=q.global_question_number,
                section=q.section,
                year=q.year,
                tier=q.tier,
                question_text=q.question_text,
                options=q.options,
                correct_option_label=q.correct_option_label,
                correct_option_text=q.correct_option_text,
                chosen_option_label=q.chosen_option_label,
                question_modality=q.question_modality,
                visual_required=q.visual_required,
                table_required=q.table_required,
                math_required=q.math_required,
                evidence_status=q.evidence_status,
                question_crop_path=q.question_crop_path,
                page_asset_path=q.page_asset_path,
                archetype_id=q.archetype_id,
                is_holdout=True,
                created_at=q.created_at,
            )
            holdout_count += 1

    # Bulk insert questions
    insert_sql = """INSERT OR REPLACE INTO questions
        (question_id, pdf_name, source_page, global_question_number, section, year, tier,
         question_text, options_json, correct_option_label, correct_option_text,
         chosen_option_label, question_modality, visual_required, table_required,
         math_required, evidence_status, question_crop_path, page_asset_path,
         archetype_id, is_holdout)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    params_list: list[tuple[Any, ...]] = []
    skipped = 0
    for q in questions:
        if not q.correct_option_label or q.correct_option_label not in ("1", "2", "3", "4"):
            skipped += 1
            continue
        params_list.append((
            q.question_id,
            q.pdf_name,
            q.source_page,
            q.global_question_number,
            q.section,
            q.year,
            q.tier,
            q.question_text,
            json.dumps([{"label": o.label, "text": o.text} for o in q.options], ensure_ascii=False),
            q.correct_option_label,
            q.correct_option_text,
            q.chosen_option_label,
            q.question_modality,
            int(q.visual_required),
            int(q.table_required),
            int(q.math_required),
            q.evidence_status,
            q.question_crop_path,
            q.page_asset_path,
            q.archetype_id,
            int(q.is_holdout),
        ))

    db.execute_many(insert_sql, params_list)

    # Record import
    db.execute(
        "INSERT INTO _corpus_import_log (import_hash, pdf_count, question_count) VALUES (?, ?, ?)",
        (import_hash, pdf_count, len(params_list)),
    )

    # Force WAL checkpoint so subsequent connections see all data
    conn = db.connect()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    db.close()

    return ImportResult(
        question_count=len(params_list),
        skipped_count=skipped,
        holdout_count=holdout_count,
        pdf_count=pdf_count,
        import_hash=import_hash,
        errors=errors,
    )


def verify_import(db_path: str | Path) -> dict[str, Any]:
    """Verify the integrity of imported data.

    Returns a dict with keys: question_count, section_counts, tier_counts,
    holdout_count, has_errors, error_details.
    """
    path = Path(db_path)
    if not path.exists():
        return {
            "question_count": 0,
            "has_errors": True,
            "error_details": ["Database file not found"],
        }

    conn = get_connection(path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # ensure all writes are visible
    errors: list[str] = []

    # Count
    total = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
    holdout = conn.execute(
        "SELECT COUNT(*) as c FROM questions WHERE is_holdout = 1"
    ).fetchone()["c"]

    # Section coverage
    sections = {
        row["section"]: row["c"]
        for row in conn.execute(
            "SELECT section, COUNT(*) as c FROM questions GROUP BY section"
        ).fetchall()
    }

    # Tier balance
    tiers = {
        row["tier"]: row["c"]
        for row in conn.execute(
            "SELECT tier, COUNT(*) as c FROM questions GROUP BY tier"
        ).fetchall()
    }

    # Check all have correct labels
    missing = conn.execute(
        "SELECT COUNT(*) as c FROM questions WHERE correct_option_label NOT IN ('1','2','3','4')"
    ).fetchone()["c"]
    if missing > 0:
        errors.append(f"{missing} questions missing valid correct_option_label")

    # Check holdout ratio is roughly 25%
    if total > 0:
        actual_ratio = holdout / total
        if actual_ratio < 0.20 or actual_ratio > 0.30:
            errors.append(f"Holdout ratio is {actual_ratio:.1%}, expected ~25%")

    # Check no missing question IDs
    null_ids = conn.execute(
        "SELECT COUNT(*) as c FROM questions WHERE question_id IS NULL OR question_id = ''"
    ).fetchone()["c"]
    if null_ids > 0:
        errors.append(f"{null_ids} questions with null/empty question_id")

    conn.close()

    return {
        "question_count": total,
        "holdout_count": holdout,
        "section_counts": sections,
        "tier_counts": tiers,
        "has_errors": len(errors) > 0,
        "error_details": errors,
    }
