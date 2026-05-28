from __future__ import annotations

import csv
from pathlib import Path

from .schemas import INTEGRITY_HEADERS, MANIFEST_HEADERS, SEED_HEADERS


TEMPLATE_SEED_ROW = {
    "canonical_id": "ssc_cgl_2024_tier1_paper1_na_2024-01-01_question_paper",
    "year": "2024",
    "tier": "tier1",
    "artifact_type": "question_paper",
    "source": "ssc",
    "source_trust_level": "official",
    "official_status": "official",
    "provisional_or_final": "na",
    "license_status": "unknown",
    "access_method": "manual",
    "url": "https://example.com/path/to/file.pdf",
    "paper": "paper1",
    "shift": "na",
    "date": "2024-01-01",
    "notes": "replace with real source",
}


def initialize_workspace(root: Path) -> None:
    for relative in [
        root / "raw_sources" / "primary",
        root / "raw_sources" / "derived_reference",
        root / "manifests",
        root / "reports",
        root / "templates",
    ]:
        relative.mkdir(parents=True, exist_ok=True)

    for year in ["2019", "2020", "2021", "2022", "2023", "2024"]:
        for tier in ["tier1", "tier2_paper1"]:
            for artifact_type in ["question_paper", "answer_key", "solution_booklet"]:
                (root / "raw_sources" / "primary" / year / tier / artifact_type).mkdir(
                    parents=True, exist_ok=True
                )

    _ensure_csv(root / "manifests" / "download_manifest.csv", MANIFEST_HEADERS)
    _ensure_csv(root / "manifests" / "integrity_report.csv", INTEGRITY_HEADERS)
    seed_path = root / "templates" / "acquisition_seed.csv"
    if not seed_path.exists():
        with seed_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=SEED_HEADERS)
            writer.writeheader()
            writer.writerow(TEMPLATE_SEED_ROW)


def _ensure_csv(path: Path, headers: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
