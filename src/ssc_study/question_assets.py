"""Safe resolution of question visual assets for the local web UI."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any

from .corpus_assets import is_answer_leaking_source

ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ASSET_ROOTS_ENV = "SSC_QUESTION_ASSET_ROOTS"


def validate_asset_path(raw_path: str | None) -> Path | None:
    """Validate a DB-backed image path."""
    if not raw_path:
        return None

    path = Path(str(raw_path))
    if not path.is_absolute():
        path = Path.cwd() / path

    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return None

    if resolved.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
        return None
    if not resolved.is_file():
        return None
    if not _is_under_allowed_root(resolved):
        return None
    return resolved


def _allowed_asset_roots() -> list[Path]:
    raw_roots = [str(Path.cwd())]
    extra_roots = os.environ.get(ASSET_ROOTS_ENV)
    if extra_roots:
        raw_roots.extend(root for root in extra_roots.split(os.pathsep) if root)

    roots: list[Path] = []
    for raw_root in raw_roots:
        try:
            roots.append(Path(raw_root).resolve(strict=False))
        except OSError:
            continue
    return roots


def _is_under_allowed_root(path: Path) -> bool:
    for root in _allowed_asset_roots():
        try:
            path.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def resolve_question_asset(conn: Any, question_id: str, kind: str) -> Path | None:
    """Return a validated local asset path for a question and asset kind."""
    if kind not in {"crop", "page"}:
        return None

    column = "question_crop_path" if kind == "crop" else "page_asset_path"
    row = conn.execute(
        f"SELECT pdf_name, {column} AS asset_path FROM questions WHERE question_id = ?",
        (question_id,),
    ).fetchone()
    if row is None:
        return None
    if kind == "page" and is_answer_leaking_source(str(row["pdf_name"] or "")):
        return None
    return validate_asset_path(row["asset_path"])


def media_type_for_asset(path: Path) -> str:
    """Return a safe image media type for a validated asset path."""
    guessed = mimetypes.guess_type(str(path))[0]
    if guessed in {"image/png", "image/jpeg", "image/webp"}:
        return guessed
    if path.suffix.lower() == ".png":
        return "image/png"
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if path.suffix.lower() == ".webp":
        return "image/webp"
    return "application/octet-stream"
