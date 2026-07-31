from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from ssc_study.answer_verification import (
    VERIFIED_EVIDENCE_STATUS,
    VerifiedAnswer,
    extract_green_answer_labels,
    extract_letter_answer_key_labels,
)
from ssc_study.baseline_web import get_baseline_preflight
from ssc_study.db import Database
from ssc_study.models import Question


REPORT_PATH = Path("reports/harvest_answer_verification_recovery_report.json")
CONFLICT_REASON = "correct_option_unresolved_or_conflict"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", type=Path, default=Path("data/study.db"))
    parser.add_argument("--pipeline-root", type=Path, default=Path("pipeline_output/harvest_batch"))
    parser.add_argument("--staging-dir", type=Path, default=Path("answer_key_candidates_staging"))
    parser.add_argument("--harvest-pdf-dir", type=Path, default=Path("data/harvest_pdfs"))
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument("--mode", choices=("recover", "postcheck"), default="recover")
    args = parser.parse_args()

    if args.mode == "recover":
        report = recover(args)
    else:
        report = postcheck(args)

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(_summary_for_stdout(report), indent=2, sort_keys=True))
    return 0


def recover(args: argparse.Namespace) -> dict[str, Any]:
    harvest_paths = sorted(args.pipeline_root.rglob("merged_questions_global_order.json"))
    harvest_pdfs = [path.parent.name for path in harvest_paths]
    if not harvest_paths:
        raise SystemExit(f"No merged_questions_global_order.json files under {args.pipeline_root}")

    answer_cache: dict[str, dict[int, VerifiedAnswer]] = {}
    before = _snapshot(args.db_path, harvest_pdfs)
    _assert_no_harvest_duplicate_ids(harvest_paths)

    conn = _connect(args.db_path)
    try:
        part_a = _recover_imported_rows(conn, harvest_pdfs, args.staging_dir, args.harvest_pdf_dir, answer_cache)
        conn.commit()
    finally:
        conn.close()

    part_b = _recover_json_rows(
        db_path=args.db_path,
        harvest_paths=harvest_paths,
        staging_dir=args.staging_dir,
        harvest_pdf_dir=args.harvest_pdf_dir,
        answer_cache=answer_cache,
    )

    report = {
        "mode": "recover",
        "harvest_pdf_count": len(harvest_pdfs),
        "before": before,
        "part_a": part_a,
        "part_b": part_b,
    }
    return report


def postcheck(args: argparse.Namespace) -> dict[str, Any]:
    prior = {}
    if args.report_path.exists():
        prior = json.loads(args.report_path.read_text(encoding="utf-8"))
    harvest_paths = sorted(args.pipeline_root.rglob("merged_questions_global_order.json"))
    harvest_pdfs = [path.parent.name for path in harvest_paths]
    after = _snapshot(args.db_path, harvest_pdfs)
    before = prior.get("before", {})
    safety = _safety_proof(args.db_path, harvest_paths, before, after)
    prior.update(
        {
            "mode": "postcheck",
            "after": after,
            "safety": safety,
            "newly_imported_count": len(
                set(after["harvest_question_ids"]) - set(before.get("harvest_question_ids", []))
            ),
        }
    )
    return prior


def _snapshot(db_path: Path, harvest_pdfs: list[str]) -> dict[str, Any]:
    conn = _connect(db_path)
    try:
        placeholders = ",".join("?" for _ in harvest_pdfs)
        protected = {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("attempts", "sessions", "sm2_state")
        }
        harvest_ids = [
            str(row["question_id"])
            for row in conn.execute(
                f"SELECT question_id FROM questions WHERE pdf_name IN ({placeholders}) ORDER BY question_id",
                harvest_pdfs,
            )
        ]
        sample_pdf_question_ids = {}
        for pdf_name in harvest_pdfs[:3] + harvest_pdfs[-2:]:
            sample_pdf_question_ids[pdf_name] = [
                str(row["question_id"])
                for row in conn.execute(
                    "SELECT question_id FROM questions WHERE pdf_name = ? ORDER BY global_question_number, question_id",
                    (pdf_name,),
                )
            ]
        return {
            "questions_total": int(conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]),
            "harvest_imported_total": len(harvest_ids),
            "harvest_pass_llm_only": int(
                conn.execute(
                    f"SELECT COUNT(*) FROM questions WHERE pdf_name IN ({placeholders}) AND evidence_status = 'PASS_LLM_ONLY'",
                    harvest_pdfs,
                ).fetchone()[0]
            ),
            "harvest_pass_with_evidence": int(
                conn.execute(
                    f"SELECT COUNT(*) FROM questions WHERE pdf_name IN ({placeholders}) AND evidence_status = ?",
                    (*harvest_pdfs, VERIFIED_EVIDENCE_STATUS),
                ).fetchone()[0]
            ),
            "protected_counts": protected,
            "preflight": get_baseline_preflight(Database(db_path)),
            "harvest_question_ids": harvest_ids,
            "sample_pdf_question_ids": sample_pdf_question_ids,
        }
    finally:
        conn.close()


