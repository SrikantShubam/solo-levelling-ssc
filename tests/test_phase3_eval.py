"""Tests for Phase 3 route evaluation."""

from __future__ import annotations

import sqlite3

import pytest

from ssc_study.gates import classify_probe_attempts
from ssc_study.phase3_eval import evaluate_phase3_predictions


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


def _insert_attempts(
    conn: sqlite3.Connection,
    session_id: int,
    question_ids: list[str],
    correctness: list[int],
    *,
    concept_tags: list[str | None] | None = None,
) -> None:
    conn.execute(
        "INSERT INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier) "
        "VALUES (?, 'analysis', '2026-06-17T00:00:00+00:00', ?, ?, 'tier1')",
        (session_id, len(question_ids), sum(correctness)),
    )
    concept_tags = concept_tags or [None] * len(question_ids)
    for idx, (question_id, is_correct, concept_tag) in enumerate(
        zip(question_ids, correctness, concept_tags, strict=True),
        start=1,
    ):
        conn.execute(
            """INSERT INTO attempts
               (question_id, session_id, user_answer, is_correct, time_spent_seconds, student_label, concept_tag)
               VALUES (?, ?, '1', ?, ?, ?, ?)""",
            (
                question_id,
                session_id,
                is_correct,
                30 + idx,
                "correct" if is_correct else "incorrect",
                concept_tag,
            ),
        )
    conn.commit()


def _seed_phase3_route_case(
    conn: sqlite3.Connection,
    archetype_id: int,
    predicted_accuracy: float | None,
    question_count: int = 5,
    holdout_count: int = 0,
) -> dict[str, list[str]]:
    """Create one archetype with dedicated non-holdout and holdout questions."""
    _add_archetype(
        conn,
        archetype_id,
        f"Phase3 {archetype_id}",
        is_unlocked=1 if predicted_accuracy is not None and predicted_accuracy >= 0.80 else 0,
        t1_accuracy=predicted_accuracy,
    )

    question_ids: list[str] = []
    for idx in range(1, question_count + 1):
        question_id = f"phase3_{archetype_id}_q{idx}"
        question_ids.append(question_id)
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, is_holdout, archetype_id)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 0, ?)""",
            (
                question_id,
                idx,
                f"Phase3 question {idx}?",
                archetype_id,
            ),
        )

    holdout_ids: list[str] = []
    for idx in range(1, holdout_count + 1):
        question_id = f"phase3_{archetype_id}_holdout_{idx}"
        holdout_ids.append(question_id)
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, is_holdout, archetype_id)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 1, ?)""",
            (
                question_id,
                question_count + idx,
                f"Phase3 holdout question {idx}?",
                archetype_id,
            ),
        )

    conn.commit()
    return {
        "question_ids": question_ids,
        "holdout_question_ids": holdout_ids,
    }


def _insert_attempt_window(
    conn: sqlite3.Connection,
    session_id: int,
    question_ids: list[str],
    correctness: list[int],
    concept_tags: list[str | None] | None = None,
    holdout: bool = False,
) -> None:
    """Insert one probe-sized attempt window for the given questions."""
    conn.execute(
        "INSERT INTO sessions (session_id, session_type, started_at, question_count, correct_count, tier) "
        "VALUES (?, 'analysis', ?, ?, ?, 'tier1')",
        (
            session_id,
            f"2026-06-25T00:{session_id % 60:02d}:00+00:00",
            len(question_ids),
            sum(correctness),
        ),
    )
    conn.execute(
        f"UPDATE questions SET is_holdout = ? WHERE question_id IN ({','.join('?' for _ in question_ids)})",
        (int(holdout), *question_ids),
    )
    concept_tags = concept_tags or [None] * len(question_ids)
    for idx, (question_id, is_correct, concept_tag) in enumerate(
        zip(question_ids, correctness, concept_tags, strict=True),
        start=1,
    ):
        conn.execute(
            """INSERT INTO attempts
               (question_id, session_id, user_answer, is_correct, time_spent_seconds, student_label, concept_tag)
               VALUES (?, ?, '1', ?, ?, ?, ?)""",
            (
                question_id,
                session_id,
                is_correct,
                20 + idx,
                "correct" if is_correct else "incorrect",
                concept_tag,
            ),
        )
    conn.commit()


