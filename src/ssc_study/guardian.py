"""Phase 4 Guardian Scheduler module.

Generates daily plan recommendations based on Plan.md rules, mock history,
readiness floors, and active notification audits.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from .db import Database
from .audit import is_audit_paused


@dataclass(frozen=True)
class GuardianPlanBlock:
    """Represents a single block in the daily study recommendation."""

    name: str
    minutes: int
    reason: str
    source_rule: str


@dataclass(frozen=True)
class GuardianPlan:
    """Contains the calculated daily study schedule recommendation."""

    plan_date: str
    total_minutes: int
    blocks: List[GuardianPlanBlock]
    mock_recommendation: str
    pulse_recommendation: str
    audit_mode: str
    readiness_context: Dict[str, Any]
    warnings: List[str]


def build_guardian_plan(db: Database, *, today: Optional[date] = None) -> GuardianPlan:
    """Build a deterministic Phase 4 Guardian daily plan recommendation.

    Args:
        db: Database instance.
        today: Optional date injection for testing.

    Returns:
        GuardianPlan with daily schedule blocks and recommendations.
    """
    if today is None:
        today = date.today()

    plan_date_str = today.isoformat()
    warnings = []

    # 1. Audit status
    audit_status = is_audit_paused(db)
    is_paused = audit_status["paused"]

    audit_mode = "normal"
    if is_paused:
        audit_mode = "notification_pause"

    # Check for recalibration (7 days since a major notification audit was triggered)
    conn = db.connect()
    recent_audit = conn.execute(
        """SELECT created_at FROM notification_audits
           WHERE audit_type = 'notification'
             AND (changes_detected LIKE '%section_weights%' OR changes_detected LIKE '%module%')
           ORDER BY created_at DESC LIMIT 1"""
    ).fetchone()

    if recent_audit and not is_paused:
        try:
            created_date = date.fromisoformat(recent_audit["created_at"].split("T")[0])
            if today - created_date <= timedelta(days=7):
                audit_mode = "recalibration"
        except Exception:
            pass

    # 2. Mock history and cadence
    last_mock_row = conn.execute(
        """SELECT started_at as taken_at FROM sessions
           WHERE session_type IN ('mock', 'sealed_mock') AND question_count > 0
           UNION ALL
           SELECT taken_at FROM external_mocks
           ORDER BY taken_at DESC LIMIT 1"""
    ).fetchone()

    first_session_row = conn.execute(
        """SELECT started_at as taken_at FROM sessions
           UNION ALL
           SELECT taken_at FROM external_mocks
           ORDER BY taken_at ASC LIMIT 1"""
    ).fetchone()

    has_125_crossed = _check_tier1_floor_125_crossed(db)
    has_135_twice = _check_tier1_floor_135_twice(db)

    # Cadence decision
    cadence = "weekly"
    mock_rec_label = "weekly mock"
    cadence_days = 7

    if has_125_crossed:
        cadence = "three-day"
        mock_rec_label = "three-day mock"
        cadence_days = 3
    elif first_session_row:
        try:
            first_date = date.fromisoformat(first_session_row["taken_at"].split("T")[0])
            days_since_start = (today - first_date).days
            if days_since_start > 56:  # 8 weeks
                cadence = "five-day"
                mock_rec_label = "five-day mock"
                cadence_days = 5
        except Exception:
            pass

    # Mock due check
    mock_due = False
    if last_mock_row:
        try:
            last_date = date.fromisoformat(last_mock_row["taken_at"].split("T")[0])
            days_since_last = (today - last_date).days
            if days_since_last >= cadence_days:
                mock_due = True
        except Exception:
            mock_due = True
    else:
        warnings.append("No mock history found; mock cadence cannot be evaluated yet.")

    uncalibrated_external_mocks = conn.execute(
        """SELECT COUNT(*) as c
           FROM external_mocks
           WHERE tier = 'tier1' AND calibrated_score IS NULL"""
    ).fetchone()["c"]
    if uncalibrated_external_mocks:
        warnings.append(
            f"{uncalibrated_external_mocks} Tier-1 external mock(s) lack calibrated score; "
            "excluded from floor checks."
        )

    # 3. Pulse day check (first Monday of the month)
    is_first_monday = (today.weekday() == 0) and (today.day <= 7)

    pulse_recommendation = "none"
    if is_first_monday:
        pulse_recommendation = "both"

    # Mock recommendation
    mock_recommendation = "none"
    if mock_due:
        if is_first_monday:
            # Collision! Push mock to next grind day
            mock_recommendation = "none"
            warnings.append("Mock due but deferred because today is a Monthly Pulse day.")
        else:
            mock_recommendation = mock_rec_label

    # 4. Build Plan Blocks
    blocks = []

    # SM-2 review is always 25 min
    blocks.append(GuardianPlanBlock(
        name="SM-2 Review",
        minutes=25,
        reason="Daily spaced repetition review slot",
        source_rule="SM-2 review",
    ))

    if audit_mode == "notification_pause":
        # Paused mode: continue only SM-2, GK/GA recall, English recall, and due pulses
        blocks.append(GuardianPlanBlock(
            name="GK/GA Memory Queue",
            minutes=20,
            reason="GK/GA fact card review",
            source_rule="GK/GA memory queue",
        ))
        blocks.append(GuardianPlanBlock(
            name="English",
            minutes=30,
            reason="Daily English practice slot",
            source_rule="English",
        ))
        blocks.append(GuardianPlanBlock(
            name="Analysis",
            minutes=10,
            reason="Daily review and failure analysis",
            source_rule="Analysis",
        ))
        blocks.append(GuardianPlanBlock(
            name="Advancement Paused",
            minutes=95,
            reason="New boss-fight advancement paused due to active major notification audit",
            source_rule="Notification Audit Pause",
        ))
    elif mock_recommendation != "none":
        # Mock day: Replaces boss-fight blocks (35 min T1 + 60 min T2 = 95 min)
        blocks.append(GuardianPlanBlock(
            name="Mock Test",
            minutes=95,
            reason=f"Scheduled mock exam ({mock_recommendation})",
            source_rule="Mock Cadence",
        ))
        blocks.append(GuardianPlanBlock(
            name="GK/GA Memory Queue",
            minutes=20,
            reason="GK/GA fact card review",
            source_rule="GK/GA memory queue",
        ))
        blocks.append(GuardianPlanBlock(
            name="English",
            minutes=30,
            reason="Daily English practice slot",
            source_rule="English",
        ))
        blocks.append(GuardianPlanBlock(
            name="Analysis",
            minutes=10,
            reason="Daily review and failure analysis",
            source_rule="Analysis",
        ))
    elif is_first_monday:
        # Pulse day: replaces boss-fight blocks
        blocks.append(GuardianPlanBlock(
            name="Foundation Pulse",
            minutes=75,
            reason="Monthly foundation concept check",
            source_rule="Monthly Pulses",
        ))
        blocks.append(GuardianPlanBlock(
            name="CK Pulse",
            minutes=20,
            reason="Monthly Computer Knowledge check",
            source_rule="Computer Knowledge Pulse",
        ))
        blocks.append(GuardianPlanBlock(
            name="GK/GA Memory Queue",
            minutes=20,
            reason="GK/GA fact card review",
            source_rule="GK/GA memory queue",
        ))
        blocks.append(GuardianPlanBlock(
            name="English",
            minutes=30,
            reason="Daily English practice slot",
            source_rule="English",
        ))
        blocks.append(GuardianPlanBlock(
            name="Analysis",
            minutes=10,
            reason="Daily review and failure analysis",
            source_rule="Analysis",
        ))
    else:
        # Normal day
        if has_135_twice:
            t1_boss_min = 25
            t2_module_min = 70
            reason_suffix = " (shifted due to Tier-1 floor > 135)"
        else:
            t1_boss_min = 35
            t2_module_min = 60
            reason_suffix = ""

        blocks.append(GuardianPlanBlock(
            name="Tier-1 Boss Fights",
            minutes=t1_boss_min,
            reason=f"Targeted practice for weak Tier-1 areas{reason_suffix}",
            source_rule="Tier-1 boss fights",
        ))
        blocks.append(GuardianPlanBlock(
            name="Tier-2 Module Queue",
            minutes=t2_module_min,
            reason=f"Focused practice for Tier-2 topics{reason_suffix}",
            source_rule="Tier-2 module queue",
        ))
        blocks.append(GuardianPlanBlock(
            name="GK/GA Memory Queue",
            minutes=20,
            reason="GK/GA fact card review",
            source_rule="GK/GA memory queue",
        ))
        blocks.append(GuardianPlanBlock(
            name="English",
            minutes=30,
            reason="Daily English practice slot",
            source_rule="English",
        ))
        blocks.append(GuardianPlanBlock(
            name="Analysis",
            minutes=10,
            reason="Daily review and failure analysis",
            source_rule="Analysis",
        ))

    total_minutes = sum(b.minutes for b in blocks)

    # Build readiness context
    days_since_last = None
    if last_mock_row:
        try:
            last_date = date.fromisoformat(last_mock_row["taken_at"].split("T")[0])
            days_since_last = (today - last_date).days
        except Exception:
            pass

    readiness_context = {
        "tier1_floor_125_crossed": has_125_crossed,
        "tier1_floor_135_twice": has_135_twice,
        "days_since_last_mock": days_since_last,
    }

    return GuardianPlan(
        plan_date=plan_date_str,
        total_minutes=total_minutes,
        blocks=blocks,
        mock_recommendation=mock_recommendation,
        pulse_recommendation=pulse_recommendation,
        audit_mode=audit_mode,
        readiness_context=readiness_context,
        warnings=warnings,
    )


def _check_tier1_floor_125_crossed(db: Database) -> bool:
    conn = db.connect()
    # Query internal mocks
    internal_rows = conn.execute(
        """SELECT question_count, correct_count
           FROM sessions
           WHERE session_type IN ('mock', 'sealed_mock') AND tier = 'tier1'
             AND question_count > 0"""
    ).fetchall()

    # Query external mocks
    external_rows = conn.execute(
        """SELECT calibrated_score
           FROM external_mocks
           WHERE tier = 'tier1'"""
    ).fetchall()

    scores = []
    for r in internal_rows:
        acc = r["correct_count"] / r["question_count"]
        scores.append(acc * 200)
    for r in external_rows:
        if r["calibrated_score"] is not None:
            scores.append(r["calibrated_score"])

    return any(score >= 125 for score in scores)


def _check_tier1_floor_135_twice(db: Database) -> bool:
    conn = db.connect()
    # Query internal mocks
    internal_rows = conn.execute(
        """SELECT started_at as taken_at, question_count, correct_count
           FROM sessions
           WHERE session_type IN ('mock', 'sealed_mock') AND tier = 'tier1'
             AND question_count > 0"""
    ).fetchall()

    # Query external mocks
    external_rows = conn.execute(
        """SELECT taken_at, calibrated_score
           FROM external_mocks
           WHERE tier = 'tier1'"""
    ).fetchall()

    scores = []
    for r in internal_rows:
        acc = r["correct_count"] / r["question_count"]
        scores.append((r["taken_at"], acc * 200))
    for r in external_rows:
        if r["calibrated_score"] is not None:
            scores.append((r["taken_at"], r["calibrated_score"]))

    scores.sort(key=lambda x: x[0])
    cleared_count = sum(1 for _, score in scores if score >= 135)
    return cleared_count >= 2
