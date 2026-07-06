"""Deterministic Phase 3 orchestration loop.

Coordinates diagnostic work across existing primitives:

- probe candidates from gates
- remediation and boss-fight eligibility from attempts/archetypes
- due review follow-up from SM-2 state

The loop is intentionally bounded and auditable. It chooses the next
best action, materializes the smallest useful payload, records why, and
stops when no eligible work remains or the step cap is reached.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .db import Database
from .gates import get_probe_candidates, run_probe


@dataclass(frozen=True)
class Phase3Action:
    """One orchestrated Phase 3 action."""

    action_type: str
    reason: str
    question_count: int = 0
    question_ids: tuple[str, ...] = ()
    target_archetype_id: int | None = None
    target_archetype_name: str | None = None
    stop_reason: str | None = None


@dataclass(frozen=True)
class Phase3RunReport:
    """Report for a bounded Phase 3 run."""

    actions: tuple[Phase3Action, ...]
    completed: bool
    stop_reason: str
    steps_executed: int


def plan_next_action(
    db: Database,
    *,
    tier: str | None = None,
    section: str | None = None,
    excluded_archetype_ids: set[int] | None = None,
    excluded_queue_types: set[str] | None = None,
) -> Phase3Action:
    """Choose the next deterministic Phase 3 action."""
    excluded_archetype_ids = excluded_archetype_ids or set()
    excluded_queue_types = excluded_queue_types or set()

    probe_action = _next_probe_action(
        db,
        tier=tier,
        section=section,
        excluded_archetype_ids=excluded_archetype_ids,
    )
    if probe_action is not None:
        return probe_action

    if "remediation" not in excluded_queue_types:
        remediation_action = _next_remediation_action(db, tier=tier, section=section)
        if remediation_action is not None:
            return remediation_action

    if "boss_fight" not in excluded_queue_types:
        boss_action = _next_boss_fight_action(db, tier=tier, section=section)
        if boss_action is not None:
            return boss_action

    if "sm2_review" not in excluded_queue_types:
        review_action = _next_sm2_action(db, tier=tier, section=section)
        if review_action is not None:
            return review_action

    return Phase3Action(
        action_type="stop",
        reason="No probe, remediation, boss-fight, or due review work is eligible.",
        stop_reason="no_eligible_work",
    )


def run_phase3_loop(
    db: Database,
    *,
    max_steps: int = 5,
    tier: str | None = None,
    section: str | None = None,
    dry_run: bool = False,
) -> Phase3RunReport:
    """Run a bounded deterministic Phase 3 orchestration loop."""
    del dry_run  # reserved for future execution hooks; current loop is planning-only

    actions: list[Phase3Action] = []
    excluded_archetype_ids: set[int] = set()
    excluded_queue_types: set[str] = set()
    stop_reason = "no_eligible_work"

    for _ in range(max_steps):
        action = plan_next_action(
            db,
            tier=tier,
            section=section,
            excluded_archetype_ids=excluded_archetype_ids,
            excluded_queue_types=excluded_queue_types,
        )
        if action.action_type == "stop":
            stop_reason = action.stop_reason or "no_eligible_work"
            return Phase3RunReport(
                actions=tuple(actions),
                completed=True,
                stop_reason=stop_reason,
                steps_executed=len(actions),
            )

        actions.append(action)

        if action.target_archetype_id is not None:
            excluded_archetype_ids.add(action.target_archetype_id)
        else:
            excluded_queue_types.add(action.action_type)

    return Phase3RunReport(
        actions=tuple(actions),
        completed=True,
        stop_reason="max_steps_reached",
        steps_executed=len(actions),
    )


def _next_probe_action(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
    excluded_archetype_ids: set[int],
) -> Phase3Action | None:
    candidates = get_probe_candidates(db)

    for candidate in candidates:
        if candidate["archetype_id"] in excluded_archetype_ids:
            continue
        if tier and candidate["tier"] not in (tier, "both"):
            continue
        if section and candidate["section"] != section:
            continue

        questions = run_probe(db, candidate["archetype_id"])
        return Phase3Action(
            action_type="probe",
            reason="Unprobed active archetype with enough non-holdout questions.",
            question_count=len(questions),
            question_ids=tuple(q["question_id"] for q in questions),
            target_archetype_id=candidate["archetype_id"],
            target_archetype_name=candidate["name"],
        )

    return None


def _next_remediation_action(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
) -> Phase3Action | None:
    rows = _eligible_remediation_rows(db, tier=tier, section=section)
    if not rows:
        return None

    archetype_name = rows[0]["name"]
    question_ids = tuple(row["question_id"] for row in rows)
    return Phase3Action(
        action_type="remediation",
        reason=f"Weak archetype remediation needed for {archetype_name}.",
        question_count=len(question_ids),
        question_ids=question_ids,
        target_archetype_id=rows[0]["archetype_id"],
        target_archetype_name=archetype_name,
    )


def _next_boss_fight_action(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
) -> Phase3Action | None:
    rows = _eligible_boss_fight_rows(db, tier=tier, section=section)
    if not rows:
        return None

    archetype_name = rows[0]["name"]
    question_ids = tuple(row["question_id"] for row in rows)
    return Phase3Action(
        action_type="boss_fight",
        reason=f"Partially-mastered archetype {archetype_name} should enter timed boss-fight work.",
        question_count=len(question_ids),
        question_ids=question_ids,
        target_archetype_id=rows[0]["archetype_id"],
        target_archetype_name=archetype_name,
    )


def _next_sm2_action(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
) -> Phase3Action | None:
    conn = db.connect()
    today = date.today().isoformat()

    conditions = [
        "s.entity_type = 'question'",
        "s.next_review IS NOT NULL",
        "s.next_review <= ?",
        "q.is_holdout = 0",
    ]
    params: list[Any] = [today]

    if tier:
        conditions.append("q.tier = ?")
        params.append(tier)
    if section:
        conditions.append("q.section = ?")
        params.append(section)

    rows = conn.execute(
        f"""SELECT q.question_id
            FROM sm2_state s
            JOIN questions q ON q.question_id = s.entity_id
            WHERE {' AND '.join(conditions)}
            ORDER BY s.next_review ASC, q.question_id ASC
            LIMIT 25""",
        tuple(params),
    ).fetchall()
    if not rows:
        return None

    question_ids = tuple(row["question_id"] for row in rows)
    return Phase3Action(
        action_type="sm2_review",
        reason="Due review exists after diagnostic queue work is exhausted.",
        question_count=len(question_ids),
        question_ids=question_ids,
    )


def _eligible_remediation_rows(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
) -> list[Any]:
    conn = db.connect()
    today = date.today().isoformat()

    conditions = [
        "a.is_active = 1",
        "(a.skip_until IS NULL OR a.skip_until < ?)",
        "q.is_holdout = 0",
    ]
    params: list[Any] = [today]

    if tier:
        conditions.append("q.tier = ?")
        params.append(tier)
    if section:
        conditions.append("q.section = ?")
        params.append(section)

    archetypes = conn.execute(
        f"""SELECT a.archetype_id, a.name,
                  COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END) as correct
           FROM archetypes a
           JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE {' AND '.join(conditions)}
           GROUP BY a.archetype_id
           HAVING COUNT(at.attempt_id) >= 5
              AND (SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END)
                   / COUNT(at.attempt_id)) < 0.50
           ORDER BY (SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END)
                     / COUNT(at.attempt_id)) ASC,
                    a.name ASC
           LIMIT 1""",
        tuple(params),
    ).fetchall()
    if not archetypes:
        return []

    archetype = archetypes[0]
    question_rows = conn.execute(
        """SELECT q.question_id, ? as name, ? as archetype_id
           FROM questions q
           WHERE q.archetype_id = ?
             AND q.is_holdout = 0
           ORDER BY q.question_id ASC
           LIMIT 25""",
        (archetype["name"], archetype["archetype_id"], archetype["archetype_id"]),
    ).fetchall()
    return list(question_rows)


def _eligible_boss_fight_rows(
    db: Database,
    *,
    tier: str | None,
    section: str | None,
) -> list[Any]:
    conn = db.connect()
    today = date.today().isoformat()

    conditions = [
        "a.is_active = 1",
        "(a.skip_until IS NULL OR a.skip_until < ?)",
        "q.is_holdout = 0",
    ]
    params: list[Any] = [today]

    if tier:
        conditions.append("q.tier = ?")
        params.append(tier)
    if section:
        conditions.append("q.section = ?")
        params.append(section)

    archetypes = conn.execute(
        f"""SELECT a.archetype_id, a.name,
                  COUNT(at.attempt_id) as attempts,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END) as correct
           FROM archetypes a
           JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE {' AND '.join(conditions)}
           GROUP BY a.archetype_id
           HAVING COUNT(at.attempt_id) >= 5
              AND (SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END)
                   / COUNT(at.attempt_id)) BETWEEN 0.50 AND 0.79
           ORDER BY a.name ASC
           LIMIT 1""",
        tuple(params),
    ).fetchall()
    if not archetypes:
        return []

    archetype = archetypes[0]
    question_rows = conn.execute(
        """SELECT q.question_id, ? as name, ? as archetype_id
           FROM questions q
           WHERE q.archetype_id = ?
             AND q.is_holdout = 0
           ORDER BY q.question_id ASC
           LIMIT 25""",
        (archetype["name"], archetype["archetype_id"], archetype["archetype_id"]),
    ).fetchall()
    return list(question_rows)
