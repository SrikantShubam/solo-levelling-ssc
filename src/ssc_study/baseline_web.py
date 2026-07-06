"""Backend service for the Phase 1 local web baseline exam."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from collections import Counter
from typing import Any

from .db import Database
from .models import Attempt, Question
from .quiz import (
    FOUNDATION_PULSE_REQUIREMENTS,
    FoundationPulseError,
    _load_foundation_pulse,
    _persist_attempt_with_sm2,
)

SMOKE_REQUIREMENTS: dict[str, int] = {
    "Quant/DI": 2,
    "Reasoning": 1,
    "English": 1,
    "GK/GA": 1,
}
SMOKE_TOTAL = sum(SMOKE_REQUIREMENTS.values())
_EXAM_TOKEN_SECRET = secrets.token_bytes(32)


class BaselineWebError(Exception):
    """Raised when baseline web operations cannot complete."""


def get_baseline_preflight(db: Database) -> dict[str, Any]:
    """Return readiness for full and smoke baseline exams."""
    conn = db.connect()
    available: dict[str, int] = {}
    for section in FOUNDATION_PULSE_REQUIREMENTS:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM questions WHERE section = ? AND is_holdout = 0",
            (section,),
        ).fetchone()
        available[section] = int(row["c"])

    missing: dict[str, int] = {}
    for section, required in FOUNDATION_PULSE_REQUIREMENTS.items():
        shortfall = required - available[section]
        if shortfall > 0:
            missing[section] = shortfall

    smoke_missing: dict[str, int] = {}
    for section, required in SMOKE_REQUIREMENTS.items():
        shortfall = required - available[section]
        if shortfall > 0:
            smoke_missing[section] = shortfall

    return {
        "full_ready": len(missing) == 0,
        "required": dict(FOUNDATION_PULSE_REQUIREMENTS),
        "available": available,
        "missing": missing,
        "smoke_ready": len(smoke_missing) == 0,
        "smoke_missing": smoke_missing,
    }


def start_baseline_exam(db: Database, mode: str) -> dict[str, Any]:
    """Load questions for a smoke or full baseline exam without answer leakage."""
    if mode == "full":
        try:
            questions = _load_foundation_pulse(db, 200)
        except FoundationPulseError as exc:
            raise BaselineWebError(str(exc)) from exc
    elif mode == "smoke":
        try:
            questions = _load_smoke_baseline(db)
        except FoundationPulseError as exc:
            raise BaselineWebError(str(exc)) from exc
    else:
        raise BaselineWebError(f"Invalid mode: {mode}")

    exam_id = str(uuid.uuid4())
    question_ids = [question.question_id for question in questions]

    return {
        "exam_id": exam_id,
        "exam_token": _encode_exam_token(exam_id, mode, question_ids),
        "mode": mode,
        "question_count": len(questions),
        "questions": [
            _question_to_client(question, index)
            for index, question in enumerate(questions, start=1)
        ],
    }


def submit_baseline_exam(db: Database, payload: dict[str, Any]) -> dict[str, Any]:
    """Persist a completed baseline exam and return the scored result."""
    mode = payload.get("mode")
    exam_id = payload.get("exam_id")
    exam_token = payload.get("exam_token")
    if mode not in {"smoke", "full"}:
        raise BaselineWebError(f"Invalid mode: {mode}")
    if not exam_id:
        raise BaselineWebError("exam_id is required")
    if not isinstance(exam_token, str) or not exam_token:
        raise BaselineWebError("exam_token is required")

    token_payload = _decode_exam_token(exam_token)
    if token_payload.get("exam_id") != str(exam_id) or token_payload.get("mode") != mode:
        raise BaselineWebError("exam_token does not match submitted exam")

    token_question_ids = token_payload.get("question_ids")
    if not isinstance(token_question_ids, list) or not all(
        isinstance(question_id, str) for question_id in token_question_ids
    ):
        raise BaselineWebError("exam_token has invalid question set")

    note = _idempotency_note(mode, str(exam_id))
    conn = db.connect()
    existing = conn.execute(
        "SELECT session_id FROM sessions WHERE notes = ?",
        (note,),
    ).fetchone()
    if existing is not None:
        return get_baseline_result(db, int(existing["session_id"]))

    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise BaselineWebError("answers must be a list")
    if not all(isinstance(item, dict) for item in answers):
        raise BaselineWebError("Each answer entry must be an object")

    expected_count = 200 if mode == "full" else SMOKE_TOTAL
    if len(answers) != expected_count:
        raise BaselineWebError(f"Expected {expected_count} answers, got {len(answers)}")

    question_ids = [str(item.get("question_id", "")) for item in answers]
    if not all(question_ids):
        raise BaselineWebError("Each answer must include question_id")
    if len(set(question_ids)) != len(question_ids):
        raise BaselineWebError("Duplicate question_id in answers")
    if sorted(question_ids) != sorted(token_question_ids):
        raise BaselineWebError("Submitted questions do not match exam_token")

    questions_by_id = _load_questions_for_submit(conn, question_ids)
    _validate_submit_distribution(questions_by_id.values(), mode)

    started_at = payload.get("started_at")
    ended_at = payload.get("ended_at")
    if not started_at or not ended_at:
        raise BaselineWebError("started_at and ended_at are required")

    session_type = "foundation_pulse" if mode == "full" else "analysis"

    with db.transaction() as tx:
        duplicate = tx.execute(
            "SELECT session_id FROM sessions WHERE notes = ?",
            (note,),
        ).fetchone()
        if duplicate is not None:
            return get_baseline_result(db, int(duplicate["session_id"]))

        cursor = tx.execute(
            """INSERT INTO sessions
               (session_type, started_at, ended_at, question_count, correct_count, notes)
               VALUES (?, ?, ?, 0, 0, ?)""",
            (session_type, started_at, ended_at, note),
        )
        session_id = int(cursor.lastrowid)

        correct_count = 0
        for answer in answers:
            question_id = str(answer["question_id"])
            question = questions_by_id[question_id]
            user_answer = answer.get("user_answer")
            if user_answer is not None:
                user_answer = str(user_answer)
                if user_answer not in {"1", "2", "3", "4"}:
                    raise BaselineWebError(f"Invalid user_answer for {question_id}")

            try:
                time_spent = int(answer.get("time_spent_seconds") or 0)
            except (TypeError, ValueError) as exc:
                raise BaselineWebError(
                    f"time_spent_seconds must be a non-negative integer for {question_id}"
                ) from exc
            if time_spent < 0:
                raise BaselineWebError(
                    f"time_spent_seconds must be a non-negative integer for {question_id}"
                )
            if user_answer is None:
                is_correct = False
                student_label = "skipped"
            else:
                is_correct = user_answer == question.correct_option_label
                student_label = "correct" if is_correct else "incorrect"
                if is_correct:
                    correct_count += 1

            attempt = Attempt(
                question_id=question_id,
                session_id=session_id,
                user_answer=user_answer,
                is_correct=is_correct,
                time_spent_seconds=time_spent,
                student_label=student_label,
            )
            _persist_attempt_with_sm2(tx, attempt, question)

        tx.execute(
            """UPDATE sessions
               SET question_count = ?, correct_count = ?, ended_at = ?
               WHERE session_id = ?""",
            (expected_count, correct_count, ended_at, session_id),
        )

    return get_baseline_result(db, session_id)


def _get_baseline_result_raw(db: Database, session_id: int) -> dict[str, Any]:
    """Return the persisted score summary for a Phase 1 web session."""
    conn = db.connect()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if session is None:
        raise BaselineWebError(f"Session not found: {session_id}")

    notes = session["notes"] or ""
    if not notes.startswith("phase1_web_"):
        raise BaselineWebError(f"Session not found: {session_id}")

    if session["ended_at"] is None:
        raise BaselineWebError(f"Session not complete: {session_id}")

    mode = "full" if notes.startswith("phase1_web_full:") else "smoke"
    question_count = int(session["question_count"] or 0)
    correct_count = int(session["correct_count"] or 0)
    accuracy = correct_count / question_count if question_count else 0.0

    rows = conn.execute(
        """SELECT q.section, COUNT(*) as total,
                  SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts a
           JOIN questions q ON q.question_id = a.question_id
           WHERE a.session_id = ?
           GROUP BY q.section""",
        (session_id,),
    ).fetchall()

    by_section: dict[str, dict[str, int]] = {}
    for row in rows:
        by_section[row["section"]] = {
            "total": int(row["total"]),
            "correct": int(row["correct"] or 0),
        }

    return {
        "session_id": session_id,
        "mode": mode,
        "question_count": question_count,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "by_section": by_section,
    }


def get_baseline_result(db: Database, session_id: int) -> dict[str, Any]:
    """Return the persisted score summary and next steps for a Phase 1 web session."""
    res = _get_baseline_result_raw(db, session_id)
    res["next_steps"] = get_baseline_next_steps(db, session_id)
    return res


def _load_smoke_baseline(db: Database) -> list[Question]:
    """Load the 5-question smoke baseline across four sections."""
    conn = db.connect()
    questions: list[Question] = []

    for section, needed in SMOKE_REQUIREMENTS.items():
        rows = conn.execute(
            "SELECT * FROM questions WHERE section = ? AND is_holdout = 0 ORDER BY RANDOM() LIMIT ?",
            (section, needed),
        ).fetchall()
        if len(rows) < needed:
            raise FoundationPulseError(
                f"Smoke baseline requires {needed} {section} questions, "
                f"but only {len(rows)} available (non-holdout)."
            )
        questions.extend(Question.from_row(row) for row in rows)

    return questions


def _question_to_client(question: Question, index: int) -> dict[str, Any]:
    return {
        "question_id": question.question_id,
        "index": index,
        "section": question.section,
        "tier": question.tier,
        "question_text": question.question_text,
        "options": [{"label": option.label, "text": option.text} for option in question.options],
    }


def _idempotency_note(mode: str, exam_id: str) -> str:
    prefix = "phase1_web_full" if mode == "full" else "phase1_web_smoke"
    return f"{prefix}:{exam_id}"


def _encode_exam_token(exam_id: str, mode: str, question_ids: list[str]) -> str:
    payload = {
        "exam_id": exam_id,
        "mode": mode,
        "question_ids": question_ids,
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii").rstrip("=")
    signature = hmac.new(_EXAM_TOKEN_SECRET, body.encode("ascii"), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{body}.{sig}"


def _decode_exam_token(token: str) -> dict[str, Any]:
    try:
        body, sig = token.split(".", 1)
    except ValueError as exc:
        raise BaselineWebError("Invalid exam_token") from exc

    expected = hmac.new(_EXAM_TOKEN_SECRET, body.encode("ascii"), hashlib.sha256).digest()
    expected_sig = base64.urlsafe_b64encode(expected).decode("ascii").rstrip("=")
    if not hmac.compare_digest(sig, expected_sig):
        raise BaselineWebError("Invalid exam_token")

    try:
        padded = body + "=" * (-len(body) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
        payload = json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise BaselineWebError("Invalid exam_token") from exc

    if not isinstance(payload, dict):
        raise BaselineWebError("Invalid exam_token")
    return payload


def _load_questions_for_submit(
    conn: Any,
    question_ids: list[str],
) -> dict[str, Question]:
    placeholders = ",".join("?" for _ in question_ids)
    rows = conn.execute(
        f"SELECT * FROM questions WHERE question_id IN ({placeholders})",
        tuple(question_ids),
    ).fetchall()

    questions_by_id = {str(row["question_id"]): Question.from_row(row) for row in rows}
    missing = [question_id for question_id in question_ids if question_id not in questions_by_id]
    if missing:
        raise BaselineWebError(f"Unknown question_id: {missing[0]}")

    holdout = [question_id for question_id, question in questions_by_id.items() if question.is_holdout]
    if holdout:
        raise BaselineWebError(f"Holdout question not allowed: {holdout[0]}")

    return questions_by_id


def _validate_submit_distribution(questions: Any, mode: str) -> None:
    requirements = FOUNDATION_PULSE_REQUIREMENTS if mode == "full" else SMOKE_REQUIREMENTS
    expected_total = sum(requirements.values())
    section_counts = Counter(question.section for question in questions)

    if sum(section_counts.values()) != expected_total:
        raise BaselineWebError(
            f"{mode} submit requires exactly {expected_total} questions, "
            f"got {sum(section_counts.values())}"
        )

    for section, required in requirements.items():
        actual = section_counts.get(section, 0)
        if actual != required:
            raise BaselineWebError(
                f"{mode} submit requires {required} {section} questions, got {actual}"
            )


def get_baseline_next_steps(db: Database, session_id: int) -> dict[str, Any]:
    """Calculate and return data-backed next-step recommendations from baseline results."""
    from .phase3 import plan_next_action
    from .guardian import build_guardian_plan

    result = _get_baseline_result_raw(db, session_id)
    mode = result["mode"]
    by_section = result["by_section"]

    if mode == "smoke":
        return {
            "session_id": session_id,
            "mode": mode,
            "overall_accuracy": result["accuracy"],
            "weak_sections": [],
            "overall_action": {
                "action_type": "smoke_warning",
                "title": "Establish Full Baseline",
                "command": "ssc-study web",
                "reason": (
                    "This was a 5-question Smoke Test. To establish a reliable baseline "
                    "and unlock the daily scheduler, please take the 200-question Full "
                    "Baseline exam."
                ),
            },
            "guardian_plan": None,
        }

    weak_sections = []
    tier_summary = {"remediation_excluded": False, "remediation_priority": False, "paired_remediation": False}
    for section, data in by_section.items():
        total = data["total"]
        correct = data["correct"]
        acc = correct / total if total > 0 else 0.0
        if acc >= 0.70:
            continue
        if acc < 0.55:
            tier = "remediation_excluded"
        elif acc < 0.65:
            tier = "remediation_priority"
        else:
            tier = "paired_remediation"
        tier_summary[tier] = True
        p3_action = plan_next_action(db, section=section)
        action_info = {
            "action_type": p3_action.action_type,
            "reason": p3_action.reason,
            "target_archetype_name": p3_action.target_archetype_name,
            "target_archetype_id": p3_action.target_archetype_id,
            "question_count": p3_action.question_count,
        }
        weak_sections.append({
            "section": section,
            "accuracy": acc,
            "correct": correct,
            "total": total,
            "tier": tier,
            "action": action_info,
        })

    # Formulate recommendation by highest-priority tier
    if tier_summary["remediation_excluded"]:
        overall = {
            "action_type": "remediation_excluded",
            "title": "Remediation-First Priority",
            "command": "ssc-study phase3",
            "reason": "Some sections scored below 55%. These sections require focused remediation first and are excluded from readiness scoring until reaching 65%.",
        }
        guardian_info = None
    elif tier_summary["remediation_priority"]:
        overall = {
            "action_type": "remediation_priority",
            "title": "Remediation Priority",
            "command": "ssc-study phase3",
            "reason": "Some sections scored 55-64%. These sections need remediation but are included in readiness scoring.",
        }
        guardian_info = None
    elif tier_summary["paired_remediation"]:
        overall = {
            "action_type": "paired_remediation",
            "title": "Boss Fight with Paired Remediation",
            "command": "ssc-study phase3",
            "reason": "All sections scored at least 65%. Sections at 65-69% may enter boss fights alongside continued remediation.",
        }
        guardian_info = None
    else:
        overall = {
            "action_type": "guardian_main_grind",
            "title": "Unlock Phase 4: Main Grind",
            "command": "ssc-study guardian plan",
            "reason": "All sections meet the 70%+ accuracy gate. You are ready to transition to the daily 180-minute study schedule.",
        }
        # Fetch Guardian daily plan details
        try:
            g_plan = build_guardian_plan(db)
            guardian_info = {
                "plan_date": g_plan.plan_date,
                "total_minutes": g_plan.total_minutes,
                "mock_recommendation": g_plan.mock_recommendation,
                "pulse_recommendation": g_plan.pulse_recommendation,
                "warnings": g_plan.warnings,
            }
        except Exception:
            guardian_info = None

    return {
        "session_id": session_id,
        "mode": mode,
        "overall_accuracy": result["accuracy"],
        "weak_sections": weak_sections,
        "overall_action": overall,
        "guardian_plan": guardian_info,
    }
