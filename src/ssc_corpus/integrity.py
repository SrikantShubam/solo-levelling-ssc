from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .schemas import INTEGRITY_HEADERS, MANIFEST_HEADERS


TARGET_YEARS = ["2019", "2020", "2021", "2022", "2023", "2024"]
TARGET_TIERS = ["tier1", "tier2_paper1"]
PAIR_TYPES = {"answer_key", "solution_booklet"}


@dataclass
class AuditResult:
    status: str
    report_rows: list[dict[str, str]]
    dossier_text: str


def audit_workspace(root: Path) -> AuditResult:
    manifest_rows = _read_manifest(root / "manifests" / "download_manifest.csv")
    report_rows: list[dict[str, str]] = []
    pair_index = defaultdict(list)
    duplicate_hashes = defaultdict(list)
    accepted_rows = []
    low_trust = []
    anomalies = []

    for row in manifest_rows:
        if row["artifact_type"] in PAIR_TYPES:
            pair_index[(row["year"], row["tier"], row["paper"], row["shift"], row["date"])].append(
                row
            )
        duplicate_hashes[row["sha256"]].append(row)

    for row in manifest_rows:
        status = "accepted"
        reason = ""
        notes = []
        rel_path = row.get("relative_path", "")
        file_path = root / rel_path if rel_path else None

        if row["source_trust_level"] != "official":
            low_trust.append(row["canonical_id"])
        if row["artifact_type"] == "frequency_analysis":
            status = "rejected"
            reason = "derived_reference_only"
        elif file_path is None or not file_path.exists() or file_path.stat().st_size == 0:
            status = "quarantined"
            reason = "corrupt_pdf"
        elif row["artifact_type"] == "answer_key" and _is_answer_key_notice_only(row):
            status = "manual_review"
            reason = "answer_key_notice_only"
        elif row["artifact_type"] == "question_paper":
            pair_key = (row["year"], row["tier"], row["paper"], row["shift"], row["date"])
            if not pair_index[pair_key] and not _has_embedded_answers(row):
                status = "manual_review"
                reason = "missing_pairing"
        if _is_cross_identity_duplicate(row, duplicate_hashes):
            status = "duplicate"
            reason = reason or "duplicate_watermarked"
        if status != "accepted":
            anomalies.append((row["canonical_id"], reason or "manual_review"))
        else:
            accepted_rows.append(row["canonical_id"])
        report_row = dict(row)
        report_row["classification_status"] = status
        report_row["classification_reason"] = reason
        report_row["manual_notes"] = row.get("manual_notes", "")
        report_row["integrity_notes"] = "; ".join(notes)
        report_rows.append(report_row)

    status = _recommendation(report_rows)
    coverage = _accepted_coverage(report_rows)
    dossier = _build_dossier(coverage, report_rows, accepted_rows, low_trust, anomalies, status)
    _write_integrity_report(root / "manifests" / "integrity_report.csv", report_rows)
    (root / "reports" / "corpus_dossier.md").write_text(dossier, encoding="utf-8")
    return AuditResult(status=status, report_rows=report_rows, dossier_text=dossier)


def _is_cross_identity_duplicate(
    row: dict[str, str], duplicate_hashes: dict[str, list[dict[str, str]]]
) -> bool:
    sha = row["sha256"]
    if not sha:
        return False
    siblings = duplicate_hashes[sha]
    if len(siblings) <= 1:
        return False
    identities = {
        (item["year"], item["tier"], item["paper"], item["shift"], item["date"])
        for item in siblings
    }
    return len(identities) > 1


def _is_answer_key_notice_only(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("notes", ""),
            row.get("manual_notes", ""),
            row.get("canonical_id", ""),
        ]
    ).lower()
    if "actual_answer_key_verified" in text:
        return False
    notice_markers = [
        "notice",
        "uploading of final answer key",
        "uploaded the final answer key",
        "candidates may check",
        "registered id and password",
        "login",
        "response sheet",
    ]
    return any(marker in text for marker in notice_markers)


def _has_embedded_answers(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("notes", ""),
            row.get("manual_notes", ""),
            row.get("classification_reason", ""),
        ]
    ).lower()
    positive_markers = [
        "user_verified_embedded_answers",
        "embedded_answers_verified",
        "embedded answer",
        "correct answers are in green",
        "correct answer in green",
        "green color",
        "green colour",
    ]
    negative_markers = [
        "question only",
        "no answer",
        "without answer",
        "lacks an answer key",
        "do_not_use_as_answer_key",
    ]
    return any(marker in text for marker in positive_markers) and not any(
        marker in text for marker in negative_markers
    )


