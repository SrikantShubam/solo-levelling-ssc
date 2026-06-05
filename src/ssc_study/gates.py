"""Archetype unlock gates — probe, evaluate, and route archetypes.

After a probe session, archetypes are routed based on accuracy:
  - 80%+        → SM-2 (spaced repetition)
  - 50-79%      → Boss fights (timed practice)
  - <50% with concept_gap   → Remediation
  - <50% without concept_gap → High-priority boss fights
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .db import Database
from .skips import record_failed_gate


@dataclass
class GateResult:
    """Result of evaluating an archetype probe."""
    archetype_id: int
    archetype_name: str
    accuracy: float
    attempt_count: int
    route: str  # 'sm2', 'boss_fight', 'remediation', 'high_priority_boss'
    concept_gap: bool  # True if failure was concept-based (not speed)
    unlocked: bool  # True if routed to SM-2
    skip_update: dict[str, Any] | None  # result of record_failed_gate if applicable


PROBE_SIZE = 10
SM2_THRESHOLD = 0.80
BOSS_FIGHT_UPPER = 0.79
BOSS_FIGHT_LOWER = 0.50


def evaluate_probe(
    db: Database,
    archetype_id: int,
    attempts: list[dict[str, Any]],
) -> GateResult:
    """Evaluate probe attempts and route the archetype.

    Args:
        db: Database instance.
        archetype_id: The archetype that was probed.
        attempts: List of attempt dicts with keys: is_correct, student_label,
                  time_spent_seconds, concept_tag.

    Returns:
        GateResult with route and unlock status.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT name FROM archetypes WHERE archetype_id = ?", (archetype_id,)
    ).fetchone()
    arch_name = row["name"] if row else f"archetype_{archetype_id}"

    total = len(attempts)
    correct = sum(1 for a in attempts if a.get("is_correct"))
    accuracy = correct / total if total > 0 else 0.0

    # Determine concept gap: look at student_label and concept_tag patterns
    concept_gap = _detect_concept_gap(attempts)

    skip_update = None
    unlocked = False

    if accuracy >= SM2_THRESHOLD:
        # Route to SM-2
        route = "sm2"
        unlocked = True
        conn.execute(
            "UPDATE archetypes SET is_unlocked = 1, t1_accuracy = ? WHERE archetype_id = ?",
            (round(accuracy, 3), archetype_id),
        )
    elif BOSS_FIGHT_LOWER <= accuracy <= BOSS_FIGHT_UPPER:
        route = "boss_fight"
        conn.execute(
            "UPDATE archetypes SET t1_accuracy = ? WHERE archetype_id = ?",
            (round(accuracy, 3), archetype_id),
        )
    elif concept_gap:
        route = "remediation"
        skip_update = record_failed_gate(db, archetype_id)
    else:
        route = "high_priority_boss"
        skip_update = record_failed_gate(db, archetype_id)

    conn.commit()

    return GateResult(
        archetype_id=archetype_id,
        archetype_name=arch_name,
        accuracy=round(accuracy, 3),
        attempt_count=total,
        route=route,
        concept_gap=concept_gap,
        unlocked=unlocked,
        skip_update=skip_update,
    )


def get_probe_candidates(db: Database) -> list[dict[str, Any]]:
    """Return archetypes that need probing.

    Candidates are active, non-skipped archetypes with at least
    PROBE_SIZE eligible non-holdout questions and no prior probe.

    Returns:
        List of dicts: archetype_id, name, section, tier, question_count.
    """
    conn = db.connect()
    today = date.today().isoformat()

    rows = conn.execute(
        """SELECT a.archetype_id, a.name, a.section, a.tier,
                  COUNT(q.question_id) as question_count
           FROM archetypes a
           JOIN questions q ON q.archetype_id = a.archetype_id
           WHERE a.is_active = 1
             AND a.is_unlocked = 0
             AND a.t1_accuracy IS NULL
             AND (a.skip_until IS NULL OR a.skip_until < ?)
             AND q.is_holdout = 0
           GROUP BY a.archetype_id
           HAVING question_count >= ?
           ORDER BY a.section, a.name""",
        (today, PROBE_SIZE),
    ).fetchall()

    return [
        {
            "archetype_id": r["archetype_id"],
            "name": r["name"],
            "section": r["section"],
            "tier": r["tier"],
            "question_count": r["question_count"],
        }
        for r in rows
    ]


