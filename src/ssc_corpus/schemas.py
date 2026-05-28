from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import ClassVar


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


INTEGRITY_HEADERS = MANIFEST_HEADERS + ["manual_notes", "integrity_notes"]


@dataclass
class ManifestRow:
    canonical_id: str
    exam: str
    year: str
    tier: str
    paper: str
    shift: str
    date: str
    artifact_type: str
    source: str
    source_trust_level: str
    official_status: str
    provisional_or_final: str
    license_status: str
    access_method: str
    original_url: str
    final_url: str
    http_status: str
    content_type: str
    downloaded_at: str
    file_size: str
    sha256: str
    notes: str
    classification_status: str = ""
    classification_reason: str = ""
    relative_path: str = ""

    headers: ClassVar[list[str]] = MANIFEST_HEADERS

    def to_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}
