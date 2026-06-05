"""Database schema and migration tests."""

from __future__ import annotations

import sqlite3

import pytest

from ssc_study.db import (
    MIGRATIONS,
    Database,
    apply_migrations,
    get_current_version,
)


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
