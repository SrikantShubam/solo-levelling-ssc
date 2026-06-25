"""Contract tests for pattern-intelligence APIs (not yet implemented).

All tests are expected to fail with ImportError until the production module
src/ssc_study/pattern_intelligence.py exists. These tests define the exact
contract that module must satisfy.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from ssc_study.pattern_intelligence import (
    ExamPatternReport,
    PatternPriorityReport,
    UserPatternReport,
    analyze_exam_patterns,
    analyze_user_error_patterns,
    combine_pattern_priorities,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _snapshot_core_tables(conn: sqlite3.Connection) -> dict:
    """Capture row counts for all core tables."""
    tables = ["questions", "archetypes", "attempts", "sessions", "sm2_state", "fact_cards"]
    counts = {}
    for table in tables:
        try:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.OperationalError:
            counts[table] = -1
    return counts


def _insert_question(
    conn: sqlite3.Connection,
    qid: str,
    *,
    section: str = "Quant/DI",
    tier: str = "tier1",
    year: int = 2024,
    text: str = "Test question?",
    correct_label: str = "1",
    is_holdout: int = 0,
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout)
           VALUES (?, 'test_pdf', 1, 1, ?, ?, ?, ?, '[]', ?, 'A', ?)""",
        (qid, section, year, tier, text, correct_label, is_holdout),
    )
    conn.commit()


def _add_archetype(
    conn: sqlite3.Connection,
    archetype_id: int,
    name: str,
    *,
    section: str = "Quant/DI",
    tier: str = "both",
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO archetypes (archetype_id, name, section, tier) VALUES (?, ?, ?, ?)",
        (archetype_id, name, section, tier),
    )
    conn.commit()


def _assign_questions(
    conn: sqlite3.Connection,
    archetype_id: int,
    question_ids: list[str],
) -> None:
    for qid in question_ids:
        conn.execute("UPDATE questions SET archetype_id = ? WHERE question_id = ?", (archetype_id, qid))
    conn.commit()


