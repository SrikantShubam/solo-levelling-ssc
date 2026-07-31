"""Tests for the Stage 2 embedding atlas expansion script."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from ssc_study.db import Database


def _insert_archetype(db: Database, archetype_id: int, name: str, section: str) -> None:
    db.connect().execute(
        """INSERT INTO archetypes (archetype_id, name, section, tier)
           VALUES (?, ?, ?, 'both')""",
        (archetype_id, name, section),
    )
    db.connect().commit()


def _insert_question(
    db: Database,
    question_id: str,
    *,
    section: str,
    embedding: list[float],
    text: str | None = None,
    archetype_id: int | None = None,
    is_holdout: int = 0,
) -> None:
    db.connect().execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout,
            archetype_id, embedding_blob)
           VALUES (?, 'stage2.pdf', 1, 1, ?, 2024, 'tier1', ?, ?,
                   '1', 'A', ?, ?, ?)""",
        (
            question_id,
            section,
            text or f"{question_id} text",
            json.dumps([
                {"label": "1", "text": "A"},
                {"label": "2", "text": "B"},
                {"label": "3", "text": "C"},
                {"label": "4", "text": "D"},
            ]),
            is_holdout,
            archetype_id,
            json.dumps(embedding).encode("utf-8"),
        ),
    )
    db.connect().commit()


def test_stage2_assigns_only_confident_untagged_non_holdout_rows(tmp_path, monkeypatch):
    from scripts import build_atlas_stage2 as stage2

    db = Database(tmp_path / "study.db")
    _insert_archetype(db, 1, "Algebra", "Quant/DI")
    _insert_archetype(db, 2, "Geometry", "Quant/DI")
    for idx in range(5):
        _insert_question(
            db,
            f"alg_seed_{idx}",
            section="Quant/DI",
            embedding=[1.0, 0.0],
            text="If x + y = 10, find the value of x.",
            archetype_id=1,
        )
        _insert_question(
            db,
            f"geo_seed_{idx}",
            section="Quant/DI",
            embedding=[0.0, 1.0],
            text="A triangle has an angle marked in a circle.",
            archetype_id=2,
        )
    _insert_question(db, "untagged_close", section="Quant/DI", embedding=[0.99, 0.01])
    _insert_question(db, "untagged_far", section="Quant/DI", embedding=[0.4, 0.6])
    _insert_question(db, "holdout_close", section="Quant/DI", embedding=[1.0, 0.0], is_holdout=1)

    monkeypatch.setattr(
        stage2,
        "select_threshold",
        lambda validation: stage2.ThresholdChoice(threshold=0.95, precision=1.0, recall=1.0),
    )
    monkeypatch.setattr(
        stage2,
        "select_section_thresholds",
        lambda predictions: [stage2.ValidationBucket("Quant/DI", 0.95, 2, 2, 2)],
    )
    monkeypatch.setattr(stage2, "MIN_VALIDATION_SAMPLE", 2)

    report = stage2.build_atlas_stage2(db)

    conn = db.connect()
    assert report.questions_assigned == 1
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'untagged_close'"
    ).fetchone()[0] == 1
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'untagged_far'"
    ).fetchone()[0] is None
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'holdout_close'"
    ).fetchone()[0] is None


def test_stage2_is_idempotent_and_does_not_flip_existing_assignments(tmp_path, monkeypatch):
    from scripts import build_atlas_stage2 as stage2

    db = Database(tmp_path / "study.db")
    _insert_archetype(db, 1, "Algebra", "Quant/DI")
    _insert_archetype(db, 2, "Geometry", "Quant/DI")
    for idx in range(5):
        _insert_question(
            db,
            f"alg_seed_{idx}",
            section="Quant/DI",
            embedding=[1.0, 0.0],
            text="If x + y = 10, find the value of x.",
            archetype_id=1,
        )
        _insert_question(
            db,
            f"geo_seed_{idx}",
            section="Quant/DI",
            embedding=[0.0, 1.0],
            text="A triangle has an angle marked in a circle.",
            archetype_id=2,
        )
    _insert_question(db, "pretagged_geometry_vector", section="Quant/DI", embedding=[1.0, 0.0], archetype_id=2)
    _insert_question(db, "new_close", section="Quant/DI", embedding=[1.0, 0.0])

    monkeypatch.setattr(
        stage2,
        "select_threshold",
        lambda validation: stage2.ThresholdChoice(threshold=0.95, precision=1.0, recall=1.0),
    )
    monkeypatch.setattr(
        stage2,
        "select_section_thresholds",
        lambda predictions: [stage2.ValidationBucket("Quant/DI", 0.95, 2, 2, 2)],
    )
    monkeypatch.setattr(stage2, "MIN_VALIDATION_SAMPLE", 2)

    first = stage2.build_atlas_stage2(db)
    second = stage2.build_atlas_stage2(db)

    conn = db.connect()
    assert first.questions_assigned == 1
    assert second.questions_assigned == 0
    assert conn.execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'pretagged_geometry_vector'"
    ).fetchone()[0] == 2


def test_stage2_requires_validation_before_backfill(tmp_path, monkeypatch):
    from scripts import build_atlas_stage2 as stage2

    db = Database(tmp_path / "study.db")
    _insert_archetype(db, 1, "Algebra", "Quant/DI")
    _insert_question(
        db,
        "only_seed",
        section="Quant/DI",
        embedding=[1.0, 0.0],
        text="If x + y = 10, find the value of x.",
        archetype_id=1,
    )
    _insert_question(db, "untagged", section="Quant/DI", embedding=[1.0, 0.0])

    monkeypatch.setattr(stage2, "MIN_VALIDATION_SAMPLE", 2)

    with pytest.raises(stage2.AtlasStage2Error, match="validation sample"):
        stage2.build_atlas_stage2(db)

    assert db.connect().execute(
        "SELECT archetype_id FROM questions WHERE question_id = 'untagged'"
    ).fetchone()[0] is None
