"""Tests for the Phase 1 baseline web service."""

from __future__ import annotations

import json

import pytest

from ssc_study.baseline_web import (
    SMOKE_REQUIREMENTS,
    BaselineWebError,
    _encode_exam_token,
    get_baseline_preflight,
    get_baseline_result,
    start_baseline_exam,
    submit_baseline_exam,
)
from ssc_study.db import Database
from ssc_study.quiz import FOUNDATION_PULSE_REQUIREMENTS


def _insert_question(
    conn,
    qid: str,
    section: str,
    *,
    correct_label: str = "1",
    is_holdout: int = 0,
) -> None:
    options = [
        {"label": "1", "text": "A"},
        {"label": "2", "text": "B"},
        {"label": "3", "text": "C"},
        {"label": "4", "text": "D"},
    ]
    conn.execute(
        """INSERT OR REPLACE INTO questions
           (question_id, pdf_name, source_page, global_question_number,
            section, year, tier, question_text, options_json,
            correct_option_label, correct_option_text, is_holdout)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            qid,
            "test_pdf",
            1,
            1,
            section,
            2021,
            "tier1",
            f"Question {qid}?",
            json.dumps(options),
            correct_label,
            "A",
            is_holdout,
        ),
    )


def _seed_section_counts(conn, counts: dict[str, int], *, holdout_extra: int = 0) -> None:
    counter = 0
    for section, count in counts.items():
        for index in range(count):
            counter += 1
            _insert_question(conn, f"{section.replace('/', '_')}_{index}", section)
        for index in range(holdout_extra):
            counter += 1
            _insert_question(
                conn,
                f"{section.replace('/', '_')}_holdout_{index}",
                section,
                is_holdout=1,
            )
    conn.commit()


@pytest.fixture
def smoke_eligible_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(conn, {"Quant/DI": 2, "Reasoning": 1, "English": 1, "GK/GA": 1})
    return study_db


@pytest.fixture
def full_eligible_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(
        conn,
        {
            "Quant/DI": 80,
            "Reasoning": 40,
            "English": 40,
            "GK/GA": 40,
        },
        holdout_extra=2,
    )
    return study_db


@pytest.fixture
def underfilled_db(study_db: Database) -> Database:
    conn = study_db.connect()
    _seed_section_counts(conn, {"Quant/DI": 10, "Reasoning": 40, "English": 40, "GK/GA": 40})
    return study_db


def _build_submit_payload(
    exam_id: str,
    mode: str,
    questions: list[dict],
    *,
    exam_token: str | None = None,
    answers: dict[str, str | None] | None = None,
) -> dict:
    answer_map = answers or {}
    payload = {
        "exam_id": exam_id,
        "mode": mode,
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": [
            {
                "question_id": question["question_id"],
                "user_answer": answer_map.get(question["question_id"]),
                "time_spent_seconds": 30,
                "marked_for_review": False,
            }
            for question in questions
        ],
    }
    if exam_token is not None:
        payload["exam_token"] = exam_token
    return payload


class TestPreflight:
    def test_preflight_ready_on_full_eligible_db(self, full_eligible_db):
        result = get_baseline_preflight(full_eligible_db)

        assert result["full_ready"] is True
        assert result["smoke_ready"] is True
        assert result["required"] == FOUNDATION_PULSE_REQUIREMENTS
        assert result["available"]["Quant/DI"] == 80
        assert result["missing"] == {}

    def test_preflight_underfilled_full(self, underfilled_db):
        result = get_baseline_preflight(underfilled_db)

        assert result["full_ready"] is False
        assert result["missing"]["Quant/DI"] == 70
        assert result["smoke_ready"] is True

    def test_preflight_smoke_not_ready_when_section_short(self, study_db):
        conn = study_db.connect()
        _seed_section_counts(conn, {"Quant/DI": 1, "Reasoning": 1, "English": 1, "GK/GA": 1})

        result = get_baseline_preflight(study_db)

        assert result["smoke_ready"] is False
        assert result["full_ready"] is False


class TestStart:
    def test_smoke_start_exact_split(self, smoke_eligible_db):
        result = start_baseline_exam(smoke_eligible_db, "smoke")

        assert result["mode"] == "smoke"
        assert result["question_count"] == 5
        assert len(result["exam_id"]) == 36
        assert result["exam_token"]

        sections = [question["section"] for question in result["questions"]]
        assert sections.count("Quant/DI") == 2
        assert sections.count("Reasoning") == 1
        assert sections.count("English") == 1
        assert sections.count("GK/GA") == 1

    def test_full_start_exact_split(self, full_eligible_db):
        result = start_baseline_exam(full_eligible_db, "full")

        assert result["mode"] == "full"
        assert result["question_count"] == 200

        sections = [question["section"] for question in result["questions"]]
        for section, required in FOUNDATION_PULSE_REQUIREMENTS.items():
            assert sections.count(section) == required

    def test_start_excludes_holdout_questions(self, full_eligible_db):
        result = start_baseline_exam(full_eligible_db, "full")
        question_ids = {question["question_id"] for question in result["questions"]}

        conn = full_eligible_db.connect()
        holdout_rows = conn.execute(
            "SELECT question_id FROM questions WHERE is_holdout = 1"
        ).fetchall()
        holdout_ids = {row["question_id"] for row in holdout_rows}
        assert question_ids.isdisjoint(holdout_ids)

    def test_start_response_has_no_correct_answers(self, smoke_eligible_db):
        result = start_baseline_exam(smoke_eligible_db, "smoke")

        for question in result["questions"]:
            assert "correct_option_label" not in question
            assert "correct_option_text" not in question
            for option in question["options"]:
                assert set(option.keys()) == {"label", "text"}

    def test_start_invalid_mode_raises(self, smoke_eligible_db):
        with pytest.raises(BaselineWebError, match="Invalid mode"):
            start_baseline_exam(smoke_eligible_db, "turbo")

    def test_start_full_underfilled_raises(self, underfilled_db):
        with pytest.raises(BaselineWebError, match="requires 80"):
            start_baseline_exam(underfilled_db, "full")


class TestSubmit:
    def test_submit_persists_session_and_attempts(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )

        result = submit_baseline_exam(smoke_eligible_db, payload)

        assert result["mode"] == "smoke"
        assert result["question_count"] == 5
        assert result["session_id"] is not None

        conn = smoke_eligible_db.connect()
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert session["session_type"] == "analysis"
        assert session["notes"] == f"phase1_web_smoke:{started['exam_id']}"

        attempts = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert attempts["c"] == 5

    def test_submit_requires_exam_token(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])

        with pytest.raises(BaselineWebError, match="exam_token"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_invalid_exam_token(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])
        payload["exam_token"] = "not-a-valid-token"

        with pytest.raises(BaselineWebError, match="exam_token"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_malformed_answer_entry(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(started["exam_id"], "smoke", started["questions"])
        payload["exam_token"] = started["exam_token"]
        payload["answers"][0] = None

        with pytest.raises(BaselineWebError, match="answer entry"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_full_uses_foundation_pulse_session_type(self, full_eligible_db):
        started = start_baseline_exam(full_eligible_db, "full")
        payload = _build_submit_payload(
            started["exam_id"],
            "full",
            started["questions"],
            exam_token=started["exam_token"],
        )

        result = submit_baseline_exam(full_eligible_db, payload)

        conn = full_eligible_db.connect()
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (result["session_id"],),
        ).fetchone()
        assert session["session_type"] == "foundation_pulse"
        assert session["notes"] == f"phase1_web_full:{started['exam_id']}"
        assert result["question_count"] == 200

    def test_submit_computes_correctness_server_side(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        first_id = started["questions"][0]["question_id"]

        conn = smoke_eligible_db.connect()
        correct_label = conn.execute(
            "SELECT correct_option_label FROM questions WHERE question_id = ?",
            (first_id,),
        ).fetchone()["correct_option_label"]
        wrong_label = "2" if correct_label != "2" else "3"

        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={
                first_id: correct_label,
                started["questions"][1]["question_id"]: wrong_label,
            },
        )

        result = submit_baseline_exam(smoke_eligible_db, payload)

        assert result["correct_count"] == 1
        assert result["accuracy"] == pytest.approx(0.2)
        assert result["by_section"][started["questions"][0]["section"]]["correct"] == 1

    def test_submit_updates_sm2_state(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        first_id = started["questions"][0]["question_id"]

        conn = smoke_eligible_db.connect()
        before = conn.execute(
            "SELECT COUNT(*) as c FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
            (first_id,),
        ).fetchone()["c"]
        assert before == 0

        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={first_id: "1"},
        )
        submit_baseline_exam(smoke_eligible_db, payload)

        row = conn.execute(
            "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
            (first_id,),
        ).fetchone()
        assert row is not None
        assert row["last_review"] is not None
        assert row["last_quality"] is not None

    def test_submit_treats_missing_answers_as_skipped(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
        )

        submit_baseline_exam(smoke_eligible_db, payload)

        conn = smoke_eligible_db.connect()
        skipped = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE student_label = 'skipped'"
        ).fetchone()
        assert skipped["c"] == 5

    def test_duplicate_submit_is_idempotent(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )

        first = submit_baseline_exam(smoke_eligible_db, payload)
        second = submit_baseline_exam(smoke_eligible_db, payload)

        assert second == first

        conn = smoke_eligible_db.connect()
        sessions = conn.execute(
            "SELECT COUNT(*) as c FROM sessions WHERE notes = ?",
            (f"phase1_web_smoke:{started['exam_id']}",),
        ).fetchone()
        attempts = conn.execute("SELECT COUNT(*) as c FROM attempts").fetchone()
        assert sessions["c"] == 1
        assert attempts["c"] == 5

    def test_submit_rejects_holdout_question(self, smoke_eligible_db):
        conn = smoke_eligible_db.connect()
        _insert_question(conn, "holdout_trap", "Quant/DI", is_holdout=1)
        conn.commit()

        started = start_baseline_exam(smoke_eligible_db, "smoke")
        questions = list(started["questions"])
        questions[0] = {
            **questions[0],
            "question_id": "holdout_trap",
        }
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="Holdout question not allowed"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_unknown_question(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        questions = list(started["questions"])
        questions[0] = {**questions[0], "question_id": "missing_q"}
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="Unknown question_id"):
            submit_baseline_exam(smoke_eligible_db, payload)

    def test_submit_rejects_wrong_smoke_distribution(self, smoke_eligible_db):
        conn = smoke_eligible_db.connect()
        _insert_question(conn, "quant_extra", "Quant/DI")
        conn.commit()

        started = start_baseline_exam(smoke_eligible_db, "smoke")
        used_ids = {question["question_id"] for question in started["questions"]}
        extra = conn.execute(
            """SELECT question_id FROM questions
               WHERE section = 'Quant/DI' AND is_holdout = 0
                 AND question_id NOT IN ({})
               LIMIT 1""".format(",".join("?" for _ in used_ids)),
            tuple(used_ids),
        ).fetchone()["question_id"]

        questions = list(started["questions"])
        reasoning_index = next(
            index for index, question in enumerate(questions) if question["section"] == "Reasoning"
        )
        questions[reasoning_index] = {**questions[reasoning_index], "question_id": extra}
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            questions,
            exam_token=_encode_exam_token(
                started["exam_id"],
                "smoke",
                [question["question_id"] for question in questions],
            ),
        )

        with pytest.raises(BaselineWebError, match="smoke submit requires"):
            submit_baseline_exam(smoke_eligible_db, payload)


class TestResult:
    def test_get_baseline_result_returns_persisted_score(self, smoke_eligible_db):
        started = start_baseline_exam(smoke_eligible_db, "smoke")
        payload = _build_submit_payload(
            started["exam_id"],
            "smoke",
            started["questions"],
            exam_token=started["exam_token"],
            answers={started["questions"][0]["question_id"]: "1"},
        )
        submitted = submit_baseline_exam(smoke_eligible_db, payload)

        result = get_baseline_result(smoke_eligible_db, submitted["session_id"])

        assert result == submitted
        assert set(result["by_section"]) <= set(SMOKE_REQUIREMENTS)

    def test_get_baseline_result_missing_session_raises(self, smoke_eligible_db):
        with pytest.raises(BaselineWebError, match="Session not found"):
            get_baseline_result(smoke_eligible_db, 9999)

    def test_get_baseline_result_rejects_non_web_session(self, smoke_eligible_db):
        conn = smoke_eligible_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at, ended_at, notes) "
            "VALUES ('mock', '2026-01-01', '2026-01-01', 'cli session')"
        )
        conn.commit()
        session_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]

        with pytest.raises(BaselineWebError, match="Session not found"):
            get_baseline_result(smoke_eligible_db, session_id)
