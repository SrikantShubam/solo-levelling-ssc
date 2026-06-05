"""Tests for skip-list lifecycle."""

from __future__ import annotations

from datetime import date, timedelta

from ssc_study.skips import (
    challenge_skip,
    get_skip_summary,
    get_skipped_archetypes,
    is_skipped,
    record_failed_gate,
    resolve_probe,
)


class TestRecordFailedGate:
    """record_failed_gate updates skip state correctly."""

    def test_first_failure_no_skip(self, seeded_db):
        """First failure increments counter, no skip."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        result = record_failed_gate(seeded_db, 1)
        assert result["skip_count"] == 1
        assert result["action_taken"] == "none"

    def test_second_failure_temp_skip(self, seeded_db):
        """Second failure creates temporary skip (14 days)."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)  # first
        result = record_failed_gate(seeded_db, 1)  # second
        assert result["skip_count"] == 2
        assert result["action_taken"] == "temporary_skip"

    def test_third_failure_permanent(self, seeded_db):
        """Third failure creates permanent skip."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)  # first
        record_failed_gate(seeded_db, 1)  # second
        result = record_failed_gate(seeded_db, 1)  # third
        assert result["skip_count"] == 3
        assert result["action_taken"] == "permanent_skip"

    def test_nonexistent_archetype(self, seeded_db):
        """Non-existent archetype returns no action."""
        result = record_failed_gate(seeded_db, 9999)
        assert result["skip_count"] == 0
        assert result["action_taken"] == "none"


class TestIsSkipped:
    """is_skipped detects skip states."""

    def test_not_skipped(self, seeded_db):
        """Unsullied archetype is not skipped."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        assert is_skipped(seeded_db, 1) is False

    def test_temp_skipped(self, seeded_db):
        """Temp-skipped archetype is skipped."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        assert is_skipped(seeded_db, 1) is True

    def test_permanent_skipped(self, seeded_db):
        """Permanently skipped archetype is skipped."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        assert is_skipped(seeded_db, 1) is True

    def test_expired_temp_skip(self, seeded_db):
        """Expired temp skip is no longer skipped."""
        conn = seeded_db.connect()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        conn.execute(
            "INSERT INTO archetypes (archetype_id, name, section, skip_until, is_active) "
            "VALUES (99, 'Test', 'Quant/DI', ?, 1)",
            (yesterday,),
        )
        conn.commit()
        assert is_skipped(seeded_db, 99) is False


class TestGetSkippedArchetypes:
    """get_skipped_archetypes lists all skipped."""

    def test_empty_when_none_skipped(self, seeded_db):
        """No archetypes means empty list."""
        skipped = get_skipped_archetypes(seeded_db)
        assert skipped == []

    def test_lists_temp_and_permanent(self, seeded_db):
        """Returns both temp and permanently skipped."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        _ensure_archetype(seeded_db, 2, "Geometry")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)  # temp skip
        record_failed_gate(seeded_db, 2)
        record_failed_gate(seeded_db, 2)
        record_failed_gate(seeded_db, 2)  # permanent skip

        skipped = get_skipped_archetypes(seeded_db)
        ids = [s.archetype_id for s in skipped]
        assert 1 in ids
        assert 2 in ids


class TestChallengeSkip:
    """challenge_skip handles re-entry probes."""

    def test_rejects_active_archetype(self, seeded_db):
        """Active archetype cannot be challenged."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        result = challenge_skip(seeded_db, 1)
        assert result["allowed"] is False

    def test_allows_permanent_skip_challenge(self, seeded_db):
        """Permanently skipped archetype can be challenged via audit."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        result = challenge_skip(seeded_db, 1)
        assert result["allowed"] is True
        assert result["probe_size"] == 5


class TestResolveProbe:
    """resolve_probe handles probe outcomes."""

    def test_passed_probe_reactivates(self, seeded_db):
        """60%+ probe accuracy re-activates archetype."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)  # permanent skip

        result = resolve_probe(seeded_db, 1, 4, 5)  # 80%
        assert result["passed"] is True
        assert is_skipped(seeded_db, 1) is False

    def test_failed_probe_stays_skipped(self, seeded_db):
        """Below-threshold probe keeps archetype skipped."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)

        result = resolve_probe(seeded_db, 1, 2, 5)  # 40%
        assert result["passed"] is False
        assert is_skipped(seeded_db, 1) is True


class TestGetSkipSummary:
    """get_skip_summary returns correct counts."""

    def test_returns_counts(self, seeded_db):
        """Summary reflects current skip state."""
        _ensure_archetype(seeded_db, 1, "Algebra")
        _ensure_archetype(seeded_db, 2, "Geometry")
        record_failed_gate(seeded_db, 1)
        record_failed_gate(seeded_db, 1)

        summary = get_skip_summary(seeded_db)
        assert summary["total_archetypes"] >= 2


def _ensure_archetype(db, arch_id: int, name: str):
    """Helper to insert an archetype."""
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO archetypes (archetype_id, name, section, tier) VALUES (?, ?, ?, ?)",
        (arch_id, name, "Quant/DI", "both"),
    )
    conn.commit()
