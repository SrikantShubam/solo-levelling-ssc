from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class OptionRegion:
    label: str
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class QuestionRegion:
    page_number: int
    question_number: int | None
    question_bbox: tuple[float, float, float, float]
    option_regions: tuple[OptionRegion, ...]


@dataclass(frozen=True)
class PageLayout:
    page_number: int
    page_rect: tuple[float, float, float, float]
    question_regions: tuple[QuestionRegion, ...]


_QUESTION_RE = re.compile(r"^Q\.?\s*(\d+)$", re.IGNORECASE)
_OPTION_RE = re.compile(r"^([1-4])\.$")


def inspect_pdf_layout(pdf_path: Path) -> list[PageLayout]:
    """Extract stable spatial anchors from digital/native PDF text."""

    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError("PyMuPDF is required for PDF layout inspection") from exc

    doc = fitz.open(str(pdf_path))
    layouts: list[PageLayout] = []
    for page_index, page in enumerate(doc, start=1):
        words = sorted(page.get_text("words"), key=lambda item: (item[1], item[0]))
        q_markers = _question_markers(words)
        regions: list[QuestionRegion] = []
        for marker_index, marker in enumerate(q_markers):
            next_y = q_markers[marker_index + 1][1] if marker_index + 1 < len(q_markers) else page.rect.y1
            block_words = [word for word in words if marker[1] - 3 <= word[1] < next_y - 2]
            option_regions = _option_regions(block_words, page.rect)
            if option_regions:
                question_bbox = (
                    max(page.rect.x0, 18.0),
                    max(page.rect.y0, marker[1] - 6.0),
                    min(page.rect.x1, page.rect.x1 - 12.0),
                    min(page.rect.y1, next_y - 4.0),
                )
                regions.append(
                    QuestionRegion(
                        page_number=page_index,
                        question_number=marker[2],
                        question_bbox=question_bbox,
                        option_regions=tuple(option_regions),
                    )
                )
        layouts.append(
            PageLayout(
                page_number=page_index,
                page_rect=(page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1),
                question_regions=tuple(regions),
            )
        )
    return layouts


def _question_markers(words: list[tuple[Any, ...]]) -> list[tuple[float, float, int | None]]:
    markers: list[tuple[float, float, int | None]] = []
    for word in words:
        match = _QUESTION_RE.match(str(word[4]).strip())
        if not match:
            continue
        markers.append((float(word[0]), float(word[1]), int(match.group(1))))
    return markers


def _option_regions(words: list[tuple[Any, ...]], page_rect: Any) -> list[OptionRegion]:
    ans_words = [word for word in words if str(word[4]).strip().lower() == "ans"]
    if not ans_words:
        return []
    ans_y = min(float(word[1]) for word in ans_words)
    labels: list[tuple[str, float, float, float, float]] = []
    for word in words:
        match = _OPTION_RE.match(str(word[4]).strip())
        if not match:
            continue
        x0, y0, x1, y1 = map(float, word[:4])
        if y0 <= ans_y or x0 > float(page_rect.x1) * 0.35:
            continue
        labels.append((match.group(1), x0, y0, x1, y1))
    labels = sorted(labels, key=lambda item: int(item[0]))
    if [label[0] for label in labels] != ["1", "2", "3", "4"]:
        return []

    centers = [((label[2] + label[4]) / 2.0) for label in labels]
    regions: list[OptionRegion] = []
    for index, label in enumerate(labels):
        top = centers[index - 1] + (centers[index] - centers[index - 1]) / 2.0 if index else label[2] - 10.0
        bottom = centers[index] + (centers[index + 1] - centers[index]) / 2.0 if index < 3 else label[4] + 14.0
        regions.append(
            OptionRegion(
                label=label[0],
                bbox=(
                    max(float(page_rect.x0), min(45.0, label[1] - 28.0)),
                    max(float(page_rect.y0), top),
                    min(float(page_rect.x1), max(float(page_rect.x1) * 0.62, label[3] + 230.0)),
                    min(float(page_rect.y1), bottom),
                ),
            )
        )
    return regions
