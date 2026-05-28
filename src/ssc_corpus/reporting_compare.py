from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_phase_comparison(run_manifest: dict[str, dict[str, Any]]) -> dict[str, Any]:
    labels = list(run_manifest.keys())
    run_rows: dict[str, dict[str, Any]] = {}
    for label, config in run_manifest.items():
        run_rows[label] = _load_run_rows(config)

    pdfs = sorted({pdf for rows in run_rows.values() for pdf in rows.keys()})
    rows = []
    for pdf in pdfs:
        row = {"pdf": pdf, "runs": {}}
        for label in labels:
            row["runs"][label] = run_rows[label].get(pdf)
        rows.append(row)
    return {"labels": labels, "rows": rows, "run_manifest": run_manifest}


def write_phase_comparison(report: dict[str, Any], md_path: Path, json_path: Path) -> None:
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Phase Comparison Report",
        "",
        "## Architecture Changes",
        "",
    ]
    for label in report["labels"]:
        config = report["run_manifest"][label]
        lines.append(f"- `{label}`: {config.get('architecture_notes', '')}")
    lines.extend(
        [
            "",
            "## Results Table",
            "",
            "| PDF | Phase | Questions | Expected | QC | Structural | Failure | Provider/Model |",
            "|---|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in report["rows"]:
        for label in report["labels"]:
            run = row["runs"].get(label)
            if not run:
                lines.append(f"| {row['pdf']} | {label} |  |  |  |  |  |  |")
                continue
            lines.append(
                "| {pdf} | {label} | {questions} | {expected} | {qc} | {structural} | {failure} | {notes} |".format(
                    pdf=row["pdf"],
                    label=label,
                    questions=run.get("question_count", ""),
                    expected=run.get("expected_count", ""),
                    qc=run.get("qc_status", ""),
                    structural=run.get("structural_status", ""),
                    failure=run.get("primary_failure_type", ""),
                    notes=str(run.get("provider_model_notes", "")).replace("|", "/"),
                )
            )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_run_rows(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summary_path = Path(str(config["summary_path"]))
    rows = json.loads(summary_path.read_text(encoding="utf-8"))
    structural_by_pdf: dict[str, dict[str, Any]] = {}
    if config.get("structural_path"):
        structural_payload = json.loads(Path(str(config["structural_path"])).read_text(encoding="utf-8"))
        structural_by_pdf = {str(row["pdf"]): row for row in structural_payload.get("rows", [])}

    loaded: dict[str, dict[str, Any]] = {}
    for row in rows:
        pdf = str(row.get("pdf") or row.get("run_id") or Path(str(row.get("source_pdf") or "")).name)
        if not pdf.endswith(".pdf") and row.get("source_pdf"):
            pdf = Path(str(row["source_pdf"])).name
        structural = structural_by_pdf.get(pdf, {})
        loaded[pdf] = {
            "question_count": row.get("question_count", row.get("questions")),
            "expected_count": row.get("expected_questions", row.get("expected_question_count")),
            "qc_status": row.get("qc_status"),
            "structural_status": structural.get("primary_failure_type") and "FAIL"
            or ("PASS" if row.get("qc_passed", row.get("structural_qc")) else "FAIL"),
            "primary_failure_type": structural.get("primary_failure_type", ""),
            "provider_model_notes": _provider_model_notes(row, config.get("default_provider_model_notes", "")),
        }
    return loaded


def _provider_model_notes(row: dict[str, Any], default: str) -> str:
    provider = row.get("primary_provider")
    model = row.get("primary_model")
    if provider or model:
        return f"{provider or ''} / {model or ''}".strip(" /")
    return default