def run_probe(
    db: Database,
    archetype_id: int,
) -> list[dict[str, Any]]:
    """Get exactly PROBE_SIZE questions for an archetype probe session.

    Args:
        db: Database instance.
        archetype_id: The archetype to probe.

    Returns:
        List of question dicts for the probe session.

    Raises:
        ValueError: If fewer than PROBE_SIZE eligible questions exist.
    """
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM questions WHERE archetype_id = ? AND is_holdout = 0 ORDER BY RANDOM() LIMIT ?",
        (archetype_id, PROBE_SIZE + 1),
    ).fetchall()

    if len(rows) < PROBE_SIZE:
        raise ValueError(
            f"Archetype {archetype_id} has only {len(rows)} eligible questions, "
            f"need {PROBE_SIZE} for a probe."
        )

    from .scheduler import _row_to_question as _to_q

    questions = [_to_q(r) for r in rows[:PROBE_SIZE]]
    return [
        {
            "question_id": q.question_id,
            "question_text": q.question_text,
            "options": [{"label": o.label, "text": o.text} for o in q.options],
            "correct_option_label": q.correct_option_label,
            "section": q.section,
            "tier": q.tier,
        }
        for q in questions
    ]


def get_archetype_accuracy_by_tier(
    db: Database,
    archetype_id: int,
    tier: str,
) -> dict[str, Any]:
    """Get accuracy for an archetype filtered by tier.

    This supports the shared Reasoning archetype pool where
    Tier-1 and Tier-2 accuracy must be tracked separately.

    Args:
        db: Database instance.
        archetype_id: The archetype.
        tier: 'tier1' or 'tier2'.

    Returns:
        Dict with: attempts, correct, accuracy.
    """
    conn = db.connect()
    row = conn.execute(
        """SELECT COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts at
           JOIN questions q ON q.question_id = at.question_id
           WHERE q.archetype_id = ?
             AND q.tier = ?""",
        (archetype_id, tier),
    ).fetchone()

    attempts = row["attempts"] or 0
    correct = row["correct"] or 0
    accuracy = correct / attempts if attempts > 0 else 0.0

    return {
        "archetype_id": archetype_id,
        "tier": tier,
        "attempts": attempts,
        "correct": correct,
        "accuracy": round(accuracy, 3),
    }


def get_tier2_readiness(
    db: Database,
    archetype_id: int,
    threshold: float = 0.80,
) -> dict[str, Any]:
    """Check if a shared Reasoning archetype meets Tier-2 readiness.

    Tier-2 readiness requires 80%+ accuracy at Tier-2 difficulty
    specifically (not Tier-1 accuracy on the same archetype).

    Args:
        db: Database instance.
        archetype_id: The shared Reasoning archetype.
        threshold: Accuracy threshold (default 0.80).

    Returns:
        Dict with: ready (bool), t1_accuracy, t2_accuracy, reason.
    """
    t1 = get_archetype_accuracy_by_tier(db, archetype_id, "tier1")
    t2 = get_archetype_accuracy_by_tier(db, archetype_id, "tier2")

    ready = t2["attempts"] >= 5 and t2["accuracy"] >= threshold
    reason = ""
    if t2["attempts"] < 5:
        reason = f"Only {t2['attempts']} Tier-2 attempts (need 5+)"
    elif t2["accuracy"] < threshold:
        reason = f"Tier-2 accuracy {t2['accuracy']:.0%} below {threshold:.0%} threshold"
    else:
        reason = f"Tier-2 ready ({t2['accuracy']:.0%} across {t2['attempts']} attempts)"

    return {
        "ready": ready,
        "t1_accuracy": t1["accuracy"],
        "t2_accuracy": t2["accuracy"],
        "t1_attempts": t1["attempts"],
        "t2_attempts": t2["attempts"],
        "reason": reason,
    }


# ── Internal helpers ──────────────────────────────────────────────────


def _detect_concept_gap(attempts: list[dict[str, Any]]) -> bool:
    """Detect whether failures indicate a concept gap vs. speed/guessing.

    A concept gap is likely when:
      - Multiple wrong answers with the same concept_tag.
      - Student label is consistently 'incorrect' (not 'timed_out').
      - Time spent on wrong answers is similar to correct ones (not rushed).
    """
    wrong_same_tag: dict[str, int] = {}
    wrong_count = 0

    for a in attempts:
        if not a.get("is_correct"):
            wrong_count += 1
            tag = a.get("concept_tag") or "unknown"
            wrong_same_tag[tag] = wrong_same_tag.get(tag, 0) + 1

    if wrong_count == 0:
        return False

    # Concept gap if any single tag accounts for >50% of wrong answers
    for tag, count in wrong_same_tag.items():
        if tag != "unknown" and count / max(wrong_count, 1) > 0.5:
            return True

    return False
