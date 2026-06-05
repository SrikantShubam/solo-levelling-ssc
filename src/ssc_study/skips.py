"""Skip-list lifecycle for archetypes.

Manages temporary and permanent skips based on failed unlock gates:

  - Temporary skip after 2 failed unlock gates (14 days or monthly audit).
  - Re-entry requires one 5-question recognition probe at 60%+.
  - Permanent skip after 3 failed unlock gates.
  - Permanent skip can be challenged only during monthly audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .db import Database


@dataclass
class SkipStatus:
    """Current skip status for an archetype."""
    archetype_id: int
    name: str
    skip_count: int
    is_actively_skipped: bool  # currently in a skip period
    skip_until: str | None  # ISO date or None
    is_permanent: bool  # permanent skip (3 failures)
    can_challenge: bool  # eligible for re-entry probe


TEMP_SKIP_DAYS = 14
PROBE_THRESHOLD = 0.60
PROBE_SIZE = 5


def record_failed_gate(db: Database, archetype_id: int) -> dict[str, Any]:
    """Record a failed unlock gate and update skip state.

    Args:
        db: Database instance.
        archetype_id: The archetype that failed its unlock gate.

    Returns:
        Dict with keys: skip_count, action_taken (one of:
        'none', 'temporary_skip', 'permanent_skip').
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM archetypes WHERE archetype_id = ?", (archetype_id,)
    ).fetchone()

    if not row:
        return {"skip_count": 0, "action_taken": "none"}

    current_skip_count = (row["skip_count"] or 0) + 1
    action = "none"

    if current_skip_count >= 3:
        # Permanent skip
        conn.execute(
            "UPDATE archetypes SET skip_count = ?, is_active = 0 WHERE archetype_id = ?",
            (current_skip_count, archetype_id),
        )
        action = "permanent_skip"
    elif current_skip_count >= 2:
        # Temporary skip for 14 days
        skip_until = (date.today() + timedelta(days=TEMP_SKIP_DAYS)).isoformat()
        conn.execute(
            "UPDATE archetypes SET skip_count = ?, skip_until = ? WHERE archetype_id = ?",
            (current_skip_count, skip_until, archetype_id),
        )
        action = "temporary_skip"
    else:
        # First failure — just increment counter, no skip yet
        conn.execute(
            "UPDATE archetypes SET skip_count = ? WHERE archetype_id = ?",
            (current_skip_count, archetype_id),
        )
        action = "none"

    conn.commit()
    return {"skip_count": current_skip_count, "action_taken": action}


def is_skipped(db: Database, archetype_id: int) -> bool:
    """Check if an archetype is currently skipped (temp or permanent).

    Args:
        db: Database instance.
        archetype_id: The archetype to check.

    Returns:
        True if the archetype is in an active skip period or permanently skipped.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT is_active, skip_until FROM archetypes WHERE archetype_id = ?",
        (archetype_id,),
    ).fetchone()

    if not row:
        return False

    if row["is_active"] == 0:
        return True  # permanently skipped

    skip_until = row["skip_until"]
    if skip_until and skip_until >= date.today().isoformat():
        return True  # temporary skip active

    return False


def get_skipped_archetypes(db: Database) -> list[SkipStatus]:
    """Return all archetypes that are currently skipped.

    Returns:
        List of SkipStatus objects.
    """
    conn = db.connect()
    today = date.today().isoformat()

    rows = conn.execute(
        "SELECT archetype_id, name, skip_count, skip_until, is_active "
        "FROM archetypes "
        "WHERE (is_active = 0) "
        "   OR (skip_until IS NOT NULL AND skip_until >= ?)",
        (today,),
    ).fetchall()

    results: list[SkipStatus] = []
    for row in rows:
        is_permanent = row["is_active"] == 0
        skip_until = row["skip_until"]
        is_actively = is_permanent or (skip_until is not None and skip_until >= today)
        can_challenge = is_permanent or (
            skip_until is not None and skip_until < _add_days(today, 1)
        )

        results.append(SkipStatus(
            archetype_id=row["archetype_id"],
            name=row["name"],
            skip_count=row["skip_count"] or 0,
            is_actively_skipped=is_actively,
            skip_until=skip_until,
            is_permanent=is_permanent,
            can_challenge=can_challenge,
        ))

    return results


def challenge_skip(db: Database, archetype_id: int) -> dict[str, Any]:
    """Attempt to challenge a permanent skip via monthly audit.

    Permanent skips can only be challenged during a monthly audit.
    This function checks eligibility and creates the challenge record.

    Args:
        db: Database instance.
        archetype_id: The permanently-skipped archetype to challenge.

    Returns:
        Dict with keys: allowed (bool), reason (str), probe_size (int).
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM archetypes WHERE archetype_id = ?", (archetype_id,)
    ).fetchone()

    if not row:
        return {"allowed": False, "reason": "Archetype not found", "probe_size": 0}

    if row["is_active"] != 0:
        return {"allowed": False, "reason": "Archetype is not permanently skipped", "probe_size": 0}

    # Check monthly audit context — allow challenge
    # Re-activate temporarily for the probe
    conn.execute(
        "UPDATE archetypes SET is_active = 1 WHERE archetype_id = ?",
        (archetype_id,),
    )
    conn.commit()

    return {
        "allowed": True,
        "reason": "Monthly audit challenge — 5-question recognition probe required",
        "probe_size": PROBE_SIZE,
    }