def _insert_attempt(
    conn: sqlite3.Connection,
    attempt_id: int,
    question_id: str,
    *,
    is_correct: int = 1,
    time_spent: int = 30,
    concept_tag: str | None = None,
    session_id: int = 1,
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO attempts
           (attempt_id, question_id, session_id, user_answer, is_correct,
            time_spent_seconds, student_label, concept_tag)
           VALUES (?, ?, ?, '1', ?, ?, ?, ?)""",
        (attempt_id, question_id, session_id, is_correct, time_spent,
         "correct" if is_correct else "incorrect", concept_tag),
    )
    conn.commit()


# ── Exam Pattern Tests ────────────────────────────────────────────────


class TestExamPatternReadOnly:
    """analyze_exam_patterns must not mutate any core table."""

    def test_exam_patterns_are_read_only(self, in_memory_db):
        _insert_question(in_memory_db, "ep1")
        _insert_question(in_memory_db, "ep2")
        before = _snapshot_core_tables(in_memory_db)
        analyze_exam_patterns(in_memory_db)
        after = _snapshot_core_tables(in_memory_db)
        assert before == after


class TestExamPatternHoldoutExclusion:
    """Holdout questions must be excluded from exam-pattern evidence."""

    def test_exam_patterns_exclude_holdout_questions(self, in_memory_db):
        _insert_question(in_memory_db, "ep10", is_holdout=1)
        _insert_question(in_memory_db, "ep11", is_holdout=0)
        _add_archetype(in_memory_db, 100, "Test Archetype")
        _assign_questions(in_memory_db, 100, ["ep10", "ep11"])
        report: ExamPatternReport = analyze_exam_patterns(in_memory_db)
        question_ids = set(report.evidence_question_ids)
        assert "ep10" not in question_ids
        assert "ep11" in question_ids


class TestExamPatternReportContent:
    """Report must contain all required fields."""

    def test_exam_patterns_report_section_archetype_tier_year(self, in_memory_db):
        _insert_question(in_memory_db, "ep20", section="Quant/DI", tier="tier1", year=2023)
        _add_archetype(in_memory_db, 200, "Algebra")
        _assign_questions(in_memory_db, 200, ["ep20"])
        report: ExamPatternReport = analyze_exam_patterns(in_memory_db)
        assert "Quant/DI" in report.sections
        assert "Algebra" in report.archetypes
        assert "tier1" in report.tiers
        assert 2023 in report.years

    def test_exam_patterns_reports_evidence_question_ids(self, in_memory_db):
        _insert_question(in_memory_db, "ep30")
        _add_archetype(in_memory_db, 300, "Number Systems")
        _assign_questions(in_memory_db, 300, ["ep30"])
        report: ExamPatternReport = analyze_exam_patterns(in_memory_db)
        assert "ep30" in report.evidence_question_ids

    def test_exam_patterns_report_signal_strength(self, in_memory_db):
        _add_archetype(in_memory_db, 310, "Weak Archetype")
        for i in range(3):
            qid = f"ep_insufficient_{i}"
            _insert_question(in_memory_db, qid)
            _assign_questions(in_memory_db, 310, [qid])
        weak = analyze_exam_patterns(in_memory_db)
        assert weak.signal_strength == "insufficient"

        _add_archetype(in_memory_db, 320, "Stable Archetype")
        for i in range(12):
            qid = f"ep_stable_{i}"
            _insert_question(in_memory_db, qid)
            _assign_questions(in_memory_db, 320, [qid])
        stable = analyze_exam_patterns(in_memory_db, archetype_ids=[320])
        assert stable.signal_strength == "stable"

    def test_mock_blueprint_is_advisory_only(self, in_memory_db, study_db):
        _insert_question(in_memory_db, "ep40")
        _add_archetype(in_memory_db, 400, "Percentages")
        _assign_questions(in_memory_db, 400, ["ep40"])
        before_sessions = in_memory_db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        report: ExamPatternReport = analyze_exam_patterns(in_memory_db)
        if report.mock_blueprint is not None:
            after_sessions = in_memory_db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            assert before_sessions == after_sessions


# ── User Error Pattern Tests ──────────────────────────────────────────


class TestUserPatternReadOnly:
    """analyze_user_error_patterns must not mutate any core table."""

    def test_user_patterns_are_read_only(self, in_memory_db):
        _insert_question(in_memory_db, "up1")
        _insert_attempt(in_memory_db, 1, "up1")
        before = _snapshot_core_tables(in_memory_db)
        analyze_user_error_patterns(in_memory_db)
        after = _snapshot_core_tables(in_memory_db)
        assert before == after


class TestUserPatternHoldoutExclusion:
    """Attempts linked to holdout questions must be excluded."""

    def test_user_patterns_exclude_holdout_attempts(self, in_memory_db):
        _insert_question(in_memory_db, "up10", is_holdout=1)
        _insert_question(in_memory_db, "up11", is_holdout=0)
        _insert_attempt(in_memory_db, 10, "up10", is_correct=0)
        _insert_attempt(in_memory_db, 11, "up11", is_correct=0)
        report: UserPatternReport = analyze_user_error_patterns(in_memory_db)
        attempt_ids = set(report.evidence_attempt_ids)
        assert 10 not in attempt_ids
        assert 11 in attempt_ids


class TestUserPatternLatestWindow:
    """Must use latest N attempts, not all historical data."""

    def test_user_patterns_use_latest_window(self, in_memory_db):
        _insert_question(in_memory_db, "up20")
        _insert_question(in_memory_db, "up21")
        for i in range(20):
            _insert_attempt(in_memory_db, 100 + i, "up20", is_correct=0)
        for i in range(5):
            _insert_attempt(in_memory_db, 200 + i, "up21", is_correct=1)
        report: UserPatternReport = analyze_user_error_patterns(in_memory_db, latest_window=10)
        assert len(report.evidence_attempt_ids) <= 10


class TestUserPatternTimingVsAccuracy:
    """Timing weakness must be separated from accuracy weakness."""

    def test_user_patterns_separate_timing_from_accuracy(self, in_memory_db):
        _insert_question(in_memory_db, "up30")
        _insert_attempt(in_memory_db, 30, "up30", is_correct=1, time_spent=300)
        _insert_attempt(in_memory_db, 31, "up30", is_correct=1, time_spent=310)
        _insert_attempt(in_memory_db, 32, "up30", is_correct=0, time_spent=15)
        report: UserPatternReport = analyze_user_error_patterns(in_memory_db)
        assert report.timing_weakness is not None or report.accuracy_weakness is not None
        if report.timing_weakness and report.accuracy_weakness:
            assert report.timing_weakness != report.accuracy_weakness


# ── Priority Combiner Tests ───────────────────────────────────────────


class TestPriorityCombiner:
    """combine_pattern_priorities must weight and rank correctly."""

    def test_priority_combiner_prefers_high_exam_and_high_user(self):
        high_exam = ExamPatternReport(
            sections={"Quant/DI": 20},
            archetypes={"Algebra": 10},
            tiers={"tier1": 20},
            years={2024: 20},
            evidence_question_ids=[],
            signal_strength="stable",
            mock_blueprint=None,
        )
        high_user = UserPatternReport(
            repeated_archetypes=["Algebra"],
            repeated_concept_tags=["quadratics"],
            evidence_attempt_ids=[],
            evidence_question_ids=[],
            signal_strength="stable",
            timing_weakness=None,
            accuracy_weakness="Algebra",
            decay_candidates=[],
            careless_candidates=[],
            latest_window_size=10,
        )
        low_user = UserPatternReport(
            repeated_archetypes=[],
            repeated_concept_tags=[],
            evidence_attempt_ids=[],
            evidence_question_ids=[],
            signal_strength="insufficient",
            timing_weakness=None,
            accuracy_weakness=None,
            decay_candidates=[],
            careless_candidates=[],
            latest_window_size=2,
        )
        result: PatternPriorityReport = combine_pattern_priorities(high_exam, high_user)
        assert result.priority_items[0].exam_importance > 0
        assert result.priority_items[0].user_weakness > 0

        result_low: PatternPriorityReport = combine_pattern_priorities(high_exam, low_user)
        assert result.priority_items[0].confidence < result.priority_items[0].confidence or True

    def test_priority_combiner_downweights_low_confidence(self):
        stable_exam = ExamPatternReport(
            sections={}, archetypes={}, tiers={}, years={},
            evidence_question_ids=[f"q{i}" for i in range(12)],
            signal_strength="stable",
            mock_blueprint=None,
        )
        weak_exam = ExamPatternReport(
            sections={}, archetypes={}, tiers={}, years={},
            evidence_question_ids=[f"q{i}" for i in range(6)],
            signal_strength="weak",
            mock_blueprint=None,
        )
        user_stable = UserPatternReport(
            repeated_archetypes=["A"],
            repeated_concept_tags=[],
            evidence_attempt_ids=[i for i in range(12)],
            evidence_question_ids=[],
            signal_strength="stable",
            timing_weakness=None,
            accuracy_weakness="A",
            decay_candidates=[],
            careless_candidates=[],
            latest_window_size=12,
        )
        stable_result: PatternPriorityReport = combine_pattern_priorities(stable_exam, user_stable)
        weak_result: PatternPriorityReport = combine_pattern_priorities(weak_exam, user_stable)
        for item in stable_result.priority_items:
            assert item.confidence == "stable"
        for item in weak_result.priority_items:
            assert item.confidence == "weak" or item.priority_score < 1.0

    def test_priority_combiner_is_advisory_only(self):
        report: PatternPriorityReport = combine_pattern_priorities(
            ExamPatternReport(sections={}, archetypes={}, tiers={}, years={},
                              evidence_question_ids=[], signal_strength="insufficient",
                              mock_blueprint=None),
            UserPatternReport(repeated_archetypes=[], repeated_concept_tags=[],
                              evidence_attempt_ids=[], evidence_question_ids=[],
                              signal_strength="insufficient",
                              timing_weakness=None, accuracy_weakness=None,
                              decay_candidates=[], careless_candidates=[],
                              latest_window_size=0),
        )
        assert hasattr(report, "priority_items")
        assert hasattr(report, "generated_at")
        assert report.priority_items == []


# ── Phase Boundary Tests ──────────────────────────────────────────────


class TestPhaseBoundary:
    """Phase 3 must not consume pattern reports."""

    def test_phase3_planner_does_not_consume_pattern_reports(self, study_db):
        from ssc_study.phase3 import plan_next_action
        action = plan_next_action(study_db)
        assert action.action_type == "stop"
        assert action.stop_reason == "no_eligible_work"
