"""Modality repair and deterministic per-question recropping utilities."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssc_corpus.crops import crop_filename, safe_crop_stem, save_pdf_region_crop
from ssc_corpus.extraction import render_pdf_pages
from ssc_study.corpus_assets import mask_answer_leaking_crop


TARGET_RECROP_SOURCES = (
    "2020_tier2_kdcampus_answer_key",
    "2024_tier1_appx_answer_key",
)

_TEXT_ONLY_SECTIONS = {"English", "GK/GA", "Computer Knowledge"}
_NUMBER_ANCHOR_RE = re.compile(r"^\s*(\d{1,3})\.")


@dataclass(frozen=True)
class ModalityRecropStats:
    modality_corrections: dict[tuple[str, str], int]
    recropped_masked_by_source: dict[str, int]
    still_excluded_by_source: dict[str, int]
    exclusion_reasons: dict[str, int]
    excluded_question_ids: tuple[str, ...]


def question_number_anchor_from_text(text: str) -> int | None:
    match = _NUMBER_ANCHOR_RE.match(text or "")
    return int(match.group(1)) if match else None


def classify_question_for_web_modality(
    *, section: str, question_text: str, option_texts: list[str]
) -> str:
    if section in _TEXT_ONLY_SECTIONS:
        combined = f"{question_text} {' '.join(option_texts)}".casefold()
        if any(token in combined for token in ("bar graph", "line graph", "pie chart", "venn diagram")):
            return "graph_chart"
        if re.search(r"\b(table|tabular data)\b", combined) and section != "English":
            return "table_di"
        return "text_only"

    from ssc_corpus.extraction_qc import classify_modality

    return classify_modality(question_text, option_texts).label


def masked_crop_preserves_question_content(raw_crop_path: str | Path, masked_crop_path: str | Path) -> bool:
    from PIL import Image

    with Image.open(raw_crop_path) as raw, Image.open(masked_crop_path) as masked:
        return masked.height >= 80 and masked.height >= int(raw.height * 0.75)


def repair_modalities_and_recrop(
    conn: Any,
    *,
    repo_root: str | Path | None = None,
    staging_dir: str | Path = "answer_key_candidates_staging",
) -> ModalityRecropStats:
    root = Path(repo_root or Path.cwd()).resolve()
    modality_corrections = _repair_modalities(conn)
    recropped, excluded, reasons, excluded_ids = _recrop_target_sources(
        conn,
        root=root,
        staging_dir=root / staging_dir,
    )
    conn.commit()
    return ModalityRecropStats(
        modality_corrections=dict(modality_corrections),
        recropped_masked_by_source=dict(recropped),
        still_excluded_by_source=dict(excluded),
        exclusion_reasons=dict(reasons),
        excluded_question_ids=tuple(excluded_ids),
    )


def _repair_modalities(conn: Any) -> Counter[tuple[str, str]]:
    rows = conn.execute(
        """SELECT question_id, section, question_text, options_json, question_modality
           FROM questions
           ORDER BY question_id"""
    ).fetchall()
    corrections: Counter[tuple[str, str]] = Counter()
    for row in rows:
        option_texts = _option_texts(row["options_json"])
        new_modality = classify_question_for_web_modality(
            section=str(row["section"] or ""),
            question_text=str(row["question_text"] or ""),
            option_texts=option_texts,
        )
        old_modality = str(row["question_modality"] or "text_only")
        if new_modality == old_modality:
            continue
        conn.execute(
            """UPDATE questions
               SET question_modality = ?,
                   visual_required = ?,
                   table_required = ?,
                   math_required = ?
               WHERE question_id = ?""",
            (
                new_modality,
                1 if new_modality in {"visual_stimulus", "visual_options", "graph_chart", "dice"} else 0,
                1 if new_modality in {"table_di", "graph_chart"} else 0,
                1 if new_modality == "math_formula" else 0,
                row["question_id"],
            ),
        )
        corrections[(old_modality, new_modality)] += 1
    return corrections


def _recrop_target_sources(
    conn: Any,
    *,
    root: Path,
    staging_dir: Path,
) -> tuple[Counter[str], Counter[str], Counter[str], list[str]]:
    recropped: Counter[str] = Counter()
    excluded: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    excluded_ids: list[str] = []
    for source in TARGET_RECROP_SOURCES:
        pdf_path = staging_dir / f"{source}.pdf"
        if not pdf_path.is_file():
            count = _target_count(conn, source)
            excluded[source] += count
            reasons["source_pdf_missing"] += count
            continue
        regions = _numbered_regions_by_page(pdf_path)
        page_images = render_pdf_pages(pdf_path, root / "pipeline_output" / "p2_gemini" / source / "page_images")
        page_image_by_number = {index: path for index, path in enumerate(page_images, start=1)}
        rows = conn.execute(
            """SELECT question_id, source_page, global_question_number, question_text
               FROM questions
               WHERE pdf_name = ?
               ORDER BY global_question_number""",
            (source,),
        ).fetchall()
        for row in rows:
            page = int(row["source_page"] or 0)
            anchor = question_number_anchor_from_text(str(row["question_text"] or ""))
            target_number = anchor or int(row["global_question_number"] or 0)
            region = regions.get(page, {}).get(target_number)
            page_image = page_image_by_number.get(page)
            if region is None or page_image is None:
                _mark_recrop_excluded(conn, row["question_id"])
                excluded[source] += 1
                reasons["numbered_boundary_not_found"] += 1
                excluded_ids.append(str(row["question_id"]))
                continue
            crop_path = (
                root
                / "pipeline_output"
                / "p2_gemini"
                / source
                / "assets"
                / "question_crops"
                / crop_filename(
                    safe_crop_stem(
                        source,
                        page_number=page,
                        question_number=int(row["global_question_number"] or 0),
                        suffix="question",
                    )
                )
            )
            save_pdf_region_crop(
                page_image_path=page_image,
                page_rect=region["page_rect"],
                bbox=region["bbox"],
                output_path=crop_path,
                page_number=page,
                question_number=int(row["global_question_number"] or 0),
                padding_px=4,
            )
            masked = mask_answer_leaking_crop(crop_path)
            if masked.masked_path is None:
                _mark_recrop_excluded(conn, row["question_id"])
                excluded[source] += 1
                reasons[masked.reason or "mask_failed"] += 1
                excluded_ids.append(str(row["question_id"]))
                continue
            if not masked_crop_preserves_question_content(crop_path, masked.masked_path):
                _mark_recrop_excluded(conn, row["question_id"])
                excluded[source] += 1
                reasons["masked_crop_too_small"] += 1
                excluded_ids.append(str(row["question_id"]))
                continue
            conn.execute(
                """UPDATE questions
                   SET question_crop_path = ?, page_asset_path = ?
                   WHERE question_id = ?""",
                (str(masked.masked_path), str(page_image), row["question_id"]),
            )
            recropped[source] += 1
    return recropped, excluded, reasons, excluded_ids


def _numbered_regions_by_page(pdf_path: Path) -> dict[int, dict[int, dict[str, Any]]]:
    import fitz

    doc = fitz.open(str(pdf_path))
    try:
        result: dict[int, dict[int, dict[str, Any]]] = {}
        for page_index, page in enumerate(doc, start=1):
            words = page.get_text("words")
            markers = []
            for word in words:
                text = str(word[4]).strip()
                if not re.match(r"^\d{1,3}\.$", text):
                    continue
                x0, y0, x1, y1 = map(float, word[:4])
                if x0 > float(page.rect.x1) - 80:
                    continue
                markers.append((int(text[:-1]), x0, y0, x1, y1))
            markers.sort(key=lambda item: (item[1] > float(page.rect.x1) / 2.0, item[2], item[1]))
            header_ys = [
                float(word[1])
                for word in words
                if str(word[4]).strip().casefold().rstrip(":") in {"comprehension", "instructions"}
            ]
            by_number: dict[int, dict[str, Any]] = {}
            for index, marker in enumerate(markers):
                number, x0, y0, _x1, _y1 = marker
                same_column_next = [
                    other for other in markers
                    if other[0] != number and _same_column(x0, other[1], page.rect.x1) and other[2] > y0
                ]
                next_marker_y = min((other[2] for other in same_column_next), default=float(page.rect.y1) - 18.0)
                next_header_y = min((y for y in header_ys if y > y0 + 10.0), default=float(page.rect.y1) - 18.0)
                bottom = min(next_marker_y, next_header_y) - 4.0
                if bottom <= y0 + 18.0:
                    continue
                if float(page.rect.x1) > 700:
                    left, right = 18.0, float(page.rect.x1) - 18.0
                elif x0 > float(page.rect.x1) / 2.0:
                    left, right = float(page.rect.x1) / 2.0, float(page.rect.x1) - 18.0
                else:
                    left = 18.0
                    right = float(page.rect.x1) / 2.0 if any(m[1] > float(page.rect.x1) / 2.0 for m in markers) else float(page.rect.x1) - 18.0
                bbox = (left, max(float(page.rect.y0), y0 - 5.0), right, min(float(page.rect.y1), bottom))
                if not _region_has_four_option_labels(words, bbox):
                    continue
                by_number[number] = {
                    "page_rect": (float(page.rect.x0), float(page.rect.y0), float(page.rect.x1), float(page.rect.y1)),
                    "bbox": bbox,
                }
            result[page_index] = by_number
        return result
    finally:
        doc.close()


def _same_column(left_a: float, left_b: float, page_width: float) -> bool:
    if page_width > 700:
        return True
    return (left_a > page_width / 2.0) == (left_b > page_width / 2.0)


def _region_has_four_option_labels(words: list[Any], bbox: tuple[float, float, float, float]) -> bool:
    left, top, right, bottom = bbox
    labels: set[str] = set()
    for word in words:
        x0, y0, x1, y1 = map(float, word[:4])
        if x0 < left or x1 > right or y0 < top or y1 > bottom:
            continue
        text = str(word[4]).strip()
        match = re.match(r"^([A-D])\.$", text, re.IGNORECASE) or re.match(r"^\(([1-4])\)$", text)
        if match:
            labels.add(match.group(1).upper())
    return labels >= {"A", "B", "C", "D"} or labels >= {"1", "2", "3", "4"}


def _option_texts(raw: Any) -> list[str]:
    import json

    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [str(item.get("text") or "") for item in data if isinstance(item, dict)]


def _mark_recrop_excluded(conn: Any, question_id: str) -> None:
    conn.execute(
        """UPDATE questions
           SET question_crop_path = NULL
           WHERE question_id = ?""",
        (question_id,),
    )


def _target_count(conn: Any, source: str) -> int:
    row = conn.execute("SELECT COUNT(*) FROM questions WHERE pdf_name = ?", (source,)).fetchone()
    return int(row[0])