def _recover_imported_rows(
    conn: sqlite3.Connection,
    harvest_pdfs: list[str],
    staging_dir: Path,
    harvest_pdf_dir: Path,
    answer_cache: dict[str, dict[int, VerifiedAnswer]],
) -> dict[str, Any]:
    placeholders = ",".join("?" for _ in harvest_pdfs)
    rows = conn.execute(
        f"""SELECT q.*, p.passage_text
            FROM questions q
            LEFT JOIN passages p ON p.passage_id = q.passage_id
            WHERE q.pdf_name IN ({placeholders})
              AND q.evidence_status = 'PASS_LLM_ONLY'
            ORDER BY q.pdf_name, q.global_question_number, q.question_id""",
        harvest_pdfs,
    ).fetchall()

    promoted = 0
    corrected = 0
    unresolved = 0
    missing_option_text = 0
    samples: list[dict[str, Any]] = []
    unresolved_by_pdf: Counter[str] = Counter()

    for row in rows:
        question = Question.from_row(row)
        answer = _answer_for_pdf_question(question.pdf_name, question.global_question_number, staging_dir, harvest_pdf_dir, answer_cache)
        if answer is None:
            unresolved += 1
            unresolved_by_pdf[question.pdf_name] += 1
            continue
        option_text = _option_text(question.options, answer.label)
        if option_text is None:
            missing_option_text += 1
            unresolved += 1
            unresolved_by_pdf[question.pdf_name] += 1
            continue
        if answer.text is not None and not _compatible_answer_text(answer.text, option_text):
            unresolved += 1
            unresolved_by_pdf[question.pdf_name] += 1
            continue

        label_changed = answer.label != question.correct_option_label
        before = {
            "question_id": question.question_id,
            "pdf_name": question.pdf_name,
            "global_question_number": question.global_question_number,
            "stored_label": question.correct_option_label,
            "stored_text": question.correct_option_text,
            "stored_status": question.evidence_status,
            "extracted_label": answer.label,
            "extracted_text": answer.text,
            "evidence_source": answer.source,
            "after_text": option_text,
        }
        conn.execute(
            """UPDATE questions
               SET correct_option_label = ?,
                   correct_option_text = ?,
                   evidence_status = ?
               WHERE question_id = ?""",
            (answer.label, option_text, VERIFIED_EVIDENCE_STATUS, question.question_id),
        )
        promoted += 1
        if label_changed:
            corrected += 1
        if len(samples) < 10 or label_changed:
            samples.append(before | {"label_changed": label_changed})

    return {
        "target_count": len(rows),
        "promoted_count": promoted,
        "corrected_count": corrected,
        "unresolved_remaining_count": unresolved,
        "missing_option_text_count": missing_option_text,
        "unresolved_by_pdf": dict(unresolved_by_pdf),
        "samples": samples[:25],
    }


