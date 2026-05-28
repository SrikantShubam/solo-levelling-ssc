from __future__ import annotations

import csv
import hashlib
import mimetypes
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from .schemas import MANIFEST_HEADERS, ManifestRow, SEED_HEADERS


def acquire_from_seed(root: Path, seed_path: Path) -> int:
    rows = list(_read_seed(seed_path))
    manifest_path = root / "manifests" / "download_manifest.csv"
    existing = _read_manifest_rows(manifest_path)
    written = 0
    failures = 0
    for row in rows:
        destination = _destination_for(root, row)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            metadata = _download(row["url"], destination)
            manifest_row = ManifestRow(
                canonical_id=row["canonical_id"],
                exam="ssc_cgl",
                year=row["year"],
                tier=row["tier"],
                paper=row["paper"],
                shift=row["shift"],
                date=row["date"],
                artifact_type=row["artifact_type"],
                source=row["source"],
                source_trust_level=row["source_trust_level"],
                official_status=row["official_status"],
                provisional_or_final=row["provisional_or_final"],
                license_status=row["license_status"],
                access_method=row["access_method"],
                original_url=row["url"],
                final_url=metadata["final_url"],
                http_status=metadata["http_status"],
                content_type=metadata["content_type"],
                downloaded_at=metadata["downloaded_at"],
                file_size=str(destination.stat().st_size),
                sha256=_sha256(destination),
                notes=row["notes"],
                relative_path=str(destination.relative_to(root)),
            )
            written += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            manifest_row = ManifestRow(
                canonical_id=row["canonical_id"],
                exam="ssc_cgl",
                year=row["year"],
                tier=row["tier"],
                paper=row["paper"],
                shift=row["shift"],
                date=row["date"],
                artifact_type=row["artifact_type"],
                source=row["source"],
                source_trust_level=row["source_trust_level"],
                official_status=row["official_status"],
                provisional_or_final=row["provisional_or_final"],
                license_status=row["license_status"],
                access_method=row["access_method"],
                original_url=row["url"],
                final_url=row["url"],
                http_status="error",
                content_type="unavailable",
                downloaded_at=datetime.now(timezone.utc).isoformat(),
                file_size="0",
                sha256="",
                notes=f"{row['notes']} | download_error={type(exc).__name__}:{exc}",
                classification_status="manual_review",
                classification_reason="download_failed",
                relative_path="",
            )
        existing = [item for item in existing if item["canonical_id"] != manifest_row.canonical_id]
        existing.append(manifest_row.to_dict())
        _write_manifest_rows(manifest_path, existing)
    return 0 if failures == 0 else 1


def _read_seed(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SEED_HEADERS:
            raise ValueError("Seed CSV headers do not match expected schema")
        return list(reader)


def _read_manifest_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_manifest_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def _destination_for(root: Path, row: dict[str, str]) -> Path:
    if row["artifact_type"] == "frequency_analysis":
        base = root / "raw_sources" / "derived_reference" / row["source"] / "frequency_analysis"
    else:
        base = (
            root
            / "raw_sources"
            / "primary"
            / row["year"]
            / row["tier"]
            / row["artifact_type"]
        )
    suffix = _suffix_from_url(row["url"])
    return base / f"{row['canonical_id']}{suffix}"


def _suffix_from_url(url: str) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix
    return suffix if suffix else ".bin"


def _download(url: str, destination: Path) -> dict[str, str]:
    downloaded_at = datetime.now(timezone.utc).isoformat()
    if url.startswith("file://"):
        source = Path(urlparse(url).path.lstrip("/"))
        shutil.copyfile(source, destination)
        content_type = mimetypes.guess_type(destination.name)[0] or "application/octet-stream"
        return {
            "final_url": url,
            "http_status": "200",
            "content_type": content_type,
            "downloaded_at": downloaded_at,
        }
    parsed = urlparse(url)
    verify = False if parsed.hostname == "ssc.nic.in" else True
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        verify=verify,
    )
    response.raise_for_status()
    destination.write_bytes(response.content)
    content_type = response.headers.get("content-type", "application/octet-stream")
    return {
        "final_url": str(response.url),
        "http_status": str(response.status_code),
        "content_type": content_type,
        "downloaded_at": downloaded_at,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
