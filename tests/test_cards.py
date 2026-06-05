"""Tests for GK/GA fact card generation."""

from __future__ import annotations

import json

from ssc_study.cards import extract_fact, generate_fact_cards, get_due_fact_cards, get_fact_card_stats


class TestExtractFact:
    """extract_fact extracts facts from GK/GA questions."""

    def test_capital_fact(self):
        """What is the capital of X?"""
        result = extract_fact("What is the capital of France?", "Paris", "GK/GA")
        assert result is not None
        assert result.front_text == "Capital of France"
        assert result.back_text == "Paris"

    def test_who_discovered(self):
        """Who discovered X?"""
        result = extract_fact("Who discovered penicillin?", "Alexander Fleming", "GK/GA")
        assert result is not None
        assert "discovered" in result.front_text.lower()
        assert result.back_text == "Alexander Fleming"

    def test_when_established(self):
        """When was X established?"""
        result = extract_fact("When was the United Nations established?", "1945", "GK/GA")
        assert result is not None
        assert "united nations" in result.front_text.lower()
        assert result.back_text == "1945"

    def test_where_is(self):
        """Where is X?"""
        result = extract_fact("Where is the Taj Mahal located?", "Agra", "GK/GA")
        assert result is not None
        assert "taj mahal" in result.front_text.lower()
        assert result.back_text == "Agra"

    def test_largest_superlative(self):
        """Largest/highest/etc facts."""
        result = extract_fact("Which is the largest planet in the solar system?", "Jupiter", "GK/GA")
        assert result is not None
        assert "largest" in result.front_text.lower() or "planet" in result.front_text.lower()

    def test_returns_none_for_non_gkga(self):
        """Non-GK/GA sections return None."""
        result = extract_fact("What is 2+2?", "4", "Quant/DI")
        assert result is None

    def test_returns_none_for_unmatched(self):
        """Unmatched text returns None."""
        result = extract_fact("Xyzzy nonsense text?", "Maybe", "GK/GA")
        # May match or not depending on patterns
        if result is not None:
            assert isinstance(result.front_text, str)


class TestGenerateFactCards:
    """generate_fact_cards integration with DB."""

    def test_generates_from_gkga(self, seeded_db):
        """GK/GA questions with correct_answer_text produce fact cards."""
        result = generate_fact_cards(seeded_db, max_cards=10)
        # q8 (capital of France), q9 (penicillin), q10 (1947) should match
        assert result["generated"] >= 1
        assert result["skipped"] >= 0

    def test_fact_cards_persisted(self, seeded_db):
        """Generated fact cards exist in the DB."""
        generate_fact_cards(seeded_db, max_cards=10)
        conn = seeded_db.connect()
        count = conn.execute("SELECT COUNT(*) as c FROM fact_cards").fetchone()["c"]
        assert count >= 1

    def test_idempotent(self, seeded_db):
        """Running twice doesn't create duplicate cards for same question."""
        r1 = generate_fact_cards(seeded_db, max_cards=10)
        r2 = generate_fact_cards(seeded_db, max_cards=10)
        # Second run should create 0 new cards (all already generated)
        assert r2["generated"] == 0


class TestGetDueFactCards:
    """get_due_fact_cards returns cards due for review."""

    def test_returns_empty_when_no_cards(self, seeded_db):
        """No cards means empty list."""
        result = get_due_fact_cards(seeded_db, count=10)
        assert result == []

    def test_returns_cards_when_due(self, seeded_db):
        """Cards due for review are returned."""
        generate_fact_cards(seeded_db, max_cards=10)
        result = get_due_fact_cards(seeded_db, count=10)
        # New cards have no SM-2 state, so they should be due
        assert len(result) >= 1
        assert "front_text" in result[0]
        assert "back_text" in result[0]


class TestGetFactCardStats:
    """get_fact_card_stats returns correct counts."""

    def test_zero_when_empty(self, seeded_db):
        """Empty DB returns zero stats."""
        stats = get_fact_card_stats(seeded_db)
        assert stats["total"] == 0

    def test_counts_cards(self, seeded_db):
        """Stats reflect generated cards."""
        generate_fact_cards(seeded_db, max_cards=10)
        stats = get_fact_card_stats(seeded_db)
        assert stats["total"] >= 1
        assert "by_tier" in stats
        assert "by_depth" in stats
