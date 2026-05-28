import csv
import hashlib
from pathlib import Path

from ssc_corpus.cli import main


SEED_HEADERS = [
    "canonical_id",
    "year",
    "tier",
    "artifact_type",
    "source",
    "source_trust_level",
    "official_status",
    "provisional_or_final",
    "license_status",
    "access_method",
    "url",
    "paper",
    "shift",
    "date",
    "notes",
]


def test_acquire_from_file_url_downloads_and_logs(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    source_pdf = tmp_path / "source.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 acquisition sample")
    seed_path = tmp_path / "templates" / "seed.csv"

    with seed_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEED_HEADERS)
        writer.writeheader()
        writer.writerow(
            {
                "canonical_id": "ssc_cgl_2024_tier1_paper1_na_2024-01-01_question_paper",
                "year": "2024",
                "tier": "tier1",
                "artifact_type": "question_paper",
                "source": "ssc",
                "source_trust_level": "official",
                "official_status": "official",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "automated",
                "url": source_pdf.as_uri(),
                "paper": "paper1",
                "shift": "na",
                "date": "2024-01-01",
                "notes": "",
            }
        )

    exit_code = main(["acquire", "--root", str(tmp_path), "--seed", str(seed_path)])

    assert exit_code == 0
    dest = (
        tmp_path
        / "raw_sources"
        / "primary"
        / "2024"
        / "tier1"
        / "question_paper"
        / "ssc_cgl_2024_tier1_paper1_na_2024-01-01_question_paper.pdf"
    )
    assert dest.exists()

    manifest_rows = list(
        csv.DictReader(
            (tmp_path / "manifests" / "download_manifest.csv").open(
                encoding="utf-8", newline=""
            )
        )
    )
    assert len(manifest_rows) == 1
    assert manifest_rows[0]["sha256"] == hashlib.sha256(dest.read_bytes()).hexdigest()
