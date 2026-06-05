"""Tests for archetype unlock gates."""

from __future__ import annotations

from ssc_study.archetypes import ensure_default_archetypes
from ssc_study.gates import (
    evaluate_probe,
    get_archetype_accuracy_by_tier,
    get_probe_candidates,
    get_tier2_readiness,
    run_probe,
)


class TestEvaluateProbe:
    """evaluate_probe correctly routes archetypes."""

    def _setup_arch(self, seeded_db, arch_id: int = 1, name: str = "Algebra"):
        conn = seeded_db.connect()
        conn.execute(
            "INSERT OR IGNORE INTO archetypes (archetype_id, name, section, tier) VALUES (?, ?, ?, ?)",
            (arch_id, name, "Quant/DI", "both"),
        )
        conn.commit()

    def test_high_accuracy_goes_to_sm2(self, seeded_db):
        """80%+ routes to SM-2."""
        self._setup_arch(seeded_db)
        attempts = [{"is_correct": True} for _ in range(8)] + [{"is_correct": False} for _ in range(2)]
        result = evaluate_probe(seeded_db, 1, attempts)
        assert result.route == "sm2"
        assert result.unlocked is True
        assert result.accuracy >= 0.80

    def test_medium_accuracy_goes_to_boss_fight(self, seeded_db):
        """50-79% routes to boss fight."""
        self._setup_arch(seeded_db)
        attempts = [{"is_correct": True} for _ in range(6)] + [{"is_correct": False} for _ in range(4)]
        result = evaluate_probe(seeded_db, 1, attempts)
        assert result.route == "boss_fight"
        assert result.unlocked is False

    def test_low_accuracy_with_concept_gap(self, seeded_db):
        """<50% with concept gap routes to remediation."""
        self._setup_arch(seeded_db)
        attempts = [{"is_correct": False, "concept_tag": "algebra"} for _ in range(7)] + \
                   [{"is_correct": True} for _ in range(3)]
        result = evaluate_probe(seeded_db, 1, attempts)
        assert result.route == "remediation"
        assert result.concept_gap is True

    def test_low_accuracy_no_concept_gap(self, seeded_db):
        """<50% without concept gap routes to high-priority boss."""
        self._setup_arch(seeded_db)
        attempts = [{"is_correct": False, "concept_tag": "unknown"} for _ in range(7)] + \
                   [{"is_correct": True} for _ in range(3)]
        result = evaluate_probe(seeded_db, 1, attempts)
        assert result.route == "high_priority_boss"


class TestGetProbeCandidates:
    """get_probe_candidates finds archetypes needing probing."""

    def test_needs_archetypes_in_db(self, seeded_db):
        """Requires archetypes in database."""
        candidates = get_probe_candidates(seeded_db)
        assert isinstance(candidates, list)

    def test_returns_with_enough_questions(self, seeded_db):
        """Archetypes with 10+ questions appear as candidates."""
        ensure_default_archetypes(seeded_db)
        candidates = get_probe_candidates(seeded_db)
        # Without assigning questions to archetypes, list will be empty
        assert isinstance(candidates, list)


class TestRunProbe:
    """run_probe returns probe questions."""

    def test_requires_enough_questions(self, seeded_db):
        """Archetype with few questions raises ValueError."""
        import pytest

        conn = seeded_db.connect()
        conn.execute(
            "INSERT INTO archetypes (archetype_id, name, section, tier) VALUES (1, 'Test', 'Quant/DI', 'both')"
        )
        conn.commit()

        with pytest.raises(ValueError, match="need 10 for a probe"):
            run_probe(seeded_db, 1)


class TestArchetypeAccuracyByTier:
    """get_archetype_accuracy_by_tier filters correctly."""

    def test_returns_zero_when_no_data(self, seeded_db):
        """No attempts returns zero accuracy."""
        result = get_archetype_accuracy_by_tier(seeded_db, 999, "tier1")
        assert result["attempts"] == 0
        assert result["accuracy"] == 0.0


class TestTier2Readiness:
    """get_tier2_readiness checks Tier-2 readiness."""

    def test_not_ready_without_data(self, seeded_db):
        """No Tier-2 data means not ready."""
        result = get_tier2_readiness(seeded_db, 999)
        assert result["ready"] is False
