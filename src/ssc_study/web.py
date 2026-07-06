"""Phase 1 local web MVP — FastAPI backend for the baseline exam UI."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from .db import Database
from .models import Option, Question
from .quiz import (
    FOUNDATION_PULSE_REQUIREMENTS,
    FOUNDATION_PULSE_TOTAL,
    FoundationPulseError,
    _load_foundation_pulse,
)

SMOKE_REQUIREMENTS: dict[str, int] = {"Quant/DI": 2, "Reasoning": 1, "English": 1, "GK/GA": 1}
SMOKE_TOTAL = sum(SMOKE_REQUIREMENTS.values())


def create_app(db: Database, templates_dir: str | Path | None = None) -> FastAPI:
    """Build the FastAPI application wired to the given Database.

    Args:
        db: Database instance.
        templates_dir: Optional path to Jinja templates directory.
                       Defaults to ``templates/`` beside this file.
    """
    if templates_dir is None:
        templates_dir = Path(__file__).resolve().parent / "templates"

    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)

    app = FastAPI(title="SSC Study — Phase 1 MVP")

    # ------------------------------------------------------------------
    # Serve static files
    # ------------------------------------------------------------------
    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # ------------------------------------------------------------------
    # HTML page
    # ------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    async def landing_page(request: Request) -> str:
        preflight = get_baseline_preflight(db)
        template = env.get_template("landing.html")
        return template.render(
            db_path=str(db.path),
            full_ready=preflight["full_ready"],
            smoke_ready=preflight["smoke_ready"],
            required=preflight["required"],
            available=preflight["available"],
            missing=preflight["missing"],
        )

    # ------------------------------------------------------------------
    # API routes
    # ------------------------------------------------------------------

    @app.get("/api/baseline/preflight")
    async def api_preflight() -> dict:
        return get_baseline_preflight(db)

    @app.post("/api/baseline/start")
    async def api_start(payload: dict) -> dict:
        mode = payload.get("mode")
        if mode not in ("smoke", "full"):
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode!r}")
        return start_baseline_exam(db, mode)

    @app.post("/api/baseline/submit")
    async def api_submit(payload: dict) -> dict:
        return submit_baseline_exam(db, payload)

    @app.get("/api/baseline/result/{session_id}")
    async def api_result(session_id: int) -> dict:
        return get_baseline_result(db, session_id)

    return app


# ------------------------------------------------------------------
# Business logic
# ------------------------------------------------------------------


def get_baseline_preflight(db: Database) -> dict:
    """Return current readiness for baseline exams."""
    conn = db.connect()

    required = dict(FOUNDATION_PULSE_REQUIREMENTS)
    available: dict[str, int] = {}
    missing: dict[str, int] = {}

    for section, needed in FOUNDATION_PULSE_REQUIREMENTS.items():
        row = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE section = ? AND is_holdout = 0",
            (section,),
        ).fetchone()
        count = row["c"]
        available[section] = count
        if count < needed:
            missing[section] = needed - count

    full_ready = len(missing) == 0

    smoke_missing: dict[str, int] = {}
    for section, needed in SMOKE_REQUIREMENTS.items():
        avail = available.get(section, 0)
        if avail < needed:
            smoke_missing[section] = needed - avail

    smoke_ready = len(smoke_missing) == 0

    return {
        "full_ready": full_ready,
        "required": required,
        "available": available,
        "missing": missing,
        "smoke_ready": smoke_ready,
        "smoke_missing": smoke_missing,
    }


def start_baseline_exam(db: Database, mode: str) -> dict:
    """Start a baseline exam (smoke or full) and return questions.

    The response uses ``exam_id`` (a UUID generated server-side for
    idempotent submit) and never includes correct-answer fields.
    """
    exam_id = str(uuid.uuid4())

    try:
        if mode == "full":
            questions = _load_foundation_pulse(db, count=FOUNDATION_PULSE_TOTAL)
        else:
            questions = _load_smoke_questions(db)
    except FoundationPulseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    payload_questions = []
    for idx, q in enumerate(questions, start=1):
        payload_questions.append({
            "question_id": q.question_id,
            "index": idx,
            "section": q.section,
            "tier": q.tier,
            "question_text": q.question_text,
            "options": [
                {"label": o.label, "text": o.text}
                for o in q.options
            ],
        })

    return {
        "exam_id": exam_id,
        "mode": mode,
        "question_count": len(payload_questions),
        "questions": payload_questions,
    }


def _load_smoke_questions(db: Database) -> list[Question]:
    """Load 5 smoke questions: 2 Quant/DI, 1 Reasoning, 1 English, 1 GK/GA.

    Raises FoundationPulseError if the required count cannot be met.
    """
    conn = db.connect()
    questions: list[Question] = []

    for section, needed in SMOKE_REQUIREMENTS.items():
        rows = conn.execute(
            "SELECT * FROM questions WHERE section = ? AND is_holdout = 0 ORDER BY RANDOM() LIMIT ?",
            (section, needed),
        ).fetchall()

        if len(rows) < needed:
            raise FoundationPulseError(
                f"Smoke exam requires {needed} {section} questions, "
                f"but only {len(rows)} available (non-holdout)."
            )

        questions.extend(Question.from_row(r) for r in rows)

    return questions


def submit_baseline_exam(db: Database, payload: dict) -> dict:
    """Persist exam answers and return the scored result.

    Idempotent: re-submitting the same ``exam_id`` returns the existing
    session result without creating duplicate attempts.
    """
    exam_id = payload.get("exam_id")
    mode = payload.get("mode", "smoke")
    answers = payload.get("answers", [])
    started_at = payload.get("started_at", "")
    ended_at = payload.get("ended_at", "")

    if not exam_id:
        raise HTTPException(status_code=400, detail="Missing exam_id")
    if mode not in ("smoke", "full"):
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode!r}")

    # Determine expected session type and notes marker
    if mode == "full":
        session_type = "foundation_pulse"
        notes_marker = f"phase1_web_full:{exam_id}"
        expected_count = FOUNDATION_PULSE_TOTAL
        expected_requirements = FOUNDATION_PULSE_REQUIREMENTS
    else:
        session_type = "analysis"
        notes_marker = f"phase1_web_smoke:{exam_id}"
        expected_count = SMOKE_TOTAL
        expected_requirements = SMOKE_REQUIREMENTS

    conn = db.connect()

    # Check for duplicate submit
    existing = conn.execute(
        "SELECT session_id FROM sessions WHERE notes = ?",
        (notes_marker,),
    ).fetchone()
    if existing is not None:
        return get_baseline_result(db, existing["session_id"])

    # Validate submitted question IDs exist, are non-holdout, and match expected count
    if len(answers) != expected_count:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {expected_count} answers, got {len(answers)}",
        )

    # Validate section distribution and question existence
    submitted_qids = [a["question_id"] for a in answers]
    placeholders = ",".join("?" for _ in submitted_qids)
    rows = conn.execute(
        f"SELECT question_id, section, correct_option_label, is_holdout FROM questions WHERE question_id IN ({placeholders})",
        submitted_qids,
    ).fetchall()

    qid_map = {r["question_id"]: r for r in rows}

    # Check all questions exist and are non-holdout
    section_counts: dict[str, int] = {}
    for a in answers:
        qid = a["question_id"]
        if qid not in qid_map:
            raise HTTPException(status_code=400, detail=f"Unknown question_id: {qid}")
        row = qid_map[qid]
        if row["is_holdout"]:
            raise HTTPException(status_code=400, detail=f"Holdout question in submit: {qid}")
        section = row["section"]
        section_counts[section] = section_counts.get(section, 0) + 1

    # Check section distribution matches expected
    for section, needed in expected_requirements.items():
        actual = section_counts.get(section, 0)
        if actual != needed:
            raise HTTPException(
                status_code=400,
                detail=f"Section {section}: expected {needed} questions, got {actual}",
            )

    now = datetime.now(timezone.utc).isoformat()

    with db.transaction() as txn:
        cursor = txn.execute(
            """INSERT INTO sessions (session_type, started_at, ended_at, question_count, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (session_type, started_at or now, ended_at or now, expected_count, notes_marker),
        )
        session_id = cursor.lastrowid

        correct_count = 0
        by_section: dict[str, dict] = {}

        for a in answers:
            qid = a["question_id"]
            user_answer = a.get("user_answer")
            time_spent = a.get("time_spent_seconds", 0)
            marked = a.get("marked_for_review", False)

            row = qid_map[qid]
            correct_label = row["correct_option_label"]
            section = row["section"]

            is_correct = user_answer == correct_label if user_answer is not None else False
            if is_correct:
                correct_count += 1

            if section not in by_section:
                by_section[section] = {"total": 0, "correct": 0}
            by_section[section]["total"] += 1
            if is_correct:
                by_section[section]["correct"] += 1

            student_label: str | None = "skipped"
            if user_answer is not None:
                student_label = "correct" if is_correct else "incorrect"

            txn.execute(
                """INSERT INTO attempts
                   (question_id, session_id, user_answer, is_correct, time_spent_seconds, student_label)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (qid, session_id, user_answer, int(is_correct), time_spent, student_label),
            )

        txn.execute(
            """UPDATE sessions SET correct_count = ? WHERE session_id = ?""",
            (correct_count, session_id),
        )

    accuracy = correct_count / expected_count if expected_count > 0 else 0.0

    return {
        "session_id": session_id,
        "mode": mode,
        "question_count": expected_count,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "by_section": by_section,
    }


def get_baseline_result(db: Database, session_id: int) -> dict:
    """Return the persisted result for a completed Phase 1 web session."""
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Determine mode from session_type / notes
    session_type = row["session_type"]
    notes = row["notes"] or ""
    if session_type == "foundation_pulse" or "phase1_web_full" in notes:
        mode = "full"
        requirements = FOUNDATION_PULSE_REQUIREMENTS
    elif session_type == "analysis" or "phase1_web_smoke" in notes:
        mode = "smoke"
        requirements = SMOKE_REQUIREMENTS
    else:
        mode = session_type
        requirements = FOUNDATION_PULSE_REQUIREMENTS

    question_count = row["question_count"]
    correct_count = row["correct_count"]
    accuracy = correct_count / question_count if question_count > 0 else 0.0

    attempts = conn.execute(
        "SELECT q.section, at.is_correct FROM attempts at JOIN questions q ON at.question_id = q.question_id WHERE at.session_id = ?",
        (session_id,),
    ).fetchall()

    by_section: dict[str, dict] = {}
    for a in attempts:
        section = a["section"]
        if section not in by_section:
            by_section[section] = {"total": 0, "correct": 0}
        by_section[section]["total"] += 1
        if a["is_correct"]:
            by_section[section]["correct"] += 1

    return {
        "session_id": session_id,
        "mode": mode,
        "question_count": question_count,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "by_section": by_section,
    }
