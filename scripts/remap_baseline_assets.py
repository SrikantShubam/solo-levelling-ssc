"""One-time repair for stale baseline question asset paths."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ssc_study.corpus_assets import remap_question_assets
from ssc_study.db import Database


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    args = parser.parse_args()

    db = Database(args.db)
    stats = remap_question_assets(db.connect(), repo_root=ROOT)
    print(f"rows_seen={stats.rows_seen}")
    print(f"rows_remapped={stats.rows_remapped}")
    print(f"missing_asset_rows={stats.missing_asset_rows}")
    print(f"masked_rows={stats.masked_rows}")
    print(f"unmaskable_answer_leak_rows={stats.unmaskable_answer_leak_rows}")
    if stats.unmaskable_question_ids:
        print("unmaskable_question_ids=" + ",".join(stats.unmaskable_question_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
