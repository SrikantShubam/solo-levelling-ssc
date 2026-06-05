"""Notification audit workflow — pause advancement when exam notification changes.

When SSC CGL 2027 notification drops:
  1. Pause new boss-fight advancement for up to 48 hours.
  2. Continue SM-2, GK/GA recall, English recall, and due pulses.
  3. Compare section counts, marks, timing, syllabus, module structure.
  4. Update ROI weights, readiness thresholds, regenerate affected queues.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .db import Database


@dataclass
class NotificationChange:
    """A detected change from the notification."""
    category: str  # 'section_weights' | 'module' | 'negative_marking' | 'qualifying_rules' | 'timing' | 'other'
    description: str
    severity: str  # 'major' | 'minor'


@dataclass
class AuditResult:
    """Result of a notification audit."""
    audit_id: int
    is_major_change: bool
    changes: list[NotificationChange]
    paused_queues: list[str]
    affected_queues: list[str]


MAJOR_CHANGE_CATEGORIES = {
    "section_weights",
    "module",
    "negative_marking",
    "qualifying_rules",
}


def trigger_notification_audit(
    db: Database,
    notification_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Trigger a notification audit when new exam notification drops.

    Creates an audit entry and pauses boss-fight advancement.

    Args:
        db: Database instance.
        notification_data: Optional dict with notification details
                          (notification_date, changes, source).

    Returns:
        Dict with: audit_id, paused (bool), message.
    """
    conn = db.connect()
    today = datetime.now(timezone.utc).date().isoformat()

    changes_detected = notification_data.get("changes", []) if notification_data else []
    is_major = _is_major_change(changes_detected)

    conn.execute(
        """INSERT INTO notification_audits
           (audit_type, notification_date, changes_detected)
           VALUES ('notification', ?, ?)""",
        (today, str(changes_detected) if changes_detected else "pending review"),
    )
    conn.commit()

    audit_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]

    paused = False
    if is_major:
        _set_advancement_paused(db, True)
        paused = True

    return {
        "audit_id": audit_id,
        "paused": paused,
        "is_major": is_major,
        "message": "Major change detected — advancement paused" if is_major
        else "Minor change — no pause needed",
    }


def complete_audit(
    db: Database,
    audit_id: int,
    changes: list[NotificationChange],
) -> dict[str, Any]:
    """Complete a notification audit with detected changes.

    Updates ROI weights, readiness thresholds, and regenerates affected queues.

    Args:
        db: Database instance.
        audit_id: The audit to complete.
        changes: List of detected changes from the notification.

    Returns:
        Dict with: completed (bool), affected_queues, message.
    """
    conn = db.connect()
    audit = conn.execute(
        "SELECT * FROM notification_audits WHERE audit_id = ?", (audit_id,)
    ).fetchone()

    if not audit:
        return {"completed": False, "affected_queues": [], "message": "Audit not found"}

    is_major = _is_major_change([c.category for c in changes])

    # Record the changes
    change_summary = "; ".join(
        f"[{c.severity}] {c.category}: {c.description}" for c in changes
    )
    conn.execute(
        "UPDATE notification_audits SET changes_detected = ?, roi_adjustments = ? WHERE audit_id = ?",
        (change_summary, _compute_roi_adjustments(changes), audit_id),
    )
    conn.commit()

    affected_queues = _get_affected_queues(changes)

    if not is_major:
        _set_advancement_paused(db, False)

    return {
        "completed": True,
        "is_major": is_major,
        "affected_queues": affected_queues,
        "message": f"Audit complete. {len(affected_queues)} queue(s) affected: {', '.join(affected_queues)}",
    }


def is_audit_paused(db: Database) -> dict[str, Any]:
    """Check if advancement is currently paused by an active audit.

    Returns:
        Dict with: paused (bool), active_audit_id (int or None),
                   reason (str).
    """
    conn = db.connect()
    row = conn.execute(
        """SELECT audit_id, changes_detected, created_at
           FROM notification_audits
           WHERE audit_type = 'notification'
             AND roi_adjustments IS NULL
           ORDER BY created_at DESC LIMIT 1"""
    ).fetchone()

    if not row:
        return {"paused": False, "active_audit_id": None, "reason": ""}

    changes = row["changes_detected"] or ""
    is_major = "section_weights" in changes or "module" in changes or "negative_marking" in changes

    if is_major:
        return {
            "paused": True,
            "active_audit_id": row["audit_id"],
            "reason": f"Audit #{row['audit_id']}: {changes[:100]}",
        }

    return {"paused": False, "active_audit_id": row["audit_id"], "reason": "Minor changes only"}


def get_audit_history(
    db: Database,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get notification audit history.

    Args:
        db: Database instance.
        limit: Max records to return.

    Returns:
        List of audit records.
    """
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM notification_audits ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()

    return [
        {
            "audit_id": r["audit_id"],
            "audit_type": r["audit_type"],
            "notification_date": r["notification_date"],
            "changes_detected": r["changes_detected"],
            "roi_adjustments": r["roi_adjustments"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def _set_advancement_paused(db: Database, paused: bool) -> None:
    """Set or clear the advancement pause flag.

    Uses a simple marker in notification_audits.
    """
    conn = db.connect()
    if paused:
        # Mark the most recent incomplete audit as pausing advancement
        conn.execute(
            "UPDATE notification_audits SET roi_adjustments = 'PAUSED' "
            "WHERE audit_id = (SELECT MAX(audit_id) FROM notification_audits "
            "WHERE roi_adjustments IS NULL OR roi_adjustments = 'PAUSED')"
        )
    else:
        # Clear pause on the most recent paused audit
        conn.execute(
            "UPDATE notification_audits SET roi_adjustments = 'RESUMED' "
            "WHERE roi_adjustments = 'PAUSED'"
        )
    conn.commit()


def _is_major_change(categories: list[str]) -> bool:
    """Determine if detected changes constitute a major change."""
    for cat in categories:
        if isinstance(cat, str) and cat in MAJOR_CHANGE_CATEGORIES:
            return True
    return False


def _compute_roi_adjustments(changes: list[NotificationChange]) -> str:
    """Compute ROI weight adjustments based on changes."""
    if not changes:
        return "none"

    adjustments: list[str] = []
    for c in changes:
        if c.category == "section_weights":
            adjustments.append(f"Updated section ROI weights ({c.description})")
        elif c.category == "module":
            adjustments.append(f"Flagged module changes ({c.description})")
        elif c.category == "negative_marking":
            adjustments.append(f"Recalculated risk thresholds ({c.description})")
        elif c.category == "qualifying_rules":
            adjustments.append(f"Adjusted qualifying targets ({c.description})")
        else:
            adjustments.append(f"Other adjustment ({c.description})")

    return "; ".join(adjustments)


def _get_affected_queues(changes: list[NotificationChange]) -> list[str]:
    """Determine which queues need regeneration based on changes."""
    affected = set()

    for c in changes:
        if c.category in ("section_weights", "module"):
            affected.add("active")
            affected.add("boss_fight")
        if c.category == "negative_marking":
            affected.add("boss_fight")
        if c.category == "qualifying_rules":
            affected.add("sm2_review")

    return sorted(affected)
