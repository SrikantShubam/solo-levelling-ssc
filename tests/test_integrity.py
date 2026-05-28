import csv
from pathlib import Path

from ssc_corpus.cli import main


MANIFEST_HEADERS = [
    "canonical_id",
    "exam",
    "year",
    "tier",
    "paper",
    "shift",
    "date",
    "artifact_type",
    "source",
    "source_trust_level",
    "official_status",
    "provisional_or_final",
    "license_status",
    "access_method",
    "original_url",
    "final_url",
    "http_status",
    "content_type",
    "downloaded_at",
    "file_size",
    "sha256",
    "notes",
    "classification_status",
    "classification_reason",
    "relative_path",
]


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def test_audit_flags_missing_pairing_and_generates_reports(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    manifest_path = tmp_path / "manifests" / "download_manifest.csv"
    question_path = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2019"
        / "tier1"
        / "question_paper"
        / "2019_tier1_official_question_paper.pdf"
    )
    question_path.write_bytes(b"%PDF-1.4 sample")
    _write_manifest(
        manifest_path,
        [
            {
                "canonical_id": "ssc_cgl_2019_tier1_paper1_na_2019-01-01_question_paper",
                "exam": "ssc_cgl",
                "year": "2019",
                "tier": "tier1",
                "paper": "paper1",
                "shift": "na",
                "date": "2019-01-01",
                "artifact_type": "question_paper",
                "source": "ssc",
                "source_trust_level": "official",
                "official_status": "official",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://ssc.example/question.pdf",
                "final_url": "https://ssc.example/question.pdf",
                "http_status": "200",
                "content_type": "application/pdf",
                "downloaded_at": "2026-05-17T12:00:00Z",
                "file_size": str(question_path.stat().st_size),
                "sha256": "abc",
                "notes": "",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(question_path.relative_to(tmp_path)),
            }
        ],
    )

    exit_code = main(["audit", "--root", str(tmp_path)])

    assert exit_code == 2
    integrity_report = (tmp_path / "manifests" / "integrity_report.csv").read_text(
        encoding="utf-8"
    )
    dossier = (tmp_path / "reports" / "corpus_dossier.md").read_text(encoding="utf-8")

    assert "missing_pairing" in integrity_report
    assert "NO_GO" in dossier
    assert "2019" in dossier


def test_audit_allows_same_pdf_for_question_and_solution_same_identity(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    manifest_path = tmp_path / "manifests" / "download_manifest.csv"
    question_path = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier2_paper1"
        / "question_paper"
        / "sample.pdf"
    )
    solution_path = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier2_paper1"
        / "solution_booklet"
        / "sample.pdf"
    )
    question_path.parent.mkdir(parents=True, exist_ok=True)
    solution_path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"%PDF-1.4 solved paper"
    question_path.write_bytes(payload)
    solution_path.write_bytes(payload)
    shared = {
        "exam": "ssc_cgl",
        "year": "2024",
        "tier": "tier2_paper1",
        "paper": "paper1",
        "shift": "1",
        "date": "2025-01-18",
        "source": "oliveboard",
        "source_trust_level": "trusted_secondary",
        "official_status": "unofficial",
        "provisional_or_final": "na",
        "license_status": "unknown",
        "access_method": "manual",
        "original_url": "https://example.com/paper.pdf",
        "final_url": "https://example.com/paper.pdf",
        "http_status": "200",
        "content_type": "application/pdf",
        "downloaded_at": "2026-05-18T12:00:00Z",
        "file_size": str(len(payload)),
        "sha256": "samehash",
        "notes": "Inline answers",
        "classification_status": "",
        "classification_reason": "",
    }
    _write_manifest(
        manifest_path,
        [
            {
                "canonical_id": "ssc_cgl_2024_tier2_paper1_1_2025-01-18_question_paper",
                "artifact_type": "question_paper",
                "relative_path": str(question_path.relative_to(tmp_path)),
                **shared,
            },
            {
                "canonical_id": "ssc_cgl_2024_tier2_paper1_1_2025-01-18_solution_booklet",
                "artifact_type": "solution_booklet",
                "relative_path": str(solution_path.relative_to(tmp_path)),
                **shared,
            },
        ],
    )

    exit_code = main(["audit", "--root", str(tmp_path)])

    assert exit_code == 1
    integrity_report = (tmp_path / "manifests" / "integrity_report.csv").read_text(
        encoding="utf-8"
    )
    assert "duplicate_watermarked" not in integrity_report


