"""Repair question modalities and generate masked per-question crops."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ssc_study.db import Database
from ssc_study.modality_recrop import repair_modalities_and_recrop


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    parser.add_argument(
        "--staging-dir",
        default="answer_key_candidates_staging",
        help="Directory containing source PDFs",
    )
    args = parser.parse_args()

    db = Database(args.db)
    stats = repair_modalities_and_recrop(
        db.connect(),
        repo_root=ROOT,
        staging_dir=args.staging_dir,
    )
    print("modality_corrections=" + dict(stats.modality_corrections).__repr__())
    print("recropped_masked_by_source=" + dict(stats.recropped_masked_by_source).__repr__())
    print("still_excluded_by_source=" + dict(stats.still_excluded_by_source).__repr__())
    print("exclusion_reasons=" + dict(stats.exclusion_reasons).__repr__())
    if stats.excluded_question_ids:
        print("excluded_question_ids=" + ",".join(stats.excluded_question_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
