from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - exercised via fallback tests
    cv2 = None


@dataclass(frozen=True)
class MarkDetectionResult:
    label: str
    source: str
    confidence: float
    green_fraction: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_green_from_rgb(
    image_rgb: Any,
    *,
    min_green_fraction: float = 0.01,
    hue_range: tuple[int, int] = (35, 90),
    min_saturation: int = 40,
    min_value: int = 40,
) -> MarkDetectionResult:
    arr = _to_numpy_rgb(image_rgb)
    if arr.size == 0:
        return MarkDetectionResult("no_green_mark", "rgb_hsv", 1.0, 0.0)

    if cv2 is not None:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
        mask = (
            (hsv[:, :, 0] >= hue_range[0])
            & (hsv[:, :, 0] <= hue_range[1])
            & (hsv[:, :, 1] >= min_saturation)
            & (hsv[:, :, 2] >= min_value)
        )
    else:
        hsv = _rgb_to_hsv_numpy(arr)
        hue_min = hue_range[0] / 179.0
        hue_max = hue_range[1] / 179.0
        sat_min = min_saturation / 255.0
        val_min = min_value / 255.0
        mask = (
            (hsv[:, :, 0] >= hue_min)
            & (hsv[:, :, 0] <= hue_max)
            & (hsv[:, :, 1] >= sat_min)
            & (hsv[:, :, 2] >= val_min)
        )

    green_fraction = float(mask.mean())
    if green_fraction >= min_green_fraction:
        confidence = min(1.0, 0.5 + (green_fraction / max(min_green_fraction, 1e-6)) * 0.1)
        return MarkDetectionResult("green_mark_present", "rgb_hsv", confidence, green_fraction)
    return MarkDetectionResult("no_green_mark", "rgb_hsv", 1.0 - min(0.8, green_fraction), green_fraction)


def detect_green_from_drawings(drawings: list[dict[str, Any]] | None) -> MarkDetectionResult:
    if not drawings:
        return MarkDetectionResult("no_green_mark", "vector_drawings", 0.7, 0.0)

    checked = 0
    green_hits = 0
    for drawing in drawings:
        for key in ("color", "fill", "fill_color", "stroke"):
            color = drawing.get(key)
            if color is None:
                continue
            checked += 1
            if _is_greenish_color(color):
                green_hits += 1

    if checked == 0:
        return MarkDetectionResult("no_green_mark", "vector_drawings", 0.65, 0.0)

    ratio = green_hits / checked
    if green_hits > 0:
        return MarkDetectionResult("green_mark_present", "vector_drawings", min(1.0, 0.75 + ratio * 0.25), ratio)
    return MarkDetectionResult("no_green_mark", "vector_drawings", max(0.55, 1.0 - ratio), ratio)


def _to_numpy_rgb(image_rgb: Any) -> np.ndarray:
    if isinstance(image_rgb, np.ndarray):
        arr = image_rgb
    else:
        arr = np.array(image_rgb)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError("image_rgb must be an RGB-like array with shape (H, W, 3+)")
    if arr.shape[2] > 3:
        arr = arr[:, :, :3]
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    return arr


def _rgb_to_hsv_numpy(rgb: np.ndarray) -> np.ndarray:
    rgbf = rgb.astype(np.float32) / 255.0
    r = rgbf[:, :, 0]
    g = rgbf[:, :, 1]
    b = rgbf[:, :, 2]

    cmax = np.max(rgbf, axis=2)
    cmin = np.min(rgbf, axis=2)
    delta = cmax - cmin

    hue = np.zeros_like(cmax)
    nonzero = delta > 0

    mask_r = nonzero & (cmax == r)
    mask_g = nonzero & (cmax == g)
    mask_b = nonzero & (cmax == b)

    hue[mask_r] = np.mod((g[mask_r] - b[mask_r]) / delta[mask_r], 6.0)
    hue[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2.0
    hue[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4.0
    hue = hue / 6.0

    sat = np.zeros_like(cmax)
    valid = cmax > 0
    sat[valid] = delta[valid] / cmax[valid]

    val = cmax
    return np.stack([hue, sat, val], axis=2)


def _is_greenish_color(color: Any) -> bool:
    if not isinstance(color, (list, tuple)) or len(color) < 3:
        return False
    r, g, b = color[0], color[1], color[2]
    scale = 255.0 if max(abs(float(r)), abs(float(g)), abs(float(b))) <= 1.0 else 1.0
    r = float(r) * scale
    g = float(g) * scale
    b = float(b) * scale
    return g >= 70 and g > r + 20 and g > b + 20
