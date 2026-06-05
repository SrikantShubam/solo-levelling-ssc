"""Corpus loader tests — import and verification."""

from __future__ import annotations

from ssc_study._normalize import QUANT_DI, REASONING, get_pdf_year_tier, normalize_section
from ssc_study.models import Question


def test_normalize_section_known():
    """Known section names map correctly."""
    assert normalize_section("Quantitative Aptitude") == QUANT_DI
    assert normalize_section("General Intelligence and Reasoning") == REASONING
    assert normalize_section("English Language and Comprehension") == "English"


def test_normalize_section_unknown():
    """Unknown section names are passed through."""
    result = normalize_section("Mystery Subject")
    assert result == "Mystery Subject"


def test_normalize_section_empty():
    """Empty string defaults to Quant/DI."""
    assert normalize_section("") == QUANT_DI


def test_get_pdf_year_tier():
    """Year and tier extraction from PDF directory names."""
    y, t = get_pdf_year_tier("2021_tier1_prepp_shift1")
    assert y == 2021
    assert t == "tier1"

    y2, t2 = get_pdf_year_tier("2024_tier2_prepp_paper1")
    assert y2 == 2024
    assert t2 == "tier2"


def test_question_from_merged_json(sample_question_data):
    """Question.from_merged_json creates a valid Question."""
    q = Question.from_merged_json(
        sample_question_data,
        section="Reasoning",
        year=2021,
        tier="tier1",
    )

    assert q.question_id == "1235689"
    assert q.section == "Reasoning"
    assert q.year == 2021
    assert q.tier == "tier1"
    assert q.correct_option_label == "3"
    assert len(q.options) == 4
    assert q.options[0].label == "1"
    assert q.options[0].text == "Sister"
    assert not q.is_holdout  # set by loader, not factory


def test_question_from_merged_json_missing_fields():
    """Factory handles missing fields gracefully."""
    minimal = {
        "question_id": "1",
        "canonical_correct_option_label": "2",
        "question_text_full": "Test?",
        "options": [],
    }
    q = Question.from_merged_json(minimal, section="Quant/DI", year=2020, tier="tier2")
    assert q.question_id == "1"
    assert q.correct_option_label == "2"
    assert q.question_text == "Test?"
    assert not q.is_holdout
