"""Corpus asset remapping and masking helpers for web-safe baseline delivery."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

ANSWER_LEAKING_SOURCES = {
    "2016_tier1_prepp_2016-08-30_shift3",
    "2016_tier1_prepp_2016-09-01_shift2",
    "2016_tier1_prepp_2016-09-11_shift1",
    "2016_tier1_testbook_compilation",
    "2017_tier1_prepp_2017-08-10_shift1",
    "2017_tier1_prepp_2017-08-12_shift1",
    "2017_tier1_testbook_compilation",
    "2018_tier1_prepp_2019-06-07_shift1",
    "2018_tier1_testbook_compilation",
    "2019_tier1_prepp_2020-03-06_shift1",
    "2019_tier1_prepp_2020-03-07",
    "2019_tier2_prepp_2020-11-15_quant_shift1",
    "2020_tier2_kdcampus_answer_key",
    "2020_tier2_prepp_2022-01-29_quant",
    "2020_tier2_prepp_2022-02-03_english",
    "2020_tier2_prepp_2022-02-03_english_akey",
    "2021_tier1_prepp_2022-04-11_shift1_en",
    "2021_tier1_prepp_2022-04-11_shift3",
    "2021_tier1_sscportal_shift1_response_sheet",
    "2022_tier1_prepp_2022-12-01_shift1",
    "2022_tier1_prepp_2022-12-02_shift1",
    "2022_tier1_prepp_2022-12-02_shift2",
    "2022_tier1_prepp_2022-12-02_shift3",
    "2022_tier1_prepp_2022-12-02_shift4",
    "2022_tier1_prepp_2022-12-06_shift1",
    "2022_tier1_prepp_2022-12-06_shift3",
    "2022_tier1_prepp_2022-12-07_shift1",
    "2022_tier1_prepp_2022-12-08_shift1",
    "2022_tier1_prepp_2022-12-08_shift4",
    "2022_tier1_prepp_2022-12-12_shift4",
    "2022_tier1_prepp_2022-12-13_shift1",
    "2022_tier1_prepp_2022-12-13_shift3",
    "2023_tier1_prepp_2023-07-14_shift1",
    "2023_tier1_prepp_2023-07-14_shift4",
    "2023_tier1_prepp_2023-07-17_shift1",
    "2023_tier1_prepp_2023-07-17_shift3",
    "2023_tier1_prepp_2023-07-17_shift4",
    "2023_tier1_prepp_2023-07-18_shift1",
    "2023_tier1_prepp_2023-07-18_shift2",
    "2023_tier1_prepp_2023-07-18_shift4",
    "2023_tier1_prepp_2023-07-19_shift1",
    "2023_tier1_prepp_2023-07-19_shift3",
    "2023_tier1_prepp_2023-07-19_shift4",
    "2023_tier1_prepp_2023-07-21_shift1",
    "2023_tier1_prepp_2023-07-21_shift1_alt",
    "2023_tier1_prepp_2023-07-21_shift3",
    "2023_tier1_prepp_2023-07-21_shift4",
    "2023_tier1_prepp_2023-07-24_shift3",
    "2023_tier1_prepp_2023-07-24_shift4",
    "2023_tier1_prepp_2023-07-25_shift1",
    "2023_tier1_prepp_2023-07-25_shift4",
    "2023_tier1_prepp_2023-07-26_shift1",
    "2023_tier1_prepp_2023-07-26_shift4",
    "2023_tier1_prepp_2023-07-27_shift1",
    "2023_tier1_prepp_2023-07-27_shift2",
    "2023_tier2_prepp_2023-10-26_shift1",
    "2024_tier1_appx_answer_key",
    "2024_tier1_prepp_2024-09-09_shift1",
    "2024_tier1_prepp_2024-09-09_shift2",
    "2024_tier1_prepp_2024-09-10_shift1",
    "2024_tier1_prepp_2024-09-10_shift3",
    "2024_tier1_prepp_2024-09-11_shift2",
    "2024_tier1_prepp_2024-09-24_shift1",
    "2024_tier1_prepp_2024-09-25_shift3",
    "2024_tier1_prepp_2024-09-26_shift2",
    "2024_tier1_sscportal_sep09_shift1_response_sheet",
    "2024_tier2_prepp_2025-01-18_paper1",
    "2024_tier2_prepp_2025-01-20_paper1",
    "2024_tier2_sscportal_jan18_response_sheet",
    "2024_tier2_sscportal_jan19_response_sheet",
    "2024_tier2_sscportal_jan20_response_sheet",
}

MASKED_CROP_DIRNAME = "question_crops_masked"
_MIN_MASK_HEIGHT = 40


@dataclass(frozen=True)
class MaskResult:
    masked_path: Path | None
    cut_y: int | None
    reason: str | None = None


@dataclass(frozen=True)
class RemapStats:
    rows_seen: int
    rows_remapped: int
    missing_asset_rows: int
    masked_rows: int
    unmaskable_answer_leak_rows: int
    unmaskable_question_ids: tuple[str, ...]


def is_answer_leaking_source(pdf_name: str | None) -> bool:
    return str(pdf_name or "") in ANSWER_LEAKING_SOURCES


def masked_crop_path_for(crop_path: str | Path) -> Path:
    path = Path(crop_path)
    return path.parent.parent / MASKED_CROP_DIRNAME / path.name


def mask_answer_leaking_crop(source: str | Path, output: str | Path | None = None) -> MaskResult:
    """Crop a response-sheet question image above the answer annotation row."""
    source_path = Path(source)
    output_path = Path(output) if output is not None else masked_crop_path_for(source_path)
    try:
        with Image.open(source_path) as image:
            rgb = image.convert("RGB")
            cut_y = _find_answer_marker_y(rgb)
            if cut_y is None or cut_y < _MIN_MASK_HEIGHT:
                return MaskResult(None, None, "answer_marker_not_found")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            rgb.crop((0, 0, rgb.width, cut_y)).save(output_path)
            return MaskResult(output_path, cut_y)
    except (OSError, UnidentifiedImageError):
        return MaskResult(None, None, "image_unreadable")


def remap_question_assets(conn: Any, *, repo_root: str | Path | None = None) -> RemapStats:
    """Rewrite stale DB asset paths to verified current local files."""
    root = Path(repo_root or Path.cwd()).resolve()
    rows = conn.execute(
        """SELECT question_id, pdf_name, question_crop_path, page_asset_path
           FROM questions
           ORDER BY question_id"""
    ).fetchall()

    rows_remapped = 0
    missing_asset_rows = 0
    masked_rows = 0
    unmaskable: list[str] = []
    resolved_crop_counts: dict[Path, int] = {}
    for row in rows:
        crop = _resolve_current_asset(root, row["pdf_name"], row["question_crop_path"])
        if crop is not None:
            resolved_crop_counts[crop] = resolved_crop_counts.get(crop, 0) + 1

    for row in rows:
        crop = _resolve_current_asset(root, row["pdf_name"], row["question_crop_path"])
        page = _resolve_current_asset(root, row["pdf_name"], row["page_asset_path"])
        if crop is not None and is_answer_leaking_source(row["pdf_name"]):
            if _is_shared_or_whole_page_crop(crop, resolved_crop_counts):
                unmaskable.append(str(row["question_id"]))
                crop = None
            else:
                result = mask_answer_leaking_crop(crop)
                if result.masked_path is None:
                    unmaskable.append(str(row["question_id"]))
                    crop = None
                else:
                    crop = result.masked_path
                    masked_rows += 1

        old_crop = row["question_crop_path"]
        old_page = row["page_asset_path"]
        new_crop = str(crop) if crop is not None else None
        new_page = str(page) if page is not None else None
        if old_crop != new_crop or old_page != new_page:
            conn.execute(
                """UPDATE questions
                   SET question_crop_path = ?, page_asset_path = ?
                   WHERE question_id = ?""",
                (new_crop, new_page, row["question_id"]),
            )
            rows_remapped += 1
        if (old_crop or old_page) and crop is None and page is None:
            missing_asset_rows += 1

    conn.commit()
    return RemapStats(
        rows_seen=len(rows),
        rows_remapped=rows_remapped,
        missing_asset_rows=missing_asset_rows,
        masked_rows=masked_rows,
        unmaskable_answer_leak_rows=len(unmaskable),
        unmaskable_question_ids=tuple(unmaskable),
    )


def _is_shared_or_whole_page_crop(crop_path: Path, resolved_crop_counts: dict[Path, int]) -> bool:
    return resolved_crop_counts.get(crop_path, 0) > 1 or crop_path.parent.name == "page_images"


def _resolve_current_asset(root: Path, pdf_name: str, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    raw = Path(str(raw_path))
    if raw.is_file() and MASKED_CROP_DIRNAME not in raw.parts:
        return raw.resolve()

    suffixes = _asset_suffixes(pdf_name, raw)
    if not suffixes:
        return None
    for base in (root / "pipeline_output" / "p2_gemini", root / "deprecated"):
        for suffix in suffixes:
            candidate = _find_existing_asset(base, pdf_name, suffix)
            if candidate is not None:
                return candidate
    return None


def _asset_suffixes(pdf_name: str, raw_path: Path) -> tuple[Path, ...]:
    parts = raw_path.parts
    if pdf_name in parts:
        index = parts.index(pdf_name)
        suffix = Path(*parts[index + 1 :])
    elif raw_path.name:
        suffix = Path(raw_path.name)
    else:
        return ()

    suffixes = [suffix]
    if MASKED_CROP_DIRNAME in suffix.parts:
        masked_parts = list(suffix.parts)
        masked_index = masked_parts.index(MASKED_CROP_DIRNAME)
        question_parts = list(masked_parts)
        question_parts[masked_index] = "question_crops"
        suffixes.insert(0, Path(*question_parts))
        page_suffix = Path(*masked_parts[:masked_index], "page_images", suffix.name)
        suffixes.insert(0, page_suffix)
    return tuple(dict.fromkeys(suffixes))


@lru_cache(maxsize=None)
def _find_existing_asset(base: Path, pdf_name: str, suffix: Path) -> Path | None:
    direct = base / pdf_name / suffix
    if direct.is_file():
        return direct.resolve()
    if not base.exists():
        return None
    for pdf_dir in base.rglob(pdf_name):
        candidate = pdf_dir / suffix
        if candidate.is_file():
            return candidate.resolve()
    return None


def _find_answer_marker_y(image: Image.Image) -> int | None:
    width, height = image.size
    pixels = image.load()
    best_y: int | None = None
    best_score = 0
    for y in range(0, height):
        red_green_pixels = 0
        dark_left_pixels = 0
        for x in range(0, min(width, 320)):
            r, g, b = pixels[x, y]
            if (r > 170 and g < 110 and b < 110) or (g > 130 and r < 140 and b < 140):
                red_green_pixels += 1
            if 80 <= x <= 160 and r < 80 and g < 80 and b < 80:
                dark_left_pixels += 1
        score = red_green_pixels + dark_left_pixels
        if score > best_score:
            best_score = score
            best_y = y

    if best_y is None or best_score < 3:
        return None
    return max(_MIN_MASK_HEIGHT, best_y - 8)
