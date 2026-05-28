from ssc_corpus.crops import CropMetadata, crop_filename, safe_crop_stem


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
