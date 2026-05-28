import csv
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


def test_acquire_continues_and_writes_manifest_on_partial_failure(tmp_path: Path) -> None:
    main(["init", "--root", str(tmp_path)])
    good_pdf = tmp_path / "good.pdf"
    good_pdf.write_bytes(b"%PDF-1.4 good")
    seed_path = tmp_path / "templates" / "mixed_seed.csv"
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
                "url": good_pdf.as_uri(),
                "paper": "paper1",
                "shift": "na",
                "date": "2024-01-01",
                "notes": "",
            }
        )
        writer.writerow(
            {
                "canonical_id": "ssc_cgl_2024_tier2_paper1_na_2024-01-01_question_paper",
                "year": "2024",
                "tier": "tier2_paper1",
                "artifact_type": "question_paper",
                "source": "ssc",
                "source_trust_level": "official",
                "official_status": "official",
                "provisional_or_final": "na",
                "license_status": "unknown",
                "access_method": "automated",
                "url": "https://example.invalid/not-found.pdf",
                "paper": "paper1",
                "shift": "na",
                "date": "2024-01-01",
                "notes": "",
            }
        )

    exit_code = main(["acquire", "--root", str(tmp_path), "--seed", str(seed_path)])

    assert exit_code == 1
    rows = list(
        csv.DictReader(
            (tmp_path / "manifests" / "download_manifest.csv").open(
                encoding="utf-8", newline=""
            )
        )
    )
    assert len(rows) == 2
    assert rows[0]["http_status"] == "200"
    assert rows[1]["classification_status"] == "manual_review"
