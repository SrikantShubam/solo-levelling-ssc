"""Tests for the Phase 3 orchestrator loop."""

from __future__ import annotations

import sqlite3

from ssc_study.db import Database, apply_migrations
from ssc_study.gates import PROBE_SIZE
from ssc_study.phase3 import plan_next_action, run_phase3_loop


def _make_test_db() -> Database:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    apply_migrations(conn)

    db = Database.__new__(Database)
    db._path = ":memory:"
    db._lock = __import__("threading").Lock()
    db._conn = conn
    return db


def _insert_question(
    conn: sqlite3.Connection,
    question_id: str,
    *,
    global_question_number: int,
    section: str = "Quant/DI",
    tier: str = "tier1",
    is_holdout: int = 0,
) -> None:
    conn.execute(
        """INSERT INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout)
           VALUES (?, 'test_pdf', 1, ?, ?, 2024, ?, ?, '[]', '1', 'A', ?)""",
        (question_id, global_question_number, section, tier, f"Question {question_id}?", is_holdout),
    )


def _add_archetype(
    conn: sqlite3.Connection,
    archetype_id: int,
    name: str,
    *,
    section: str = "Quant/DI",
    tier: str = "both",
    is_unlocked: int = 0,
    is_active: int = 1,
    t1_accuracy: float | None = None,
) -> None:
    conn.execute(
        """INSERT INTO archetypes
           (archetype_id, name, section, tier, is_unlocked, is_active, t1_accuracy)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (archetype_id, name, section, tier, is_unlocked, is_active, t1_accuracy),
    )
    conn.commit()


def _assign_questions_to_archetype(
    conn: sqlite3.Connection,
    archetype_id: int,
    question_ids: list[str],
) -> None:
    for question_id in question_ids:
        conn.execute(
            "UPDATE questions SET archetype_id = ? WHERE question_id = ?",
            (archetype_id, question_id),
        )
    conn.commit()


def _seed_probe_candidate(
    conn: sqlite3.Connection,
    archetype_id: int,
    question_ids: list[str],
    holdout_ids: tuple[str, ...] = (),
) -> None:
    holdout_set = set(holdout_ids)
    _add_archetype(conn, archetype_id, f"Probe Archetype {archetype_id}")
    for idx, question_id in enumerate(question_ids, start=1):
        _insert_question(
            conn,
            question_id,
            global_question_number=10_000 + idx,
            is_holdout=1 if question_id in holdout_set else 0,
        )
    _assign_questions_to_archetype(conn, archetype_id, question_ids)


def _insert_attempts(
    conn: sqlite3.Connection,
    session_id: int,
    question_ids: list[str],
    correctness: list[int],
) -> None:
    conn.execute(
        "INSERT INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier) "
        "VALUES (?, 'analysis', '2026-06-17T00:00:00+00:00', ?, ?, 'tier1')",
        (session_id, len(question_ids), sum(correctness)),
    )
    for idx, (question_id, is_correct) in enumerate(zip(question_ids, correctness, strict=True), start=1):
        conn.execute(
            """INSERT INTO attempts
               (question_id, session_id, user_answer, is_correct, time_spent_seconds, student_label)
               VALUES (?, ?, '1', ?, ?, ?)""",
            (question_id, session_id, is_correct, 30 + idx, "correct" if is_correct else "incorrect"),
        )
    conn.commit()


def _action_signature(action) -> tuple[str, int | None, str | None, int, str | None]:
    return (
        action.action_type,
        action.target_archetype_id,
        action.target_archetype_name,
        action.question_count,
        action.stop_reason,
    )


def test_plan_next_action_prefers_probe_candidates(seeded_db) -> None:
    conn = seeded_db.connect()

    for idx in range(12, 22):
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, is_holdout)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 0)""",
            (f"probe_q{idx}", idx, f"Probe question {idx}?"),
        )
    conn.commit()

    _add_archetype(conn, 101, "Percentages")
    _assign_questions_to_archetype(conn, 101, [f"probe_q{idx}" for idx in range(12, 22)])

    action = plan_next_action(seeded_db)

    assert action.action_type == "probe"
    assert action.target_archetype_id == 101
    assert action.question_count == 10


