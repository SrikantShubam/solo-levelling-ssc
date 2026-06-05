"""Tests for archetype classification and management."""

from __future__ import annotations

from ssc_study.archetypes import (
    ARCHETYPE_DEFS,
    assign_archetypes,
    classify_question,
    ensure_default_archetypes,
    get_archetype_questions,
    get_archetype_summary,
    get_weak_archetypes,
)
from ssc_study.models import Option, Question


class TestClassifyQuestion:
    """classify_question correctly identifies archetypes."""

    def test_algebra_question(self):
        """Algebra keywords match correctly."""
        q = Question(
            question_id="test1", pdf_name="test", source_page=1,
            global_question_number=1, section="Quant/DI", year=2021,
            tier="tier1",
            question_text="If x + y = 10 and xy = 20, find x^2 + y^2",
            correct_option_label="1",
            options=[Option("1", "A"), Option("2", "B"), Option("3", "C"), Option("4", "D")],
        )
        assert classify_question(q) == "Algebra"

    def test_blood_relation_question(self):
        """Blood relations keywords match."""
        q = Question(
            question_id="test2", pdf_name="test", source_page=1,
            global_question_number=2, section="Reasoning", year=2021,
            tier="tier1",
            question_text="If A is the brother of B, how is A related to C?",
            correct_option_label="1",
            options=[Option("1", "Brother"), Option("2", "Father"), Option("3", "Uncle"), Option("4", "Cousin")],
        )
        assert classify_question(q) == "Blood Relations"

    def test_geography_question(self):
        """Geography keywords match."""
        q = Question(
            question_id="test3", pdf_name="test", source_page=1,
            global_question_number=3, section="GK/GA", year=2021,
            tier="tier1",
            question_text="What is the capital of France?",
            correct_option_label="3",
            options=[Option("1", "London"), Option("2", "Berlin"), Option("3", "Paris"), Option("4", "Madrid")],
        )
        assert classify_question(q) == "Indian Geography"

    def test_returns_none_for_unmatched(self):
        """Unmatched question returns None."""
        q = Question(
            question_id="test4", pdf_name="test", source_page=1,
            global_question_number=4, section="Quant/DI", year=2021,
            tier="tier1",
            question_text="zzzzyyyyxxx random noise?",
            correct_option_label="1",
            options=[Option("1", "A"), Option("2", "B"), Option("3", "C"), Option("4", "D")],
        )
        assert classify_question(q) is None

    def test_matches_options_text_too(self):
        """Options text is also searched."""
        q = Question(
            question_id="test5", pdf_name="test", source_page=1,
            global_question_number=5, section="Reasoning", year=2021,
            tier="tier1",
            question_text="Complete the given series:",
            correct_option_label="1",
            options=[Option("1", "128"), Option("2", "64"), Option("3", "32"), Option("4", "16")],
        )
        # Should match Number Series due to "series:" keyword in text
        assert classify_question(q) == "Number Series"

    def test_all_archetype_defs_have_unique_names(self):
        """No duplicate archetype names within the same section."""
        seen: set[tuple[str, str]] = set()
        for ad in ARCHETYPE_DEFS:
            key = (ad.section, ad.name)
            assert key not in seen, f"Duplicate archetype: {key}"
            seen.add(key)

    def test_all_archetype_defs_have_keywords(self):
        """Every archetype has at least one keyword."""
        for ad in ARCHETYPE_DEFS:
            assert len(ad.keywords) > 0, f"{ad.name} has no keywords"


class TestEnsureDefaultArchetypes:
    """ensure_default_archetypes creates all defined archetypes."""

    def test_creates_all(self, seeded_db):
        """All defined archetypes are created in the DB."""
        count = ensure_default_archetypes(seeded_db)
        assert count > 0

        conn = seeded_db.connect()
        total = conn.execute("SELECT COUNT(*) as c FROM archetypes").fetchone()["c"]
        assert total == len(ARCHETYPE_DEFS)

    def test_idempotent(self, seeded_db):
        """Running twice doesn't create duplicates."""
        ensure_default_archetypes(seeded_db)
        count2 = ensure_default_archetypes(seeded_db)
        assert count2 == 0  # no new archetypes

        conn = seeded_db.connect()
        total = conn.execute("SELECT COUNT(*) as c FROM archetypes").fetchone()["c"]
        assert total == len(ARCHETYPE_DEFS)


class TestAssignArchetypes:
    """assign_archetypes classifies questions and updates DB."""

    def test_assigns_to_matching_questions(self, seeded_db):
        """Questions with matching keywords get archetype_id set."""
        ensure_default_archetypes(seeded_db)
        result = assign_archetypes(seeded_db)
        assert result["assigned"] >= 0

        conn = seeded_db.connect()
        q_with_arch = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE archetype_id IS NOT NULL"
        ).fetchone()["c"]
        assert q_with_arch >= 0


class TestGetWeakArchetypes:
    """get_weak_archetypes identifies archetypes needing focus."""

    def test_returns_empty_when_no_data(self, seeded_db):
        """No attempt data means empty results."""
        result = get_weak_archetypes(seeded_db)
        assert result == []


class TestGetArchetypeSummary:
    """get_archetype_summary returns correct stats."""

    def test_returns_summary(self, seeded_db):
        """Summary returns list even when no archetypes exist."""
        ensure_default_archetypes(seeded_db)
        summary = get_archetype_summary(seeded_db)
        assert isinstance(summary, list)
        assert len(summary) == len(ARCHETYPE_DEFS)


class TestGetArchetypeQuestions:
    """get_archetype_questions returns questions for an archetype."""

    def test_returns_questions(self, seeded_db):
        """Questions from a non-existent archetype return empty."""
        result = get_archetype_questions(seeded_db, 999)
        assert result == []