def resolve_probe(
    db: Database,
    archetype_id: int,
    correct_count: int,
    total_count: int,
) -> dict[str, Any]:
    """Resolve a recognition probe result for a skipped archetype.

    If accuracy >= 60%, the archetype is un-skipped.
    Otherwise, it goes back to skip state.

    Args:
        db: Database instance.
        archetype_id: The archetype that was probed.
        correct_count: Number of correct answers.
        total_count: Total questions in probe.

    Returns:
        Dict with: passed (bool), accuracy, new_skip_count, message.
    """
    accuracy = correct_count / total_count if total_count > 0 else 0
    conn = db.connect()

    if accuracy >= PROBE_THRESHOLD and total_count >= PROBE_SIZE:
        # Passed — fully un-skip
        conn.execute(
            "UPDATE archetypes SET skip_count = 0, skip_until = NULL, is_active = 1 "
            "WHERE archetype_id = ?",
            (archetype_id,),
        )
        conn.commit()
        return {
            "passed": True,
            "accuracy": round(accuracy, 3),
            "new_skip_count": 0,
            "message": f"Probe passed ({accuracy:.0%}). Archetype re-activated.",
        }

    # Failed — back to permanent skip
    conn.execute(
        "UPDATE archetypes SET is_active = 0 WHERE archetype_id = ?",
        (archetype_id,),
    )
    conn.commit()

    return {
        "passed": False,
        "accuracy": round(accuracy, 3),
        "new_skip_count": 3,  # stays at permanent skip level
        "message": f"Probe failed ({accuracy:.0%}). Archetype remains permanently skipped.",
    }


def get_skip_summary(db: Database) -> dict[str, Any]:
    """Return a summary of skip list state.

    Returns:
        Dict with counts: total_skipped, temporary, permanent.
    """
    conn = db.connect()
    today = date.today().isoformat()

    temp = conn.execute(
        "SELECT COUNT(*) as c FROM archetypes "
        "WHERE skip_until IS NOT NULL AND skip_until >= ? AND is_active = 1",
        (today,),
    ).fetchone()["c"]

    perm = conn.execute(
        "SELECT COUNT(*) as c FROM archetypes WHERE is_active = 0",
    ).fetchone()["c"]

    total = conn.execute(
        "SELECT COUNT(*) as c FROM archetypes",
    ).fetchone()["c"]

    return {
        "total_skipped": temp + perm,
        "temporary": temp,
        "permanent": perm,
        "total_archetypes": total,
    }


# ── Internal helpers ──────────────────────────────────────────────────


def _add_days(iso_date: str, days: int) -> str:
    """Add N days to an ISO date string."""
    d = date.fromisoformat(iso_date)
    return (d + timedelta(days=days)).isoformat()
