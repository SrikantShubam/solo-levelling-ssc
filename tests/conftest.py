"""Shared fixtures for all tests (corpus + study)."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# ── Study app fixtures ──────────────────────────────────────────────────


@pytest.fixture
def in_memory_db() -> sqlite3.Connection:
    """Create an in-memory SQLite database with full schema applied."""
    from ssc_study.db import apply_migrations

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    apply_migrations(conn)
    return conn


@pytest.fixture
def study_db(in_memory_db) -> "Database":
    """A Database instance wrapping an in-memory SQLite DB."""
    from ssc_study.db import Database

    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


@pytest.fixture
def sample_question_data() -> dict:
    """A single well-formed question dict matching merged JSON format."""
    return {
        "question_id": "1235689",
        "section": "General Intelligence and Reasoning",
        "question_text_full": (
            "If A is the brother of B, and B is the sister of C, "
            "then how is A related to C?"
        ),
        "question_number": 1,
        "global_question_number": 1,
        "source_page": 1,
        "canonical_correct_option_label": "3",
        "correct_option_text": "Brother",
        "chosen_option_label": "3",
        "question_modality": "text_only",
        "visual_required": False,
        "table_required": False,
        "math_required": False,
        "evidence_status": "PASS",
        "question_crop_path": None,
        "page_asset_path": None,
        "practice_ready": True,
        "options": [
            {"label": "1", "text": "Sister"},
            {"label": "2", "text": "Father"},
            {"label": "3", "text": "Brother"},
            {"label": "4", "text": "Cousin"},
        ],
    }


@pytest.fixture
def sm2_default_state():
    """Default SM-2 starting state."""
    from ssc_study.models import SM2State
    return SM2State()


# ── Seeded database fixtures ──────────────────────────────────────────


def _insert_question(
    conn: sqlite3.Connection,
    qid: str,
    section: str = "Quant/DI",
    tier: str = "tier1",
    text: str = "Test question?",
    correct_label: str = "1",
    options: list[dict] | None = None,
    year: int = 2021,
    is_holdout: int = 0,
) -> None:
    """Helper to insert a single question."""
    if options is None:
        options = [
            {"label": "1", "text": "Option A"},
            {"label": "2", "text": "Option B"},
            {"label": "3", "text": "Option C"},
            {"label": "4", "text": "Option D"},
        ]
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (qid, "test_pdf", 1, 1, section, year, tier, text,
         json.dumps(options), correct_label, options[0]["text"], is_holdout),
    )
    conn.commit()


@pytest.fixture
def seeded_conn(in_memory_db) -> sqlite3.Connection:
    """DB with diverse questions across sections/tiers and some SM-2 state."""
    conn = in_memory_db

    # Quant questions
    _insert_question(conn, "q1", "Quant/DI", "tier1",
                     "If x + y = 10, find x?", "2")
    _insert_question(conn, "q2", "Quant/DI", "tier2",
                     "What is the derivative of x^2?", "1")
    _insert_question(conn, "q3", "Quant/DI", "tier1",
                     "A train travels 60km in 1 hour. What is its speed?", "3")

    # Reasoning questions
    _insert_question(conn, "q4", "Reasoning", "tier1",
                     "If A is brother of B, how is A related to C?", "1")
    _insert_question(conn, "q5", "Reasoning", "tier2",
                     "Complete the series: 2, 4, 8, 16, ?", "4")

    # English questions
    _insert_question(conn, "q6", "English", "tier1",
                     "Choose the correct spelling: accommodate", "1")
    _insert_question(conn, "q7", "English", "tier2",
                     "Fill in the blank: He ___ to school every day.", "2")

    # GK/GA questions
    _insert_question(conn, "q8", "GK/GA", "tier1",
                     "What is the capital of France?", "3",
                     options=[
                         {"label": "1", "text": "London"},
                         {"label": "2", "text": "Berlin"},
                         {"label": "3", "text": "Paris"},
                         {"label": "4", "text": "Madrid"},
                     ])
    _insert_question(conn, "q9", "GK/GA", "tier2",
                     "Who discovered penicillin?", "2",
                     options=[
                         {"label": "1", "text": "Einstein"},
                         {"label": "2", "text": "Alexander Fleming"},
                         {"label": "3", "text": "Newton"},
                         {"label": "4", "text": "Darwin"},
                     ])
    _insert_question(conn, "q10", "GK/GA", "tier1",
                     "In which year did India get independence?", "1",
                     options=[
                         {"label": "1", "text": "1947"},
                         {"label": "2", "text": "1950"},
                         {"label": "3", "text": "1937"},
                         {"label": "4", "text": "1942"},
                     ])

    # Holdout question
    _insert_question(conn, "q11", "Quant/DI", "tier1",
                     "Holdout question?", "1", is_holdout=1)

    # Add some SM-2 state: q1 is due, q2 due later
    conn.execute(
        "INSERT INTO sm2_state (entity_type, entity_id, easiness, interval_days, repetitions, next_review, last_review, last_quality) "
        "VALUES ('question', 'q1', 2.5, 1, 1, '2020-01-01', '2019-12-31', 4)"
    )
    conn.execute(
        "INSERT INTO sm2_state (entity_type, entity_id, easiness, interval_days, repetitions, next_review, last_review, last_quality) "
        "VALUES ('question', 'q2', 2.6, 6, 2, '2099-01-01', '2099-01-01', 5)"
    )
    conn.commit()

    return conn


@pytest.fixture
def seeded_db(seeded_conn) -> "Database":
    """Database instance wrapping seeded_conn."""
    from ssc_study.db import Database

    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = seeded_conn
    return db
