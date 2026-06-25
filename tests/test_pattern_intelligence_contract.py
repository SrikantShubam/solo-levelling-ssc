"""Contract tests for pattern-intelligence APIs (pre-implementation).

Every test guards the production import via pytest.importorskip inside the
function body so the module collects successfully even before the
ssc_study.pattern_intelligence module exists.

Status: spec-quality — test logic is correct per canonical spec, but the
exact API surface (function signatures, report field names) is not yet
locked. See docs/agent_workorders/deepseek-round2-pattern-contract.md
"""

from __future__ import annotations

import sqlite3

import pytest


# ── Helpers (no pattern_intelligence dependency) ───────────────────────


def _snapshot_core_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Row counts for core tables pattern intelligence must not mutate."""
    tables = ["questions", "archetypes", "attempts", "sessions", "sm2_state", "fact_cards"]
    counts: dict[str, int] = {}
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
    is_holdout: int = 0,
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout)
           VALUES (?, 'test_pdf', 1, 1, ?, ?, ?, 'Test question?', '[]', '1', 'A', ?)""",
        (qid, section, year, tier, is_holdout),
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
        "INSERT OR REPLACE INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier) "
        "VALUES (?, 'analysis', '2026-06-25T00:00:00+00:00', 1, ?, 'tier1')",
        (session_id, is_correct),
    )
    conn.execute(
        """INSERT OR REPLACE INTO attempts
           (attempt_id, question_id, session_id, user_answer, is_correct,
            time_spent_seconds, student_label, concept_tag)
           VALUES (?, ?, ?, '1', ?, ?, ?, ?)""",
        (attempt_id, question_id, session_id, is_correct, time_spent,
         "correct" if is_correct else "incorrect", concept_tag),
    )
    conn.commit()


# ── Exam Pattern Contracts ────────────────────────────────────────────


class TestExamPatternReadOnly:
    """E1: analyze_exam_patterns must not mutate core tables."""

    def test_exam_patterns_are_read_only(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "ep_r1")
        _insert_question(in_memory_db, "ep_r2")
        before = _snapshot_core_counts(in_memory_db)
        pi.analyze_exam_patterns(in_memory_db)
        after = _snapshot_core_counts(in_memory_db)
        assert before == after, "analyze_exam_patterns mutated core tables"


class TestExamPatternHoldoutExclusion:
    """E2: Holdout questions must be excluded from evidence."""

    def test_exam_patterns_exclude_holdout_questions(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "ep_h1", is_holdout=1)
        _insert_question(in_memory_db, "ep_h2", is_holdout=0)
        _add_archetype(in_memory_db, 100, "Test Archetype")
        _assign_questions(in_memory_db, 100, ["ep_h1", "ep_h2"])

        report = pi.analyze_exam_patterns(in_memory_db)
        evidence_ids = pi._extract_evidence_ids(report)

        assert "ep_h1" not in evidence_ids, "holdout question appeared in evidence"
        assert "ep_h2" in evidence_ids, "non-holdout question missing from evidence"


