"""Adversarial tests for the Phase 1 frontend MVP.

Covers preflight, start, submit, result, duplicate-idempotency,
holdout safety, correct-answer secrecy, section-distribution
validation, and adversarial edge cases.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ssc_study.db import Database
from ssc_study.models import Question
from ssc_study.quiz import (
    FOUNDATION_PULSE_REQUIREMENTS,
    FOUNDATION_PULSE_TOTAL,
    FoundationPulseError,
    _load_foundation_pulse,
)
from ssc_study.web import (
    SMOKE_REQUIREMENTS,
    SMOKE_TOTAL,
    create_app,
)


# ── Fixtures ──────────────────────────────────────────────────────────


def _insert_question(
    conn: sqlite3.Connection,
    qid: str,
    section: str = "Quant/DI",
    tier: str = "tier1",
    text: str = "Test question?",
    correct_label: str = "1",
    is_holdout: int = 0,
) -> None:
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
        (qid, "test_pdf", 1, 1, section, 2021, tier, text,
         json.dumps(options), correct_label, options[0]["text"], is_holdout),
    )
    conn.commit()


def _seed_full_eligible(conn: sqlite3.Connection) -> None:
    """Seed enough non-holdout questions for full baseline + some holdout trap."""
    qid = 0
    for section, needed in FOUNDATION_PULSE_REQUIREMENTS.items():
        for i in range(needed + 5):
            qid += 1
            _insert_question(conn, f"q{qid}", section, correct_label="1")
    # Add holdout trap questions
    _insert_question(conn, "holdout_quant", "Quant/DI", is_holdout=1)
    _insert_question(conn, "holdout_reason", "Reasoning", is_holdout=1)
    _insert_question(conn, "holdout_eng", "English", is_holdout=1)
    _insert_question(conn, "holdout_gk", "GK/GA", is_holdout=1)


def _seed_smoke_eligible(conn: sqlite3.Connection) -> None:
    """Seed minimum non-holdout questions for smoke + some holdout trap."""
    _insert_question(conn, "s_q1", "Quant/DI")
    _insert_question(conn, "s_q2", "Quant/DI")
    _insert_question(conn, "s_q3", "Reasoning")
    _insert_question(conn, "s_q4", "English")
    _insert_question(conn, "s_q5", "GK/GA")
    _insert_question(conn, "holdout_q", "Quant/DI", is_holdout=1)


@pytest.fixture
def in_memory_db() -> sqlite3.Connection:
    from ssc_study.db import apply_migrations
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    apply_migrations(conn)
    return conn


@pytest.fixture
def study_db(in_memory_db) -> Database:
    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


@pytest.fixture
def full_eligible_db(in_memory_db) -> Database:
    _seed_full_eligible(in_memory_db)
    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


@pytest.fixture
def smoke_eligible_db(in_memory_db) -> Database:
    _seed_smoke_eligible(in_memory_db)
    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


@pytest.fixture
def underfilled_db(in_memory_db) -> Database:
    """Only Quant/DI has enough — other sections are short."""
    for i in range(85):
        _insert_question(in_memory_db, f"u_q{i}", "Quant/DI")
    _insert_question(in_memory_db, "u_r1", "Reasoning")
    _insert_question(in_memory_db, "u_e1", "English")
    _insert_question(in_memory_db, "u_g1", "GK/GA")
    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


@pytest.fixture
def empty_db(in_memory_db) -> Database:
    db = Database.__new__(Database)
    db._path = Path(":memory:")
    db._lock = __import__("threading").Lock()
    db._conn = in_memory_db
    return db


# ── Client fixtures ───────────────────────────────────────────────────


@pytest.fixture
def full_client(full_eligible_db) -> TestClient:
    return TestClient(create_app(full_eligible_db))


@pytest.fixture
def smoke_client(smoke_eligible_db) -> TestClient:
    return TestClient(create_app(smoke_eligible_db))


@pytest.fixture
def underfilled_client(underfilled_db) -> TestClient:
    return TestClient(create_app(underfilled_db))


@pytest.fixture
def empty_client(empty_db) -> TestClient:
    return TestClient(create_app(empty_db))


# ══════════════════════════════════════════════════════════════════════
# Preflight tests
# ══════════════════════════════════════════════════════════════════════


class TestPreflight:
    def test_full_ready_when_eligible(self, full_client):
        resp = full_client.get("/api/baseline/preflight")
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_ready"] is True
        assert data["smoke_ready"] is True
        assert data["missing"] == {}

    def test_full_not_ready_when_underfilled(self, underfilled_client):
        resp = underfilled_client.get("/api/baseline/preflight")
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_ready"] is False
        assert "Reasoning" in data["missing"]
        assert "English" in data["missing"]
        assert "GK/GA" in data["missing"]

    def test_smoke_not_ready_when_underfilled(self):
        """Smoke needs 2/1/1/1 — a single GK/GA shouldn't be enough."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        from ssc_study.db import apply_migrations
        apply_migrations(conn)
        _insert_question(conn, "a", "Quant/DI")
        _insert_question(conn, "b", "Quant/DI")
        _insert_question(conn, "c", "Reasoning")
        _insert_question(conn, "d", "English")
        # Missing GK/GA
        conn.commit()
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = conn
        client = TestClient(create_app(db))
        resp = client.get("/api/baseline/preflight")
        data = resp.json()
        assert data["smoke_ready"] is False
        assert "GK/GA" in data.get("smoke_missing", {})

    def test_preflight_returns_required_and_available(self, full_client):
        resp = full_client.get("/api/baseline/preflight")
        data = resp.json()
        assert data["required"] == FOUNDATION_PULSE_REQUIREMENTS
        for section in FOUNDATION_PULSE_REQUIREMENTS:
            assert data["available"][section] >= FOUNDATION_PULSE_REQUIREMENTS[section]

    def test_empty_db_preflight(self, empty_client):
        resp = empty_client.get("/api/baseline/preflight")
        data = resp.json()
        assert data["full_ready"] is False
        assert data["smoke_ready"] is False

    def test_landing_page_renders(self, full_client):
        resp = full_client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "SSC Study" in resp.text