def test_derived_reference_only_rows_do_not_force_no_go(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    manifest_path = tmp_path / "manifests" / "download_manifest.csv"
    qpath = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier1"
        / "question_paper"
        / "q.pdf"
    )
    spath = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier1"
        / "solution_booklet"
        / "s.pdf"
    )
    dpath = (
        tmp_path
        / "raw_sources"
        / "derived_reference"
        / "oliveboard"
        / "frequency_analysis"
        / "f.bin"
    )
    qpath.parent.mkdir(parents=True, exist_ok=True)
    spath.parent.mkdir(parents=True, exist_ok=True)
    dpath.parent.mkdir(parents=True, exist_ok=True)
    qpath.write_bytes(b"%PDF")
    spath.write_bytes(b"%PDF")
    dpath.write_bytes(b"<html></html>")
    _write_manifest(
        manifest_path,
        [
            {
                "canonical_id": "ssc_cgl_2024_tier1_paper1_1_2024-09-10_question_paper",
                "exam": "ssc_cgl",
                "year": "2024",
                "tier": "tier1",
                "paper": "paper1",
                "shift": "1",
                "date": "2024-09-10",
                "artifact_type": "question_paper",
                "source": "oliveboard",
                "source_trust_level": "trusted_secondary",
                "official_status": "unofficial",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://example.com/q.pdf",
                "final_url": "https://example.com/q.pdf",
                "http_status": "200",
                "content_type": "application/pdf",
                "downloaded_at": "2026-05-18T12:00:00Z",
                "file_size": "4",
                "sha256": "qhash",
                "notes": "",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(qpath.relative_to(tmp_path)),
            },
            {
                "canonical_id": "ssc_cgl_2024_tier1_paper1_1_2024-09-10_solution_booklet",
                "exam": "ssc_cgl",
                "year": "2024",
                "tier": "tier1",
                "paper": "paper1",
                "shift": "1",
                "date": "2024-09-10",
                "artifact_type": "solution_booklet",
                "source": "oliveboard",
                "source_trust_level": "trusted_secondary",
                "official_status": "unofficial",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://example.com/s.pdf",
                "final_url": "https://example.com/s.pdf",
                "http_status": "200",
                "content_type": "application/pdf",
                "downloaded_at": "2026-05-18T12:00:00Z",
                "file_size": "4",
                "sha256": "shash",
                "notes": "",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(spath.relative_to(tmp_path)),
            },
            {
                "canonical_id": "ssc_cgl_multi_multi_na_na_na_frequency_analysis_oliveboard_quant",
                "exam": "ssc_cgl",
                "year": "multi",
                "tier": "multi",
                "paper": "na",
                "shift": "na",
                "date": "na",
                "artifact_type": "frequency_analysis",
                "source": "oliveboard",
                "source_trust_level": "derived_reference",
                "official_status": "derived",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://example.com/freq",
                "final_url": "https://example.com/freq",
                "http_status": "200",
                "content_type": "text/html",
                "downloaded_at": "2026-05-18T12:00:00Z",
                "file_size": "13",
                "sha256": "fhash",
                "notes": "",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(dpath.relative_to(tmp_path)),
            },
        ],
    )

    exit_code = main(["audit", "--root", str(tmp_path)])

    assert exit_code == 1


def test_answer_key_notice_does_not_count_as_usable_answer_key(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    manifest_path = tmp_path / "manifests" / "download_manifest.csv"
    answer_key_path = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier1"
        / "answer_key"
        / "notice.pdf"
    )
    answer_key_path.parent.mkdir(parents=True, exist_ok=True)
    answer_key_path.write_bytes(b"%PDF notice")
    _write_manifest(
        manifest_path,
        [
            {
                "canonical_id": "ssc_cgl_2024_tier1_paper1_na_na_answer_key",
                "exam": "ssc_cgl",
                "year": "2024",
                "tier": "tier1",
                "paper": "paper1",
                "shift": "na",
                "date": "na",
                "artifact_type": "answer_key",
                "source": "ssc",
                "source_trust_level": "official",
                "official_status": "official",
                "provisional_or_final": "final",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://ssc.example/notice.pdf",
                "final_url": "https://ssc.example/notice.pdf",
                "http_status": "200",
                "content_type": "application/pdf",
                "downloaded_at": "2026-05-19T12:00:00Z",
                "file_size": str(answer_key_path.stat().st_size),
                "sha256": "noticehash",
                "notes": "Uploading of Final Answer Key(s) notice; login required.",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(answer_key_path.relative_to(tmp_path)),
            }
        ],
    )

    exit_code = main(["audit", "--root", str(tmp_path)])

    assert exit_code == 2
    integrity_report = (tmp_path / "manifests" / "integrity_report.csv").read_text(
        encoding="utf-8"
    )
    dossier = (tmp_path / "reports" / "corpus_dossier.md").read_text(encoding="utf-8")
    assert "answer_key_notice_only" in integrity_report
    assert "| 2024 | tier1 | 0 | 0 | 0 | 0 |" in dossier


def test_embedded_answer_question_paper_satisfies_pairing(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    manifest_path = tmp_path / "manifests" / "download_manifest.csv"
    question_path = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier1"
        / "question_paper"
        / "embedded.pdf"
    )
    question_path.parent.mkdir(parents=True, exist_ok=True)
    question_path.write_bytes(b"%PDF embedded answers")
    _write_manifest(
        manifest_path,
        [
            {
                "canonical_id": "ssc_cgl_2024_tier1_paper1_1_2024-09-10_question_paper",
                "exam": "ssc_cgl",
                "year": "2024",
                "tier": "tier1",
                "paper": "paper1",
                "shift": "1",
                "date": "2024-09-10",
                "artifact_type": "question_paper",
                "source": "prepp",
                "source_trust_level": "trusted_secondary",
                "official_status": "unofficial",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "manual",
                "original_url": "https://example.com/embedded.pdf",
                "final_url": "https://example.com/embedded.pdf",
                "http_status": "200",
                "content_type": "application/pdf",
                "downloaded_at": "2026-05-19T12:00:00Z",
                "file_size": str(question_path.stat().st_size),
                "sha256": "embeddedhash",
                "notes": "user_verified_embedded_answers; all questions rendered correctly; correct answers are in green color",
                "classification_status": "",
                "classification_reason": "",
                "relative_path": str(question_path.relative_to(tmp_path)),
            }
        ],
    )

    exit_code = main(["audit", "--root", str(tmp_path)])

    assert exit_code == 1
    integrity_report = (tmp_path / "manifests" / "integrity_report.csv").read_text(
        encoding="utf-8"
    )
    dossier = (tmp_path / "reports" / "corpus_dossier.md").read_text(encoding="utf-8")
    assert "missing_pairing" not in integrity_report
    assert "| 2024 | tier1 | 1 | 0 | 0 | 1 |" in dossier
