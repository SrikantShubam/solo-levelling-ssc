"""Tests for the SM-2 review scheduler."""

from __future__ import annotations

from ssc_study.scheduler import (
    DueStats,
    get_due_archetypes,
    get_due_questions,
    get_due_stats,
    record_review,
)


class TestGetDueQuestions:
    """get_due_questions returns correct questions in priority order."""

    def test_returns_overdue_first(self, seeded_db):
        """Overdue questions (next_review <= today) come first."""
        questions = get_due_questions(seeded_db, count=10)
        ids = [q.question_id for q in questions]

        # q1 is overdue (2020-01-01); should be first
        assert ids[0] == "q1", f"Expected q1 first, got {ids}"

    def test_excludes_holdout(self, seeded_db):
        """Holdout questions should not appear."""
        questions = get_due_questions(seeded_db, count=50)
        ids = [q.question_id for q in questions]
        assert "q11" not in ids, "Holdout q11 should be excluded"

    def test_tier_filter(self, seeded_db):
        """Tier filter narrows results to the given tier."""
        questions = get_due_questions(seeded_db, count=50, tier="tier2")
        for q in questions:
            assert q.tier == "tier2", f"Expected tier2, got {q.tier} for {q.question_id}"

    def test_section_filter(self, seeded_db):
        """Section filter narrows results."""
        questions = get_due_questions(seeded_db, count=50, section="English")
        for q in questions:
            assert q.section == "English", f"Expected English, got {q.section}"

    def test_count_limit(self, seeded_db):
        """Count parameter limits the number returned."""
        questions = get_due_questions(seeded_db, count=3)
        assert len(questions) <= 3

    def test_empty_db(self, in_memory_db):
        """Empty database returns empty list."""
        from pathlib import Path

        from ssc_study.db import Database

        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = in_memory_db

        questions = get_due_questions(db, count=10)
        assert questions == []


class TestGetDueStats:
    """get_due_stats returns correct summary statistics."""

    def test_counts_overdue(self, seeded_db):
        """One question overdue, one not due, rest never reviewed."""
        stats = get_due_stats(seeded_db)
        assert stats.total_due == 1  # only q1
        assert stats.new_questions == 8  # q3-q10 have no SM-2 state
        assert stats.total_questions == 10  # excluding holdout

    def test_returns_due_stats_object(self, seeded_db):
        """Returns a DueStats instance with all fields."""
        stats = get_due_stats(seeded_db)
        assert isinstance(stats, DueStats)
        assert stats.by_section is not None
        assert stats.by_tier is not None


class TestRecordReview:
    """record_review records a review with SM-2 update."""

    def test_records_new_review(self, seeded_db):
        """Reviewing a previously unseen question creates SM-2 state."""
        record_review(seeded_db, "q3", 5)
        conn = seeded_db.connect()
        row = conn.execute(
            "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = 'q3'"
        ).fetchone()
        assert row is not None
        assert row["easiness"] == 2.6  # 2.5 + 0.1 for quality 5
        assert row["repetitions"] == 1
        assert row["interval_days"] == 1

    def test_updates_existing_review(self, seeded_db):
        """Reviewing an already-reviewed question updates SM-2 state."""
        record_review(seeded_db, "q1", 5)
        conn = seeded_db.connect()
        row = conn.execute(
            "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = 'q1'"
        ).fetchone()
        assert row is not None
        assert row["repetitions"] == 2  # was 1, now 2
        assert row["interval_days"] == 6  # n=1 -> 6


class TestGetDueArchetypes:
    """get_due_archetypes returns archetypes needing probing."""

    def test_returns_empty_when_no_archetypes(self, seeded_db):
        """No archetypes means empty list."""
        result = get_due_archetypes(seeded_db)
        assert result == []