def _accepted_coverage(rows: list[dict[str, str]]) -> Counter:
    coverage = Counter()
    for row in rows:
        if row["classification_status"] == "accepted":
            coverage[(row["year"], row["tier"], row["artifact_type"])] += 1
            if row["artifact_type"] == "question_paper" and _has_embedded_answers(row):
                coverage[(row["year"], row["tier"], "embedded_answers")] += 1
    return coverage


def _read_manifest(path: Path) -> list[dict[str, str]]:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with path.open("r", newline="", encoding=encoding) as handle:
                reader = csv.reader(handle)
                raw_headers = next(reader)
                headers = _normalize_manifest_headers(raw_headers)
                return [dict(zip(headers, row)) for row in reader]
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []


def _normalize_manifest_headers(headers: list[str]) -> list[str]:
    normalized = []
    seen = Counter()
    for header in headers:
        clean = header.strip()
        seen[clean] += 1
        if clean == "notes" and seen[clean] == 2:
            normalized.append("manual_notes")
        elif clean.lower() == "z":
            normalized.append("manual_notes")
        else:
            normalized.append(clean)
    required = normalized[: len(MANIFEST_HEADERS)]
    if required != MANIFEST_HEADERS:
        raise ValueError("Manifest headers do not match expected schema")
    if "manual_notes" not in normalized:
        normalized.append("manual_notes")
    return normalized


def _write_integrity_report(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=INTEGRITY_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def _recommendation(rows: list[dict[str, str]]) -> str:
    coverage = _accepted_coverage(rows)
    accepted_question_rows = [
        row
        for row in rows
        if row["classification_status"] == "accepted" and row["artifact_type"] == "question_paper"
    ]
    if not accepted_question_rows:
        return "NO_GO"
    for row in accepted_question_rows:
        key = (row["year"], row["tier"])
        pair_count = (
            coverage[(key[0], key[1], "answer_key")]
            + coverage[(key[0], key[1], "solution_booklet")]
            + coverage[(key[0], key[1], "embedded_answers")]
        )
        if pair_count == 0:
            return "NO_GO"

    blocking_rows = [
        row
        for row in rows
        if not _is_nonblocking_anomaly(row)
    ]
    statuses = {row["classification_status"] for row in blocking_rows}
    if "quarantined" in statuses or "manual_review" in statuses or "rejected" in statuses:
        return "NO_GO"
    if any(row["source_trust_level"] != "official" for row in blocking_rows):
        return "GO_WITH_EXCEPTIONS"
    return "GO"


def _is_nonblocking_anomaly(row: dict[str, str]) -> bool:
    return (
        row["artifact_type"] == "frequency_analysis"
        and row["classification_reason"] == "derived_reference_only"
    ) or (
        row["artifact_type"] == "answer_key"
        and row["classification_reason"] == "answer_key_notice_only"
    )


def _build_dossier(
    coverage: Counter,
    rows: list[dict[str, str]],
    accepted_rows: list[str],
    low_trust: list[str],
    anomalies: list[tuple[str, str]],
    status: str,
) -> str:
    lines = [
        "# Corpus Dossier",
        "",
        f"Recommendation: **{status}**",
        "",
        "## Accepted Coverage Table",
        "",
        "| Year | Tier | Question Papers | Answer Keys | Solution Booklets | Embedded Answers |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for year in TARGET_YEARS:
        for tier in TARGET_TIERS:
            lines.append(
                "| {year} | {tier} | {q} | {a} | {s} | {e} |".format(
                    year=year,
                    tier=tier,
                    q=coverage[(year, tier, "question_paper")],
                    a=coverage[(year, tier, "answer_key")],
                    s=coverage[(year, tier, "solution_booklet")],
                    e=coverage[(year, tier, "embedded_answers")],
                )
            )
    counts = Counter(row["classification_status"] for row in rows)
    lines.extend(
        [
            "",
            "## Status Counts",
            "",
            f"- accepted: {counts['accepted']}",
            f"- duplicate: {counts['duplicate']}",
            f"- quarantined: {counts['quarantined']}",
            f"- rejected: {counts['rejected']}",
            f"- manual_review: {counts['manual_review']}",
            "",
            "## Low-Trust Artifacts",
            "",
        ]
    )
    if low_trust:
        lines.extend([f"- {item}" for item in sorted(low_trust)])
    else:
        lines.append("- none")
    lines.extend(["", "## Anomalies", ""])
    if anomalies:
        lines.extend([f"- {cid}: {reason}" for cid, reason in anomalies])
    else:
        lines.append("- none")
    lines.extend(["", "## Accepted Artifact Count", "", f"- {len(accepted_rows)}"])
    return "\n".join(lines) + "\n"