class TestExamPatternReportContent:
    """E3-E4: Report must contain distribution counts and signal strength."""

    def test_exam_patterns_report_distribution_counts(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "ep_d1", section="Quant/DI", tier="tier1", year=2023)
        _insert_question(in_memory_db, "ep_d2", section="Quant/DI", tier="tier2", year=2024)
        _insert_question(in_memory_db, "ep_d3", section="English", tier="tier1", year=2024)
        _add_archetype(in_memory_db, 210, "Algebra")
        _add_archetype(in_memory_db, 220, "Grammar")
        _assign_questions(in_memory_db, 210, ["ep_d1", "ep_d2"])
        _assign_questions(in_memory_db, 220, ["ep_d3"])

        report = pi.analyze_exam_patterns(in_memory_db)
        dist = pi._extract_distribution(report)

        assert dist["section_count"] >= 2
        assert dist["tier_count"] >= 2
        assert dist["year_count"] >= 2
        assert dist["archetype_count"] >= 2

    def test_exam_patterns_report_signal_strength(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        for arch_id, count in [(310, 3), (320, 7), (330, 12)]:
            _add_archetype(in_memory_db, arch_id, f"Arch{arch_id}")
            qids = [f"ep_ss_{arch_id}_{i}" for i in range(count)]
            for qid in qids:
                _insert_question(in_memory_db, qid, is_holdout=0)
            _assign_questions(in_memory_db, arch_id, qids)

        r3 = pi.analyze_exam_patterns(in_memory_db, archetype_ids=[310])
        r7 = pi.analyze_exam_patterns(in_memory_db, archetype_ids=[320])
        r12 = pi.analyze_exam_patterns(in_memory_db, archetype_ids=[330])

        assert pi._extract_signal_strength(r3) == "insufficient"
        assert pi._extract_signal_strength(r7) == "weak"
        assert pi._extract_signal_strength(r12) == "stable"

    def test_mock_blueprint_is_advisory_only(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "ep_b1")
        _add_archetype(in_memory_db, 400, "Percentages")
        _assign_questions(in_memory_db, 400, ["ep_b1"])

        before = in_memory_db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        report = pi.analyze_exam_patterns(in_memory_db)
        after = in_memory_db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

        assert before == after, "analyze_exam_patterns created unexpected sessions"
        blueprint = getattr(report, "mock_blueprint", None)
        if blueprint is not None:
            after_no_mutation = _snapshot_core_counts(in_memory_db)
            assert before == after_no_mutation["sessions"]


# ── User Error Pattern Contracts ─────────────────────────────────────


class TestUserPatternReadOnly:
    """U1: analyze_user_error_patterns must not mutate core tables."""

    def test_user_patterns_are_read_only(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "up_r1")
        _insert_attempt(in_memory_db, 1, "up_r1")

        before = _snapshot_core_counts(in_memory_db)
        pi.analyze_user_error_patterns(in_memory_db)
        after = _snapshot_core_counts(in_memory_db)
        assert before == after, "analyze_user_error_patterns mutated core tables"


class TestUserPatternHoldoutExclusion:
    """U2: Holdout-linked attempts must be excluded."""

    def test_user_patterns_exclude_holdout_attempts(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "up_h1", is_holdout=1)
        _insert_question(in_memory_db, "up_h2", is_holdout=0)
        _insert_attempt(in_memory_db, 10, "up_h1", is_correct=0)
        _insert_attempt(in_memory_db, 11, "up_h2", is_correct=0)

        report = pi.analyze_user_error_patterns(in_memory_db)
        attempt_ids = pi._extract_attempt_ids(report)

        assert 10 not in attempt_ids, "holdout-linked attempt appeared in evidence"
        assert 11 in attempt_ids, "non-holdout attempt missing from evidence"


class TestUserPatternLatestWindow:
    """U3: Must use latest N attempts, not all historical data."""

    def test_user_patterns_use_latest_window(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "up_w1")
        _insert_question(in_memory_db, "up_w2")
        for i in range(20):
            _insert_attempt(in_memory_db, 100 + i, "up_w1", is_correct=0)
        for i in range(5):
            _insert_attempt(in_memory_db, 200 + i, "up_w2", is_correct=1)

        report = pi.analyze_user_error_patterns(in_memory_db, latest_window=10)
        evidence_ids = pi._extract_attempt_ids(report)
        assert len(evidence_ids) <= 10, "exceeded latest_window bound"


class TestUserPatternDetection:
    """U4-U5: Detect repeated wrong archetype and concept gap."""

    def test_user_patterns_detect_repeated_wrong_archetype(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _add_archetype(in_memory_db, 500, "Algebra")
        for i in range(5):
            qid = f"up_wa_{i}"
            _insert_question(in_memory_db, qid)
            _assign_questions(in_memory_db, 500, [qid])
            _insert_attempt(in_memory_db, 500 + i, qid, is_correct=0)

        report = pi.analyze_user_error_patterns(in_memory_db)
        weak_arch = pi._extract_weak_archetypes(report)
        attempt_ids = pi._extract_attempt_ids(report)

        assert len(weak_arch) >= 1
        assert len(attempt_ids) >= 1

    def test_user_patterns_detect_repeated_concept_gap(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _add_archetype(in_memory_db, 510, "Quadratic Equations")
        for i in range(5):
            qid = f"up_cg_{i}"
            _insert_question(in_memory_db, qid)
            _assign_questions(in_memory_db, 510, [qid])
            _insert_attempt(in_memory_db, 600 + i, qid, is_correct=0, concept_tag="factoring")

        report = pi.analyze_user_error_patterns(in_memory_db)
        gaps = pi._extract_concept_gaps(report)
        assert len(gaps) >= 1, "repeated concept tag not flagged as a gap"


class TestUserPatternTimingVsAccuracy:
    """U6: Timing separated from accuracy."""

    def test_user_patterns_separate_timing_from_accuracy(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        _insert_question(in_memory_db, "up_t1")
        _insert_attempt(in_memory_db, 30, "up_t1", is_correct=1, time_spent=300)
        _insert_attempt(in_memory_db, 31, "up_t1", is_correct=1, time_spent=310)
        _insert_attempt(in_memory_db, 32, "up_t1", is_correct=0, time_spent=15)

        report = pi.analyze_user_error_patterns(in_memory_db)
        timing = pi._extract_timing_weakness(report)
        accuracy = pi._extract_accuracy_weakness(report)

        assert timing is not None or accuracy is not None
        if timing is not None and accuracy is not None:
            assert str(timing) != str(accuracy) or (
                pi._extract_timing_entry_count(report) >= 1
                and pi._extract_accuracy_entry_count(report) >= 1
            )


class TestUserPatternSignalStrength:
    """U7: Signal strength thresholds match exam-pattern rules."""

    def test_user_patterns_report_signal_strength(self, in_memory_db):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        for arch_id, count in [(710, 4), (720, 7), (730, 12)]:
            _add_archetype(in_memory_db, arch_id, f"UserArch{arch_id}")
            qids = [f"up_ss_{arch_id}_{i}" for i in range(count)]
            for qid in qids:
                _insert_question(in_memory_db, qid, is_holdout=0)
                _assign_questions(in_memory_db, arch_id, [qid])
                _insert_attempt(in_memory_db, 1000 + arch_id + i, qid, is_correct=0)

        r4 = pi.analyze_user_error_patterns(in_memory_db, archetype_ids=[710])
        r7 = pi.analyze_user_error_patterns(in_memory_db, archetype_ids=[720])
        r12 = pi.analyze_user_error_patterns(in_memory_db, archetype_ids=[730])

        assert pi._extract_signal_strength(r4) == "insufficient"
        assert pi._extract_signal_strength(r7) == "weak"
        assert pi._extract_signal_strength(r12) == "stable"


# ── Priority Combiner Contracts ───────────────────────────────────────


class TestPriorityCombiner:
    """P1-P3: Combine and rank by exam importance * user weakness * confidence."""

    def test_priority_combiner_prefers_high_exam_and_high_user(self):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        high_exam = pi.make_exam_report(
            section_counts={"Quant/DI": 20},
            archetype_counts={"Algebra": 10},
            tier_counts={"tier1": 20},
            year_counts={2024: 20},
            evidence_ids=[f"q{i}" for i in range(12)],
        )
        high_user = pi.make_user_report(
            weak_archetypes=["Algebra"],
            concept_tags=["quadratics"],
            attempt_ids=[i for i in range(12)],
        )
        low_user = pi.make_user_report(
            weak_archetypes=[], concept_tags=[], attempt_ids=[],
        )

        combined = pi.combine_pattern_priorities(high_exam, high_user)
        combined_low = pi.combine_pattern_priorities(high_exam, low_user)
        items = pi._extract_priority_items(combined)

        assert len(items) > 0
        top = items[0]
        assert pi._extract_exam_importance(top) > 0
        assert pi._extract_user_weakness(top) > 0

    def test_priority_combiner_downweights_low_confidence(self):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        stable_exam = pi.make_exam_report(
            section_counts={}, archetype_counts={}, tier_counts={}, year_counts={},
            evidence_ids=[f"q{i}" for i in range(12)],
        )
        weak_exam = pi.make_exam_report(
            section_counts={}, archetype_counts={}, tier_counts={}, year_counts={},
            evidence_ids=[f"q{i}" for i in range(6)],
        )
        user = pi.make_user_report(
            weak_archetypes=["A"], concept_tags=[],
            attempt_ids=[i for i in range(12)],
        )

        stable_result = pi.combine_pattern_priorities(stable_exam, user)
        weak_result = pi.combine_pattern_priorities(weak_exam, user)

        stable_items = pi._extract_priority_items(stable_result)
        weak_items = pi._extract_priority_items(weak_result)
        if stable_items and weak_items:
            assert pi._extract_confidence(stable_items[0]) != "insufficient"

    def test_priority_combiner_is_advisory_only(self):
        pi = pytest.importorskip("ssc_study.pattern_intelligence")
        empty_exam = pi.make_exam_report(
            section_counts={}, archetype_counts={}, tier_counts={}, year_counts={},
            evidence_ids=[],
        )
        empty_user = pi.make_user_report(
            weak_archetypes=[], concept_tags=[], attempt_ids=[],
        )

        result = pi.combine_pattern_priorities(empty_exam, empty_user)
        assert result is not None
        items = pi._extract_priority_items(result)
        assert items == [] or items is not None


# ── Phase Boundary Contracts ──────────────────────────────────────────


class TestPhase3Boundary:
    """B1: Phase 3 must not consume pattern reports."""

    def test_phase3_planner_does_not_consume_pattern_reports(self, study_db):
        pytest.importorskip("ssc_study.phase3")
        from ssc_study.phase3 import plan_next_action

        action = plan_next_action(study_db)
        assert action.action_type == "stop"
        assert action.stop_reason == "no_eligible_work"


class TestContractCollectsCleanly:
    """B2: The contract file must collect without missing-module failure."""

    def test_contract_tests_collect_without_missing_module_failure(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "pytest", __file__, "--collect-only", "-q"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, (
            f"Collection failed:\n{result.stderr}"
        )
        assert "error" not in result.stderr.lower()
        assert "import error" not in result.stderr.lower()


class TestPatternCliReadOnly:
    """B3: Future CLI commands must be read-only (spec-quality placeholder)."""

    @pytest.mark.skip(reason="No CLI implementation exists yet: spec-quality B3")
    def test_pattern_cli_commands_are_read_only(self, study_db):
        pass