def _snapshot_phase3_tables(conn: sqlite3.Connection) -> dict[str, object]:
    """Capture the Phase 3 tables used by evaluation so read-only checks are precise."""
    return {
        "counts": {
            "archetypes": conn.execute("SELECT COUNT(*) FROM archetypes").fetchone()[0],
            "questions": conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0],
            "attempts": conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0],
            "sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "sm2_state": conn.execute("SELECT COUNT(*) FROM sm2_state").fetchone()[0],
        },
        "archetypes": tuple(
            tuple(row)
            for row in conn.execute(
                """SELECT archetype_id, name, t1_accuracy, is_unlocked, is_active, skip_count, skip_until
                   FROM archetypes
                   ORDER BY archetype_id"""
            ).fetchall()
        ),
        "questions": tuple(
            tuple(row)
            for row in conn.execute(
                """SELECT question_id, archetype_id, is_holdout, section, tier
                   FROM questions
                   ORDER BY question_id"""
            ).fetchall()
        ),
        "attempts": tuple(
            tuple(row)
            for row in conn.execute(
                """SELECT attempt_id, question_id, session_id, is_correct,
                          student_label, time_spent_seconds, concept_tag
                   FROM attempts
                   ORDER BY attempt_id"""
            ).fetchall()
        ),
        "sessions": tuple(
            tuple(row)
            for row in conn.execute(
                """SELECT session_id, session_type, question_count, correct_count, tier, notes
                   FROM sessions
                   ORDER BY session_id"""
            ).fetchall()
        ),
        "sm2_state": tuple(
            tuple(row)
            for row in conn.execute(
                """SELECT entity_type, entity_id, easiness, interval_days, repetitions,
                          next_review, last_review, last_quality
                   FROM sm2_state
                   ORDER BY entity_type, entity_id"""
            ).fetchall()
        ),
    }


def _assert_phase3_snapshot_unchanged(before: dict[str, object], after: dict[str, object]) -> None:
    assert after == before


def test_phase3_eval_reports_match_for_boss_fight(seeded_db) -> None:
    conn = seeded_db.connect()

    _add_archetype(conn, 501, "Time And Work", t1_accuracy=0.6)
    _assign_questions_to_archetype(conn, 501, ["q1", "q2", "q3", "q4", "q5"])
    _insert_attempts(conn, 9501, ["q1", "q2", "q3", "q4", "q5"], [1, 1, 0, 0, 1])

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[501])

    assert report.total == 1
    comparison = report.comparisons[0]
    assert comparison.predicted_route == "boss_fight"
    assert comparison.actual_route == "boss_fight"
    assert comparison.matches is True


def test_phase3_eval_reports_mismatch_against_recent_actuals(seeded_db) -> None:
    conn = seeded_db.connect()

    _add_archetype(conn, 502, "Percentages", is_unlocked=1, t1_accuracy=0.85)
    _assign_questions_to_archetype(conn, 502, ["q1", "q2", "q3", "q4", "q5"])
    _insert_attempts(
        conn,
        9502,
        ["q1", "q2", "q3", "q4", "q5"],
        [0, 0, 1, 0, 0],
        concept_tags=["algebra", "algebra", "algebra", "algebra", "algebra"],
    )

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[502])

    comparison = report.comparisons[0]
    assert comparison.predicted_route == "sm2"
    assert comparison.actual_route == "remediation"
    assert comparison.matches is False


def test_phase3_eval_marks_probe_without_actual_outcome(seeded_db) -> None:
    conn = seeded_db.connect()

    for idx in range(12, 22):
        conn.execute(
            """INSERT INTO questions
               (question_id, pdf_name, source_page, global_question_number,
                section, year, tier, question_text, options_json,
                correct_option_label, correct_option_text, is_holdout)
               VALUES (?, 'test_pdf', 1, ?, 'Quant/DI', 2024, 'tier1', ?, '[]', '1', 'A', 0)""",
            (f"eval_q{idx}", idx, f"Eval question {idx}?"),
        )
    conn.commit()

    _add_archetype(conn, 503, "Ratios")
    _assign_questions_to_archetype(conn, 503, [f"eval_q{idx}" for idx in range(12, 22)])

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[503])

    comparison = report.comparisons[0]
    assert comparison.predicted_route == "probe"
    assert comparison.actual_route is None
    assert comparison.matches is None
    assert comparison.reason == "insufficient_actual_attempts"


def test_phase3_eval_is_read_only(seeded_db) -> None:
    conn = seeded_db.connect()

    seeded = _seed_phase3_route_case(conn, 601, predicted_accuracy=0.6, question_count=5)
    _insert_attempt_window(conn, 9601, seeded["question_ids"], [1, 1, 1, 0, 0])

    before = _snapshot_phase3_tables(conn)

    evaluate_phase3_predictions(seeded_db, archetype_ids=[601])

    after = _snapshot_phase3_tables(conn)
    _assert_phase3_snapshot_unchanged(before, after)


