"""Tests for session and daily reports."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from ssc_study.reports import daily_report, session_report


class TestSessionReport:
    """session_report renders session results correctly."""

    def test_nonexistent_session(self, seeded_db):
        """Non-existent session ID shows error."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        output = session_report(seeded_db, 9999, console)
        assert "not found" in output.lower()

    def test_renders_summary(self, seeded_db):
        """Report includes summary table for a real session."""
        conn = seeded_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        conn.commit()
        sid = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]

        conn.execute(
            "INSERT INTO attempts (question_id, session_id, is_correct) VALUES ('q1', ?, 1)",
            (sid,),
        )
        conn.execute(
            "INSERT INTO attempts (question_id, session_id, is_correct) VALUES ('q2', ?, 0)",
            (sid,),
        )
        conn.commit()

        console = Console(file=StringIO(), force_terminal=True, width=80)
        output = session_report(seeded_db, sid, console)

        assert "Session" in output
        assert "50.0%" in output  # 1/2 = 50% accuracy


class TestDailyReport:
    """daily_report renders today's practice summary."""

    def test_no_sessions_today(self, seeded_db):
        """Empty day shows appropriate message."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        output = daily_report(seeded_db, console)
        assert "no practice sessions" in output.lower()

    def test_renders_todays_sessions(self, seeded_db):
        """Report includes today's sessions."""
        from datetime import datetime, timezone

        today = datetime.now(timezone.utc).date().isoformat()
        conn = seeded_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at, question_count, correct_count, duration_minutes) "
            "VALUES ('mock', ?, 10, 7, 15)",
            (today,),
        )
        conn.commit()

        console = Console(file=StringIO(), force_terminal=True, width=80)
        output = daily_report(seeded_db, console)
        assert today in output
        assert "mock" in output.lower()
        assert "10" in output  # question count
