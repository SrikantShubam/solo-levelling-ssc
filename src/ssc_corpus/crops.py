from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CropMetadata:
    page_number: int
    question_number: int
    option_label: str | None
    bbox: tuple[float, float, float, float]
    image_width: int
    image_height: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def safe_crop_stem(
    pdf_stem: str,
    *,
    page_number: int,
    question_number: int,
    option_label: str | None = None,
    suffix: str | None = None,
) -> str:
    base = _sanitize(pdf_stem)
    option = f"_opt_{_sanitize(option_label)}" if option_label else ""
    extra = f"_{_sanitize(suffix)}" if suffix else ""
    return f"{base}_p{page_number:02d}_q{question_number:03d}{option}{extra}"


def crop_filename(stem: str, extension: str = ".png") -> str:
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"{stem}{ext}"


def save_pdf_region_crop(
    *,
    page_image_path: Path,
    page_rect: tuple[float, float, float, float],
    bbox: tuple[float, float, float, float],
    output_path: Path,
    page_number: int,
    question_number: int,
    option_label: str | None = None,
    padding_px: int = 2,
) -> CropMetadata:
    """Save a crop by mapping PDF coordinates onto the rendered page image."""

    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(page_image_path) as image:
        image = image.convert("RGB")
        page_width = max(page_rect[2] - page_rect[0], 1.0)
        page_height = max(page_rect[3] - page_rect[1], 1.0)
        scale_x = image.width / page_width
        scale_y = image.height / page_height
        left = int(max(0, round((bbox[0] - page_rect[0]) * scale_x) - padding_px))
        top = int(max(0, round((bbox[1] - page_rect[1]) * scale_y) - padding_px))
        right = int(min(image.width, round((bbox[2] - page_rect[0]) * scale_x) + padding_px))
        bottom = int(min(image.height, round((bbox[3] - page_rect[1]) * scale_y) + padding_px))
        image.crop((left, top, right, bottom)).save(output_path)
        width = right - left
        height = bottom - top
    return CropMetadata(
        page_number=page_number,
        question_number=question_number,
        option_label=option_label,
        bbox=(left, top, right, bottom),
        image_width=width,
        image_height=height,
    )


def _sanitize(value: str | None) -> str:
    if not value:
        return "na"
    cleaned = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in value.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "na"
