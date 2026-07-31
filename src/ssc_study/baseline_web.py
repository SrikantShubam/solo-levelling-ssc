"""Backend service for the Phase 1 local web baseline exam."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import random
import re
import secrets
import sqlite3
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from .corpus_assets import (
    ANSWER_LEAKING_SOURCES as ANSWER_LEAKING_SOURCES,
    MASKED_CROP_DIRNAME,
    is_answer_leaking_source,
)
from .db import Database
from .models import Attempt, Question
from .quiz import (
    FOUNDATION_PULSE_REQUIREMENTS,
    _persist_attempt_with_sm2,
)
from .question_assets import validate_asset_path

SMOKE_REQUIREMENTS: dict[str, int] = {
    "Quant/DI": 2,
    "Reasoning": 1,
    "English": 1,
    "GK/GA": 1,
}
SMOKE_TOTAL = sum(SMOKE_REQUIREMENTS.values())
_WEB_TEXT_MODALITIES = {"", "text_only", "math_formula"}
_MOJIBAKE_MARKERS = (chr(0xFFFD), chr(0x00C3), chr(0x00C2), chr(0x00E2), chr(0x00F0))
_INCOMPLETE_STEM_PREFIXES = (
    "...",
    "pair does not belong",
    "constituent digits.",
    "performing mathematical operations",
)
_UNVERIFIED_EVIDENCE_STATUSES = {"PASS_LLM_ONLY", "BLOCKED"}
_PASSAGE_DEPENDENT_PATTERNS = (
    re.compile(r"\bfill in blank number\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bblank number\s+\d+\b", re.IGNORECASE),
)
_BACKUP_KEEP_LATEST = 20
_CORRECT_MARKS = 2.0
_WRONG_MARKS = -0.5
_APP_SECRET_NAME = "baseline_exam_token_secret"
_EXAM_TOKEN_SECRET_CACHE: dict[str, bytes] = {}
logger = logging.getLogger(__name__)


class BaselineWebError(Exception):
    """Raised when baseline web operations cannot complete."""


def get_baseline_preflight(db: Database) -> dict[str, Any]:
    """Return readiness for full and smoke baseline exams."""
    pool = _build_web_safe_question_pool(db)
    available = {
        section: len(pool["questions_by_section"].get(section, []))
        for section in FOUNDATION_PULSE_REQUIREMENTS
    }

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
        "raw_available": pool["raw_available"],
        "quality_exclusions": dict(pool["quality_exclusions"]),
        "missing": missing,
        "smoke_ready": len(smoke_missing) == 0,
        "smoke_missing": smoke_missing,
    }


def start_baseline_exam(db: Database, mode: str) -> dict[str, Any]:
    """Load questions for a smoke or full baseline exam without answer leakage."""
    if mode == "full":
        questions = _load_web_baseline_questions(db, FOUNDATION_PULSE_REQUIREMENTS, "full baseline")
    elif mode == "smoke":
        questions = _load_web_baseline_questions(db, SMOKE_REQUIREMENTS, "smoke baseline")
    else:
        raise BaselineWebError(f"Invalid mode: {mode}")

    exam_id = str(uuid.uuid4())
    question_ids = [question.question_id for question in questions]

    return {
        "exam_id": exam_id,
        "exam_token": _encode_exam_token(db, exam_id, mode, question_ids),
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

    token_payload = _decode_exam_token(db, exam_token)
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
    if mode == "full":
        _backup_study_db(db)

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
                marked_for_review=bool(answer.get("marked_for_review")),
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
        """SELECT q.section,
                  COUNT(*) as total,
                  SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                  SUM(CASE WHEN a.user_answer IS NULL THEN 1 ELSE 0 END) as skipped
           FROM attempts a
           JOIN questions q ON q.question_id = a.question_id
           WHERE a.session_id = ?
           GROUP BY q.section""",
        (session_id,),
    ).fetchall()

    by_section: dict[str, dict[str, int]] = {}
    for row in rows:
        total = int(row["total"] or 0)
        correct = int(row["correct"] or 0)
        skipped = int(row["skipped"] or 0)
        wrong = total - correct - skipped
        by_section[row["section"]] = {
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "skipped": skipped,
            "accuracy": (correct / total) if total else 0.0,
            "marks_earned": _score_marks(correct, wrong),
            "marks_max": total * _CORRECT_MARKS,
        }
    wrong_count = sum(section["wrong"] for section in by_section.values())
    skipped_count = sum(section["skipped"] for section in by_section.values())

    return {
        "session_id": session_id,
        "mode": mode,
        "question_count": question_count,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "skipped_count": skipped_count,
        "accuracy": accuracy,
        "marks_earned": _score_marks(correct_count, wrong_count),
        "marks_max": question_count * _CORRECT_MARKS,
        "by_section": by_section,
    }


def get_baseline_result(db: Database, session_id: int) -> dict[str, Any]:
    """Return the persisted score summary and next steps for a Phase 1 web session."""
    res = _get_baseline_result_raw(db, session_id)
    res["next_steps"] = get_baseline_next_steps(db, session_id)
    return res


def _load_web_baseline_questions(
    db: Database,
    requirements: dict[str, int],
    label: str,
) -> list[Question]:
    """Load web-renderable baseline questions across the requested section split."""
    pool = _build_web_safe_question_pool(db)
    questions: list[Question] = []
    rng = random.SystemRandom()

    for section, needed in requirements.items():
        candidates = list(pool["questions_by_section"].get(section, []))
        rng.shuffle(candidates)
        if len(candidates) < needed:
            raise BaselineWebError(
                f"{label} requires {needed} web-safe {section} questions, "
                f"but only {len(candidates)} are available after excluding duplicates, "
                "mojibake, invalid options, and visual/table questions with missing assets."
            )
        questions.extend(candidates[:needed])

    return questions


def _build_web_safe_question_pool(db: Database) -> dict[str, Any]:
    conn = db.connect()
    rows = conn.execute(
        """SELECT q.*, p.passage_text
           FROM questions q
           LEFT JOIN passages p ON p.passage_id = q.passage_id
           WHERE q.is_holdout = 0
           ORDER BY q.section, q.question_id"""
    ).fetchall()
    required_sections = set(FOUNDATION_PULSE_REQUIREMENTS)
    raw_available = {section: 0 for section in FOUNDATION_PULSE_REQUIREMENTS}
    questions_by_section: dict[str, list[Question]] = {
        section: [] for section in FOUNDATION_PULSE_REQUIREMENTS
    }
    quality_exclusions: Counter[str] = Counter()
    seen_fingerprints: set[str] = set()

    for row in rows:
        section = str(row["section"])
        if section not in required_sections:
            continue
        raw_available[section] += 1
        question = Question.from_row(row)

        rejection = _web_baseline_rejection_reason(question)
        if rejection:
            quality_exclusions[rejection] += 1
            continue

        fingerprint = _question_fingerprint(question)
        if fingerprint in seen_fingerprints:
            quality_exclusions["duplicate_content"] += 1
            continue
        seen_fingerprints.add(fingerprint)
        questions_by_section[section].append(question)

    return {
        "raw_available": raw_available,
        "questions_by_section": questions_by_section,
        "quality_exclusions": quality_exclusions,
    }


def _web_baseline_rejection_reason(question: Question) -> str | None:
    options = question.options
    labels = {option.label for option in options}
    if (
        len(options) != 4
        or any(not option.text.strip() for option in options)
    ):
        return "invalid_options"

    if str(question.evidence_status or "") in _UNVERIFIED_EVIDENCE_STATUSES:
        return "unverified_answer"

    if _has_answer_integrity_failure(question):
        return "answer_integrity_failure"

    if labels != {"1", "2", "3", "4"}:
        return "invalid_options"

    combined_text = question.question_text + " " + " ".join(option.text for option in options)
    if any(marker in combined_text for marker in _MOJIBAKE_MARKERS):
        return "mojibake"

    if _looks_like_incomplete_stem(question.question_text):
        return "incomplete_stem"

    if _looks_passage_dependent(question.question_text) and not _has_linked_passage(question):
        return "passage_dependent"

    if _has_unmaskable_answer_leak(question):
        return "unmaskable_answer_leak"

    if _has_drifted_asset_path(question):
        return "missing_asset"

    if _question_needs_visual_asset(question) and not _question_has_visual_asset(question):
        return "missing_visual_asset"

    if not _question_fingerprint(question):
        return "blank_content"
    return None


def _looks_like_incomplete_stem(text: str) -> bool:
    normalized = text.strip().casefold()
    return any(normalized.startswith(prefix) for prefix in _INCOMPLETE_STEM_PREFIXES)


def _looks_passage_dependent(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip())
    if re.search(r"\bin the following passage\b", normalized, re.IGNORECASE) and len(normalized.split()) >= 30:
        return False
    return any(pattern.search(normalized) for pattern in _PASSAGE_DEPENDENT_PATTERNS)


def _has_linked_passage(question: Question) -> bool:
    return question.passage_id is not None and bool(str(question.passage_text or "").strip())


def _has_answer_integrity_failure(question: Question) -> bool:
    option_by_label = {option.label: option.text for option in question.options}
    option_text = option_by_label.get(question.correct_option_label)
    if option_text is None:
        return True
    if question.correct_option_text is None:
        return False
    return _normalize_answer_text(option_text) != _normalize_answer_text(question.correct_option_text)


def _normalize_answer_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip()).casefold()


def _has_drifted_asset_path(question: Question) -> bool:
    return (
        (bool(question.question_crop_path) and validate_asset_path(question.question_crop_path) is None)
        or (bool(question.page_asset_path) and validate_asset_path(question.page_asset_path) is None)
    )


def _has_unmaskable_answer_leak(question: Question) -> bool:
    if not is_answer_leaking_source(question.pdf_name):
        return False
    crop_path = question.question_crop_path
    if not crop_path:
        return _question_needs_visual_asset(question)
    validated_crop = validate_asset_path(crop_path)
    if validated_crop is None:
        return True
    return MASKED_CROP_DIRNAME not in {part for part in str(crop_path).replace("\\", "/").split("/")}


def _question_needs_visual_asset(question: Question) -> bool:
    return (
        question.visual_required
        or question.table_required
        or question.question_modality not in _WEB_TEXT_MODALITIES
    )


def _question_has_visual_asset(question: Question) -> bool:
    return (
        validate_asset_path(question.question_crop_path) is not None
        or validate_asset_path(question.page_asset_path) is not None
    )


def _question_asset_urls(question: Question) -> dict[str, str]:
    urls: dict[str, str] = {}
    if validate_asset_path(question.question_crop_path) is not None:
        urls["crop"] = f"/api/question-assets/{question.question_id}/crop"
    if (
        not is_answer_leaking_source(question.pdf_name)
        and validate_asset_path(question.page_asset_path) is not None
    ):
        urls["page"] = f"/api/question-assets/{question.question_id}/page"
    return urls


def _question_fingerprint(question: Question) -> str:
    text = question.question_text + " " + " ".join(option.text for option in question.options)
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.casefold())).strip()


def _question_to_client(question: Question, index: int) -> dict[str, Any]:
    payload = {
        "question_id": question.question_id,
        "index": index,
        "section": question.section,
        "tier": question.tier,
        "question_modality": question.question_modality,
        "visual_required": question.visual_required,
        "table_required": question.table_required,
        "asset_urls": _question_asset_urls(question),
        "question_text": question.question_text,
        "options": [{"label": option.label, "text": option.text} for option in question.options],
    }
    if _has_linked_passage(question):
        payload["passage_text"] = str(question.passage_text)
    return payload


def _idempotency_note(mode: str, exam_id: str) -> str:
    prefix = "phase1_web_full" if mode == "full" else "phase1_web_smoke"
    return f"{prefix}:{exam_id}"


def _encode_exam_token(db: Database, exam_id: str, mode: str, question_ids: list[str]) -> str:
    payload = {
        "exam_id": exam_id,
        "mode": mode,
        "question_ids": question_ids,
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii").rstrip("=")
    signature = hmac.new(_get_exam_token_secret(db), body.encode("ascii"), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{body}.{sig}"


def _decode_exam_token(db: Database, token: str) -> dict[str, Any]:
    try:
        body, sig = token.split(".", 1)
    except ValueError as exc:
        raise BaselineWebError("Invalid exam_token") from exc

    expected = hmac.new(_get_exam_token_secret(db), body.encode("ascii"), hashlib.sha256).digest()
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


def _get_exam_token_secret(db: Database) -> bytes:
    conn = db.connect()
    if str(db.path) == ":memory:":
        cache_key = f"memory:{id(conn)}"
    else:
        cache_key = str(db.path.resolve(strict=False))
    cached = _EXAM_TOKEN_SECRET_CACHE.get(cache_key)
    if cached is not None:
        return cached

    row = conn.execute(
        "SELECT secret_value FROM _app_secrets WHERE secret_name = ?",
        (_APP_SECRET_NAME,),
    ).fetchone()
    if row is None:
        secret = secrets.token_bytes(32)
        encoded = base64.b64encode(secret).decode("ascii")
        conn.execute(
            "INSERT INTO _app_secrets (secret_name, secret_value) VALUES (?, ?)",
            (_APP_SECRET_NAME, encoded),
        )
        conn.commit()
    else:
        secret = base64.b64decode(str(row["secret_value"]))

    _EXAM_TOKEN_SECRET_CACHE[cache_key] = secret
    return secret


def _backup_study_db(db: Database) -> None:
    source_path = db.path
    backups_dir = source_path.parent / "backups"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backups_dir / f"study-{timestamp}.db"
    try:
        backups_dir.mkdir(parents=True, exist_ok=True)
        source_conn = db.connect()
        with sqlite3.connect(str(backup_path)) as backup_conn:
            source_conn.backup(backup_conn)
            backup_conn.commit()
        _prune_old_backups(backups_dir)
    except Exception as exc:
        logger.warning("Failed to create pre-submit study DB backup at %s: %s", backup_path, exc)


def _prune_old_backups(backups_dir: Path) -> None:
    backups = sorted(backups_dir.glob("study-*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    for old_path in backups[_BACKUP_KEEP_LATEST:]:
        try:
            old_path.unlink()
        except OSError as exc:
            logger.warning("Failed to delete old study DB backup %s: %s", old_path, exc)


def _score_marks(correct_count: int, wrong_count: int) -> float:
    return (correct_count * _CORRECT_MARKS) + (wrong_count * _WRONG_MARKS)


def _load_questions_for_submit(
    conn: Any,
    question_ids: list[str],
) -> dict[str, Question]:
    placeholders = ",".join("?" for _ in question_ids)
    rows = conn.execute(
        f"""SELECT q.*, p.passage_text
            FROM questions q
            LEFT JOIN passages p ON p.passage_id = q.passage_id
            WHERE q.question_id IN ({placeholders})""",
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
