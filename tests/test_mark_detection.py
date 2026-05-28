import numpy as np

from ssc_corpus.mark_detection import detect_green_from_drawings, detect_green_from_rgb


def test_detect_green_from_rgb_hsv_positive() -> None:
    rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    rgb[:, :] = [0, 220, 0]
    result = detect_green_from_rgb(rgb, min_green_fraction=0.05)
    assert result.label == "green_mark_present"
    assert result.green_fraction >= 0.95


def test_detect_green_from_rgb_hsv_no_green() -> None:
    rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    rgb[:, :] = [220, 0, 0]
    result = detect_green_from_rgb(rgb, min_green_fraction=0.05)
    assert result.label == "no_green_mark"
    assert result.green_fraction == 0.0


def test_detect_green_from_drawings_unavailable_or_non_green() -> None:
    result_none = detect_green_from_drawings(None)
    assert result_none.label == "no_green_mark"

    drawings = [{"color": (1.0, 0.0, 0.0)}, {"fill": (0.0, 0.0, 1.0)}]
    result_non_green = detect_green_from_drawings(drawings)
    assert result_non_green.label == "no_green_mark"


def test_detect_green_from_drawings_green_fallback() -> None:
    drawings = [{"color": (0.0, 1.0, 0.0)}]
    result = detect_green_from_drawings(drawings)
    assert result.label == "green_mark_present"
    assert result.source == "vector_drawings"
