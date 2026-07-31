from ssc_corpus.crops import CropMetadata, crop_filename, safe_crop_stem
from ssc_corpus.crops import save_pdf_region_crop
from ssc_study.modality_recrop import (
    classify_question_for_web_modality,
    masked_crop_preserves_question_content,
    question_number_anchor_from_text,
)


def test_safe_crop_stem_sanitizes_values() -> None:
    stem = safe_crop_stem(
        "paper v1",
        page_number=3,
        question_number=12,
        option_label="A/1",
        suffix="raw crop",
    )
    assert stem == "paper_v1_p03_q012_opt_A_1_raw_crop"
    assert crop_filename(stem, "png").endswith(".png")


def test_crop_metadata_to_dict() -> None:
    metadata = CropMetadata(
        page_number=1,
        question_number=2,
        option_label="3",
        bbox=(1.0, 2.0, 3.0, 4.0),
        image_width=100,
        image_height=200,
    )
    data = metadata.to_dict()
    assert data["page_number"] == 1
    assert data["bbox"] == (1.0, 2.0, 3.0, 4.0)


def test_save_pdf_region_crop_rejects_degenerate_region(tmp_path) -> None:
    from PIL import Image
    import pytest

    image_path = tmp_path / "page.png"
    Image.new("RGB", (100, 100), color="white").save(image_path)

    with pytest.raises(ValueError, match="Degenerate crop region"):
        save_pdf_region_crop(
            page_image_path=image_path,
            page_rect=(0.0, 0.0, 100.0, 100.0),
            bbox=(50.0, 50.0, 50.0, 80.0),
            output_path=tmp_path / "crop.png",
            page_number=1,
            question_number=1,
        )


def test_classify_question_for_web_modality_corrects_english_keyword_false_positive() -> None:
    result = classify_question_for_web_modality(
        section="English",
        question_text="Select the most appropriate meaning of the idiom: cut a sorry figure",
        option_texts=["be ashamed", "look foolish", "draw a chart", "make a sketch"],
    )

    assert result == "text_only"


def test_question_number_anchor_from_text_uses_explicit_leading_number() -> None:
    assert question_number_anchor_from_text("28. Three of the following options are alike") == 28


def test_question_number_anchor_from_text_ignores_non_leading_numbers() -> None:
    assert question_number_anchor_from_text("Select the option to fill in blank no. 3.") is None


def test_masked_crop_preserves_question_content_rejects_stem_only_crop(tmp_path) -> None:
    from PIL import Image

    raw = tmp_path / "raw.png"
    masked = tmp_path / "masked.png"
    Image.new("RGB", (500, 220), "white").save(raw)
    Image.new("RGB", (500, 38), "white").save(masked)

    assert masked_crop_preserves_question_content(raw, masked) is False
