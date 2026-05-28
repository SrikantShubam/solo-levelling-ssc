from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ModalityResult:
    label: str
    matched_keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceDecision:
    status: str
    deterministic_label: str
    gemini_label: str | None
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("table_di", ("table", "tabular", "row", "column")),
    ("graph_chart", ("bar graph", "line graph", "pie chart", "graph", "chart", "histogram")),
    ("visual_stimulus", ("venn", "venn diagram")),
    ("dice", ("dice", "die", "faces of a cube", "opposite face")),
    ("visual_options", ("mirror", "reflection", "water image")),
    ("visual_options", ("figure", "diagram", "shown below", "given figure", "following figure")),
    ("math_formula", ("solve", "equation", "simplify", "value of", "find x", "ratio", "percentage", "tan", "cos", "sin", "√")),
]


def classify_modality(question_text: str, options: list[str] | None = None) -> ModalityResult:
    combined = (question_text or "") + " " + " ".join(options or [])
    lowered = combined.lower()
    for label, keys in _KEYWORDS:
        hits = tuple(k for k in keys if k in lowered)
        if hits:
            return ModalityResult(label=label, matched_keywords=hits)
    return ModalityResult(label="text_only", matched_keywords=tuple())


def decide_evidence_status(
    *,
    gemini_label: str | None,
    deterministic_label: str,
) -> EvidenceDecision:
    reasons: list[str] = []
    if not gemini_label:
        reasons.append("gemini_label_missing")
        return EvidenceDecision(
            status="manual_review",
            deterministic_label=deterministic_label,
            gemini_label=gemini_label,
            reasons=tuple(reasons),
        )

    if gemini_label == deterministic_label:
        return EvidenceDecision(
            status="aligned",
            deterministic_label=deterministic_label,
            gemini_label=gemini_label,
            reasons=("labels_match",),
        )

    reasons.append("label_conflict")
    return EvidenceDecision(
        status="manual_review",
        deterministic_label=deterministic_label,
        gemini_label=gemini_label,
        reasons=tuple(reasons),
    )


def decide_correct_answer_evidence(
    *,
    gemini_label: str | None,
    deterministic_label: str | None,
    simple_text_only: bool,
) -> EvidenceDecision:
    gemini = _normalize_label(gemini_label)
    if str(deterministic_label or "").upper() == "AMBIGUOUS":
        return EvidenceDecision(
            "PASS_WITH_MANUAL_REVIEW",
            "AMBIGUOUS",
            gemini,
            ("correct_option_ambiguous_deterministic_evidence",),
        )
    deterministic = _normalize_label(deterministic_label)
    if deterministic and gemini and deterministic == gemini:
        return EvidenceDecision("PASS_WITH_EVIDENCE", deterministic, gemini, ("labels_match",))
    if deterministic and gemini and deterministic != gemini:
        return EvidenceDecision(
            "PASS_WITH_MANUAL_REVIEW",
            deterministic,
            gemini,
            ("correct_option_conflict",),
        )
    if deterministic and not gemini:
        return EvidenceDecision("PASS_WITH_EVIDENCE", deterministic, gemini, ("deterministic_only",))
    if gemini and not deterministic and simple_text_only:
        return EvidenceDecision("PASS_LLM_ONLY", deterministic or "", gemini, ("llm_only_text",))
    if gemini and not deterministic:
        return EvidenceDecision(
            "PASS_WITH_MANUAL_REVIEW",
            deterministic or "",
            gemini,
            ("llm_only_visual_or_complex",),
        )
    return EvidenceDecision(
        "BLOCKED",
        deterministic or "",
        gemini,
        ("correct_option_unresolved",),
    )


def review_reasons_for_question(
    *,
    modality: str,
    evidence_status: str,
    chosen_missing: bool,
    option_issue: bool = False,
    low_confidence: bool = False,
    has_page_asset: bool = True,
    has_visual_asset: bool = True,
    has_question_crop: bool = True,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if option_issue:
        reasons.append("malformed_options")
    if evidence_status in {"PASS_WITH_MANUAL_REVIEW", "BLOCKED"}:
        reasons.append("correct_option_unresolved_or_conflict")
    if chosen_missing:
        reasons.append("chosen_option_missing")
    if low_confidence:
        reasons.append("low_confidence")
    if not has_page_asset:
        reasons.append("page_asset_missing")
    if modality in {"visual_stimulus", "visual_options", "table_di", "graph_chart"} and not has_visual_asset:
        reasons.append("visual_asset_missing")
    if modality == "math_formula" and (low_confidence or not has_question_crop):
        reasons.append("math_parse_lossy")
    return tuple(dict.fromkeys(reasons))


def build_review_decision(
    *,
    question_text: str,
    options: list[str] | None = None,
    gemini_label: str | None = None,
) -> EvidenceDecision:
    modality = classify_modality(question_text=question_text, options=options)
    decision = decide_evidence_status(
        gemini_label=gemini_label,
        deterministic_label=modality.label,
    )
    reasons = list(decision.reasons)
    if modality.matched_keywords:
        reasons.append(f"keywords:{','.join(modality.matched_keywords)}")
    return EvidenceDecision(
        status=decision.status,
        deterministic_label=decision.deterministic_label,
        gemini_label=decision.gemini_label,
        reasons=tuple(reasons),
    )


def _normalize_label(label: str | None) -> str | None:
    if label is None:
        return None
    value = str(label).strip()
    return value if value in {"1", "2", "3", "4"} else None
