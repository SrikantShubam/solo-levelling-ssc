"""SQLite connection, schema DDL, and ordered migrations."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any


class StudyDBError(Exception):
    """Raised for database-level failures."""


# Ordered migration list: (version, description, SQL)
MIGRATIONS: list[tuple[int, str, str]] = [
    (1, "schema version tracking", """
        CREATE TABLE IF NOT EXISTS _schema_version (
            version     INTEGER PRIMARY KEY,
            applied_at  TEXT NOT NULL DEFAULT (datetime('now')),
            description TEXT NOT NULL
        )
    """),
    (2, "corpus import log", """
        CREATE TABLE IF NOT EXISTS _corpus_import_log (
            import_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            import_hash    TEXT NOT NULL UNIQUE,
            pdf_count      INTEGER NOT NULL,
            question_count INTEGER NOT NULL,
            imported_at    TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (3, "questions table", """
        CREATE TABLE IF NOT EXISTS questions (
            question_id            TEXT PRIMARY KEY,
            pdf_name               TEXT NOT NULL,
            source_page            INTEGER NOT NULL,
            global_question_number INTEGER NOT NULL,
            section                TEXT NOT NULL,
            year                   INTEGER NOT NULL,
            tier                   TEXT NOT NULL CHECK (tier IN ('tier1', 'tier2')),
            question_text          TEXT NOT NULL,
            options_json           TEXT NOT NULL,
            correct_option_label   TEXT NOT NULL CHECK (correct_option_label IN ('1','2','3','4')),
            correct_option_text    TEXT,
            chosen_option_label    TEXT,
            question_modality      TEXT NOT NULL DEFAULT 'text_only',
            visual_required        INTEGER NOT NULL DEFAULT 0,
            table_required         INTEGER NOT NULL DEFAULT 0,
            math_required          INTEGER NOT NULL DEFAULT 0,
            evidence_status        TEXT,
            question_crop_path     TEXT,
            page_asset_path        TEXT,
            archetype_id           INTEGER REFERENCES archetypes(archetype_id),
            is_holdout             INTEGER NOT NULL DEFAULT 0,
            embedding_blob         BLOB,
            created_at             TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (4, "questions indexes", """
        CREATE INDEX IF NOT EXISTS idx_questions_section ON questions(section);
        CREATE INDEX IF NOT EXISTS idx_questions_tier ON questions(tier);
        CREATE INDEX IF NOT EXISTS idx_questions_archetype ON questions(archetype_id);
        CREATE INDEX IF NOT EXISTS idx_questions_section_tier ON questions(section, tier);
    """),
    (5, "archetypes table", """
        CREATE TABLE IF NOT EXISTS archetypes (
            archetype_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL UNIQUE,
            section          TEXT NOT NULL,
            tier             TEXT NOT NULL DEFAULT 'both' CHECK (tier IN ('tier1', 'tier2', 'both')),
            difficulty       TEXT NOT NULL DEFAULT 'medium' CHECK (difficulty IN ('easy','medium','hard')),
            t1_accuracy      REAL,
            t2_accuracy      REAL,
            unlock_condition TEXT,
            skip_until       TEXT,
            skip_count       INTEGER NOT NULL DEFAULT 0,
            is_unlocked      INTEGER NOT NULL DEFAULT 0,
            is_active        INTEGER NOT NULL DEFAULT 1,
            created_at       TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (6, "sessions table", """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type      TEXT NOT NULL CHECK (session_type IN (
                'sm2_review','boss_fight','tier2_module','gkga_memory',
                'english','mock','analysis','foundation_pulse','ck_pulse'
            )),
            started_at        TEXT NOT NULL,
            ended_at          TEXT,
            duration_minutes  INTEGER,
            question_count    INTEGER NOT NULL DEFAULT 0,
            correct_count     INTEGER NOT NULL DEFAULT 0,
            tier              TEXT CHECK (tier IN ('tier1', 'tier2')),
            notes             TEXT,
            created_at        TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (7, "attempts table", """
        CREATE TABLE IF NOT EXISTS attempts (
            attempt_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id        TEXT NOT NULL REFERENCES questions(question_id),
            session_id         INTEGER NOT NULL REFERENCES sessions(session_id),
            user_answer        TEXT CHECK (user_answer IN ('1','2','3','4')),
            is_correct         INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
            time_spent_seconds INTEGER NOT NULL DEFAULT 0,
            student_label      TEXT,
            timing_inference   TEXT,
            concept_tag        TEXT,
            quality_score      INTEGER CHECK (quality_score BETWEEN 0 AND 5),
            was_remediated     INTEGER NOT NULL DEFAULT 0,
            created_at         TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (8, "attempts indexes", """
        CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_session ON attempts(session_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_created ON attempts(created_at);
    """),
    (9, "sm2_state table", """
        CREATE TABLE IF NOT EXISTS sm2_state (
            entity_type   TEXT NOT NULL CHECK (entity_type IN ('question', 'archetype', 'fact_card')),
            entity_id     TEXT NOT NULL,
            easiness      REAL NOT NULL DEFAULT 2.5,
            interval_days INTEGER NOT NULL DEFAULT 0,
            repetitions   INTEGER NOT NULL DEFAULT 0,
            next_review   TEXT,
            last_review   TEXT,
            last_quality  INTEGER CHECK (last_quality BETWEEN 0 AND 5),
            created_at    TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (entity_type, entity_id)
        )
    """),
    (10, "external mocks table", """
        CREATE TABLE IF NOT EXISTS external_mocks (
            mock_id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mock_name            TEXT NOT NULL,
            source               TEXT NOT NULL,
            taken_at             TEXT NOT NULL,
            tier                 TEXT NOT NULL CHECK (tier IN ('tier1', 'tier2')),
            raw_score            INTEGER NOT NULL,
            calibrated_score     INTEGER,
            section_scores_json  TEXT,
            notes                TEXT,
            created_at           TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (11, "fact cards table", """
        CREATE TABLE IF NOT EXISTS fact_cards (
            card_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id     TEXT REFERENCES questions(question_id),
            front_text      TEXT NOT NULL,
            back_text       TEXT NOT NULL,
            tier_scope      TEXT NOT NULL CHECK (tier_scope IN ('tier1', 'tier2', 'both')),
            depth_level     TEXT NOT NULL CHECK (depth_level IN ('basic', 'deep')),
            cbic_relevance  INTEGER NOT NULL DEFAULT 0,
            source          TEXT,
            expires_on      TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
    (12, "fact cards indexes", """
        CREATE INDEX IF NOT EXISTS idx_fact_cards_cbic ON fact_cards(cbic_relevance);
    """),
    (13, "notification audits table", """
        CREATE TABLE IF NOT EXISTS notification_audits (
            audit_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_type         TEXT NOT NULL CHECK (audit_type IN ('notification','monthly','recalibration')),
            notification_date  TEXT,
            changes_detected   TEXT,
            roi_adjustments    TEXT,
            created_at         TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """),
]


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Create a SQLite connection with WAL mode, FK enforcement, and busy timeout.

    Args:
        db_path: Path to the SQLite database file (created if missing,
                 parent directories created if needed).

    Returns:
        A configured sqlite3.Connection ready for use.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def get_current_version(conn: sqlite3.Connection) -> int:
    """Return the highest applied migration version, or 0 if none."""
    try:
        row = conn.execute(
            "SELECT MAX(version) as v FROM _schema_version"
        ).fetchone()
        return row["v"] if row and row["v"] is not None else 0
    except sqlite3.OperationalError:
        return 0


def apply_migrations(conn: sqlite3.Connection) -> int:
    """Apply all pending migrations. Idempotent — safe to call repeatedly.

    Args:
        conn: A SQLite connection (WAL + FK pragmas should already be set).

    Returns:
        The number of migrations applied in this call.
    """
    current = get_current_version(conn)
    applied = 0

    for version, description, sql in MIGRATIONS:
        if version <= current:
            continue
        needs_fk_off = False
        try:
            needs_fk_off = sql.strip().startswith("-- FK_OFF")
            sql_to_run = sql.strip()
            if needs_fk_off:
                sql_to_run = sql_to_run.removeprefix("-- FK_OFF").strip()
                conn.execute("PRAGMA foreign_keys=OFF")

            conn.execute("BEGIN")
            for statement in sql_to_run.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(stmt)
            conn.execute(
                "INSERT INTO _schema_version (version, description) VALUES (?, ?)",
                (version, description),
            )
            conn.execute("COMMIT")
            if needs_fk_off:
                conn.execute("PRAGMA foreign_keys=ON")
            applied += 1
        except Exception as exc:
            try:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
            except Exception:
                pass
            if needs_fk_off:
                conn.execute("PRAGMA foreign_keys=ON")
            raise StudyDBError(
                f"Migration {version} ({description}) failed — {exc}"
            ) from exc

    return applied


class Database:
    """Thread-safe persistent database connection.

    Usage:
        db = Database("~/.ssc_study/study.db")
        with db.connect() as conn:
            ...
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path).expanduser()
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self._init_connection()

    def _init_connection(self) -> None:
        conn = get_connection(self._path)
        apply_migrations(conn)
        self._conn = conn

    @property
    def path(self) -> Path:
        return self._path

    def connect(self) -> sqlite3.Connection:
        """Return the shared connection (thread-safe)."""
        if self._conn is None:
            with self._lock:
                if self._conn is None:
                    self._init_connection()
        return self._conn  # type: ignore[return-value]

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute a write query with automatic commit under the lock."""
        assert self._conn is not None
        with self._lock:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            return cursor

    def execute_many(self, sql: str, params_list: list[tuple[Any, ...]]) -> sqlite3.Cursor:
        """Execute many parameterized inserts in a single transaction."""
        assert self._conn is not None
        with self._lock:
            cursor = self._conn.executemany(sql, params_list)
            self._conn.commit()
            return cursor

    def close(self) -> None:
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None

    def __enter__(self) -> Database:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
