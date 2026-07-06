"""Phase 2c Pattern Priority Combiner.

Combines exam frequency/importance metrics with user diagnostic performance signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .patterns_exam import ExamPatternReport


@dataclass(frozen=True)
class PatternPriorityReport:
    """Contains prioritizations combining exam importance and user diagnostic signals."""

    priorities: List[Dict[str, Any]]
    advisory_status: str


def combine_pattern_priorities(
    exam_report: ExamPatternReport,
    user_report: Optional[Dict[str, Any]] = None,
) -> PatternPriorityReport:
    """Combine exam frequency with user diagnostic signals to advise on study priorities.

    Args:
        exam_report: An ExamPatternReport instance.
        user_report: Optional dict mapping archetype names to user accuracy (float 0.0 to 1.0).

    Returns:
        PatternPriorityReport ranking archetypes by priority.
    """
    user_report = user_report or {}

    priorities = []
    for arch_name, count in exam_report.archetype_distribution.items():
        user_acc = user_report.get(arch_name, 1.0)
        # Priority score: Higher score means higher priority.
        # It's high when frequency is high and user accuracy is low.
        priority_score = count * (1.0 - user_acc)

        # Determine recommended action based on accuracy thresholds
        if user_acc < 0.50:
            action = "remediation"
        elif user_acc < 0.80:
            action = "boss_fight"
        else:
            action = "sm2_review"

        priorities.append({
            "archetype_name": arch_name,
            "exam_count": count,
            "user_accuracy": user_acc,
            "priority_score": round(priority_score, 2),
            "recommended_action": action,
        })

    # Sort primarily by priority_score descending, then exam_count descending, then name alphabetically
    priorities.sort(key=lambda x: (x["priority_score"], x["exam_count"], x["archetype_name"]), reverse=True)

    return PatternPriorityReport(
        priorities=priorities,
        advisory_status="advisory",
    )
