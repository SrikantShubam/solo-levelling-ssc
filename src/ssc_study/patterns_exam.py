"""Phase 2c Exam Pattern Intelligence module.

Analyzes non-holdout question metrics from the corpus database.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .db import Database


@dataclass(frozen=True)
class ExamPatternReport:
    """Contains analyzed metrics from the question corpus."""

    total_eligible_questions: int
    filters_applied: Dict[str, Any]
    section_distribution: Dict[str, int]
    tier_distribution: Dict[str, int]
    year_distribution: Dict[str, int]
    archetype_distribution: Dict[str, int]
    source_question_ids: List[str]
    signal_strength: str
    advisory_blueprint: Dict[str, Any]


def analyze_exam_patterns(
    db: Database,
    *,
    tier: Optional[str] = None,
    years: Optional[List[int] | int] = None,
    exclude_holdout: bool = True,
) -> ExamPatternReport:
    """Compute read-only exam pattern intelligence over the corpus questions.

    Args:
        db: The study Database instance.
        tier: Optional tier filter ('tier1' or 'tier2').
        years: Optional list of years or single year.
        exclude_holdout: Exclude holdout questions (is_holdout = 1) if True.

    Returns:
        ExamPatternReport with distributions and advisory blueprint.
    """
    conn = db.connect()

    where_clauses = []
    params = []

    if exclude_holdout:
        where_clauses.append("q.is_holdout = 0")

    if tier:
        where_clauses.append("q.tier = ?")
        params.append(tier)

    if years is not None:
        if isinstance(years, (list, tuple, set)):
            if years:
                placeholders = ",".join("?" for _ in years)
                where_clauses.append(f"q.year IN ({placeholders})")
                params.extend(years)
            else:
                where_clauses.append("1=0")  # empty years list match nothing
        else:
            where_clauses.append("q.year = ?")
            params.append(years)

    where_str = " AND ".join(where_clauses) if where_clauses else "1=1"

    # 1. Total questions count
    total_row = conn.execute(
        f"SELECT COUNT(*) as count FROM questions q WHERE {where_str}",
        tuple(params),
    ).fetchone()
    total_count = total_row["count"] if total_row else 0

    # 2. Section distribution
    sec_rows = conn.execute(
        f"SELECT q.section, COUNT(*) as count FROM questions q WHERE {where_str} GROUP BY q.section",
        tuple(params),
    ).fetchall()
    section_dist = {r["section"]: r["count"] for r in sec_rows}

    # 3. Tier distribution
    tier_rows = conn.execute(
        f"SELECT q.tier, COUNT(*) as count FROM questions q WHERE {where_str} GROUP BY q.tier",
        tuple(params),
    ).fetchall()
    tier_dist = {r["tier"]: r["count"] for r in tier_rows}

    # 4. Year distribution
    year_rows = conn.execute(
        f"SELECT q.year, COUNT(*) as count FROM questions q WHERE {where_str} GROUP BY q.year",
        tuple(params),
    ).fetchall()
    year_dist = {r["year"]: r["count"] for r in year_rows}

    # 5. Archetype distribution
    arch_rows = conn.execute(
        f"""SELECT a.name, COUNT(q.question_id) as count
           FROM questions q
           JOIN archetypes a ON q.archetype_id = a.archetype_id
           WHERE {where_str}
           GROUP BY q.archetype_id""",
        tuple(params),
    ).fetchall()
    archetype_dist = {r["name"]: r["count"] for r in arch_rows}

    # 6. Source question IDs
    q_rows = conn.execute(
        f"SELECT q.question_id FROM questions q WHERE {where_str} ORDER BY q.question_id ASC",
        tuple(params),
    ).fetchall()
    source_qids = [r["question_id"] for r in q_rows]

    # Signal strength logic:
    # - insufficient: fewer than 30 eligible questions or fewer than 3 archetypes
    # - weak: at least 30 eligible questions but fewer than 100, or fewer than 10 archetypes
    # - stable: at least 100 eligible questions and at least 10 archetypes
    unique_archetypes_count = len(archetype_dist)
    if total_count < 30 or unique_archetypes_count < 3:
        signal_strength = "insufficient"
    elif total_count < 100 or unique_archetypes_count < 10:
        signal_strength = "weak"
    else:
        signal_strength = "stable"

    # Advisory blueprint composition
    sorted_archetypes = sorted(archetype_dist.items(), key=lambda x: x[1], reverse=True)
    top_archetypes = sorted_archetypes[:10]

    advisory_blueprint = {
        "label": "Advisory Mock Blueprint",
        "description": "This blueprint is advisory only and does not mutate runtime state.",
        "section_allocation": section_dist,
        "top_archetype_allocation": {k: v for k, v in top_archetypes},
        "evidence_question_ids": source_qids,
    }

    filters_applied = {
        "tier": tier,
        "years": years,
        "exclude_holdout": exclude_holdout,
    }

    return ExamPatternReport(
        total_eligible_questions=total_count,
        filters_applied=filters_applied,
        section_distribution=section_dist,
        tier_distribution=tier_dist,
        year_distribution=year_dist,
        archetype_distribution=archetype_dist,
        source_question_ids=source_qids,
        signal_strength=signal_strength,
        advisory_blueprint=advisory_blueprint,
    )