def test_phase3_eval_ignores_holdout_attempts_when_deriving_actual_route(seeded_db) -> None:
    conn = seeded_db.connect()

    seeded = _seed_phase3_route_case(
        conn,
        602,
        predicted_accuracy=0.6,
        question_count=5,
        holdout_count=5,
    )
    _insert_attempt_window(conn, 9602, seeded["question_ids"], [1, 1, 1, 0, 0])
    _insert_attempt_window(
        conn,
        9603,
        seeded["holdout_question_ids"],
        [0, 0, 0, 0, 0],
        concept_tags=["fractions"] * 5,
        holdout=True,
    )

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[602])

    comparison = report.comparisons[0]
    assert comparison.actual_route == "boss_fight"


def test_phase3_eval_uses_latest_attempt_window_not_all_historical_attempts(seeded_db) -> None:
    conn = seeded_db.connect()

    seeded = _seed_phase3_route_case(conn, 603, predicted_accuracy=0.85, question_count=10)
    _insert_attempt_window(
        conn,
        9604,
        seeded["question_ids"],
        [0] * 10,
        concept_tags=["ratios"] * 10,
    )
    _insert_attempt_window(conn, 9605, seeded["question_ids"], [1] * 10)

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[603])

    comparison = report.comparisons[0]
    assert comparison.actual_route == "sm2"


@pytest.mark.parametrize(
    ("archetype_id", "correct_count", "total_count"),
    [
        (604, 8, 10),
        (605, 7, 10),
        (606, 5, 10),
        (607, 4, 10),
    ],
)
def test_phase3_eval_route_boundaries_match_gate_classifier(
    seeded_db,
    archetype_id: int,
    correct_count: int,
    total_count: int,
) -> None:
    conn = seeded_db.connect()

    seeded = _seed_phase3_route_case(
        conn,
        archetype_id,
        predicted_accuracy=0.6,
        question_count=total_count,
    )
    correctness = [1] * correct_count + [0] * (total_count - correct_count)
    concept_tags = [None] * total_count
    expected = classify_probe_attempts(
        [
            {"is_correct": bool(is_correct), "concept_tag": concept_tag}
            for is_correct, concept_tag in zip(correctness, concept_tags, strict=True)
        ]
    )
    _insert_attempt_window(
        conn,
        9600 + archetype_id,
        seeded["question_ids"],
        correctness,
        concept_tags=concept_tags,
    )

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[archetype_id])

    comparison = report.comparisons[0]
    assert comparison.actual_route == expected.route


def test_phase3_eval_reports_high_priority_boss_without_concept_gap(seeded_db) -> None:
    conn = seeded_db.connect()

    seeded = _seed_phase3_route_case(conn, 608, predicted_accuracy=0.3, question_count=5)
    _insert_attempt_window(
        conn,
        9608,
        seeded["question_ids"],
        [0, 0, 0, 1, 1],
        concept_tags=[None, None, None, None, None],
    )

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[608])

    comparison = report.comparisons[0]
    assert comparison.actual_route == "high_priority_boss"
    assert comparison.actual_accuracy == 0.4


def test_phase3_eval_reports_signal_strength(seeded_db) -> None:
    conn = seeded_db.connect()

    stable_seed = _seed_phase3_route_case(conn, 609, predicted_accuracy=0.6, question_count=10)
    _insert_attempt_window(conn, 9609, stable_seed["question_ids"], [1, 1, 1, 1, 1, 1, 0, 0, 0, 0])

    weak_seed = _seed_phase3_route_case(conn, 610, predicted_accuracy=0.6, question_count=5)
    _insert_attempt_window(conn, 9610, weak_seed["question_ids"], [1, 1, 1, 0, 0])

    insufficient_seed = _seed_phase3_route_case(conn, 611, predicted_accuracy=0.6, question_count=4)
    _insert_attempt_window(conn, 9611, insufficient_seed["question_ids"], [1, 1, 0, 0])

    report = evaluate_phase3_predictions(seeded_db, archetype_ids=[609, 610, 611])

    comparisons = {comparison.archetype_id: comparison for comparison in report.comparisons}
    assert comparisons[609].actual_attempt_count == 10
    assert comparisons[609].actual_accuracy == 0.6
    assert comparisons[609].signal_strength == "stable"
    assert comparisons[610].actual_attempt_count == 5
    assert comparisons[610].actual_accuracy == 0.6
    assert comparisons[610].signal_strength == "weak"
    assert comparisons[611].actual_attempt_count == 4
    assert comparisons[611].actual_accuracy == 0.5
    assert comparisons[611].signal_strength == "insufficient"
