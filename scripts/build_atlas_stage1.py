"""Activate the Stage 1 rule-based archetype atlas."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ssc_study.archetypes import (  # noqa: E402
    classify_question,
    ensure_default_archetypes,
)
from ssc_study.db import Database  # noqa: E402
from ssc_study.models import Question  # noqa: E402


@dataclass(frozen=True)
class AtlasStage1Report:
    """Summary of one Stage 1 atlas activation run."""

    archetypes_created: int
    questions_assigned: int
    total_non_holdout: int
    assigned_non_holdout: int
    unassigned_by_section: dict[str, int]
    per_archetype_counts: list[tuple[str, str, int]]


def build_atlas_stage1(db: Database) -> AtlasStage1Report:
    """Populate default archetypes and assign rule matches to non-holdouts."""
    archetypes_created = ensure_default_archetypes(db)
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM questions WHERE is_holdout = 0 ORDER BY question_id"
    ).fetchall()

    questions_assigned = 0
    with db.transaction() as tx:
        for row in rows:
            question = Question.from_row(row)
            archetype_name = classify_question(question)
            if archetype_name is None:
                continue

            archetype_row = tx.execute(
                "SELECT archetype_id FROM archetypes WHERE name = ? AND section = ?",
                (archetype_name, question.section),
            ).fetchone()
            if archetype_row is None:
                continue

            archetype_id = archetype_row["archetype_id"]
            if row["archetype_id"] != archetype_id:
                tx.execute(
                    "UPDATE questions SET archetype_id = ? WHERE question_id = ?",
                    (archetype_id, question.question_id),
                )
                questions_assigned += 1

    unassigned_by_section = {
        row["section"]: row["count"]
        for row in conn.execute(
            """SELECT section, COUNT(*) AS count
               FROM questions
               WHERE is_holdout = 0 AND archetype_id IS NULL
               GROUP BY section
               ORDER BY section"""
        ).fetchall()
    }
    count_row = conn.execute(
        """SELECT
              COUNT(*) AS total_non_holdout,
              SUM(CASE WHEN archetype_id IS NOT NULL THEN 1 ELSE 0 END) AS assigned_non_holdout
           FROM questions
           WHERE is_holdout = 0"""
    ).fetchone()
    per_archetype_counts = [
        (row["section"], row["name"], row["count"])
        for row in conn.execute(
            """SELECT a.section, a.name, COUNT(q.question_id) AS count
               FROM archetypes a
               LEFT JOIN questions q
                 ON q.archetype_id = a.archetype_id
                AND q.is_holdout = 0
               GROUP BY a.archetype_id
               ORDER BY a.section, a.name"""
        ).fetchall()
    ]

    return AtlasStage1Report(
        archetypes_created=archetypes_created,
        questions_assigned=questions_assigned,
        total_non_holdout=count_row["total_non_holdout"] or 0,
        assigned_non_holdout=count_row["assigned_non_holdout"] or 0,
        unassigned_by_section=unassigned_by_section,
        per_archetype_counts=per_archetype_counts,
    )


def print_report(report: AtlasStage1Report) -> None:
    """Print a stable line-oriented report for CLI use and audits."""
    print(f"archetypes_created={report.archetypes_created}")
    print(f"questions_assigned={report.questions_assigned}")
    print(f"assigned_non_holdout={report.assigned_non_holdout}")
    print(f"total_non_holdout={report.total_non_holdout}")
    if report.total_non_holdout:
        coverage = report.assigned_non_holdout / report.total_non_holdout
    else:
        coverage = 0.0
    print(f"coverage_non_holdout={coverage:.3f}")
    print("unassigned_by_section:")
    if report.unassigned_by_section:
        for section, count in report.unassigned_by_section.items():
            print(f"  {section}={count}")
    else:
        print("  none=0")
    print("per_archetype_counts:")
    for section, name, count in report.per_archetype_counts:
        print(f"  {section} | {name}={count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    args = parser.parse_args(argv)

    db = Database(args.db)
    report = build_atlas_stage1(db)
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
