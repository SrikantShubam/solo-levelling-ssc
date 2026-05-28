from ssc_corpus.extraction_qc import (
    build_review_decision,
    classify_modality,
    decide_correct_answer_evidence,
    decide_evidence_status,
    review_reasons_for_question,
)


def test_classify_modality_graph() -> None:
    result = classify_modality("Study the bar graph and answer", options=["A", "B"])
    assert result.label == "graph_chart"
    assert "bar graph" in result.matched_keywords


def test_classify_modality_dice() -> None:
    result = classify_modality("If opposite faces of a cube are marked as shown on dice")
    assert result.label == "dice"


def test_conflict_sets_manual_review() -> None:
    decision = decide_evidence_status(gemini_label="text", deterministic_label="table")
    assert decision.status == "manual_review"
    assert "label_conflict" in decision.reasons


def test_build_review_decision_includes_keyword_reason() -> None:
    decision = build_review_decision(
        question_text="In the following Venn diagram choose correct option",
        options=["opt1", "opt2"],
        gemini_label="graph",
    )
    assert decision.status == "manual_review"
    assert decision.deterministic_label == "visual_stimulus"
    assert any(reason.startswith("keywords:") for reason in decision.reasons)


def test_correct_answer_conflict_sets_manual_review() -> None:
    decision = decide_correct_answer_evidence(
        gemini_label="2",
        deterministic_label="3",
        simple_text_only=False,
    )
    assert decision.status == "PASS_WITH_MANUAL_REVIEW"
    assert "correct_option_conflict" in decision.reasons


def test_ambiguous_deterministic_evidence_requires_manual_review() -> None:
    decision = decide_correct_answer_evidence(
        gemini_label="2",
        deterministic_label="AMBIGUOUS",
        simple_text_only=True,
    )
    assert decision.status == "PASS_WITH_MANUAL_REVIEW"
    assert "correct_option_ambiguous_deterministic_evidence" in decision.reasons


def test_llm_only_allowed_for_text_only() -> None:
    decision = decide_correct_answer_evidence(
        gemini_label="2",
        deterministic_label=None,
        simple_text_only=True,
    )
    assert decision.status == "PASS_LLM_ONLY"


def test_review_reasons_include_nonblocking_chosen_option() -> None:
    reasons = review_reasons_for_question(
        modality="text_only",
        evidence_status="PASS_LLM_ONLY",
        chosen_missing=True,
    )
    assert reasons == ("chosen_option_missing",)


def test_visual_asset_missing_is_review_reason() -> None:
    reasons = review_reasons_for_question(
        modality="visual_options",
        evidence_status="PASS_WITH_EVIDENCE",
        chosen_missing=False,
        has_visual_asset=False,
    )
    assert reasons == ("visual_asset_missing",)


def test_math_without_question_crop_is_lossy() -> None:
    reasons = review_reasons_for_question(
        modality="math_formula",
        evidence_status="PASS_LLM_ONLY",
        chosen_missing=False,
        has_question_crop=False,
    )
    assert reasons == ("math_parse_lossy",)
