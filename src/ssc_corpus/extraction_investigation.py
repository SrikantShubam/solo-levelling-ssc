from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .extraction import _classify_failure_type


def build_extraction_investigation(batch_summary_path: Path) -> dict[str, Any]:
    batch_rows = json.loads(batch_summary_path.read_text(encoding="utf-8"))
    rows = [_investigate_batch_row(row) for row in batch_rows]
    summary = Counter(row["recommended_action"] for row in rows)
    summary.update({f"failure:{row['primary_failure_type']}": 1 for row in rows if row["primary_failure_type"]})
    return {
        "source_batch_summary": str(batch_summary_path),
        "pdf_count": len(rows),
        "summary": dict(summary),
        "rows": rows,
    }


def write_extraction_investigation_report(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# P2 Extraction Failure Investigation",
        "",
        f"- Source batch summary: `{report['source_batch_summary']}`",
        f"- PDFs inspected: {report['pdf_count']}",
        "",
        "## Action Summary",
        "",
        "| Bucket | Count |",
        "|---|---:|",
    ]
    for key, value in sorted(report["summary"].items()):
        if key.startswith("failure:"):
            continue
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## PDF Matrix",
            "",
            "| PDF | Class | Expected | Extracted | QC | Failure | Error pages | Action |",
            "|---|---|---:|---:|---|---|---:|---|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| {pdf} | {document_class} | {expected_questions} | {question_count} | {qc_status} | {failure} | {error_pages} | {action} |".format(
                pdf=row["pdf"],
                document_class=row["document_class"],
                expected_questions=row["expected_questions"] if row["expected_questions"] is not None else "",
                question_count=row["question_count"] if row["question_count"] is not None else "",
                qc_status=row["qc_status"],
                failure=row["primary_failure_type"] or "",
                error_pages=row["error_page_count"],
                action=row["recommended_action"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _investigate_batch_row(row: dict[str, Any]) -> dict[str, Any]:
    output_dir = Path(row.get("output_dir") or "")
    page_payloads = _load_page_payloads(output_dir / "page_json")
    page_failures = [_page_failure(page) for page in page_payloads]
    failure_counts = Counter(failure for failure in page_failures if failure)
    primary_failure_type = _primary_failure_type(row, failure_counts)
    expected = row.get("expected_questions")
    question_count = row.get("question_count")
    document_class = infer_document_class(str(row.get("pdf") or ""), page_payloads)
    recommended_action = _recommended_action(
        document_class=document_class,
        primary_failure_type=primary_failure_type,
        expected_questions=expected,
        question_count=question_count,
        qc_status=str(row.get("qc_status") or ""),
    )
    return {
        "pdf": row.get("pdf"),
        "output_dir": row.get("output_dir"),
        "document_class": document_class,
        "expected_questions": expected,
        "question_count": question_count,
        "qc_status": row.get("qc_status"),
        "primary_failure_type": primary_failure_type,
        "error_page_count": sum(1 for failure in page_failures if failure),
        "failure_counts": dict(failure_counts),
        "recommended_action": recommended_action,
        "raw_error": row.get("error"),
    }


def infer_document_class(pdf_name: str, page_payloads: list[dict[str, Any]] | None = None) -> str:
    lowered = pdf_name.lower()
    if "appx" in lowered or "notice" in lowered or "notification" in lowered:
        return "answer_key_notice_or_non_question"
    if "sscportal" in lowered or "response_sheet" in lowered or "response" in lowered:
        return "response_sheet_green_answer"
    if "tier2" in lowered and ("english" in lowered or "quant" in lowered or "paper1" in lowered):
        return "tier2_section_booklet"
    if "prepp" in lowered or "kdcampus" in lowered:
        return "coaching_pdf_with_answers"
    return "unknown"


def _load_page_payloads(page_json_dir: Path) -> list[dict[str, Any]]:
    if not page_json_dir.is_dir():
        return []
    payloads: list[dict[str, Any]] = []
    for path in sorted(page_json_dir.glob("page_*.json")):
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            payloads.append(
                {
                    "page": path.stem,
                    "questions": [],
                    "warnings": [f"ERROR JSONDecodeError: failed to read {path.name}"],
                }
            )
    return payloads


def _page_failure(page_payload: dict[str, Any]) -> str | None:
    explicit = page_payload.get("failure_type")
    if explicit:
        return str(explicit)
    warnings = "\n".join(str(item) for item in page_payload.get("warnings") or [])
    return _classify_failure_type(warnings)


def _primary_failure_type(row: dict[str, Any], failure_counts: Counter[str]) -> str | None:
    if failure_counts:
        return failure_counts.most_common(1)[0][0]
    raw_error = row.get("error")
    if raw_error:
        return _classify_failure_type(str(raw_error)) or "layout_class_unsupported"
    return None


def _recommended_action(
    *,
    document_class: str,
    primary_failure_type: str | None,
    expected_questions: int | None,
    question_count: int | None,
    qc_status: str,
) -> str:
    if document_class == "answer_key_notice_or_non_question":
        return "quarantine"
    if primary_failure_type == "api_quota_or_rate_limit":
        return "rerun_needed"
    if primary_failure_type in {"model_refusal", "json_or_schema_failure"}:
        return "fallback_needed"
    if expected_questions is not None and question_count == expected_questions:
        return "usable_with_review" if qc_status in {"BLOCKED", "PASS_WITH_MANUAL_REVIEW"} else "usable"
    if expected_questions is None and question_count and question_count > 0 and not primary_failure_type:
        return "usable_with_review" if qc_status in {"BLOCKED", "PASS_WITH_MANUAL_REVIEW"} else "usable"
    if question_count == 0:
        return "quarantine"
    return "fallback_needed"
