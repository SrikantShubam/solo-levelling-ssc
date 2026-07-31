"""Re-verify web-baseline answers from staged answer-key evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ssc_study.answer_verification import reverify_answers
from ssc_study.db import Database


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    parser.add_argument(
        "--staging-dir",
        default="answer_key_candidates_staging",
        help="Directory containing staged answer-key PDFs",
    )
    args = parser.parse_args()

    db = Database(args.db)
    stats = reverify_answers(db.connect(), staging_dir=args.staging_dir)
    print("before_reasons=" + dict(stats.before_reasons).__repr__())
    print(f"resolved_from_crop_ground_truth={stats.resolved_from_crop_ground_truth}")
    print(f"resolved_from_staging={stats.resolved_from_staging}")
    print("after_reasons=" + dict(stats.after_reasons).__repr__())
    print("unresolved_by_reason=" + dict(stats.unresolved_by_reason).__repr__())
    if stats.updated_question_ids:
        print("updated_question_ids=" + ",".join(stats.updated_question_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

