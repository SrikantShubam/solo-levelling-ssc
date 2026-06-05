"""Domain dataclasses for the SSC study application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SM2State:
    """Current SM-2 state for a question, archetype, or fact card."""

    easiness: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    next_review: str | None = None  # ISO date
    last_review: str | None = None
    last_quality: int | None = None  # 0–5


@dataclass(frozen=True)
class SM2Result:
    """Output from compute_sm2 — new state after a review."""

    easiness: float
    interval_days: int
    repetitions: int
    next_review: str  # ISO date = today + interval_days


@dataclass(frozen=True)
class Option:
    label: str  # "1", "2", "3", or "4"
    text: str


@dataclass(frozen=True)
class Question:
    """A single question from the corpus."""

    question_id: str
    pdf_name: str
    source_page: int
    global_question_number: int
    section: str
    year: int
    tier: str  # 'tier1' | 'tier2'
    question_text: str
    options: list[Option]
    correct_option_label: str  # '1'|'2'|'3'|'4'
    correct_option_text: str | None = None
    chosen_option_label: str | None = None
    question_modality: str = "text_only"
    visual_required: bool = False
    table_required: bool = False
    math_required: bool = False
    evidence_status: str | None = None
    question_crop_path: str | None = None
    page_asset_path: str | None = None
    archetype_id: int | None = None
    is_holdout: bool = False
    created_at: str = ""

    @classmethod
    def from_merged_json(cls, data: dict[str, Any], section: str, year: int, tier: str) -> Question:
        """Build a Question from a merged_questions_global_order.json entry.

        The section, year, and tier are derived from the PDF name by the loader.
        """
        options = []
        for o in data.get("options", []):
            if isinstance(o, dict):
                options.append(Option(label=str(o.get("label", "")), text=str(o.get("text", ""))))

        return cls(
            question_id=str(data.get("resolved_question_id") or data.get("question_id", "")),
            pdf_name=data.get("pdf_name", ""),
            source_page=int(data.get("source_page") or 0),
            global_question_number=int(data.get("global_question_number") or 0),
            section=section,
            year=year,
            tier=tier,
            question_text=str(data.get("question_text_full") or ""),
            options=options,
            correct_option_label=str(data.get("canonical_correct_option_label") or ""),
            correct_option_text=data.get("correct_option_text"),
            chosen_option_label=data.get("chosen_option_label"),
            question_modality=str(data.get("question_modality") or "text_only"),
            visual_required=bool(data.get("visual_required")),
            table_required=bool(data.get("table_required")),
            math_required=bool(data.get("math_required")),
            evidence_status=data.get("evidence_status"),
            question_crop_path=data.get("question_crop_path"),
            page_asset_path=data.get("page_asset_path"),
            is_holdout=False,  # set by loader
            created_at="",
        )


@dataclass
class Attempt:
    """A single question attempt recorded during a session."""

    question_id: str
    session_id: int
    user_answer: str | None = None  # '1'|'2'|'3'|'4' or None for skipped
    is_correct: bool = False
    time_spent_seconds: int = 0
    student_label: str | None = None  # 'correct','incorrect','skipped','timed_out'
    timing_inference: str | None = None
    concept_tag: str | None = None
    quality_score: int | None = None  # 0–5 SM-2 quality
    was_remediated: bool = False
    created_at: str = ""
    attempt_id: int | None = None  # set by DB after insert


@dataclass(frozen=True)
class Session:
    """A practice session."""

    session_type: str  # sm2_review, boss_fight, tier2_module, etc.
    started_at: str  # ISO datetime
    ended_at: str | None = None
    duration_minutes: int | None = None
    question_count: int = 0
    correct_count: int = 0
    tier: str | None = None
    notes: str | None = None
    session_id: int | None = None


@dataclass(frozen=True)
class Archetype:
    """A question archetype (concept cluster)."""

    name: str
    section: str
    tier: str = "both"
    difficulty: str = "medium"
    t1_accuracy: float | None = None
    t2_accuracy: float | None = None
    is_unlocked: bool = False
    is_active: bool = True
    skip_count: int = 0
    skip_until: str | None = None
    archetype_id: int | None = None


@dataclass(frozen=True)
class FactCard:
    """A GK/GA fact card for memory recall."""

    front_text: str
    back_text: str
    tier_scope: str = "both"  # 'tier1' | 'tier2' | 'both'
    depth_level: str = "basic"  # 'basic' | 'deep'
    cbic_relevance: bool = False
    source: str | None = None
    expires_on: str | None = None
    question_id: str | None = None
    card_id: int | None = None


@dataclass(frozen=True)
class ExternalMock:
    """An externally-taken mock test result."""

    mock_name: str
    source: str
    taken_at: str
    tier: str
    raw_score: int
    calibrated_score: int | None = None
    section_scores: dict[str, int] | None = None
    notes: str | None = None
    mock_id: int | None = None


@dataclass
class StudyConfig:
    """User configuration with JSON persistence."""

    db_path: str = "~/.ssc_study/study.db"
    daily_split_minutes: dict[str, int] = field(default_factory=lambda: {
        "sm2_review": 25,
        "tier1_boss_fight": 35,
        "tier2_module": 60,
        "gkga_memory": 20,
        "english": 30,
        "analysis": 10,
    })
    tier1_floor_target: int = 140
    tier2_floor_target: int = 110
    archetype_probe_count: int = 10
    archetype_unlock_accuracy: float = 0.70
    holdout_ratio: float = 0.25
    backup_reminder: bool = True
