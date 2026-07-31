"""Namespace harvested question IDs before live corpus import."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MERGED_FILENAME = "merged_questions_global_order.json"


def namespaced_question_id(pdf_name: str, global_question_number: int | str) -> str:
    """Return the deterministic import-safe ID for one harvested question."""
    return f"harvest_{pdf_name}_q{int(global_question_number)}"


def rewrite_question_ids(data: dict[str, Any], pdf_name: str) -> int:
    """Rewrite question_id and resolved_question_id in a loaded merged JSON object."""
    changed = 0
    for question in data.get("questions", []):
        if not isinstance(question, dict):
            continue
        new_id = namespaced_question_id(pdf_name, question.get("global_question_number") or 0)
        if question.get("question_id") != new_id:
            question["question_id"] = new_id
            changed += 1
        if question.get("resolved_question_id") != new_id:
            question["resolved_question_id"] = new_id
            changed += 1
    return changed


def rewrite_harvest_root(root: Path, *, apply: bool = False) -> dict[str, int]:
    """Rewrite all harvest merged JSON files under root when apply=True."""
    files = sorted(root.glob(f"*/{MERGED_FILENAME}"))
    files_changed = 0
    fields_changed = 0
    questions_seen = 0
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        questions_seen += len(data.get("questions", []))
        changed = rewrite_question_ids(data, path.parent.name)
        if changed:
            files_changed += 1
            fields_changed += changed
            if apply:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "files_seen": len(files),
        "files_changed": files_changed,
        "questions_seen": questions_seen,
        "fields_changed": fields_changed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="pipeline_output/harvest_batch", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    report = rewrite_harvest_root(args.root, apply=args.apply)
    for key, value in report.items():
        print(f"{key}={value}")
    print(f"mode={'apply' if args.apply else 'dry-run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
