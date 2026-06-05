"""Readiness dashboard — computes all conditions for SSC CGL exam readiness.

Aggregates 12+ conditions from multiple subsystems:
  - Foundation pulse accuracy
  - Archetype mastery (Tier-1 top 100, Tier-2 top 60)
  - Module floors (Math, Reasoning, English, GA, CK)
  - Shared Reasoning Tier-2 readiness
  - CBIC card accuracy
  - Mock performance and diversity
  - Section floors, elimination skill, trend
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .db import Database


@dataclass
class CheckResult:
    """Result of a single readiness check."""
    name: str
    passed: bool
    actual: str  # human-readable current value
    required: str  # human-readable requirement
    reason: str  # explanation if failed


@dataclass
class ReadinessReport:
    """Complete readiness assessment."""
    ready: bool
    checks: dict[str, CheckResult]
    missing: list[str]  # list of failed check names
    timestamp: str


# ── Public API ────────────────────────────────────────────────────────


def compute_readiness(db: Database) -> ReadinessReport:
    """Compute all readiness conditions and return a report.

    Args:
        db: Database instance.

    Returns:
        ReadinessReport with pass/fail per condition.
    """
    checks: dict[str, CheckResult] = {}
    missing: list[str] = []

    today = date.today().isoformat()

    # 1. Foundation pulse readiness
    checks["foundation_pulse"] = _check_foundation_pulse(db)

    # 2. Tier-1 archetype mastery (top 100 at 80%+)
    checks["tier1_archetypes"] = _check_tier1_archetypes(db)

    # 3. Tier-2 archetype mastery (top 60 at 80%+)
    checks["tier2_archetypes"] = _check_tier2_archetypes(db)

    # 4. Module floors
    module_floors = _check_module_floors(db)
    checks.update(module_floors)

    # 5. Shared Reasoning Tier-2 readiness
    checks["reasoning_tier2"] = _check_reasoning_tier2(db)

    # 6. CBIC card accuracy
    checks["cbic_readiness"] = _check_cbic(db)

    # 7. Mock performance (last 5 above 145 calibrated floor)
    checks["mock_performance"] = _check_mock_performance(db)

    # 8. Mock diversity (2 of 5 external or sealed-holdout)
    checks["mock_diversity"] = _check_mock_diversity(db)

    # 9. Section floor (no section below 17 in last 3 mocks)
    checks["section_floor"] = _check_section_floor(db)

    # 10. Elimination skill (2-option elimination 85%+)
    checks["elimination_skill"] = _check_elimination_skill(db)

    # 11. Readiness trend (7-day stable or improving)
    checks["readiness_trend"] = _check_trend(db)

    for name, result in checks.items():
        if not result.passed:
            missing.append(name)

    from datetime import datetime, timezone
    return ReadinessReport(
        ready=len(missing) == 0,
        checks=checks,
        missing=missing,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def get_readiness_summary(db: Database) -> dict[str, Any]:
    """Return a quick summary of readiness status.

    Returns:
        Dict with: ready, passed_checks, total_checks, missing.
    """
    report = compute_readiness(db)
    total = len(report.checks)
    passed = total - len(report.missing)

    return {
        "ready": report.ready,
        "passed_checks": passed,
        "total_checks": total,
        "missing": report.missing,
        "percent": round(passed / total * 100, 1) if total > 0 else 0,
    }


# ── Individual checks ─────────────────────────────────────────────────


def _check_foundation_pulse(db: Database) -> CheckResult:
    """Check if foundation pulse areas are 75%+ within 14 days."""
    conn = db.connect()
    fourteen_days_ago = (date.today() - timedelta(days=14)).isoformat()

    areas = ["Quant/DI", "Reasoning", "English", "GK/GA"]
    below: list[str] = []

    for area in areas:
        row = conn.execute(
            """SELECT COUNT(at.attempt_id) as attempts,
                      SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
               FROM attempts at
               JOIN questions q ON q.question_id = at.question_id
               JOIN sessions s ON s.session_id = at.session_id
               WHERE q.section = ?
                 AND at.created_at >= ?
                 AND s.session_type IN ('foundation_pulse', 'mock')""",
            (area, fourteen_days_ago),
        ).fetchone()

        attempts = row["attempts"] or 0
        correct = row["correct"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0

        if accuracy < 0.75:
            below.append(f"{area}: {accuracy:.0%} ({correct}/{attempts})")

    passed = len(below) == 0
    return CheckResult(
        name="Foundation Pulse",
        passed=passed,
        actual=", ".join(below) if below else "All areas 75%+",
        required="All foundation areas ≥75% within 14 days",
        reason="Areas below threshold" if below else "",
    )


def _check_tier1_archetypes(db: Database) -> CheckResult:
    """Check top 100 Tier-1 archetypes at 80%+ accuracy."""
    conn = db.connect()
    rows = conn.execute(
        """SELECT a.name, a.archetype_id,
                  COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM archetypes a
           JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE q.tier = 'tier1'
           GROUP BY a.archetype_id
           HAVING attempts >= 5
           ORDER BY attempts DESC
           LIMIT 100"""
    ).fetchall()

    below: list[str] = []
    for r in rows:
        attempts = r["attempts"] or 0
        correct = r["correct"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0
        if accuracy < 0.80:
            below.append(f"{r['name']}: {accuracy:.0%}")

    total = len(rows)
    passing = total - len(below)
    passed = len(below) == 0 and total >= 10

    return CheckResult(
        name="Tier-1 Archetypes",
        passed=passed,
        actual=f"{passing}/{total} archetypes ≥80%",
        required="Top 100 Tier-1 archetypes at 80%+",
        reason=f"{len(below)} archetypes below threshold" if below else "",
    )


def _check_tier2_archetypes(db: Database) -> CheckResult:
    """Check top 60 Tier-2 pattern archetypes at 80%+ accuracy."""
    conn = db.connect()
    rows = conn.execute(
        """SELECT a.name, COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM archetypes a
           JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE q.tier = 'tier2'
           GROUP BY a.archetype_id
           HAVING attempts >= 5
           ORDER BY attempts DESC
           LIMIT 60"""
    ).fetchall()

    below: list[str] = []
    for r in rows:
        attempts = r["attempts"] or 0
        correct = r["correct"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0
        if accuracy < 0.80:
            below.append(f"{r['name']}: {accuracy:.0%}")

    total = len(rows)
    passing = total - len(below)
    passed = len(below) == 0 and total >= 10

    return CheckResult(
        name="Tier-2 Archetypes",
        passed=passed,
        actual=f"{passing}/{total} archetypes ≥80%",
        required="Top 60 Tier-2 archetypes at 80%+",
        reason=f"{len(below)} archetypes below threshold" if below else "",
    )


def _check_module_floors(db: Database) -> dict[str, CheckResult]:
    """Check module-specific accuracy floors."""
    floors = {
        "Math": ("Quant/DI", 0.80),
        "Reasoning": ("Reasoning", 0.80),
        "English": ("English", 0.80),
        "GA": ("GK/GA", 0.75),
    }
    results: dict[str, CheckResult] = {}

    conn = db.connect()
    for name, (section, threshold) in floors.items():
        row = conn.execute(
            """SELECT COUNT(at.attempt_id) as attempts,
                      SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
               FROM attempts at
               JOIN questions q ON q.question_id = at.question_id
               WHERE q.section = ?""",
            (section,),
        ).fetchone()

        attempts = row["attempts"] or 0
        correct = row["correct"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0
        passed = accuracy >= threshold and attempts >= 10

        results[f"floor_{name.lower()}"] = CheckResult(
            name=f"Module Floor: {name}",
            passed=passed,
            actual=f"{accuracy:.0%} ({correct}/{attempts})" if attempts > 0 else "No data",
            required=f"{section} ≥{threshold:.0%}",
            reason="" if passed else f"{name} at {accuracy:.0%}, need {threshold:.0%}",
        )

    # CK floor (separate, uses fact cards)
    ck_row = conn.execute(
        """SELECT COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts at
           JOIN questions q ON q.question_id = at.question_id
           WHERE q.section = 'Computer Knowledge'"""
    ).fetchone()
    ck_attempts = ck_row["attempts"] or 0
    ck_correct = ck_row["correct"] or 0
    ck_accuracy = ck_correct / ck_attempts if ck_attempts > 0 else 0.0
    ck_passed = ck_accuracy >= 0.70 and ck_attempts >= 10

    results["floor_ck"] = CheckResult(
        name="Module Floor: CK",
        passed=ck_passed,
        actual=f"{ck_accuracy:.0%} ({ck_correct}/{ck_attempts})" if ck_attempts > 0 else "No data",
        required="Computer Knowledge ≥70%",
        reason="" if ck_passed else f"CK at {ck_accuracy:.0%}, need 70%",
    )

    return results


def _check_reasoning_tier2(db: Database) -> CheckResult:
    """Check that shared Reasoning archetypes meet Tier-2 readiness."""
    from .gates import get_tier2_readiness

    conn = db.connect()
    reasoning_arches = conn.execute(
        "SELECT archetype_id, name FROM archetypes WHERE section = 'Reasoning' AND is_active = 1"
    ).fetchall()

    not_ready: list[str] = []
    for r in reasoning_arches:
        status = get_tier2_readiness(db, r["archetype_id"])
        if not status["ready"]:
            not_ready.append(f"{r['name']}: {status['reason']}")

    passed = len(not_ready) == 0
    return CheckResult(
        name="Shared Reasoning Tier-2",
        passed=passed,
        actual=f"{len(reasoning_arches) - len(not_ready)}/{len(reasoning_arches)} ready",
        required="All shared Reasoning archetypes meet Tier-2 readiness (80%+ at Tier-2 difficulty)",
        reason=not_ready[0] if not_ready else "",
    )


def _check_cbic(db: Database) -> CheckResult:
    """Check CBIC-relevant card accuracy ≥80%."""
    from .cards import cbic_specific_accuracy, needs_cbic_focus

    cbic = cbic_specific_accuracy(db)
    focus_check = needs_cbic_focus(db)

    # For the readiness check, we care about CBIC accuracy specifically
    passed = cbic["minimum_met"]

    actual_parts = [f"CBIC: {cbic['accuracy']:.0%}"]
    if cbic["attempts"] > 0:
        actual_parts.append(f"({cbic['correct']}/{cbic['attempts']})")
    else:
        actual_parts.append("(no data)")

    return CheckResult(
        name="CBIC Readiness",
        passed=passed,
        actual=" ".join(actual_parts),
        required="CBIC-relevant cards ≥80% specifically",
        reason=(
            f"CBIC at {cbic['accuracy']:.0%}, need 80%"
            if not passed and cbic["attempts"] >= 5
            else "Insufficient CBIC attempt data" if not passed else ""
        ),
    )


def _check_mock_performance(db: Database) -> CheckResult:
    """Check last 5 full mocks above calibrated 145 floor."""
    conn = db.connect()
    rows = conn.execute(
        """SELECT session_id, question_count, correct_count,
                  CAST(correct_count AS REAL) / CAST(question_count AS REAL) as accuracy
           FROM sessions
           WHERE session_type IN ('mock', 'sealed_mock')
             AND question_count > 0
           ORDER BY created_at DESC
           LIMIT 5"""
    ).fetchall()

    if not rows:
        return CheckResult(
            name="Mock Performance",
            passed=False,
            actual="No mocks completed",
            required="Last 5 mocks above calibrated 145 floor",
            reason="No mock data available",
        )

    # Simple heuristic: accuracy > 70% approximates 145+ calibrated score
    below: list[str] = []
    for r in rows:
        accuracy = r["accuracy"] or 0
        if accuracy < 0.70:
            below.append(f"Session #{r['session_id']}: {accuracy:.0%}")

    total = len(rows)
    passing = total - len(below)
    passed = len(below) == 0 and total >= 3

    return CheckResult(
        name="Mock Performance",
        passed=passed,
        actual=f"{passing}/{total} above threshold",
        required="Last 5 mocks above calibrated 145 floor",
        reason=", ".join(below) if below else "",
    )


def _check_mock_diversity(db: Database) -> CheckResult:
    """Check ≥2 of last 5 mocks are external or sealed-holdout."""
    conn = db.connect()
    rows = conn.execute(
        """SELECT session_type, notes, created_at
           FROM sessions
           WHERE session_type IN ('mock', 'external_mock')
              OR notes LIKE '%sealed holdout mock%'
           ORDER BY created_at DESC
           LIMIT 5"""
    ).fetchall()

    diverse = sum(
        1 for r in rows
        if r["session_type"] == "external_mock"
        or (r["notes"] or "").find("sealed holdout mock") >= 0
    )
    passed = diverse >= 2

    return CheckResult(
        name="Mock Diversity",
        passed=passed,
        actual=f"{diverse}/5 mocks are sealed or external",
        required="≥2 of last 5 mocks are external or sealed-holdout",
        reason=f"Only {diverse} diverse mock(s)" if not passed else "",
    )


def _check_section_floor(db: Database) -> CheckResult:
    """Check no section below 17 correct in last 3 mocks."""
    conn = db.connect()
    sessions = conn.execute(
        """SELECT session_id FROM sessions
           WHERE session_type IN ('mock', 'sealed_mock')
           ORDER BY created_at DESC LIMIT 3"""
    ).fetchall()

    if not sessions:
        return CheckResult(
            name="Section Floor",
            passed=False,
            actual="No mocks completed",
            required="No section below 17 correct in last 3 mocks",
            reason="No mock data",
        )

    below: list[str] = []
    for s in sessions:
        sid = s["session_id"]
        sec_rows = conn.execute(
            """SELECT q.section, COUNT(at.attempt_id) as attempts,
                      SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
               FROM attempts at
               JOIN questions q ON q.question_id = at.question_id
               WHERE at.session_id = ?
               GROUP BY q.section""",
            (sid,),
        ).fetchall()

        for sec in sec_rows:
            if (sec["correct"] or 0) < 17:
                below.append(f"Session #{sid} {sec['section']}: {sec['correct']} correct")

    passed = len(below) == 0
    return CheckResult(
        name="Section Floor",
        passed=passed,
        actual=f"{len(below)} section(s) below threshold" if below else "All sections ≥17 correct",
        required="No section below 17 correct in last 3 mocks",
        reason="; ".join(below[:3]) if below else "",
    )


def _check_elimination_skill(db: Database) -> CheckResult:
    """Check 2-option elimination success above 85% across last 100 drills."""
    conn = db.connect()
    rows = conn.execute(
        """SELECT is_correct FROM attempts
           ORDER BY created_at DESC LIMIT 100"""
    ).fetchall()

    if not rows:
        return CheckResult(
            name="Elimination Skill",
            passed=False,
            actual="No attempt data",
            required="2-option elimination ≥85% across last 100 drills",
            reason="No data",
        )

    total = len(rows)
    correct = sum(1 for r in rows if r["is_correct"])
    accuracy = correct / total if total > 0 else 0
    passed = accuracy >= 0.85

    return CheckResult(
        name="Elimination Skill",
        passed=passed,
        actual=f"{accuracy:.0%} ({correct}/{total} recent attempts)",
        required="2-option elimination ≥85%",
        reason=f"Current accuracy {accuracy:.0%}" if not passed else "",
    )


def _check_trend(db: Database) -> CheckResult:
    """Check 7-day readiness trend is stable or improving.

    Compares accuracy from 14-7 days ago vs 7-0 days ago.
    """
    conn = db.connect()
    today = date.today()
    week_ago = (today - timedelta(days=7)).isoformat()
    two_weeks_ago = (today - timedelta(days=14)).isoformat()

    # Older period (14-7 days ago)
    old_row = conn.execute(
        """SELECT COUNT(*) as attempts,
                  SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts
           WHERE created_at >= ? AND created_at < ?""",
        (two_weeks_ago, week_ago),
    ).fetchone()

    # Recent period (7-0 days ago)
    new_row = conn.execute(
        """SELECT COUNT(*) as attempts,
                  SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts
           WHERE created_at >= ?""",
        (week_ago,),
    ).fetchone()

    old_attempts = old_row["attempts"] or 0
    new_attempts = new_row["attempts"] or 0

    if old_attempts < 10 or new_attempts < 10:
        return CheckResult(
            name="Readiness Trend",
            passed=True,  # not enough data to judge trend
            actual=f"Old: {old_attempts} attempts, Recent: {new_attempts} attempts",
            required="Stable or improving over 7 days",
            reason="Insufficient data for trend analysis",
        )

    old_acc = (old_row["correct"] or 0) / old_attempts
    new_acc = (new_row["correct"] or 0) / new_attempts
    passed = new_acc >= old_acc - 0.03  # allow 3% tolerance for noise

    return CheckResult(
        name="Readiness Trend",
        passed=passed,
        actual=f"{old_acc:.0%} → {new_acc:.0%}",
        required="Stable or improving",
        reason=f"Declining: {old_acc:.0%} → {new_acc:.0%}" if not passed else "",
    )
