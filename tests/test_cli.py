"""CLI tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from click.testing import CliRunner

from ssc_study.cli import cli
from ssc_study.db import Database


def _seed_phase3_eval_data(db_path: Path) -> None:
    db = Database(db_path)
    conn = db.connect()

    conn.execute(
        """INSERT INTO archetypes
           (archetype_id, name, section, tier, is_unlocked, is_active, t1_accuracy)
           VALUES (801, 'CLI Percentages', 'Quant/DI', 'both', 0, 1, 0.6)"""
    )
    for idx in range(5):
        question_id = f"cli_eval_q{idx}"
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, archetype_id, is_holdout)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 801, 0)""",
            (question_id, idx + 1, f"CLI eval question {idx}?"),
        )

    conn.execute(
        "INSERT INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier) "
        "VALUES (9801, 'analysis', '2026-06-17T00:00:00+00:00', 5, 3, 'tier1')"
    )
    correctness = [1, 1, 0, 0, 1]
    for idx, is_correct in enumerate(correctness):
        conn.execute(
            """INSERT INTO attempts
               (question_id, session_id, user_answer, is_correct, time_spent_seconds, student_label)
               VALUES (?, 9801, '1', ?, ?, ?)""",
            (
                f"cli_eval_q{idx}",
                is_correct,
                30 + idx,
                "correct" if is_correct else "incorrect",
            ),
        )
    conn.commit()


def test_phase3_command_runs_dry_run(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"

    result = runner.invoke(cli, ["phase3", "--db-path", str(db_path), "--dry-run", "--max-steps", "1"])

    assert result.exit_code == 0
    assert "Phase 3" in result.output
    assert "Stop reason" in result.output


def test_phase3_eval_command_runs(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"

    result = runner.invoke(cli, ["phase3-eval", "--db-path", str(db_path), "--limit", "5"])

    assert result.exit_code == 0
    assert "Phase 3 Evaluation" in result.output
    assert "Compared archetypes" in result.output


def test_phase3_eval_command_prints_signal_strength(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"
    _seed_phase3_eval_data(db_path)

    result = runner.invoke(cli, ["phase3-eval", "--db-path", str(db_path), "--limit", "5"])

    assert result.exit_code == 0
    assert "signal=weak" in result.output
    assert "attempts=5" in result.output


def test_patterns_exam_command_runs(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"
    # Create empty database tables
    db = Database(db_path)
    db.connect()  # runs migrations automatically

    result = runner.invoke(cli, ["patterns", "exam", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Exam Pattern Analysis" in result.output
    assert "Section Distribution" in result.output


def test_patterns_priority_command_runs(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"
    db = Database(db_path)
    db.connect()

    result = runner.invoke(cli, ["patterns", "priority", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Exam Pattern & User Priority Combiner" in result.output


def test_patterns_priority_ignores_holdout_attempts(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"
    db = Database(db_path)
    conn = db.connect()
    conn.execute(
        """INSERT INTO archetypes
           (archetype_id, name, section, tier, is_active)
           VALUES (9901, 'Holdout Leak Check', 'Quant/DI', 'both', 1)"""
    )
    for question_id, is_holdout in (
        ("priority_non_holdout", 0),
        ("priority_holdout", 1),
    ):
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, archetype_id, is_holdout)
               VALUES (?, 'test_pdf', 1, 1, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 9901, ?)""",
            (question_id, f"{question_id}?", is_holdout),
        )
    conn.execute(
        """INSERT INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier)
           VALUES (9901, 'analysis', '2026-07-01T00:00:00', 2, 1, 'tier1')"""
    )
    conn.execute(
        """INSERT INTO attempts (question_id, session_id, user_answer, is_correct, time_spent_seconds)
           VALUES ('priority_non_holdout', 9901, '1', 1, 20)"""
    )
    conn.execute(
        """INSERT INTO attempts (question_id, session_id, user_answer, is_correct, time_spent_seconds)
           VALUES ('priority_holdout', 9901, '1', 0, 20)"""
    )
    conn.commit()

    result = runner.invoke(cli, ["patterns", "priority", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Holdout Leak Check" in result.output
    assert "user_accuracy=100%" in result.output
    assert "user_accuracy=50%" not in result.output


def test_guardian_plan_command_runs(tmp_path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "study.db"
    db = Database(db_path)
    db.connect()

    result = runner.invoke(cli, ["guardian", "plan", "--db-path", str(db_path), "--date", "2026-07-08"])

    assert result.exit_code == 0
    assert "Guardian Plan Recommendation" in result.output
    assert "SM-2 Review" in result.output
