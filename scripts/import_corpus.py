#!/usr/bin/env python3
"""One-shot corpus import from pipeline output into SQLite."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ssc_study.loader import import_corpus, verify_import


def main() -> int:
    pipeline_root = Path("pipeline_output/p2_gemini")
    db_path = Path.home() / ".ssc_study" / "study.db"

    print(f"Pipeline: {pipeline_root}")
    print(f"Database: {db_path}")
    print()

    result = import_corpus(pipeline_root, db_path)

    if result.errors and "Already imported" in result.errors[0]:
        print(result.errors[0])
    else:
        print(f"Imported {result.question_count} questions from {result.pdf_count} PDFs")
        print(f"Holdout: {result.holdout_count}")
        if result.errors:
            for err in result.errors:
                print(f"  WARNING: {err}")

    print()
    integrity = verify_import(db_path)
    print(f"Verification: {integrity['question_count']} questions, "
          f"{'PASS' if not integrity['has_errors'] else 'FAIL'}")
    if integrity["has_errors"]:
        for err in integrity["error_details"]:
            print(f"  ERROR: {err}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
