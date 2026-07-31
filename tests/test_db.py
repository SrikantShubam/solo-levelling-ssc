"""Database schema and migration tests."""

from __future__ import annotations

import sqlite3

import pytest

from ssc_study.db import (
    MIGRATIONS,
    Database,
    StudyDBError,
    apply_migrations,
    get_current_version,
)


def _apply_migrations_through(conn: sqlite3.Connection, max_version: int) -> None:
    """Apply migrations up to max_version without using apply_migrations."""
    for version, description, sql in MIGRATIONS:
        if version > max_version:
            continue
        sql_to_run = sql.strip()
        if sql_to_run.startswith("-- FK_OFF"):
            sql_to_run = sql_to_run.removeprefix("-- FK_OFF").strip()
        for statement in sql_to_run.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(stmt)
        conn.execute(
            "INSERT INTO _schema_version (version, description) VALUES (?, ?)",
            (version, description),
        )
    conn.commit()


def test_schema_version_from_zero(in_memory_db):
    """First-run migration creates all tables."""
    conn = in_memory_db
    version = get_current_version(conn)
    assert version == len(MIGRATIONS), (
        f"Expected version {len(MIGRATIONS)}, got {version}"
    )


def test_migration_idempotent(in_memory_db):
    """Running migrations twice on the same DB is safe."""
    conn = in_memory_db
    v1 = get_current_version(conn)
    applied = apply_migrations(conn)
    v2 = get_current_version(conn)
    assert applied == 0, f"Expected 0 migrations, got {applied}"
    assert v1 == v2, f"Version changed: {v1} → {v2}"


def test_migration_14_preserves_existing_sessions_with_attempts():
    """v13 databases upgrade without breaking attempt session FKs."""
    assert any(version == 14 for version, _, _ in MIGRATIONS)

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row

    _apply_migrations_through(conn, max_version=13)
    assert get_current_version(conn) == 13

    conn.execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number, section,
            year, tier, question_text, options_json, correct_option_label)
           VALUES ('q_m14', 'pdf', 1, 1, 'Quant/DI', 2021, 'tier1',
                   'Question?', '[]', '1')"""
    )
    conn.execute(
        "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
    )
    session_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.execute(
        """INSERT INTO attempts (question_id, session_id, is_correct)
           VALUES ('q_m14', ?, 1)""",
        (session_id,),
    )
    conn.commit()

    applied = apply_migrations(conn)

    assert applied == sum(1 for version, _, _ in MIGRATIONS if version > 13)
    assert get_current_version(conn) == len(MIGRATIONS)
    session_type = conn.execute(
        "SELECT session_type FROM sessions WHERE session_id = ?", (session_id,)
    ).fetchone()["session_type"]
    assert session_type == "mock"
    conn.execute(
        "INSERT INTO sessions (session_type, started_at) VALUES ('sealed_mock', '2025-01-02')"
    )
    conn.commit()
    attempt = conn.execute(
        "SELECT marked_for_review FROM attempts WHERE question_id = 'q_m14'"
    ).fetchone()
    assert attempt["marked_for_review"] == 0


def test_all_tables_exist(in_memory_db):
    """Verify all expected tables are created."""
    conn = in_memory_db
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = {r["name"] for r in rows}

    expected = {
        "_schema_version",
        "_corpus_import_log",
        "passages",
        "questions",
        "archetypes",
        "sessions",
        "attempts",
        "sm2_state",
        "external_mocks",
        "fact_cards",
        "notification_audits",
    }
    missing = expected - names
    assert not missing, f"Missing tables: {missing}"


def test_passage_schema_links_questions(in_memory_db):
    conn = in_memory_db

    conn.execute(
        """INSERT INTO passages (pdf_name, source_page, passage_text)
           VALUES ('pdf', 1, 'Recovered passage text')"""
    )
    passage_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number, section,
            year, tier, question_text, options_json, correct_option_label, passage_id)
           VALUES ('q_passage', 'pdf', 1, 1, 'English', 2021, 'tier1',
                   'Select the most appropriate option to fill in blank number 1.',
                   '[]', '1', ?)""",
        (passage_id,),
    )
    conn.commit()

    row = conn.execute(
        """SELECT q.passage_id, p.passage_text
           FROM questions q
           JOIN passages p ON p.passage_id = q.passage_id
           WHERE q.question_id = 'q_passage'"""
    ).fetchone()
    assert row["passage_id"] == passage_id
    assert row["passage_text"] == "Recovered passage text"


def test_foreign_keys_enforced(in_memory_db):
    """Foreign key constraints are actually enforced."""
    conn = in_memory_db

    # Insert into sessions (parent) → ok
    conn.execute(
        "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
    )
    conn.commit()

    # Insert attempt with invalid session_id → should fail with IntegrityError
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        conn.execute(
            """INSERT INTO attempts
               (question_id, session_id, is_correct)
               VALUES ('nonexistent', 99999, 1)"""
        )


def test_new_database():
    """Creating a new temp database works end-to-end."""
    db = Database(":memory:")
    conn = db.connect()
    v = get_current_version(conn)
    assert v == len(MIGRATIONS)
    db.close()


def test_database_context_manager():
    """Database can be used as context manager."""
    import os
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    with Database(path) as db:
        conn = db.connect()
        v = get_current_version(conn)
        assert v == len(MIGRATIONS)

    # Cleanup
    import os as _os
    _os.unlink(path)
    for ext in ("-wal", "-shm"):
        p = path + ext
        if _os.path.exists(p):
            _os.unlink(p)


def test_execute_raises_study_db_error_when_connection_closed():
    db = Database(":memory:")
    db.close()

    with pytest.raises(StudyDBError, match="closed"):
        db.execute("SELECT 1")


def test_transaction_rolls_back_on_error(in_memory_db):
    db = Database.__new__(Database)
    db._path = ":memory:"
    db._lock = __import__("threading").RLock()
    db._conn = in_memory_db
    before = in_memory_db.execute("SELECT COUNT(*) FROM archetypes").fetchone()[0]

    with pytest.raises(RuntimeError, match="boom"):
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO archetypes (archetype_id, name, section, tier) VALUES (901, 'Rollback Test', 'Quant/DI', 'both')"
            )
            raise RuntimeError("boom")

    after = in_memory_db.execute("SELECT COUNT(*) FROM archetypes").fetchone()[0]
    assert after == before


def test_nested_transaction_uses_savepoints(in_memory_db):
    db = Database.__new__(Database)
    db._path = ":memory:"
    db._lock = __import__("threading").RLock()
    db._conn = in_memory_db

    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO archetypes (archetype_id, name, section, tier) VALUES (910, 'Outer', 'Quant/DI', 'both')"
        )
        with pytest.raises(ValueError, match="inner"):
            with db.transaction() as nested_conn:
                nested_conn.execute(
                    "INSERT INTO archetypes (archetype_id, name, section, tier) VALUES (911, 'Inner', 'Quant/DI', 'both')"
                )
                raise ValueError("inner")
        conn.execute(
            "INSERT INTO archetypes (archetype_id, name, section, tier) VALUES (912, 'Outer After', 'Quant/DI', 'both')"
        )

    rows = in_memory_db.execute(
        "SELECT archetype_id FROM archetypes WHERE archetype_id IN (910, 911, 912) ORDER BY archetype_id"
    ).fetchall()
    assert [row[0] for row in rows] == [910, 912]
