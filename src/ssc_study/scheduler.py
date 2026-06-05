"""SM-2 review scheduler — determines which questions are due for review.

Queries the sm2_state table to find questions whose next_review date is
<= today, distributing picks across sections and tiers for balanced
practice sessions.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .db import Database
from .models import Option, Question, SM2State


@dataclass
class DueStats:
    """Summary of due and upcoming reviews."""
    total_due: int
    by_section: dict[str, int]
    by_tier: dict[str, int]
    new_questions: int  # questions never reviewed
    total_questions: int
    upcoming_7d: int  # due in the next 7 days
    upcoming_30d: int  # due in the next 30 days


def get_due_questions(
    db: Database,
    count: int = 25,
    tier: str | None = None,
    section: str | None = None,
    exclude_holdout: bool = True,
) -> list[Question]:
    """Load questions due for SM-2 review.

    Priority order:
      1. Questions past their next_review date (overdue first).
      2. Questions never reviewed (new), limited by count.
      3. Falls back to random unreviewed questions if count not met.

    Args:
        db: Database instance.
        count: Maximum number of questions to return.
        tier: Optional tier filter ('tier1' or 'tier2').
        section: Optional section filter.
        exclude_holdout: Exclude holdout questions (default True).

    Returns:
        List of Question objects ready for review.
    """
    conn = db.connect()
    today = date.today().isoformat()

    conditions = ["1=1"]
    params: list[Any] = []

    if exclude_holdout:
        conditions.append("q.is_holdout = 0")
    if tier:
        conditions.append("q.tier = ?")
        params.append(tier)
    if section:
        conditions.append("q.section = ?")
        params.append(section)

    where = " AND ".join(conditions)

    # Phase 1: Overdue questions (next_review <= today), ordered by oldest first
    overdue_sql = f"""
        SELECT q.*, s.easiness, s.interval_days, s.repetitions,
               s.next_review, s.last_review, s.last_quality
        FROM questions q
        LEFT JOIN sm2_state s ON s.entity_type = 'question' AND s.entity_id = q.question_id
        WHERE {where}
          AND s.next_review IS NOT NULL
          AND s.next_review <= ?
        ORDER BY s.next_review ASC
        LIMIT ?
    """
    overdue_params = params + [today, count]
    overdue_rows = conn.execute(overdue_sql, tuple(overdue_params)).fetchall()

    # Phase 2: New (never reviewed) questions
    new_count = count - len(overdue_rows)
    new_questions: list[Question] = []
    if new_count > 0:
        new_sql = f"""
            SELECT q.*
            FROM questions q
            LEFT JOIN sm2_state s ON s.entity_type = 'question' AND s.entity_id = q.question_id
            WHERE {where}
              AND s.entity_id IS NULL
            ORDER BY RANDOM()
            LIMIT ?
        """
        new_params = params + [new_count]
        new_rows = conn.execute(new_sql, tuple(new_params)).fetchall()
        new_questions = [_row_to_question(r) for r in new_rows]

    overdue_questions = [_row_to_question(r) for r in overdue_rows]

    # Interleave: overdue first (sorted by oldest), then new
    all_questions = overdue_questions + new_questions

    # Phase 3: If still not enough, pull any unreviewed that exist
    if len(all_questions) < count:
        remaining = count - len(all_questions)
        reviewed_ids = [q.question_id for q in all_questions]
        placeholders = ",".join("?" for _ in reviewed_ids) if reviewed_ids else "''"

        fill_sql = f"""
            SELECT q.*
            FROM questions q
            LEFT JOIN sm2_state s ON s.entity_type = 'question' AND s.entity_id = q.question_id
            WHERE {where}
              AND (s.entity_id IS NULL OR s.next_review IS NULL)
              AND q.question_id NOT IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT ?
        """
        fill_params = params + reviewed_ids + [remaining]
        fill_rows = conn.execute(fill_sql, tuple(fill_params)).fetchall()
        all_questions.extend(_row_to_question(r) for r in fill_rows)

    return all_questions[:count]


def get_due_stats(db: Database) -> DueStats:
    """Compute summary statistics about due and upcoming reviews.

    Args:
        db: Database instance.

    Returns:
        DueStats with counts broken down by section, tier, and time horizon.
    """
    conn = db.connect()
    today = date.today().isoformat()

    total = conn.execute("SELECT COUNT(*) as c FROM questions WHERE is_holdout = 0").fetchone()["c"]

    # Questions with no SM-2 state (never reviewed)
    new_q = conn.execute(
        """SELECT COUNT(*) as c FROM questions q
           LEFT JOIN sm2_state s ON s.entity_type = 'question' AND s.entity_id = q.question_id
           WHERE q.is_holdout = 0 AND s.entity_id IS NULL"""
    ).fetchone()["c"]

    # Due today
    due_rows = conn.execute(
        """SELECT s.next_review, q.section, q.tier
           FROM sm2_state s
           JOIN questions q ON q.question_id = s.entity_id
           WHERE s.entity_type = 'question'
             AND s.next_review IS NOT NULL
             AND q.is_holdout = 0"""
    ).fetchall()

    by_section: Counter = Counter()
    by_tier: Counter = Counter()
    due_today = 0
    upcoming_7d = 0
    upcoming_30d = 0

    for row in due_rows:
        nr = row["next_review"]
        if nr <= today:
            due_today += 1
            by_section[row["section"]] += 1
            by_tier[row["tier"]] += 1
        elif nr <= _add_days(today, 7):
            upcoming_7d += 1
        elif nr <= _add_days(today, 30):
            upcoming_30d += 1

    return DueStats(
        total_due=due_today,
        by_section=dict(by_section),
        by_tier=dict(by_tier),
        new_questions=new_q,
        total_questions=total,
        upcoming_7d=upcoming_7d,
        upcoming_30d=upcoming_30d,
    )


def get_due_archetypes(db: Database) -> list[dict[str, Any]]:
    """Return archetypes that need accuracy re-probing.

    An archetype needs probing when:
      - It has < archetype_probe_count attempts total, OR
      - Its accuracy has dropped below the unlock threshold.

    Returns:
        List of dicts with archetype_id, name, section, attempts, accuracy.
    """
    conn = db.connect()
    rows = conn.execute(
        """SELECT a.archetype_id, a.name, a.section,
                  COUNT(at.attempt_id) as attempt_count,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct_count
           FROM archetypes a
           LEFT JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE a.is_active = 1
           GROUP BY a.archetype_id
           ORDER BY attempt_count ASC"""
    ).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        attempts = row["attempt_count"] or 0
        correct = row["correct_count"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0
        results.append({
            "archetype_id": row["archetype_id"],
            "name": row["name"],
            "section": row["section"],
            "attempts": attempts,
            "accuracy": round(accuracy, 3),
        })

    return results


def record_review(
    db: Database,
    question_id: str,
    quality: int,
) -> None:
    """Directly record a review and update SM-2 state outside of a quiz session.

    Useful for batch operations or CLI commands.

    Args:
        db: Database instance.
        question_id: The question to record a review for.
        quality: SM-2 quality score (0-5).
    """
    from .models import SM2State
    from .sm2 import compute_sm2

    today = date.today().isoformat()

    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
        (question_id,),
    ).fetchone()

    prev = SM2State()
    if row:
        prev = SM2State(
            easiness=row["easiness"],
            interval_days=row["interval_days"],
            repetitions=row["repetitions"],
            next_review=row["next_review"],
            last_review=row["last_review"],
            last_quality=row["last_quality"],
        )

    result = compute_sm2(quality, prev, today)
    conn.execute(
        """INSERT OR REPLACE INTO sm2_state
           (entity_type, entity_id, easiness, interval_days, repetitions,
            next_review, last_review, last_quality)
           VALUES ('question', ?, ?, ?, ?, ?, ?, ?)""",
        (question_id, result.easiness, result.interval_days,
         result.repetitions, result.next_review, today, quality),
    )
    conn.commit()


# ── Internal helpers ──────────────────────────────────────────────────


def _row_to_question(row: sqlite3.Row) -> Question:
    """Convert a SQLite row (with optional sm2_state fields) to a Question."""
    options_data = json.loads(row["options_json"]) if isinstance(row["options_json"], str) else []
    options = [Option(label=o["label"], text=o["text"]) for o in options_data]

    # created_at may not be present in all queries
    try:
        created_at = row["created_at"]
    except (KeyError, IndexError):
        created_at = ""

    return Question(
        question_id=row["question_id"],
        pdf_name=row["pdf_name"],
        source_page=row["source_page"],
        global_question_number=row["global_question_number"],
        section=row["section"],
        year=row["year"],
        tier=row["tier"],
        question_text=row["question_text"],
        options=options,
        correct_option_label=row["correct_option_label"],
        correct_option_text=row["correct_option_text"],
        chosen_option_label=row["chosen_option_label"],
        question_modality=row["question_modality"],
        visual_required=bool(row["visual_required"]),
        table_required=bool(row["table_required"]),
        math_required=bool(row["math_required"]),
        evidence_status=row["evidence_status"],
        question_crop_path=row["question_crop_path"],
        page_asset_path=row["page_asset_path"],
        archetype_id=row["archetype_id"],
        is_holdout=bool(row["is_holdout"]),
        created_at=created_at,
    )


def _add_days(iso_date: str, days: int) -> str:
    """Add N days to an ISO date string."""
    d = date.fromisoformat(iso_date)
    return (d + timedelta(days=days)).isoformat()