def test_plan_next_action_uses_remediation_when_no_probe_candidates(seeded_db) -> None:
    conn = seeded_db.connect()

    _add_archetype(conn, 201, "Algebra", t1_accuracy=0.4)
    _assign_questions_to_archetype(conn, 201, ["q1", "q2", "q3"])
    _insert_attempts(conn, 9001, ["q1", "q2", "q3", "q1", "q2"], [0, 0, 1, 0, 1])

    action = plan_next_action(seeded_db)

    assert action.action_type == "remediation"
    assert action.question_count > 0
    assert "weak archetype" in action.reason.lower()


def test_plan_next_action_prefers_boss_fight_before_sm2(seeded_db) -> None:
    conn = seeded_db.connect()

    _add_archetype(conn, 301, "Time And Work", t1_accuracy=0.6)
    _assign_questions_to_archetype(conn, 301, ["q1", "q2", "q3"])
    _insert_attempts(conn, 9002, ["q1", "q2", "q3", "q1", "q2"], [1, 1, 0, 0, 1])

    action = plan_next_action(seeded_db)

    assert action.action_type == "boss_fight"
    assert action.question_count > 0


def test_plan_next_action_stops_when_no_eligible_work(study_db) -> None:
    action = plan_next_action(study_db)

    assert action.action_type == "stop"
    assert action.stop_reason == "no_eligible_work"


def test_plan_next_action_skips_probe_when_non_holdout_count_below_probe_size(study_db) -> None:
    conn = study_db.connect()
    non_holdout_ids = [f"threshold_nonholdout_{idx}" for idx in range(PROBE_SIZE - 1)]
    holdout_ids = tuple(f"threshold_holdout_{idx}" for idx in range(3))

    _seed_probe_candidate(conn, 601, non_holdout_ids + list(holdout_ids), holdout_ids=holdout_ids)

    action = plan_next_action(study_db)

    assert action.action_type == "stop"
    assert action.stop_reason == "no_eligible_work"


def test_plan_next_action_is_invariant_to_question_id_order() -> None:
    shuffled_question_ids = [
        "qid_204",
        "qid_017",
        "qid_930",
        "qid_041",
        "qid_502",
        "qid_008",
        "qid_777",
        "qid_119",
        "qid_360",
        "qid_055",
    ]

    db_a = _make_test_db()
    db_b = _make_test_db()
    _seed_probe_candidate(db_a.connect(), 602, shuffled_question_ids)
    _seed_probe_candidate(db_b.connect(), 602, list(reversed(shuffled_question_ids)))

    action_a = plan_next_action(db_a)
    action_b = plan_next_action(db_b)

    assert _action_signature(action_a) == _action_signature(action_b)


def test_run_phase3_loop_respects_max_steps(seeded_db) -> None:
    conn = seeded_db.connect()

    for idx in range(12, 32):
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, is_holdout)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 0)""",
            (f"loop_q{idx}", idx, f"Loop question {idx}?"),
        )
    conn.commit()

    _add_archetype(conn, 401, "Ratios")
    _add_archetype(conn, 402, "Mixtures")
    _assign_questions_to_archetype(conn, 401, [f"loop_q{idx}" for idx in range(12, 22)])
    _assign_questions_to_archetype(conn, 402, [f"loop_q{idx}" for idx in range(22, 32)])

    report = run_phase3_loop(seeded_db, max_steps=1, dry_run=True)

    assert len(report.actions) == 1
    assert report.stop_reason == "max_steps_reached"


def test_run_phase3_loop_dry_run_does_not_create_sessions(seeded_db) -> None:
    conn = seeded_db.connect()

    before = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
    report = run_phase3_loop(seeded_db, max_steps=2, dry_run=True)
    after = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]

    assert report.completed is True
    assert before == after


def test_run_phase3_loop_does_not_repeat_an_archetype_across_steps(study_db) -> None:
    conn = study_db.connect()
    for archetype_id in (701, 702, 703):
        question_ids = [f"loop_arch_{archetype_id}_{idx:02d}" for idx in range(PROBE_SIZE)]
        _seed_probe_candidate(conn, archetype_id, question_ids)

    report = run_phase3_loop(study_db, max_steps=3, dry_run=True)
    target_ids = [action.target_archetype_id for action in report.actions if action.target_archetype_id is not None]

    assert len(report.actions) == 3
    assert len(target_ids) == len(set(target_ids))
