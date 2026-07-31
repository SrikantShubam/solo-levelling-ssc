"""Repair the 7 known Wave 3a mojibake rows in the study DB."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

TARGET_IDS = (
    "2024_tier1_prepp_shift1_q47",
    "2024_tier1_prepp_shift1_q60",
    "2024_tier1_prepp_shift1_q61",
    "2024_tier1_prepp_shift1_q62",
    "2024_tier1_prepp_shift1_q64",
    "2024_tier1_prepp_shift1_q70",
    "2024_tier1_prepp_shift1_q89",
)


def _repair_text(value: str) -> str:
    return value.encode("cp1252").decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    args = parser.parse_args()

    conn = sqlite3.connect(str(Path(args.db)))
    conn.row_factory = sqlite3.Row

    repaired = 0
    for question_id in TARGET_IDS:
        row = conn.execute(
            "SELECT question_text, options_json FROM questions WHERE question_id = ?",
            (question_id,),
        ).fetchone()
        if row is None:
            print(f"{question_id}: missing")
            continue

        options = json.loads(row["options_json"])
        fixed_question_text = _repair_text(str(row["question_text"]))
        fixed_options = [{**option, "text": _repair_text(str(option["text"]))} for option in options]

        conn.execute(
            "UPDATE questions SET question_text = ?, options_json = ? WHERE question_id = ?",
            (fixed_question_text, json.dumps(fixed_options, ensure_ascii=False), question_id),
        )
        repaired += 1
        print(f"{question_id}: repaired")

    conn.commit()
    print(f"rows_repaired={repaired}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
