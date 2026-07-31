"""Repair known split question stems in the local study database.

This script is intentionally narrow. It only repairs rows where the missing
stem was found in adjacent DB rows or the source PDF/page text during manual
audit. It does not infer arbitrary missing content.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import textwrap


@dataclass(frozen=True)
class StemRepair:
    question_id: str
    repaired_text: str
    evidence: str


REPAIRS = {
    "2024_tier1_appx_answer_key_q8": StemRepair(
        question_id="2024_tier1_appx_answer_key_q8",
        repaired_text=(
            "7. The same operation(s) are followed in all the given number pairs "
            "except one. Find that odd number pair. (NOTE : Operations should be "
            "performed on the whole numbers, without breaking down the numbers "
            "into its constituent digits. E.g. 13 - Operations on 13 such as "
            "adding /deleting /multiplying etc., to 13 can be performed. "
            "Breaking down 13 into 1 and 3 and then performing mathematical "
            "operations on 1 and 3 is not allowed.) (11/09/2024 SHIFT-1)"
        ),
        evidence=(
            "Joined DB/source split: q7 contains the leading stem and q8 contains "
            "the continuation/options. Also visible in pipeline_output/p2_gemini/"
            "2024_tier1_appx_answer_key/page_json/page_01.json and page_02.json."
        ),
    ),
    "2024_tier1_appx_answer_key_q22": StemRepair(
        question_id="2024_tier1_appx_answer_key_q22",
        repaired_text=(
            "20. Three of the following numbers are alike in a certain way and "
            "one is different. Pick the odd one out. (NOTE : Operations should be "
            "performed on the whole numbers, without breaking down the numbers "
            "into its constituent digits. E.g. 13 - Operations on 13 such as "
            "adding /deleting /multiplying etc., to 13 can be performed. "
            "Breaking down 13 into 1 and 3 and then performing mathematical "
            "operations on 1 and 3 is not allowed.) (18/09/2024 SHIFT-2)"
        ),
        evidence=(
            "Joined DB/source split: q21 contains the leading stem and q22 "
            "contains the continuation/options. Also visible in pipeline_output/"
            "p2_gemini/2024_tier1_appx_answer_key/page_json/page_03.json and "
            "page_04.json."
        ),
    ),
    "2024_tier1_appx_answer_key_q29": StemRepair(
        question_id="2024_tier1_appx_answer_key_q29",
        repaired_text=(
            "27. Three of the following number-pairs are alike in some manner "
            "and hence form a group. Which number-pair does not belong to that "
            "group? (NOTE: Operations should be performed on the whole numbers, "
            "without breaking down the numbers into its constituent digits. "
            "E.g. 13 - Operations on 13 such as adding/subtracting/multiplying "
            "etc. to 13 can be performed. Breaking down 13 into 1 and 3 and then "
            "performing mathematical operations on 1 and 3 is not allowed.) "
            "(23/09/2024 SHIFT-3)"
        ),
        evidence=(
            "Source PDF split across pages: answer_key_candidates_staging/"
            "2024_tier1_appx_answer_key.pdf page 4 ends with the leading stem "
            "'27. Three of the following number-pairs ... Which number-' and "
            "page 5 continues 'pair does not belong to that group?...'."
        ),
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/study.db")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--report",
        default="reports/incomplete_stem_repair_report.md",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    lines = [
        "# Incomplete Stem Repair Report",
        "",
        f"Database: `{db_path}`",
        f"Mode: `{'apply' if args.apply else 'dry-run'}`",
        "",
    ]

    changed = 0
    for repair in REPAIRS.values():
        row = conn.execute(
            "SELECT question_text FROM questions WHERE question_id = ?",
            (repair.question_id,),
        ).fetchone()
        lines.append(f"## `{repair.question_id}`")
        if row is None:
            lines.append("")
            lines.append("- Status: missing from DB")
            lines.append("")
            continue

        current = str(row["question_text"] or "")
        already_repaired = current == repair.repaired_text
        needs_repair = not already_repaired
        lines.append("")
        if already_repaired:
            status = "already repaired"
        elif args.apply:
            status = "repaired in this run"
        else:
            status = "needs repair"
        lines.append(f"- Status: {status}")
        lines.append(f"- Evidence: {repair.evidence}")
        lines.append("- Repaired text:")
        lines.append("")
        lines.append(textwrap.indent(repair.repaired_text, "  "))
        lines.append("")

        if args.apply and needs_repair:
            conn.execute(
                "UPDATE questions SET question_text = ? WHERE question_id = ?",
                (repair.repaired_text, repair.question_id),
            )
            changed += 1

    if args.apply:
        conn.commit()
    else:
        conn.rollback()

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Rows changed: {changed}")
    lines.append("- Unrepaired known fragment rows: none in the scoped repair set")
    lines.append("")

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"changed={changed}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