def _recover_json_rows(
    *,
    db_path: Path,
    harvest_paths: list[Path],
    staging_dir: Path,
    harvest_pdf_dir: Path,
    answer_cache: dict[str, dict[int, VerifiedAnswer]],
) -> dict[str, Any]:
    existing_ids = _existing_question_pdf_by_id(db_path)
    resolved = 0
    newly_qualified = 0
    still_excluded_by_reasons: Counter[str] = Counter()
    unresolved = 0
    target_count = 0
    touched_files: list[str] = []
    samples: list[dict[str, Any]] = []

    for path in harvest_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        pdf_name = path.parent.name
        changed = False
        for question in data.get("questions", []):
            reasons = list(question.get("blocking_review_reasons") or [])
            if CONFLICT_REASON not in reasons:
                continue
            target_count += 1
            answer = _answer_for_pdf_question(
                pdf_name,
                int(question.get("global_question_number") or 0),
                staging_dir,
                harvest_pdf_dir,
                answer_cache,
            )
            if answer is None:
                unresolved += 1
                still_excluded_by_reasons[CONFLICT_REASON] += 1
                continue
            option_text = _option_text_from_json(question, answer.label)
            if option_text is None:
                unresolved += 1
                still_excluded_by_reasons["verified_label_missing_from_options"] += 1
                continue
            if answer.text is not None and not _compatible_answer_text(answer.text, option_text):
                unresolved += 1
                still_excluded_by_reasons["verified_option_text_mismatch"] += 1
                continue

            question_id = str(question.get("question_id") or f"{pdf_name}_q{question.get('global_question_number')}")
            existing_pdf = existing_ids.get(question_id)
            if existing_pdf is not None and existing_pdf != pdf_name:
                raise SystemExit(f"Refusing JSON promotion: question_id collision {question_id}: {existing_pdf} vs {pdf_name}")

            before_reasons = reasons
            remaining = [reason for reason in reasons if reason != CONFLICT_REASON]
            question["deterministic_correct_option_label"] = answer.label
            question["correct_evidence_source"] = answer.source
            question["canonical_correct_option_label"] = answer.label
            question["correct_option_label"] = answer.label
            question["correct_option_text"] = option_text
            question["evidence_status"] = VERIFIED_EVIDENCE_STATUS
            question["blocking_review_reasons"] = remaining
            canonical = [reason for reason in list(question.get("canonical_review_reasons") or []) if reason != CONFLICT_REASON]
            question["canonical_review_reasons"] = canonical
            question["practice_ready"] = not remaining and bool(question.get("canonical_correct_option_label"))
            resolved += 1
            if question["practice_ready"]:
                newly_qualified += 1
            else:
                for reason in remaining:
                    still_excluded_by_reasons[str(reason)] += 1
            changed = True
            if len(samples) < 10:
                samples.append(
                    {
                        "question_id": question_id,
                        "pdf_name": pdf_name,
                        "global_question_number": question.get("global_question_number"),
                        "extracted_label": answer.label,
                        "option_text": option_text,
                        "before_reasons": before_reasons,
                        "after_reasons": remaining,
                        "practice_ready": question["practice_ready"],
                    }
                )
        if changed:
            _refresh_json_qc_summary(data)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            touched_files.append(str(path))

    return {
        "target_count": target_count,
        "resolved_count": resolved,
        "newly_qualified_count": newly_qualified,
        "unresolved_count": unresolved,
        "still_excluded_by_reasons": dict(still_excluded_by_reasons),
        "touched_files_count": len(touched_files),
        "touched_files": touched_files,
        "samples": samples,
    }


def _answer_for_pdf_question(
    pdf_name: str,
    global_question_number: int,
    staging_dir: Path,
    harvest_pdf_dir: Path,
    answer_cache: dict[str, dict[int, VerifiedAnswer]],
) -> VerifiedAnswer | None:
    if pdf_name not in answer_cache:
        pdf_path = staging_dir / f"{pdf_name}.pdf"
        if not pdf_path.is_file():
            pdf_path = harvest_pdf_dir / f"{pdf_name}.pdf"
        answers = extract_green_answer_labels(pdf_path)
        answers.update({k: v for k, v in extract_letter_answer_key_labels(pdf_path).items() if k not in answers})
        answer_cache[pdf_name] = answers
    return answer_cache[pdf_name].get(global_question_number)


def _option_text(options: list[Any], label: str) -> str | None:
    for option in options:
        if getattr(option, "label", None) == label:
            return str(getattr(option, "text", ""))
    return None


def _option_text_from_json(question: dict[str, Any], label: str) -> str | None:
    for option in question.get("options") or []:
        if isinstance(option, dict) and str(option.get("label")) == label:
            return str(option.get("text") or "")
    return None


def _compatible_answer_text(extracted_text: str, option_text: str) -> bool:
    extracted = _normalize_answer_text(extracted_text)
    option = _normalize_answer_text(option_text)
    if not extracted or not option:
        return False
    return extracted == option or extracted in option or option in extracted


