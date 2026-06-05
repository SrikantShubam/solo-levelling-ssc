"""Queue manager — replaces random question loading with structured queues.

Four queues:
  - active:       General non-holdout pool, excludes skipped archetypes.
  - sm2_review:   Due-for-review via scheduler.
  - remediation:  Weak-archetype questions + similar to recently missed.
  - boss_fight:   Archetypes in the 50-79% accuracy band, timed practice.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Any

from .db import Database
from .models import Question
from .scheduler import _row_to_question as _row_to_question_sched


@dataclass
class QueueSizes:
    active: int = 0
    sm2_review: int = 0
    remediation: int = 0
    boss_fight: int = 0


class QueueManager:
    """Manages question queues for the study app.

    Usage:
        qm = QueueManager(db)
        questions = qm.get_batch("active", count=25, tier="tier1")
        sizes = qm.get_queue_sizes()
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    # ── Public API ──────────────────────────────────────────────────

    def get_batch(
        self,
        queue_type: str,
        count: int = 25,
        tier: str | None = None,
        section: str | None = None,
    ) -> list[Question]:
        """Get the next batch of questions from the given queue.

        Args:
            queue_type: One of 'active', 'sm2_review', 'remediation', 'boss_fight'.
            count: Maximum number of questions to return.
            tier: Optional tier filter ('tier1' or 'tier2').
            section: Optional section filter.

        Returns:
            List of Question objects.
        """
        dispatch = {
            "active": self._active_batch,
            "sm2_review": self._sm2_batch,
            "remediation": self._remediation_batch,
            "boss_fight": self._boss_fight_batch,
        }
        handler = dispatch.get(queue_type)
        if handler is None:
            raise ValueError(f"Unknown queue type: {queue_type}")
        return handler(count, tier, section)

    def get_queue_sizes(self) -> QueueSizes:
        """Return the size of each queue."""
        return QueueSizes(
            active=self._count_active(),
            sm2_review=self._count_sm2(),
            remediation=self._count_remediation(),
            boss_fight=self._count_boss_fight(),
        )

    def get_available_queues(self) -> list[str]:
        """Return queue types that have questions available."""
        sizes = self.get_queue_sizes()
        available: list[str] = []
        if sizes.active > 0:
            available.append("active")
        if sizes.sm2_review > 0:
            available.append("sm2_review")
        if sizes.remediation > 0:
            available.append("remediation")
        if sizes.boss_fight > 0:
            available.append("boss_fight")
        return available

    # ── Active queue ────────────────────────────────────────────────

    def _active_batch(
        self, count: int, tier: str | None, section: str | None,
    ) -> list[Question]:
        """General pool: non-holdout, not from skipped archetypes."""
        conn = self.db.connect()
        conditions = ["q.is_holdout = 0"]
        params: list[Any] = []

        # Exclude skipped archetypes
        conditions.append(
            "(q.archetype_id IS NULL OR q.archetype_id NOT IN "
            "(SELECT archetype_id FROM archetypes "
            "WHERE is_active = 0 OR (skip_until IS NOT NULL AND skip_until >= ?)))"
        )
        params.append(date.today().isoformat())

        if tier:
            conditions.append("q.tier = ?")
            params.append(tier)
        if section:
            conditions.append("q.section = ?")
            params.append(section)

        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT q.* FROM questions q WHERE {where} ORDER BY RANDOM() LIMIT ?",
            params + [count],
        ).fetchall()
        return [_row_to_question_sched(r) for r in rows]

    def _count_active(self) -> int:
        conn = self.db.connect()
        today = date.today().isoformat()
        row = conn.execute(
            """SELECT COUNT(*) as c FROM questions q
               WHERE q.is_holdout = 0
                 AND (q.archetype_id IS NULL OR q.archetype_id NOT IN
                      (SELECT archetype_id FROM archetypes
                       WHERE is_active = 0 OR (skip_until IS NOT NULL AND skip_until >= ?)))""",
            (today,),
        ).fetchone()
        return row["c"] if row else 0

    # ── SM-2 review queue ───────────────────────────────────────────

    def _sm2_batch(
        self, count: int, tier: str | None, section: str | None,
    ) -> list[Question]:
        """Due-for-review questions via scheduler."""
        from .scheduler import get_due_questions
        return get_due_questions(
            self.db, count=count, tier=tier, section=section, exclude_holdout=True,
        )

    def _count_sm2(self) -> int:
        conn = self.db.connect()
        today = date.today().isoformat()
        row = conn.execute(
            "SELECT COUNT(*) as c FROM sm2_state s "
            "JOIN questions q ON q.question_id = s.entity_id "
            "WHERE s.entity_type = 'question' AND s.next_review <= ? "
            "AND q.is_holdout = 0",
            (today,),
        ).fetchone()
        return row["c"] if row else 0

    # ── Remediation queue ───────────────────────────────────────────

    def _remediation_batch(
        self, count: int, tier: str | None, section: str | None,
    ) -> list[Question]:
        """Questions from weak archetypes and similar to recently missed.

        Priority:
          1. Questions from archetypes with <65% accuracy (weak).
          2. Questions similar to recently missed questions (past 7 days).
        """
        conn = self.db.connect()
        weak_ids = self._get_weak_archetype_question_ids(conn, tier, section)

        if not weak_ids:
            return []

        # Shuffle weak IDs for variety
        import random
        random.shuffle(weak_ids)

        selected = weak_ids[:count]
        placeholders = ",".join("?" for _ in selected)
        rows = conn.execute(
            f"SELECT * FROM questions q WHERE q.question_id IN ({placeholders}) "
            f"AND q.is_holdout = 0 ORDER BY RANDOM() LIMIT ?",
            selected + [count],
        ).fetchall()
        return [_row_to_question_sched(r) for r in rows]

    def _count_remediation(self) -> int:
        conn = self.db.connect()
        weak_ids = self._get_weak_archetype_question_ids(conn, None, None)
        return len(weak_ids)

    def _get_weak_archetype_question_ids(
        self, conn: sqlite3.Connection, tier: str | None, section: str | None,
    ) -> list[str]:
        """Get question IDs from archetypes with below-threshold accuracy."""
        today = date.today().isoformat()

        # Find weak archetypes: <65% accuracy with at least 5 attempts
        tier_filter = ""
        params: list[Any] = []
        if tier:
            tier_filter = " AND q.tier = ?"
            params.append(tier)
        if section:
            tier_filter += " AND q.section = ?"
            params.append(section)

        weak_arch_rows = conn.execute(
            f"""SELECT a.archetype_id
                FROM archetypes a
                JOIN questions q ON q.archetype_id = a.archetype_id
                LEFT JOIN attempts at ON at.question_id = q.question_id
                WHERE a.is_active = 1
                  AND (a.skip_until IS NULL OR a.skip_until < ?)
                  AND q.is_holdout = 0
                  {tier_filter}
                GROUP BY a.archetype_id
                HAVING COUNT(at.attempt_id) >= 5
                   AND (SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END)
                        / COUNT(at.attempt_id)) < 0.65""",
            [today] + params,
        ).fetchall()

        if not weak_arch_rows:
            return []

        arch_ids = [str(r["archetype_id"]) for r in weak_arch_rows]
        placeholders = ",".join("?" for _ in arch_ids)

        q_rows = conn.execute(
            f"SELECT q.question_id FROM questions q "
            f"WHERE q.archetype_id IN ({placeholders}) AND q.is_holdout = 0",
            arch_ids,
        ).fetchall()
        return [r["question_id"] for r in q_rows]

    # ── Boss-fight queue ────────────────────────────────────────────

    def _boss_fight_batch(
        self, count: int, tier: str | None, section: str | None,
    ) -> list[Question]:
        """Questions from archetypes in the 50-79% accuracy band.

        These are archetypes that have been probed but need more work
        before graduating to SM-2.
        """
        conn = self.db.connect()

        boss_arch_rows = conn.execute(
            """SELECT a.archetype_id
               FROM archetypes a
               JOIN questions q ON q.archetype_id = a.archetype_id
               LEFT JOIN attempts at ON at.question_id = q.question_id
               WHERE a.is_active = 1 AND a.is_unlocked = 0
                 AND q.is_holdout = 0
               GROUP BY a.archetype_id
               HAVING COUNT(at.attempt_id) >= 5
                  AND (SUM(CASE WHEN at.is_correct = 1 THEN 1.0 ELSE 0.0 END)
                       / COUNT(at.attempt_id)) BETWEEN 0.50 AND 0.79""",
        ).fetchall()

        if not boss_arch_rows:
            # Fallback to active queue
            return self._active_batch(count, tier, section)

        arch_ids = [str(r["archetype_id"]) for r in boss_arch_rows]
        placeholders = ",".join("?" for _ in arch_ids)

        conditions = [
            f"q.archetype_id IN ({placeholders})",
            "q.is_holdout = 0",
        ]
        params: list[Any] = arch_ids
        if tier:
            conditions.append("q.tier = ?")
            params.append(tier)
        if section:
            conditions.append("q.section = ?")
            params.append(section)

        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT * FROM questions q WHERE {where} ORDER BY RANDOM() LIMIT ?",
            params + [count],
        ).fetchall()

        if rows:
            return [_row_to_question_sched(r) for r in rows]
        # Fallback
        return self._active_batch(count, tier, section)

    def _count_boss_fight(self) -> int:
        conn = self.db.connect()
        row = conn.execute(
            """SELECT COUNT(*) as c FROM questions q
               JOIN archetypes a ON a.archetype_id = q.archetype_id
               WHERE a.is_active = 1 AND a.is_unlocked = 0
                 AND q.is_holdout = 0"""
        ).fetchone()
        return row["c"] if row else 0
