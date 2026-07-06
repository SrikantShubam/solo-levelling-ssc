"""Phase 3 evaluation: compare pipeline prediction vs actual observed outcome."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .db import Database
from .gates import classify_probe_attempts

ACTUAL_ATTEMPT_WINDOW = 10
MIN_ACTUAL_ATTEMPTS = 5


@dataclass(frozen=True)
class Phase3RouteComparison:
    archetype_id: int
    archetype_name: str
    predicted_route: str
    actual_route: str | None
    actual_attempt_count: int
    actual_accuracy: float | None
    signal_strength: str
    matches: bool | None
    reason: str


@dataclass(frozen=True)
class Phase3EvaluationReport:
    comparisons: tuple[Phase3RouteComparison, ...]
    total: int
    matched: int
    mismatched: int
    pending: int


def evaluate_phase3_predictions(
    db: Database,
    *,
    archetype_ids: list[int] | None = None,
    limit: int = 20,
) -> Phase3EvaluationReport:
    """Compare persisted pipeline prediction against recent actual outcomes."""
    conn = db.connect()

    params: list[Any] = []
    where = "1=1"
    if archetype_ids:
        placeholders = ",".join("?" for _ in archetype_ids)
        where = f"a.archetype_id IN ({placeholders})"
        params.extend(archetype_ids)

    rows = conn.execute(
        f"""SELECT a.archetype_id, a.name, a.is_unlocked, a.is_active, a.t1_accuracy,
                  COUNT(q.question_id) as question_count
           FROM archetypes a
           LEFT JOIN questions q ON q.archetype_id = a.archetype_id
           WHERE {where}
           GROUP BY a.archetype_id
           ORDER BY a.name ASC
           LIMIT ?""",
        tuple(params + [limit]),
    ).fetchall()

    comparisons: list[Phase3RouteComparison] = []
    for row in rows:
        predicted_route = _predicted_route(row)
        actual_attempts = _recent_attempts_for_archetype(db, row["archetype_id"])
        actual_attempt_count = len(actual_attempts)
        actual_accuracy = _actual_accuracy(actual_attempts)
        signal_strength = _signal_strength(actual_attempt_count)
        if actual_attempt_count < MIN_ACTUAL_ATTEMPTS:
            comparisons.append(
                Phase3RouteComparison(
                    archetype_id=row["archetype_id"],
                    archetype_name=row["name"],
                    predicted_route=predicted_route,
                    actual_route=None,
                    actual_attempt_count=actual_attempt_count,
                    actual_accuracy=actual_accuracy,
                    signal_strength=signal_strength,
                    matches=None,
                    reason="insufficient_actual_attempts",
                )
            )
            continue

        actual = classify_probe_attempts(actual_attempts)
        comparisons.append(
            Phase3RouteComparison(
                archetype_id=row["archetype_id"],
                archetype_name=row["name"],
                predicted_route=predicted_route,
                actual_route=actual.route,
                actual_attempt_count=actual_attempt_count,
                actual_accuracy=actual.accuracy,
                signal_strength=signal_strength,
                matches=predicted_route == actual.route,
                reason="matched" if predicted_route == actual.route else "route_mismatch",
            )
        )

    matched = sum(1 for item in comparisons if item.matches is True)
    mismatched = sum(1 for item in comparisons if item.matches is False)
    pending = sum(1 for item in comparisons if item.matches is None)
    return Phase3EvaluationReport(
        comparisons=tuple(comparisons),
        total=len(comparisons),
        matched=matched,
        mismatched=mismatched,
        pending=pending,
    )


def _predicted_route(row: Any) -> str:
    if row["is_unlocked"] == 1 or (row["t1_accuracy"] is not None and row["t1_accuracy"] >= 0.80):
        return "sm2"
    if row["t1_accuracy"] is None:
        return "probe"
    if row["t1_accuracy"] >= 0.50:
        return "boss_fight"
    return "remediation"


def _recent_attempts_for_archetype(db: Database, archetype_id: int) -> list[dict[str, Any]]:
    conn = db.connect()
    rows = conn.execute(
        """SELECT at.is_correct, at.student_label, at.time_spent_seconds, at.concept_tag
           FROM attempts at
           JOIN questions q ON q.question_id = at.question_id
           WHERE q.archetype_id = ?
             AND q.is_holdout = 0
           ORDER BY at.attempt_id DESC
           LIMIT ?""",
        (archetype_id, ACTUAL_ATTEMPT_WINDOW),
    ).fetchall()
    ordered = list(reversed(rows))
    return [
        {
            "is_correct": bool(row["is_correct"]),
            "student_label": row["student_label"],
            "time_spent_seconds": row["time_spent_seconds"],
            "concept_tag": row["concept_tag"],
        }
        for row in ordered
    ]


def _actual_accuracy(attempts: list[dict[str, Any]]) -> float | None:
    if not attempts:
        return None
    correct = sum(1 for attempt in attempts if attempt.get("is_correct"))
    return round(correct / len(attempts), 3)


def _signal_strength(attempt_count: int) -> str:
    if attempt_count < MIN_ACTUAL_ATTEMPTS:
        return "insufficient"
    if attempt_count < ACTUAL_ATTEMPT_WINDOW:
        return "weak"
    return "stable"
