from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .extraction import (
    DEFAULT_MODEL,
    ExtractionResult,
    extract_pdf_with_gemini,
    extract_pdf_with_openai_compatible_vision,
)


def retry_failed_extractions(
    *,
    batch_summary_path: Path,
    output_root: Path,
    primary_provider: str,
    primary_model: str,
    primary_endpoint: str | None,
    primary_api_key: str,
    force: bool = True,
    investigation_path: Path | None = None,
    page_delay_seconds: float = 0.0,
) -> dict[str, Any]:
    batch_rows = json.loads(batch_summary_path.read_text(encoding="utf-8"))
    action_by_pdf = _investigation_actions(investigation_path) if investigation_path else {}
    output_root.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, Any]] = []

    for row in batch_rows:
        pdf_name = str(row.get("pdf") or "")
        if not _should_retry(row, action_by_pdf.get(pdf_name)):
            continue
        source_pdf = Path(str(row.get("source_pdf") or ""))
        if not source_pdf.is_absolute():
            source_pdf = (batch_summary_path.parent.parent.parent / source_pdf).resolve()
        out_dir = output_root / source_pdf.stem
        expected_questions = row.get("expected_questions")
        try:
            result = _run_retry(
                source_pdf=source_pdf,
                out_dir=out_dir,
                expected_questions=expected_questions,
                primary_provider=primary_provider,
                primary_model=primary_model,
                primary_endpoint=primary_endpoint,
                primary_api_key=primary_api_key,
                force=force,
                page_delay_seconds=page_delay_seconds,
            )
            summary_rows.append(
                {
                    "pdf": pdf_name,
                    "source_pdf": str(source_pdf),
                    "expected_questions": expected_questions,
                    "question_count": result.question_count,
                    "qc_passed": result.qc_passed,
                    "qc_status": result.qc_status,
                    "output_dir": str(out_dir),
                    "primary_provider": primary_provider,
                    "primary_model": primary_model,
                    "error": None,
                }
            )
        except Exception as exc:
            summary_rows.append(
                {
                    "pdf": pdf_name,
                    "source_pdf": str(source_pdf),
                    "expected_questions": expected_questions,
                    "question_count": None,
                    "qc_passed": False,
                    "qc_status": "ERROR",
                    "output_dir": str(out_dir),
                    "primary_provider": primary_provider,
                    "primary_model": primary_model,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    report = {
        "source_batch_summary": str(batch_summary_path),
        "primary_provider": primary_provider,
        "primary_model": primary_model,
        "rows": summary_rows,
    }
    (output_root / "batch_summary.json").write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "batch_summary.md").write_text(_batch_summary_markdown(report), encoding="utf-8")
    return report


def _run_retry(
    *,
    source_pdf: Path,
    out_dir: Path,
    expected_questions: int | None,
    primary_provider: str,
    primary_model: str,
    primary_endpoint: str | None,
    primary_api_key: str,
    force: bool,
    page_delay_seconds: float = 0.0,
) -> ExtractionResult:
    if primary_provider == "gemini":
        return extract_pdf_with_gemini(
            pdf_path=source_pdf,
            output_dir=out_dir,
            api_key=primary_api_key,
            expected_questions=expected_questions,
            model_name=primary_model or DEFAULT_MODEL,
            force=force,
        )
    page_delay = page_delay_seconds if "openrouter" in str(primary_provider).lower() else 0.0
    return extract_pdf_with_openai_compatible_vision(
        pdf_path=source_pdf,
        output_dir=out_dir,
        provider=primary_provider,
        model_name=primary_model,
        endpoint=str(primary_endpoint),
        api_key=primary_api_key,
        expected_questions=expected_questions,
        force=force,
        page_delay_seconds=page_delay,
    )


def _should_retry(row: dict[str, Any], recommended_action: str | None) -> bool:
    if recommended_action == "quarantine":
        return False
    if recommended_action in {"rerun_needed", "fallback_needed"}:
        return True
    return str(row.get("qc_status") or "") in {"FAIL", "ERROR"}


def _investigation_actions(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(row["pdf"]): str(row["recommended_action"]) for row in payload.get("rows", [])}


def _batch_summary_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Retry Batch Summary",
        "",
        f"- Source batch summary: `{report['source_batch_summary']}`",
        f"- Primary provider: `{report['primary_provider']}`",
        f"- Primary model: `{report['primary_model']}`",
        "",
        "| PDF | Expected | Extracted | QC | Error |",
        "|---|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {pdf} | {expected} | {count} | {qc} | {error} |".format(
                pdf=row["pdf"],
                expected=row["expected_questions"] if row["expected_questions"] is not None else "",
                count=row["question_count"] if row["question_count"] is not None else "",
                qc=row["qc_status"],
                error=(row["error"] or "").replace("|", "/"),
            )
        )
    return "\n".join(lines) + "\n"
