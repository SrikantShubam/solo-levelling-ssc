"""Sealed-holdout mock policy — monthly-capped usage of holdout questions.

Holdout questions (25% of corpus) are sealed for accurate mock assessment.
Policy:
  - Max 2 sealed-holdout full mocks per calendar month.
  - Usage is auditable by month.
  - Expired current-affairs holdout questions are excluded from active use.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .db import Database


@dataclass
class HoldoutUsage:
    """Record of a holdout mock usage."""
    session_id: int
    tier: str
    month: str  # YYYY-MM
    question_count: int
    created_at: str


MAX_MONTHLY_MOCKS = 2


def ensure_holdout_usage_table(db: Database) -> None:
    """Create the holdout usage tracking table if it doesn't exist."""
    conn = db.connect()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS holdout_usage_log (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES sessions(session_id),
            tier        TEXT NOT NULL,
            month       TEXT NOT NULL,
            question_count INTEGER NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_holdout_usage_month ON holdout_usage_log(month)"
    )
    conn.commit()


def check_monthly_cap(db: Database, month: str | None = None) -> dict[str, Any]:
    """Check if a new sealed-holdout mock can be created this month.

    Args:
        db: Database instance.
        month: YYYY-MM format (defaults to current month).

    Returns:
        Dict with: allowed (bool), used (int), remaining (int),
                   month (str), reason (str if denied).
    """
    ensure_holdout_usage_table(db)
    if month is None:
        month = date.today().strftime("%Y-%m")

    conn = db.connect()
    row = conn.execute(
        "SELECT COUNT(*) as c FROM holdout_usage_log WHERE month = ?",
        (month,),
    ).fetchone()
    used = row["c"] if row else 0
    remaining = MAX_MONTHLY_MOCKS - used

    return {
        "allowed": remaining > 0,
        "used": used,
        "remaining": remaining,
        "month": month,
        "reason": "" if remaining > 0 else f"Monthly cap reached ({MAX_MONTHLY_MOCKS}/month). Wait until next month.",
    }


def create_sealed_mock(
    db: Database,
    tier: str | None = None,
    count: int = 25,
) -> dict[str, Any]:
    """Create a sealed-holdout mock session.

    Uses holdout questions only. Enforces monthly cap.

    Args:
        db: Database instance.
        tier: Optional tier filter ('tier1' or 'tier2').
        count: Number of questions.

    Returns:
        Dict with keys: created (bool), session_id (int or None),
                        question_count, reason (str if denied).
    """
    ensure_holdout_usage_table(db)

    # Check cap
    cap = check_monthly_cap(db)
    if not cap["allowed"]:
        return {"created": False, "session_id": None, "question_count": 0, "reason": cap["reason"]}

    conn = db.connect()

    # Build query for holdout questions
    conditions = ["is_holdout = 1"]
    params: list[Any] = []

    # Exclude expired current-affairs holdout questions
    today = date.today().isoformat()
    conditions.append(
        "(question_id NOT IN (SELECT question_id FROM fact_cards "
        "WHERE expires_on IS NOT NULL AND expires_on < ?))"
    )
    params.append(today)

    if tier:
        conditions.append("tier = ?")
        params.append(tier)

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"SELECT * FROM questions WHERE {where} ORDER BY RANDOM() LIMIT ?",
        params + [count],
    ).fetchall()

    if not rows:
        return {"created": False, "session_id": None, "question_count": 0,
                "reason": "No holdout questions available."}

    from .scheduler import _row_to_question as _to_q
    questions = [_to_q(r) for r in rows]

    # Create session
    from datetime import datetime, timezone


    cursor = conn.execute(
        "INSERT INTO sessions (session_type, started_at, tier, question_count, notes) "
        "VALUES ('sealed_mock', ?, ?, ?, 'sealed holdout mock')",
        (datetime.now(timezone.utc).isoformat(), tier, len(questions)),
    )
    conn.commit()
    session_id = cursor.lastrowid

    # Log holdout usage
    month = date.today().strftime("%Y-%m")
    conn.execute(
        "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, ?, ?, ?)",
        (session_id, tier or "both", month, len(questions)),
    )
    conn.commit()

    return {
        "created": True,
        "session_id": session_id,
        "question_count": len(questions),
        "reason": "",
        "month": month,
    }


def get_holdout_usage(
    db: Database,
    year: int | None = None,
    month: int | None = None,
) -> list[HoldoutUsage]:
    """Get holdout usage records, optionally filtered by month.

    Args:
        db: Database instance.
        year: Filter by year (e.g. 2026).
        month: Filter by month (1-12).

    Returns:
        List of HoldoutUsage records.
    """
    conn = db.connect()

    conditions = ["1=1"]
    params: list[Any] = []

    if year is not None and month is not None:
        month_str = f"{year:04d}-{month:02d}"
        conditions.append("month = ?")
        params.append(month_str)
    elif year is not None:
        prefix = f"{year:04d}-"
        conditions.append("month LIKE ?")
        params.append(f"{prefix}%")

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"SELECT * FROM holdout_usage_log WHERE {where} ORDER BY created_at DESC",
        params,
    ).fetchall()

    return [
        HoldoutUsage(
            session_id=r["session_id"],
            tier=r["tier"],
            month=r["month"],
            question_count=r["question_count"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


def count_holdout_available(db: Database, tier: str | None = None) -> int:
    """Count available holdout questions (not expired)."""
    conn = db.connect()
    today = date.today().isoformat()

    conditions = ["is_holdout = 1"]
    params: list[Any] = []
    conditions.append(
        "(question_id NOT IN (SELECT question_id FROM fact_cards "
        "WHERE expires_on IS NOT NULL AND expires_on < ?))"
    )
    params.append(today)

    if tier:
        conditions.append("tier = ?")
        params.append(tier)

    where = " AND ".join(conditions)
    row = conn.execute(
        f"SELECT COUNT(*) as c FROM questions WHERE {where}",
        params,
    ).fetchone()
    return row["c"] if row else 0


def get_holdout_stats(db: Database) -> dict[str, Any]:
    """Return holdout system statistics.

    Returns:
        Dict with total_holdout, available, usage_this_month, usage_all_time.
    """
    ensure_holdout_usage_table(db)
    conn = db.connect()
    total = conn.execute("SELECT COUNT(*) as c FROM questions WHERE is_holdout = 1").fetchone()["c"]
    available = count_holdout_available(db)
    month = date.today().strftime("%Y-%m")

    used_this = conn.execute(
        "SELECT SUM(question_count) as c FROM holdout_usage_log WHERE month = ?",
        (month,),
    ).fetchone()["c"] or 0

    used_all = conn.execute(
        "SELECT SUM(question_count) as c FROM holdout_usage_log",
    ).fetchone()["c"] or 0

    return {
        "total_holdout": total,
        "available": available,
        "usage_this_month": used_this,
        "mocks_this_month": conn.execute(
            "SELECT COUNT(*) as c FROM holdout_usage_log WHERE month = ?", (month,)
        ).fetchone()["c"],
        "usage_all_time": used_all,
    }
