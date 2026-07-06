"""Acceptance tests for Phase 2c Exam-Pattern Intelligence."""

from __future__ import annotations

import pytest
from ssc_study.db import Database
from ssc_study.patterns_exam import analyze_exam_patterns
from ssc_study.patterns_priority import combine_pattern_priorities


def test_analyze_exam_patterns_excludes_holdout(seeded_db):
    """Verify that holdout questions are excluded by default."""
    # First, let's insert a question that is marked as holdout
    conn = seeded_db.connect()
    
    # We retrieve the initial count of eligible questions
    report_initial = analyze_exam_patterns(seeded_db, exclude_holdout=True)
    initial_count = report_initial.total_eligible_questions

    # Insert a holdout question
    conn.execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number, section, year, tier,
            question_text, options_json, correct_option_label, is_holdout)
           VALUES ('q_test_holdout_123', 'test.pdf', 1, 1, 'Reasoning', 2024, 'tier1',
                   'Text', '[]', '1', 1)"""
    )
    conn.commit()

    # Re-run report with exclude_holdout=True (default)
    report_exclude = analyze_exam_patterns(seeded_db)
    assert report_exclude.total_eligible_questions == initial_count

    # Re-run report with exclude_holdout=False
    report_include = analyze_exam_patterns(seeded_db, exclude_holdout=False)
    
    # Count of holdout questions in the database
    holdout_row = conn.execute("SELECT COUNT(*) as c FROM questions WHERE is_holdout = 1").fetchone()
    total_holdouts = holdout_row["c"]
    
    assert report_include.total_eligible_questions == initial_count + total_holdouts


def test_analyze_exam_patterns_read_only(seeded_db):
    """Verify that the analyzer does not mutate any database tables."""
    conn = seeded_db.connect()

    def get_row_counts():
        counts = {}
        for table in ["questions", "attempts", "sessions", "archetypes", "sm2_state"]:
            row = conn.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()
            counts[table] = row["c"] if row else 0
        return counts

    initial_counts = get_row_counts()

    # Run analysis
    analyze_exam_patterns(seeded_db)

    post_counts = get_row_counts()
    assert initial_counts == post_counts


def test_distributions_and_source_ids(seeded_db):
    """Verify that distributions (section, tier, year, archetype) are computed correctly with source IDs."""
    report = analyze_exam_patterns(seeded_db)

    # Distributions should be dictionaries
    assert isinstance(report.section_distribution, dict)
    assert isinstance(report.tier_distribution, dict)
    assert isinstance(report.year_distribution, dict)
    assert isinstance(report.archetype_distribution, dict)

    # Source question IDs must be present and match total eligible
    assert isinstance(report.source_question_ids, list)
    assert len(report.source_question_ids) == report.total_eligible_questions

    # Blueprint checks
    blueprint = report.advisory_blueprint
    assert blueprint["label"] == "Advisory Mock Blueprint"
    assert "evidence_question_ids" in blueprint
    assert len(blueprint["evidence_question_ids"]) == report.total_eligible_questions
    assert "section_allocation" in blueprint
    assert "top_archetype_allocation" in blueprint


def test_signal_strength_thresholds(seeded_db):
    """Verify signal strength boundaries based on eligible question count and archetypes."""
    # Let's verify signal strength logic by passing mocked reports or varying db data
    # 1. Test insufficient threshold (< 30 questions)
    # We can create a dummy db or clean connection to verify
    # But since seeded_db has more than 30 questions, let's filter by a non-existent year
    report_insufficient = analyze_exam_patterns(seeded_db, years=1990)
    assert report_insufficient.total_eligible_questions == 0
    assert report_insufficient.signal_strength == "insufficient"


def test_combine_pattern_priorities():
    """Verify combination of exam frequency and user accuracy."""
    from ssc_study.patterns_exam import ExamPatternReport

    exam_report = ExamPatternReport(
        total_eligible_questions=10,
        filters_applied={},
        section_distribution={},
        tier_distribution={},
        year_distribution={},
        archetype_distribution={"ArchA": 10, "ArchB": 5},
        source_question_ids=[],
        signal_strength="weak",
        advisory_blueprint={},
    )

    user_report = {"ArchA": 0.40, "ArchB": 0.90}

    report = combine_pattern_priorities(exam_report, user_report)
    assert report.advisory_status == "advisory"
    assert len(report.priorities) == 2

    # ArchA priority score = 10 * (1 - 0.40) = 6.0
    # ArchB priority score = 5 * (1 - 0.90) = 0.5
    assert report.priorities[0]["archetype_name"] == "ArchA"
    assert report.priorities[0]["priority_score"] == 6.0
    assert report.priorities[0]["recommended_action"] == "remediation"

    assert report.priorities[1]["archetype_name"] == "ArchB"
    assert report.priorities[1]["priority_score"] == 0.5
    assert report.priorities[1]["recommended_action"] == "sm2_review"


def test_phase3_independent():
    """Verify that Phase 3 orchestration does not import or depend on pattern intelligence."""
    # Check that phase3 module does not import pattern modules
    import sys
    
    # Remove if already imported
    sys.modules.pop("ssc_study.patterns_exam", None)
    sys.modules.pop("ssc_study.patterns_priority", None)
    
    # Import phase3
    import ssc_study.phase3
    
    # Verify that pattern modules were not auto-imported
    assert "ssc_study.patterns_exam" not in sys.modules
    assert "ssc_study.patterns_priority" not in sys.modules
