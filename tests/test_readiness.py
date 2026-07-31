"""Tests for readiness dashboard."""

from __future__ import annotations

from ssc_study.readiness import (
    CheckResult,
    ReadinessReport,
    compute_readiness,
    get_readiness_summary,
)


class TestComputeReadiness:
    """compute_readiness returns a complete report."""

    def test_returns_report(self, seeded_db):
        """Returns a ReadinessReport even with no data."""
        report = compute_readiness(seeded_db)
        assert isinstance(report, ReadinessReport)
        assert isinstance(report.ready, bool)
        assert isinstance(report.checks, dict)
        assert isinstance(report.missing, list)
        assert report.timestamp is not None

    def test_all_checks_present(self, seeded_db):
        """All required checks are in the report."""
        report = compute_readiness(seeded_db)
        required_checks = {
            "foundation_pulse",
            "tier1_archetypes",
            "tier2_archetypes",
            "floor_math",
            "floor_reasoning",
            "floor_english",
            "floor_ga",
            "floor_ck",
            "reasoning_tier2",
            "cbic_readiness",
            "mock_performance",
            "mock_diversity",
            "section_floor",
            "elimination_skill",
            "readiness_trend",
        }
        present = set(report.checks.keys())
        missing = required_checks - present
        assert not missing, f"Missing checks: {missing}"

    def test_each_check_has_result(self, seeded_db):
        """Every check has a CheckResult with all fields."""
        report = compute_readiness(seeded_db)
        for name, check in report.checks.items():
            assert isinstance(check, CheckResult), f"{name} is not a CheckResult"
            assert check.name, f"{name} has no name"
            assert isinstance(check.passed, bool), f"{name}.passed not bool"
            assert check.actual, f"{name} has no actual value"
            assert check.required, f"{name} has no required value"


class TestFoundationPulseSealedMock:
    """Regression: sealed_mock must count toward foundation pulse like mock did pre-rename."""

    def test_sealed_mock_attempts_feed_foundation_pulse_check(self, seeded_db):
        """Quant/DI attempts from sealed_mock sessions count in the 14-day pulse check."""
        from datetime import datetime, timezone

        from ssc_study.readiness import _check_foundation_pulse

        conn = seeded_db.connect()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO sessions (session_type, started_at, tier, question_count, notes)
               VALUES ('sealed_mock', ?, 'tier1', 4, 'sealed holdout mock')""",
            (now,),
        )
        session_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        for qid in ("q1", "q2", "q3", "q11"):
            conn.execute(
                """INSERT INTO attempts (session_id, question_id, user_answer, is_correct)
                   VALUES (?, ?, '1', 1)""",
                (session_id, qid),
            )
        conn.commit()

        result = _check_foundation_pulse(seeded_db)

        # Before the fix, sealed_mock is excluded and Quant/DI shows 0 attempts.
        assert "Quant/DI: 0% (0/0)" not in result.actual


class TestGetReadinessSummary:
    """get_readiness_summary returns a compact summary."""

    def test_returns_summary(self, seeded_db):
        """Summary has all required fields."""
        summary = get_readiness_summary(seeded_db)
        assert "ready" in summary
        assert "passed_checks" in summary
        assert "total_checks" in summary
        assert "missing" in summary
        assert "percent" in summary

    def test_totals_match(self, seeded_db):
        """passed + len(missing) == total."""
        summary = get_readiness_summary(seeded_db)
        assert summary["passed_checks"] + len(summary["missing"]) == summary["total_checks"]
