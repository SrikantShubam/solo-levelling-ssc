"""Tests for QueueManager."""

from __future__ import annotations

from ssc_study.queues import QueueManager


class TestQueueManager:
    """QueueManager basic functionality."""

    def test_get_batch_active(self, seeded_db):
        """Active queue returns non-holdout questions."""
        qm = QueueManager(seeded_db)
        questions = qm.get_batch("active", count=5)
        assert len(questions) <= 5
        assert all(not q.is_holdout for q in questions)

    def test_get_batch_sm2(self, seeded_db):
        """SM-2 queue returns due questions."""
        qm = QueueManager(seeded_db)
        questions = qm.get_batch("sm2_review", count=5)
        assert isinstance(questions, list)

    def test_get_batch_unknown_type(self, seeded_db):
        """Unknown queue type raises ValueError."""
        qm = QueueManager(seeded_db)
        import pytest
        with pytest.raises(ValueError, match="Unknown queue type"):
            qm.get_batch("nonexistent", count=5)

    def test_get_queue_sizes(self, seeded_db):
        """Queue sizes returns a QueueSizes object."""
        qm = QueueManager(seeded_db)
        sizes = qm.get_queue_sizes()
        assert sizes.active >= 0
        assert sizes.sm2_review >= 0
        assert sizes.remediation >= 0
        assert sizes.boss_fight >= 0

    def test_get_available_queues(self, seeded_db):
        """Available queues lists non-empty queues."""
        qm = QueueManager(seeded_db)
        available = qm.get_available_queues()
        assert isinstance(available, list)
        assert "active" in available

    def test_active_excludes_holdout(self, seeded_db):
        """Active queue excludes holdout questions."""
        qm = QueueManager(seeded_db)
        questions = qm.get_batch("active", count=50)
        ids = [q.question_id for q in questions]
        assert "q11" not in ids  # q11 is holdout

    def test_tier_filter(self, seeded_db):
        """Tier filter narrows results."""
        qm = QueueManager(seeded_db)
        questions = qm.get_batch("active", count=10, tier="tier2")
        assert all(q.tier == "tier2" for q in questions)

    def test_section_filter(self, seeded_db):
        """Section filter narrows results."""
        qm = QueueManager(seeded_db)
        questions = qm.get_batch("active", count=10, section="English")
        assert all(q.section == "English" for q in questions)