# ══════════════════════════════════════════════════════════════════════
# Start exam tests
# ══════════════════════════════════════════════════════════════════════


class TestStart:
    def test_smoke_returns_exactly_5_questions(self, smoke_client):
        resp = smoke_client.post("/api/baseline/start", json={"mode": "smoke"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "smoke"
        assert data["question_count"] == SMOKE_TOTAL
        assert len(data["questions"]) == SMOKE_TOTAL

    def test_smoke_has_correct_section_split(self, smoke_client):
        resp = smoke_client.post("/api/baseline/start", json={"mode": "smoke"})
        data = resp.json()
        sections = [q["section"] for q in data["questions"]]
        assert sections.count("Quant/DI") == SMOKE_REQUIREMENTS["Quant/DI"]
        assert sections.count("Reasoning") == SMOKE_REQUIREMENTS["Reasoning"]
        assert sections.count("English") == SMOKE_REQUIREMENTS["English"]
        assert sections.count("GK/GA") == SMOKE_REQUIREMENTS["GK/GA"]

    def test_full_returns_exactly_200_questions(self, full_client):
        resp = full_client.post("/api/baseline/start", json={"mode": "full"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "full"
        assert data["question_count"] == FOUNDATION_PULSE_TOTAL
        assert len(data["questions"]) == FOUNDATION_PULSE_TOTAL

    def test_full_has_correct_section_split(self, full_client):
        resp = full_client.post("/api/baseline/start", json={"mode": "full"})
        data = resp.json()
        sections = [q["section"] for q in data["questions"]]
        for section, needed in FOUNDATION_PULSE_REQUIREMENTS.items():
            assert sections.count(section) == needed

    def test_no_correct_answers_in_start_response(self, smoke_client):
        """The start endpoint must never include correct-answer fields."""
        resp = smoke_client.post("/api/baseline/start", json={"mode": "smoke"})
        data = resp.json()
        for q in data["questions"]:
            assert "correct_option_label" not in q
            assert "correct_option_text" not in q
            for opt in q["options"]:
                assert "is_correct" not in opt

    def test_no_holdout_in_smoke_response(self):
        """Smoke start excludes holdout questions."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        from ssc_study.db import apply_migrations
        apply_migrations(conn)
        _insert_question(conn, "a", "Quant/DI")
        _insert_question(conn, "b", "Quant/DI")
        _insert_question(conn, "c", "Reasoning")
        _insert_question(conn, "d", "English")
        _insert_question(conn, "e", "GK/GA")
        _insert_question(conn, "h", "Quant/DI", is_holdout=1)
        conn.commit()
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = conn
        client = TestClient(create_app(db))
        resp = client.post("/api/baseline/start", json={"mode": "smoke"})
        data = resp.json()
        qids = [q["question_id"] for q in data["questions"]]
        assert "h" not in qids

    def test_no_holdout_in_full_response(self, full_client):
        resp = full_client.post("/api/baseline/start", json={"mode": "full"})
        data = resp.json()
        qids = [q["question_id"] for q in data["questions"]]
        for hid in ["holdout_quant", "holdout_reason", "holdout_eng", "holdout_gk"]:
            assert hid not in qids

    def test_invalid_mode_returns_400(self, smoke_client):
        resp = smoke_client.post("/api/baseline/start", json={"mode": "invalid"})
        assert resp.status_code == 400
        assert "Invalid mode" in resp.text

    def test_start_returns_exam_id(self, smoke_client):
        resp = smoke_client.post("/api/baseline/start", json={"mode": "smoke"})
        data = resp.json()
        assert "exam_id" in data
        assert len(data["exam_id"]) > 0
        assert "exam_token" in data
        assert len(data["exam_token"]) > 0

    def test_smoke_fails_when_underfilled(self):
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        from ssc_study.db import apply_migrations
        apply_migrations(conn)
        _insert_question(conn, "a", "Quant/DI")
        conn.commit()
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = conn
        client = TestClient(create_app(db))
        resp = client.post("/api/baseline/start", json={"mode": "smoke"})
        assert resp.status_code == 400
        assert "requires" in resp.text


# ══════════════════════════════════════════════════════════════════════
# Submit tests
# ══════════════════════════════════════════════════════════════════════


class TestSubmit:
    def _start_and_get_answers(self, client: TestClient, mode: str = "smoke") -> dict:
        """Helper: start an exam and extract the correct answers from DB to verify
        server-side correctness computation."""
        resp = client.post("/api/baseline/start", json={"mode": mode})
        assert resp.status_code == 200
        return resp.json()

    def _get_correct_answers(self, db: Database, questions: list[dict]) -> dict:
        """Look up correct answers from the database."""
        conn = db.connect()
        qids = [q["question_id"] for q in questions]
        placeholders = ",".join("?" for _ in qids)
        rows = conn.execute(
            f"SELECT question_id, correct_option_label FROM questions WHERE question_id IN ({placeholders})",
            qids,
        ).fetchall()
        return {r["question_id"]: r["correct_option_label"] for r in rows}

    def test_submit_smoke_returns_score(self, smoke_client, smoke_eligible_db):
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]],
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "smoke"
        assert data["question_count"] == SMOKE_TOTAL
        assert data["correct_count"] == SMOKE_TOTAL
        assert data["accuracy"] == 1.0
        assert "by_section" in data

    def test_submit_computes_correctness_server_side(self, smoke_client, smoke_eligible_db):
        """Client could send wrong answers — server must compute from DB."""
        exam = self._start_and_get_answers(smoke_client, "smoke")

        # Send wrong answers
        answers = []
        for q in exam["questions"]:
            wrong_answer = "2" if q["options"][0]["label"] == "1" else "1"
            answers.append({
                "question_id": q["question_id"],
                "user_answer": wrong_answer,
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["correct_count"] == 0
        assert data["accuracy"] == 0.0

    def test_duplicate_submit_returns_existing_result(self, smoke_client, smoke_eligible_db):
        """Same exam_id must not create duplicate attempts."""
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]],
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        payload = {
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        }

        # First submit
        resp1 = smoke_client.post("/api/baseline/submit", json=payload)
        assert resp1.status_code == 200
        session_id = resp1.json()["session_id"]

        # Second submit with same exam_id
        conn = smoke_eligible_db.connect()
        before_count = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE session_id = ?",
            (session_id,),
        ).fetchone()["c"]

        resp2 = smoke_client.post("/api/baseline/submit", json=payload)
        assert resp2.status_code == 200
        assert resp2.json()["session_id"] == session_id

        after_count = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE session_id = ?",
            (session_id,),
        ).fetchone()["c"]
        assert after_count == before_count

    def test_submit_rejects_holdout_question(self, smoke_client, smoke_eligible_db):
        """Client sending a holdout question_id must be rejected."""
        exam = self._start_and_get_answers(smoke_client, "smoke")

        # Replace one question_id with a holdout
        answers = []
        for q in exam["questions"][:-1]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": "1",
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })
        answers.append({
            "question_id": "holdout_q",
            "user_answer": "1",
            "time_spent_seconds": 30,
            "marked_for_review": False,
        })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 400
        assert "exam_token" in resp.text.lower()

    def test_submit_rejects_unknown_question(self, smoke_client):
        exam = self._start_and_get_answers(smoke_client, "smoke")
        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": "1",
                "time_spent_seconds": 10,
                "marked_for_review": False,
            })
        answers[0]["question_id"] = "nonexistent_qid"
        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 400
        assert "exam_token" in resp.text.lower()

    def test_submit_rejects_wrong_count(self, smoke_client):
        """Submitting fewer answers than expected must be rejected."""
        exam = self._start_and_get_answers(smoke_client, "smoke")
        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": [],
        })
        assert resp.status_code == 400
        assert "Expected" in resp.text

    def test_submit_rejects_full_with_smoke_count(self, full_client):
        """Sending smoke-sized payload in full mode should fail."""
        exam = full_client.post("/api/baseline/start", json={"mode": "full"}).json()
        answers = []
        for q in exam["questions"][:SMOKE_TOTAL]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": "1",
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })
        resp = full_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "full",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 400

    def test_submit_treats_null_answer_as_skipped(self, smoke_client, smoke_eligible_db):
        """Questions where user_answer is null should be counted as incorrect/skipped."""
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        answers = []
        for i, q in enumerate(exam["questions"]):
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]] if i == 0 else None,
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["correct_count"] == 1

    def test_submit_creates_one_session_row(self, smoke_client, smoke_eligible_db, monkeypatch):
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        conn = smoke_eligible_db.connect()
        before_count = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]],
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200

        after_count = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
        assert after_count == before_count + 1

    def test_submit_creates_one_attempt_per_question(self, smoke_client, smoke_eligible_db):
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]],
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]

        conn = smoke_eligible_db.connect()
        attempt_count = conn.execute(
            "SELECT COUNT(*) as c FROM attempts WHERE session_id = ?",
            (session_id,),
        ).fetchone()["c"]
        assert attempt_count == SMOKE_TOTAL

    def test_smoke_session_not_recorded_as_foundation_pulse(self, smoke_client, smoke_eligible_db):
        exam = self._start_and_get_answers(smoke_client, "smoke")
        correct = self._get_correct_answers(smoke_eligible_db, exam["questions"])

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct[q["question_id"]],
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]

        conn = smoke_eligible_db.connect()
        row = conn.execute(
            "SELECT session_type, notes FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        assert row["session_type"] == "analysis"
        assert "phase1_web_smoke" in (row["notes"] or "")

    def test_adversarial_duplicate_question_ids(self, smoke_client, smoke_eligible_db):
        """Client sends duplicate question IDs — server should not crash."""
        exam = self._start_and_get_answers(smoke_client, "smoke")
        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": "1",
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })
        # Replace one answer with a duplicate while keeping the expected count.
        answers[-1] = dict(answers[0])
        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 400

    def test_adversarial_negative_time_values(self, smoke_client, smoke_eligible_db):
        """Client sends negative time_spent_seconds — server should reject it."""
        exam = self._start_and_get_answers(smoke_client, "smoke")
        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": "1",
                "time_spent_seconds": -999,
                "marked_for_review": False,
            })
        resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        assert resp.status_code == 400
        assert "time_spent_seconds" in resp.text

    def test_missing_exam_id_rejected(self, smoke_client):
        resp = smoke_client.post("/api/baseline/submit", json={
            "mode": "smoke",
            "answers": [],
        })
        assert resp.status_code == 400
        assert "exam_id" in resp.text.lower()


# ══════════════════════════════════════════════════════════════════════
# Result tests
# ══════════════════════════════════════════════════════════════════════


class TestResult:
    def test_result_returns_for_valid_session(self, smoke_client, smoke_eligible_db):
        exam = smoke_client.post("/api/baseline/start", json={"mode": "smoke"}).json()
        conn = smoke_eligible_db.connect()
        correct = {r["question_id"]: r["correct_option_label"]
                   for r in conn.execute(
                       "SELECT question_id, correct_option_label FROM questions"
                   ).fetchall()}

        answers = []
        for q in exam["questions"]:
            answers.append({
                "question_id": q["question_id"],
                "user_answer": correct.get(q["question_id"], "1"),
                "time_spent_seconds": 30,
                "marked_for_review": False,
            })

        submit_resp = smoke_client.post("/api/baseline/submit", json={
            "exam_id": exam["exam_id"],
            "exam_token": exam["exam_token"],
            "mode": "smoke",
            "started_at": "2026-07-06T10:00:00Z",
            "ended_at": "2026-07-06T10:05:00Z",
            "answers": answers,
        })
        sid = submit_resp.json()["session_id"]

        result_resp = smoke_client.get(f"/api/baseline/result/{sid}")
        assert result_resp.status_code == 200
        result = result_resp.json()
        assert result["session_id"] == sid
        assert "by_section" in result
        assert result["question_count"] == SMOKE_TOTAL

    def test_result_404_for_bad_session(self, smoke_client):
        resp = smoke_client.get("/api/baseline/result/999999")
        assert resp.status_code == 404
        assert "not found" in resp.text.lower()


# ══════════════════════════════════════════════════════════════════════
# Static file tests
# ══════════════════════════════════════════════════════════════════════


class TestStatic:
    def test_static_css_served(self, full_client):
        resp = full_client.get("/static/app.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers["content-type"]

    def test_static_js_served(self, full_client):
        resp = full_client.get("/static/app.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers["content-type"]

    def test_landing_page_has_no_external_font_dependency(self, full_client):
        resp = full_client.get("/")
        assert resp.status_code == 200
        assert "fonts.googleapis.com" not in resp.text
        assert "fonts.gstatic.com" not in resp.text

    def test_frontend_can_restore_draft_without_querystring(self):
        app_js = Path("src/ssc_study/static/app.js").read_text(encoding="utf-8")
        assert "loadMostRecentDraft" in app_js
        assert "Object.keys(localStorage)" in app_js

    def test_frontend_escapes_db_sourced_fields_in_inner_html(self):
        app_js = Path("src/ssc_study/static/app.js").read_text(encoding="utf-8")
        assert "escapeHtml(q.section)" in app_js
        assert "escapeHtml(q.tier)" in app_js
        assert "escapeHtml(o.label)" in app_js
        assert "escapeHtml(section)" in app_js

    def test_failed_submit_restarts_timer(self):
        app_js = Path("src/ssc_study/static/app.js").read_text(encoding="utf-8")
        assert "if (!result) {\n          currentQuestionStartTime = Date.now();\n          startTimer();\n          return;\n        }" in app_js


# ══════════════════════════════════════════════════════════════════════
# Backend unit tests for business logic functions
# ══════════════════════════════════════════════════════════════════════


class TestBusinessLogic:
    def test_get_baseline_preflight_full_ready(self, full_eligible_db):
        from ssc_study.web import get_baseline_preflight
        data = get_baseline_preflight(full_eligible_db)
        assert data["full_ready"] is True

    def test_get_baseline_preflight_underfilled(self, underfilled_db):
        from ssc_study.web import get_baseline_preflight
        data = get_baseline_preflight(underfilled_db)
        assert data["full_ready"] is False

    def test_start_baseline_smoke_returns_5(self, smoke_eligible_db):
        from ssc_study.web import start_baseline_exam
        data = start_baseline_exam(smoke_eligible_db, "smoke")
        assert data["question_count"] == SMOKE_TOTAL

    def test_start_baseline_full_returns_200(self, full_eligible_db):
        from ssc_study.web import start_baseline_exam
        data = start_baseline_exam(full_eligible_db, "full")
        assert data["question_count"] == FOUNDATION_PULSE_TOTAL

    def test_start_response_no_correct_labels(self, smoke_eligible_db):
        from ssc_study.web import start_baseline_exam
        data = start_baseline_exam(smoke_eligible_db, "smoke")
        for q in data["questions"]:
            assert "correct_option_label" not in q

    def test_get_baseline_result_404(self):
        from ssc_study.web import get_baseline_result
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        from ssc_study.db import apply_migrations
        apply_migrations(conn)
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = conn
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            get_baseline_result(db, 999)
        assert exc.value.status_code == 404


# ══════════════════════════════════════════════════════════════════════
# Regression: existing CLI behavior still works
# ══════════════════════════════════════════════════════════════════════


class TestRegression:
    """Quick smoke-tests borrowed from existing test_quiz.py to confirm
    we haven't broken the backend."""

    def test_load_questions_excludes_holdout(self, seeded_db):
        from ssc_study.quiz import _load_questions
        questions = _load_questions(seeded_db, "mock", None, 50)
        ids = [q.question_id for q in questions]
        assert "q11" not in ids

    def test_foundation_pulse_requires_200(self, seeded_db):
        from ssc_study.quiz import FoundationPulseError, _load_foundation_pulse
        with pytest.raises(FoundationPulseError, match="exactly 200"):
            _load_foundation_pulse(seeded_db, count=100)

    def test_foundation_pulse_fails_if_section_short(self, seeded_db):
        from ssc_study.quiz import FoundationPulseError, _load_foundation_pulse
        with pytest.raises(FoundationPulseError, match="requires 80"):
            _load_foundation_pulse(seeded_db, count=200)

    @pytest.fixture
    def seeded_db(self, seeded_conn) -> Database:
        db = Database.__new__(Database)
        db._path = Path(":memory:")
        db._lock = __import__("threading").Lock()
        db._conn = seeded_conn
        return db

    @pytest.fixture
    def seeded_conn(self, in_memory_db) -> sqlite3.Connection:
        """Reuse the same seeding as conftest.py for regression tests."""
        from tests.conftest import _insert_question
        conn = in_memory_db
        _insert_question(conn, "q1", "Quant/DI", "tier1", "Test?", "2")
        _insert_question(conn, "q2", "Quant/DI", "tier2", "Test?", "1")
        _insert_question(conn, "q3", "Quant/DI", "tier1", "Test?", "3")
        _insert_question(conn, "q4", "Reasoning", "tier1", "Test?", "1")
        _insert_question(conn, "q5", "Reasoning", "tier2", "Test?", "4")
        _insert_question(conn, "q6", "English", "tier1", "Test?", "1")
        _insert_question(conn, "q7", "English", "tier2", "Test?", "2")
        _insert_question(conn, "q8", "GK/GA", "tier1", "Test?", "3")
        _insert_question(conn, "q9", "GK/GA", "tier2", "Test?", "2")
        _insert_question(conn, "q10", "GK/GA", "tier1", "Test?", "1")
        _insert_question(conn, "q11", "Quant/DI", "tier1", "Holdout?", "1", is_holdout=1)
        conn.executemany(
            "INSERT INTO sm2_state (entity_type, entity_id, easiness, interval_days, repetitions, next_review, last_review, last_quality) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("question", "q1", 2.5, 1, 1, "2020-01-01", "2019-12-31", 4),
                ("question", "q2", 2.6, 6, 2, "2099-01-01", "2099-01-01", 5),
            ],
        )
        conn.commit()
        return conn
