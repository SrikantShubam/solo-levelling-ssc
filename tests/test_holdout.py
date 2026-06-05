"""Tests for sealed-holdout mock policy."""

from __future__ import annotations

import json

from ssc_study.holdout import (
    check_monthly_cap,
    count_holdout_available,
    create_sealed_mock,
    ensure_holdout_usage_table,
    get_holdout_stats,
    get_holdout_usage,
)


def _add_holdout_question(conn, qid: str, tier: str = "tier1"):
    """Add a holdout question to the DB."""
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, is_holdout)
           VALUES (?, 'test', 1, 1, 'Quant/DI', 2021, ?, 'Holdout?', ?, '1', 1)""",
        (qid, tier, json.dumps([
            {"label": "1", "text": "A"},
            {"label": "2", "text": "B"},
            {"label": "3", "text": "C"},
            {"label": "4", "text": "D"},
        ])),
    )
    conn.commit()


class TestCheckMonthlyCap:
    """check_monthly_cap enforces max mocks per month."""

    def test_allows_first_mock(self, seeded_db):
        """First mock in a month is allowed."""
        cap = check_monthly_cap(seeded_db, "2026-06")
        assert cap["allowed"] is True
        assert cap["remaining"] == 2

    def test_rejects_third_mock(self, seeded_db):
        """Third mock in a month is rejected."""
        # Add sessions first, then log usage
        conn = seeded_db.connect()
        ensure_holdout_usage_table(seeded_db)
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        sid1 = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        sid2 = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        conn.execute(
            "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, 'tier1', '2026-06', 25)",
            (sid1,),
        )
        conn.execute(
            "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, 'tier1', '2026-06', 25)",
            (sid2,),
        )
        conn.commit()

        cap = check_monthly_cap(seeded_db, "2026-06")
        assert cap["allowed"] is False
        assert cap["remaining"] == 0


class TestCountHoldoutAvailable:
    """count_holdout_available counts holdout questions."""

    def test_counts_only_holdout(self, in_memory_db):
        """Only holdout questions are counted."""
        _add_holdout_question(in_memory_db, "hold_q1")
        _add_holdout_question(in_memory_db, "hold_q2")

        from pathlib import Path

        from ssc_study.db import Database
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = in_memory_db

        count = count_holdout_available(db)
        assert count >= 2


class TestCreateSealedMock:
    """create_sealed_mock creates holdout-based sessions."""

    def test_creates_session(self, seeded_db):
        """Creates a sealed mock when holdout questions exist."""
        _add_holdout_question(seeded_db.connect(), "hold_q1")

        result = create_sealed_mock(seeded_db, count=1)
        assert result["created"] is True
        assert result["session_id"] is not None
        row = seeded_db.connect().execute(
            "SELECT session_type FROM sessions WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert row["session_type"] == "mock"

    def test_rejects_when_cap_hit(self, seeded_db):
        """Rejects when monthly cap is reached."""
        conn = seeded_db.connect()
        _add_holdout_question(conn, "hold_q1")
        ensure_holdout_usage_table(seeded_db)
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        sid1 = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        sid2 = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        month = __import__("datetime").date.today().strftime("%Y-%m")
        conn.execute(
            "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, 'tier1', ?, 25)",
            (sid1, month),
        )
        conn.execute(
            "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, 'tier1', ?, 25)",
            (sid2, month),
        )
        conn.commit()

        result = create_sealed_mock(seeded_db, count=1)
        assert result["created"] is False


class TestGetHoldoutUsage:
    """get_holdout_usage returns usage records."""

    def test_returns_records(self, seeded_db):
        """Returns usage records after mocks are created."""
        ensure_holdout_usage_table(seeded_db)
        conn = seeded_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        sid = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
        conn.execute(
            "INSERT INTO holdout_usage_log (session_id, tier, month, question_count) VALUES (?, 'tier1', '2026-06', 25)",
            (sid,),
        )
        conn.commit()

        records = get_holdout_usage(seeded_db)
        assert len(records) >= 1
        assert records[0].tier == "tier1"


class TestGetHoldoutStats:
    """get_holdout_stats returns system stats."""

    def test_returns_stats(self, seeded_db):
        """Stats are returned even with no holdout data."""
        stats = get_holdout_stats(seeded_db)
        assert stats["total_holdout"] >= 0
        assert "available" in stats
        assert "usage_all_time" in stats
