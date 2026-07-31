"""Tests for the Stage 1 atlas activation script."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_atlas_stage1 import build_atlas_stage1, main
from ssc_study.archetypes import ARCHETYPE_DEFS, ensure_default_archetypes
from ssc_study.db import Database


def _insert_question(
    db: Database,
    question_id: str,
    *,
    section: str,
    text: str,
    is_holdout: int = 0,
    archetype_id: int | None = None,
) -> None:
    db.connect().execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout, archetype_id)
           VALUES (?, 'test.pdf', 1, 1, ?, 2024, 'tier1', ?, ?, '1', 'A', ?, ?)""",
        (
            question_id,
            section,
            text,
            json.dumps([
                {"label": "1", "text": "A"},
                {"label": "2", "text": "B"},
                {"label": "3", "text": "C"},
                {"label": "4", "text": "D"},
            ]),
            is_holdout,
            archetype_id,
        ),
    )
    db.connect().commit()


def test_build_atlas_stage1_is_idempotent_and_skips_holdout(tmp_path, capsys):
    db_path = tmp_path / "study.db"
    db = Database(db_path)
    _insert_question(
        db,
        "non_holdout_match",
        section="Quant/DI",
        text="If x + y = 10, find the value of x.",
    )
    _insert_question(
        db,
        "holdout_match",
        section="Quant/DI",
        text="If x + y = 10, find the value of x.",
        is_holdout=1,
    )
    _insert_question(
        db,
        "non_holdout_unknown",
        section="English",
        text="A deliberately unmatched sentence with no taxonomy keywords.",
    )
    db.close()

    assert main(["--db", str(db_path)]) == 0
    first_output = capsys.readouterr().out

    db = Database(db_path)
    conn = db.connect()
    assert conn.execute("SELECT COUNT(*) FROM archetypes").fetchone()[0] == len(ARCHETYPE_DEFS)
    assert conn.execute(
        "SELECT archetype_id IS NOT NULL FROM questions WHERE question_id = 'non_holdout_match'"
    ).fetchone()[0] == 1
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'holdout_match'"
    ).fetchone()[0] is None
    assert "archetypes_created=48" in first_output
    assert "questions_assigned=1" in first_output
    assert "English=1" in first_output

    assert main(["--db", str(db_path)]) == 0
    second_output = capsys.readouterr().out
    assert "archetypes_created=0" in second_output
    assert "questions_assigned=0" in second_output
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'holdout_match'"
    ).fetchone()[0] is None


def test_build_atlas_stage1_updates_changed_non_holdout_rule_match(tmp_path):
    db = Database(tmp_path / "study.db")
    ensure_default_archetypes(db)
    algebra_id = db.connect().execute(
        "SELECT archetype_id FROM archetypes WHERE section = 'Quant/DI' AND name = 'Algebra'"
    ).fetchone()[0]
    speed_id = db.connect().execute(
        "SELECT archetype_id FROM archetypes WHERE section = 'Quant/DI' AND name = 'Speed, Time & Distance'"
    ).fetchone()[0]
    _insert_question(
        db,
        "stale_match",
        section="Quant/DI",
        text="A train travels 60km in 1 hour. What is its speed?",
        archetype_id=algebra_id,
    )

    report = build_atlas_stage1(db)

    assert report.questions_assigned == 1
    assert db.connect().execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'stale_match'"
    ).fetchone()[0] == speed_id