def _normalize_answer_text(text: str) -> str:
    normalized = (
        str(text or "")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized.strip()).casefold()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _existing_question_pdf_by_id(db_path: Path) -> dict[str, str]:
    conn = _connect(db_path)
    try:
        return {str(row["question_id"]): str(row["pdf_name"]) for row in conn.execute("SELECT question_id, pdf_name FROM questions")}
    finally:
        conn.close()


def _assert_no_harvest_duplicate_ids(harvest_paths: list[Path]) -> None:
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for path in harvest_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        pdf_name = path.parent.name
        for question in data.get("questions", []):
            qid = str(question.get("question_id") or f"{pdf_name}_q{question.get('global_question_number')}")
            previous = seen.setdefault(qid, pdf_name)
            if previous != pdf_name:
                duplicates.append(f"{qid}: {previous} / {pdf_name}")
    if duplicates:
        raise SystemExit("Harvest duplicate question_id collision(s): " + "; ".join(duplicates[:10]))


def _refresh_json_qc_summary(data: dict[str, Any]) -> None:
    questions = data.get("questions") or []
    blocking_count = sum(1 for question in questions if question.get("blocking_review_reasons"))
    review_count = sum(1 for question in questions if question.get("canonical_review_reasons"))
    data["blocking_review_count"] = blocking_count
    data["canonical_review_count"] = review_count
    if not data.get("qc_passed") or blocking_count:
        data["qc_status"] = "BLOCKED" if data.get("qc_passed") else data.get("structural_status", "FAIL")
    elif review_count:
        data["qc_status"] = "PASS_WITH_MANUAL_REVIEW"
    else:
        statuses = {question.get("evidence_status") for question in questions}
        data["qc_status"] = "PASS_LLM_ONLY" if statuses == {"PASS_LLM_ONLY"} else "PASS"


def _safety_proof(
    db_path: Path,
    harvest_paths: list[Path],
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    conn = _connect(db_path)
    try:
        harvest_pdfs = [path.parent.name for path in harvest_paths]
        placeholders = ",".join("?" for _ in harvest_pdfs)
        duplicate_ids = int(
            conn.execute("SELECT COUNT(*) FROM (SELECT question_id FROM questions GROUP BY question_id HAVING COUNT(*) > 1)").fetchone()[0]
        )
        sample_stable = before.get("sample_pdf_question_ids", {}) == after.get("sample_pdf_question_ids", {})
        previous_harvest_ids = set(before.get("harvest_question_ids", []))
        current_harvest_ids = set(after.get("harvest_question_ids", []))
        existing_ids_missing = sorted(previous_harvest_ids - current_harvest_ids)
        non_harvest_collision_count = int(
            conn.execute(
                f"""SELECT COUNT(*) FROM questions
                    WHERE question_id IN (
                        SELECT question_id FROM questions WHERE pdf_name IN ({placeholders})
                    )
                    AND pdf_name NOT IN ({placeholders})""",
                (*harvest_pdfs, *harvest_pdfs),
            ).fetchone()[0]
        )
        protected_unchanged = before.get("protected_counts") == after.get("protected_counts")
        return {
            "duplicate_question_id_count": duplicate_ids,
            "non_harvest_collision_count": non_harvest_collision_count,
            "protected_counts_before": before.get("protected_counts"),
            "protected_counts_after": after.get("protected_counts"),
            "protected_counts_unchanged": protected_unchanged,
            "previous_harvest_ids_missing_count": len(existing_ids_missing),
            "previous_harvest_ids_missing_sample": existing_ids_missing[:10],
            "sample_pdf_question_id_sets_unchanged": sample_stable,
        }
    finally:
        conn.close()


def _summary_for_stdout(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": report.get("mode"),
        "before_questions_total": report.get("before", {}).get("questions_total"),
        "after_questions_total": report.get("after", {}).get("questions_total"),
        "part_a": {
            key: report.get("part_a", {}).get(key)
            for key in ("target_count", "promoted_count", "corrected_count", "unresolved_remaining_count")
        },
        "part_b": {
            key: report.get("part_b", {}).get(key)
            for key in ("target_count", "resolved_count", "newly_qualified_count", "unresolved_count")
        },
        "newly_imported_count": report.get("newly_imported_count"),
        "safety": report.get("safety"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
