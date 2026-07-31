"""Expand the archetype atlas with embedding nearest-centroid classification."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ssc_study.baseline_web import _build_web_safe_question_pool  # noqa: E402
from ssc_study.archetypes import classify_question  # noqa: E402
from ssc_study.db import Database  # noqa: E402
from ssc_study.embeddings import (  # noqa: E402
    _cosine_similarity,
    get_embedding_stats,
    update_all_embeddings,
)
from ssc_study.models import Question  # noqa: E402

VALIDATION_RATIO = 0.20
MIN_VALIDATION_SAMPLE = 20
MIN_PRECISION = 0.90
THRESHOLDS = tuple(round(value / 100, 2) for value in range(95, 29, -5))


class AtlasStage2Error(RuntimeError):
    """Raised when Stage 2 cannot safely classify questions."""


@dataclass(frozen=True)
class ThresholdChoice:
    threshold: float
    precision: float
    recall: float


@dataclass(frozen=True)
class ValidationBucket:
    section: str
    threshold: float
    attempted: int
    correct: int
    sample_size: int

    @property
    def precision(self) -> float:
        return self.correct / self.attempted if self.attempted else 0.0

    @property
    def recall(self) -> float:
        return self.correct / self.sample_size if self.sample_size else 0.0


@dataclass(frozen=True)
class AtlasStage2Report:
    embedding_before: dict[str, int]
    embedding_after: dict[str, int]
    embedding_update: dict[str, int]
    threshold: ThresholdChoice
    section_thresholds: list[ValidationBucket]
    validation_by_section: list[ValidationBucket]
    questions_assigned: int
    assigned_by_section: list[tuple[str, int]]
    assigned_by_archetype: list[tuple[str, str, int]]
    coverage_by_section: list[tuple[str, int, int]]
    holdout_archetype_non_null: int


def build_atlas_stage2(db: Database) -> AtlasStage2Report:
    """Validate and apply Stage 2 nearest-centroid archetype backfill."""
    embedding_before = get_embedding_stats(db)
    embedding_update = update_all_embeddings(db)
    embedding_after = get_embedding_stats(db)

    conn = db.connect()
    archetypes = _load_archetypes(db)
    seed_rows = conn.execute(
        """SELECT q.*, a.name AS archetype_name
           FROM questions q
           JOIN archetypes a ON a.archetype_id = q.archetype_id
           WHERE q.is_holdout = 0
             AND q.archetype_id IS NOT NULL
             AND q.embedding_blob IS NOT NULL
             AND length(q.embedding_blob) > 0
           ORDER BY q.archetype_id, q.question_id"""
    ).fetchall()
    seeds_by_archetype: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in seed_rows:
        if classify_question(Question.from_row(row)) != row["archetype_name"]:
            continue
        embedding = _embedding_from_blob(row["embedding_blob"])
        if embedding is None:
            continue
        seeds_by_archetype[int(row["archetype_id"])].append({
            "question_id": row["question_id"],
            "section": row["section"],
            "archetype_id": int(row["archetype_id"]),
            "embedding": _normalize(embedding),
        })

    validation_rows = _select_validation_rows(seeds_by_archetype)
    if len(validation_rows) < MIN_VALIDATION_SAMPLE:
        raise AtlasStage2Error(
            f"validation sample too small: {len(validation_rows)} < {MIN_VALIDATION_SAMPLE}"
        )
    validation_lookup = {row["question_id"] for row in validation_rows}
    train_by_archetype = {
        archetype_id: [
            row for row in rows if row["question_id"] not in validation_lookup
        ]
        for archetype_id, rows in seeds_by_archetype.items()
    }
    validation_centroids = _build_centroids(train_by_archetype, archetypes)
    if not validation_centroids:
        raise AtlasStage2Error("no validation centroids available")

    predictions = _score_rows(validation_rows, validation_centroids)
    validation_by_threshold = _evaluate_thresholds(predictions, len(validation_rows))
    threshold = select_threshold(validation_by_threshold)
    section_thresholds = select_section_thresholds(predictions)
    validation_by_section = _evaluate_sections_by_thresholds(predictions, section_thresholds)

    centroids = _build_centroids(seeds_by_archetype, archetypes)
    assignments = _classify_untagged(
        db,
        centroids,
        {bucket.section: bucket.threshold for bucket in section_thresholds},
    )
    with db.transaction() as tx:
        for question_id, archetype_id, _section, _name, _score in assignments:
            tx.execute(
                """UPDATE questions
                   SET archetype_id = ?
                   WHERE question_id = ?
                     AND is_holdout = 0
                     AND archetype_id IS NULL""",
                (archetype_id, question_id),
            )

    return AtlasStage2Report(
        embedding_before=embedding_before,
        embedding_after=embedding_after,
        embedding_update=embedding_update,
        threshold=threshold,
        section_thresholds=section_thresholds,
        validation_by_section=validation_by_section,
        questions_assigned=len(assignments),
        assigned_by_section=_assigned_by_section(assignments),
        assigned_by_archetype=_assigned_by_archetype(assignments),
        coverage_by_section=_coverage_by_section(db),
        holdout_archetype_non_null=_holdout_archetype_non_null(db),
    )


def select_threshold(validation: list[ValidationBucket]) -> ThresholdChoice:
    """Pick the highest-recall threshold that preserves high precision."""
    eligible = [
        bucket for bucket in validation
        if bucket.attempted > 0 and bucket.precision >= MIN_PRECISION
    ]
    if not eligible:
        best = max(validation, key=lambda b: (b.precision, b.recall, b.threshold))
        raise AtlasStage2Error(
            "no threshold met the precision floor "
            f"{MIN_PRECISION:.2f}; best={best.threshold:.2f} "
            f"precision={best.precision:.3f} recall={best.recall:.3f}"
        )
    chosen = max(eligible, key=lambda b: (b.recall, b.precision, b.threshold))
    return ThresholdChoice(
        threshold=chosen.threshold,
        precision=chosen.precision,
        recall=chosen.recall,
    )


def select_section_thresholds(predictions: list[dict[str, Any]]) -> list[ValidationBucket]:
    """Pick high-precision thresholds independently per section."""
    sections = sorted({prediction["section"] for prediction in predictions})
    choices: list[ValidationBucket] = []
    for section in sections:
        section_predictions = [
            prediction for prediction in predictions
            if prediction["section"] == section
        ]
        if len(section_predictions) < 10:
            continue
        buckets = _evaluate_thresholds(section_predictions, len(section_predictions))
        eligible = [
            bucket for bucket in buckets
            if bucket.attempted > 0 and bucket.precision >= MIN_PRECISION
        ]
        if not eligible:
            continue
        chosen = max(eligible, key=lambda b: (b.recall, b.precision, b.threshold))
        choices.append(ValidationBucket(
            section,
            chosen.threshold,
            chosen.attempted,
            chosen.correct,
            chosen.sample_size,
        ))
    return choices


def print_report(report: AtlasStage2Report) -> None:
    """Print a stable line-oriented report for CLI use and audits."""
    print("embedding_coverage_before:")
    _print_mapping(report.embedding_before)
    print("embedding_update:")
    _print_mapping(report.embedding_update)
    print("embedding_coverage_after:")
    _print_mapping(report.embedding_after)
    print(
        "chosen_threshold="
        f"{report.threshold.threshold:.2f} "
        f"precision={report.threshold.precision:.3f} "
        f"recall={report.threshold.recall:.3f}"
    )
    print("section_thresholds:")
    for bucket in report.section_thresholds:
        print(
            f"  {bucket.section}={bucket.threshold:.2f} "
            f"precision={bucket.precision:.3f} recall={bucket.recall:.3f}"
        )
    print("validation_by_section:")
    for bucket in report.validation_by_section:
        print(
            f"  {bucket.section} | sample={bucket.sample_size} "
            f"attempted={bucket.attempted} correct={bucket.correct} "
            f"precision={bucket.precision:.3f} recall={bucket.recall:.3f}"
        )
    print(f"questions_assigned={report.questions_assigned}")
    print("assigned_by_section:")
    _print_pairs(report.assigned_by_section)
    print("assigned_by_archetype:")
    if report.assigned_by_archetype:
        for section, name, count in report.assigned_by_archetype:
            print(f"  {section} | {name}={count}")
    else:
        print("  none=0")
    print("coverage_by_section:")
    for section, tagged, servable in report.coverage_by_section:
        print(f"  {section}={tagged}/{servable}")
    print(f"holdout_archetype_non_null={report.holdout_archetype_non_null}")


def _load_archetypes(db: Database) -> dict[int, dict[str, str]]:
    rows = db.connect().execute(
        "SELECT archetype_id, name, section FROM archetypes ORDER BY archetype_id"
    ).fetchall()
    return {
        int(row["archetype_id"]): {
            "name": str(row["name"]),
            "section": str(row["section"]),
        }
        for row in rows
    }


def _embedding_from_blob(blob: bytes | str | None) -> list[float] | None:
    if blob is None:
        return None
    try:
        raw = blob.decode("utf-8") if isinstance(blob, bytes) else blob
        values = json.loads(raw)
    except (AttributeError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(values, list):
        return None
    try:
        return [float(value) for value in values]
    except (TypeError, ValueError):
        return None


def _normalize(vector: list[float]) -> list[float]:
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _mean_vector(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    width = len(vectors[0])
    totals = [0.0] * width
    for vector in vectors:
        for idx, value in enumerate(vector[:width]):
            totals[idx] += value
    return _normalize([value / len(vectors) for value in totals])


def _select_validation_rows(
    seeds_by_archetype: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for rows in seeds_by_archetype.values():
        if len(rows) < 2:
            continue
        sample_size = max(1, round(len(rows) * VALIDATION_RATIO))
        sample_size = min(sample_size, len(rows) - 1)
        selected.extend(rows[:: max(1, len(rows) // sample_size)][:sample_size])
    selected.sort(key=lambda row: row["question_id"])
    return selected


def _build_centroids(
    rows_by_archetype: dict[int, list[dict[str, Any]]],
    archetypes: dict[int, dict[str, str]],
) -> list[dict[str, Any]]:
    centroids: list[dict[str, Any]] = []
    for archetype_id, rows in rows_by_archetype.items():
        if not rows or archetype_id not in archetypes:
            continue
        centroid = _mean_vector([row["embedding"] for row in rows])
        if not centroid:
            continue
        centroids.append({
            "archetype_id": archetype_id,
            "name": archetypes[archetype_id]["name"],
            "section": archetypes[archetype_id]["section"],
            "embedding": centroid,
        })
    return centroids


def _score_rows(
    rows: list[dict[str, Any]],
    centroids: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        match = _nearest_centroid(row["embedding"], row["section"], centroids)
        if match is None:
            continue
        predictions.append({
            "section": row["section"],
            "actual_archetype_id": row["archetype_id"],
            "predicted_archetype_id": match["archetype_id"],
            "score": match["score"],
        })
    return predictions


def _nearest_centroid(
    embedding: list[float],
    section: str,
    centroids: list[dict[str, Any]],
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for centroid in centroids:
        if centroid["section"] != section:
            continue
        score = _cosine_similarity(embedding, centroid["embedding"])
        if best is None or score > best["score"]:
            best = {
                "archetype_id": centroid["archetype_id"],
                "name": centroid["name"],
                "section": centroid["section"],
                "score": score,
            }
    return best


def _evaluate_thresholds(
    predictions: list[dict[str, Any]],
    sample_size: int,
) -> list[ValidationBucket]:
    buckets: list[ValidationBucket] = []
    for threshold in THRESHOLDS:
        attempted = 0
        correct = 0
        for prediction in predictions:
            if prediction["score"] < threshold:
                continue
            attempted += 1
            if prediction["predicted_archetype_id"] == prediction["actual_archetype_id"]:
                correct += 1
        buckets.append(ValidationBucket("ALL", threshold, attempted, correct, sample_size))
    return buckets


def _evaluate_sections(
    predictions: list[dict[str, Any]],
    threshold: float,
) -> list[ValidationBucket]:
    sample_by_section = Counter(prediction["section"] for prediction in predictions)
    attempted_by_section: Counter[str] = Counter()
    correct_by_section: Counter[str] = Counter()
    for prediction in predictions:
        section = prediction["section"]
        if prediction["score"] < threshold:
            continue
        attempted_by_section[section] += 1
        if prediction["predicted_archetype_id"] == prediction["actual_archetype_id"]:
            correct_by_section[section] += 1
    return [
        ValidationBucket(
            section,
            threshold,
            attempted_by_section[section],
            correct_by_section[section],
            sample_by_section[section],
        )
        for section in sorted(sample_by_section)
    ]


def _evaluate_sections_by_thresholds(
    predictions: list[dict[str, Any]],
    thresholds: list[ValidationBucket],
) -> list[ValidationBucket]:
    threshold_by_section = {bucket.section: bucket.threshold for bucket in thresholds}
    sample_by_section = Counter(prediction["section"] for prediction in predictions)
    attempted_by_section: Counter[str] = Counter()
    correct_by_section: Counter[str] = Counter()
    for prediction in predictions:
        section = prediction["section"]
        threshold = threshold_by_section.get(section)
        if threshold is None or prediction["score"] < threshold:
            continue
        attempted_by_section[section] += 1
        if prediction["predicted_archetype_id"] == prediction["actual_archetype_id"]:
            correct_by_section[section] += 1
    return [
        ValidationBucket(
            section,
            threshold_by_section.get(section, 0.0),
            attempted_by_section[section],
            correct_by_section[section],
            sample_by_section[section],
        )
        for section in sorted(sample_by_section)
    ]


def _classify_untagged(
    db: Database,
    centroids: list[dict[str, Any]],
    thresholds_by_section: dict[str, float],
) -> list[tuple[str, int, str, str, float]]:
    rows = db.connect().execute(
        """SELECT question_id, section, embedding_blob
           FROM questions
           WHERE is_holdout = 0
             AND archetype_id IS NULL
             AND embedding_blob IS NOT NULL
             AND length(embedding_blob) > 0
           ORDER BY section, question_id"""
    ).fetchall()
    assignments: list[tuple[str, int, str, str, float]] = []
    for row in rows:
        threshold = thresholds_by_section.get(str(row["section"]))
        if threshold is None:
            continue
        embedding = _embedding_from_blob(row["embedding_blob"])
        if embedding is None:
            continue
        match = _nearest_centroid(_normalize(embedding), row["section"], centroids)
        if match is None or match["score"] < threshold:
            continue
        assignments.append((
            row["question_id"],
            int(match["archetype_id"]),
            str(match["section"]),
            str(match["name"]),
            float(match["score"]),
        ))
    return assignments


def _assigned_by_section(
    assignments: list[tuple[str, int, str, str, float]],
) -> list[tuple[str, int]]:
    counts = Counter(section for _qid, _aid, section, _name, _score in assignments)
    return sorted(counts.items())


def _assigned_by_archetype(
    assignments: list[tuple[str, int, str, str, float]],
) -> list[tuple[str, str, int]]:
    counts = Counter((section, name) for _qid, _aid, section, name, _score in assignments)
    return [(section, name, count) for (section, name), count in sorted(counts.items())]


def _coverage_by_section(db: Database) -> list[tuple[str, int, int]]:
    pool = _build_web_safe_question_pool(db)
    coverage: list[tuple[str, int, int]] = []
    conn = db.connect()
    for section, questions in pool["questions_by_section"].items():
        question_ids = [question.question_id for question in questions]
        if not question_ids:
            coverage.append((section, 0, 0))
            continue
        placeholders = ",".join("?" for _ in question_ids)
        tagged = conn.execute(
            f"""SELECT COUNT(*) FROM questions
                WHERE question_id IN ({placeholders})
                  AND archetype_id IS NOT NULL""",
            question_ids,
        ).fetchone()[0]
        coverage.append((section, int(tagged or 0), len(question_ids)))
    return coverage


def _holdout_archetype_non_null(db: Database) -> int:
    return int(db.connect().execute(
        """SELECT COUNT(*) FROM questions
           WHERE is_holdout = 1 AND archetype_id IS NOT NULL"""
    ).fetchone()[0] or 0)


def _print_mapping(values: dict[str, int]) -> None:
    for key in sorted(values):
        print(f"  {key}={values[key]}")


def _print_pairs(values: list[tuple[str, int]]) -> None:
    if values:
        for key, count in values:
            print(f"  {key}={count}")
    else:
        print("  none=0")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/study.db", help="SQLite study DB path")
    args = parser.parse_args(argv)

    db = Database(args.db)
    report = build_atlas_stage2(db)
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
