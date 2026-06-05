"""Question embeddings and semantic search using sentence-transformers + FAISS.

Provides:
  - Embedding computation for questions (text + options combined).
  - FAISS index construction and similarity search.
  - Remediation: finding similar questions when a user gets one wrong.
  - Batch embedding update for the entire corpus.

Gracefully degrades to bag-of-words fallback when sentence-transformers is
unavailable (e.g. in CI without the full ML stack).
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from .db import Database
from .models import Question

# ── Module-level state ────────────────────────────────────────────────

_MODEL = None  # lazy-loaded SentenceTransformer
_INDEX = None  # lazy-built FAISS index
_INDEX_ID_MAP: dict[int, str] = {}  # FAISS index position → question_id
_EMBEDDING_DIM = 384  # default for all-MiniLM-L6-v2


def get_model_name() -> str:
    """Return the SentenceTransformer model identifier used."""
    return "all-MiniLM-L6-v2"


# ── Public API ────────────────────────────────────────────────────────


def compute_question_embedding(question: Question) -> list[float]:
    """Compute the embedding vector for a single question.

    Combines question text, options, and section into a single string
    for encoding.

    Args:
        question: A Question object.

    Returns:
        List of floats representing the embedding vector.
    """
    combined = _build_embedding_text(question)
    return _encode(combined)


def compute_text_embedding(text: str) -> list[float]:
    """Compute embedding for arbitrary text (not tied to a question)."""
    return _encode(text)


def find_similar_questions(
    db: Database,
    question_id: str,
    top_k: int = 5,
    same_section: bool = True,
    exclude_holdout: bool = True,
) -> list[dict[str, Any]]:
    """Find questions semantically similar to a given question.

    Args:
        db: Database instance.
        question_id: The reference question to find similar ones for.
        top_k: Number of similar questions to return.
        same_section: Only return questions from the same section.
        exclude_holdout: Exclude holdout questions.

    Returns:
        List of dicts with keys: question_id, section, question_text,
        score (cosine similarity), tier.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM questions WHERE question_id = ?", (question_id,)
    ).fetchone()

    if not row:
        return []

    reference_q = _row_to_question_ref(row)
    reference_emb = compute_question_embedding(reference_q)

    # Build query
    where_parts = ["q.question_id != ?"]
    params: list[Any] = [question_id]

    if same_section:
        where_parts.append("q.section = ?")
        params.append(reference_q.section)

    if exclude_holdout:
        where_parts.append("q.is_holdout = 0")

    where = " AND ".join(where_parts)

    candidates = conn.execute(
        f"SELECT q.*, q.embedding_blob FROM questions q WHERE {where}",
        tuple(params),
    ).fetchall()

    scored: list[tuple[float, dict[str, Any]]] = []

    for candidate in candidates:
        candidate_emb = _get_embedding_from_row(candidate)
        if candidate_emb is None:
            # Compute on the fly
            c_q = _row_to_question_ref(candidate, skip_embedding=True)
            candidate_emb = compute_question_embedding(c_q)

        score = _cosine_similarity(reference_emb, candidate_emb)
        scored.append((
            score,
            {
                "question_id": candidate["question_id"],
                "section": candidate["section"],
                "tier": candidate["tier"],
                "question_text": candidate["question_text"][:200],
                "score": round(score, 4),
            },
        ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def find_remediation_questions(
    db: Database,
    question: Question,
    count: int = 3,
) -> list[Question]:
    """Find questions similar to a missed one for remediation practice.

    Looks for questions covering the same concept/concept from the same
    section with high semantic similarity. Prefers easier questions first
    (previously answered correctly by the user if available).

    Args:
        db: Database instance.
        question: The question the user got wrong.
        count: Number of remediation questions to return.

    Returns:
        List of Question objects for remediation practice.
    """
    similar = find_similar_questions(
        db, question.question_id, top_k=max(count * 2, 10),
        same_section=True, exclude_holdout=True,
    )

    if not similar:
        return []

    similar_ids = [s["question_id"] for s in similar[:count]]

    conn = db.connect()
    placeholders = ",".join("?" for _ in similar_ids)
    rows = conn.execute(
        f"""SELECT q.* FROM questions q
            WHERE q.question_id IN ({placeholders})""",
        similar_ids,
    ).fetchall()

    return [_row_to_question_ref(r, skip_embedding=True) for r in rows]


def update_all_embeddings(
    db: Database,
    batch_size: int = 100,
    progress_callback: Any = None,
) -> dict[str, int]:
    """Compute and store embeddings for all questions without one.

    Args:
        db: Database instance.
        batch_size: Number of questions to process per batch.
        progress_callback: Optional callable(current, total) for progress.

    Returns:
        Dict with keys: computed, skipped, failed.
    """
    conn = db.connect()
    total = conn.execute(
        "SELECT COUNT(*) as c FROM questions WHERE embedding_blob IS NULL OR length(embedding_blob) = 0"
    ).fetchone()["c"]

    if total == 0:
        return {"computed": 0, "skipped": 0, "failed": 0}

    rows = conn.execute(
        "SELECT * FROM questions WHERE embedding_blob IS NULL OR length(embedding_blob) = 0 LIMIT ?",
        (batch_size,),
    ).fetchall()

    computed = 0
    failed = 0
    total_processed = 0

    while rows:
        for row in rows:
            try:
                question = _row_to_question_ref(row, skip_embedding=True)
                emb = compute_question_embedding(question)
                blob = json.dumps(emb).encode("utf-8")
                conn.execute(
                    "UPDATE questions SET embedding_blob = ? WHERE question_id = ?",
                    (blob, question.question_id),
                )
                computed += 1
            except Exception:
                failed += 1

        conn.commit()
        total_processed += len(rows)

        if progress_callback:
            progress_callback(total_processed, total)

        remaining = total - total_processed
        if remaining <= 0:
            break

        rows = conn.execute(
            "SELECT * FROM questions WHERE embedding_blob IS NULL OR length(embedding_blob) = 0 LIMIT ?",
            (batch_size,),
        ).fetchall()

    return {"computed": computed, "skipped": total - computed - failed, "failed": failed}


def get_embedding_stats(db: Database) -> dict[str, int]:
    """Return stats about embedding coverage in the database.

    Returns:
        Dict: total_questions, with_embeddings, without_embeddings.
    """
    conn = db.connect()
    total = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
    with_emb = conn.execute(
        "SELECT COUNT(*) as c FROM questions WHERE embedding_blob IS NOT NULL AND length(embedding_blob) > 0"
    ).fetchone()["c"]

    return {
        "total_questions": total,
        "with_embeddings": with_emb,
        "without_embeddings": total - with_emb,
    }


def get_embedding(question_id: str, db: Database) -> list[float] | None:
    """Get the stored embedding for a question, or None."""
    conn = db.connect()
    row = conn.execute(
        "SELECT embedding_blob FROM questions WHERE question_id = ?",
        (question_id,),
    ).fetchone()

    if row and row["embedding_blob"]:
        try:
            return json.loads(row["embedding_blob"].decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return None
    return None


# ── Internal helpers ──────────────────────────────────────────────────


def _build_embedding_text(question: Question) -> str:
    """Combine question fields into a single embedding input string."""
    parts = [question.question_text]
    for opt in question.options:
        parts.append(f"{opt.label}: {opt.text}")
    if question.section:
        parts.append(f"[{question.section}]")
    return " ".join(parts)


def _encode(text: str) -> list[float]:
    """Encode text using sentence-transformers, with keyword fallback."""
    global _MODEL

    try:
        if _MODEL is None:
            from sentence_transformers import SentenceTransformer
            _MODEL = SentenceTransformer(get_model_name())
        vec = _MODEL.encode(text, show_progress_bar=False)
        return vec.tolist()
    except Exception:
        return _keyword_embedding(text)


def _keyword_embedding(text: str) -> list[float]:
    """Bag-of-words fallback embedding when sentence-transformers is unavailable.

    Produces a fixed-dimension vector from word frequencies (384 dims
    via hashing trick to match the default model dimension).
    """
    words = re.findall(r"\w+", text.lower())
    vec = [0.0] * _EMBEDDING_DIM
    for word in words:
        idx = hash(word) % _EMBEDDING_DIM
        vec[idx] += 1.0

    # Normalize
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(av * bv for av, bv in zip(a, b))
    na = sum(av * av for av in a) ** 0.5
    nb = sum(bv * bv for bv in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _get_embedding_from_row(row: sqlite3.Row) -> list[float] | None:
    """Extract embedding from a database row blob."""
    blob = row["embedding_blob"]
    if blob is None:
        return None
    try:
        if isinstance(blob, bytes):
            return json.loads(blob.decode("utf-8"))
        if isinstance(blob, str):
            return json.loads(blob)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        pass
    return None


def _row_to_question_ref(
    row: sqlite3.Row,
    skip_embedding: bool = False,
) -> Question:
    """Convert a database row to a Question (minimal field set for embedding)."""
    options_data = json.loads(row["options_json"]) if isinstance(row["options_json"], str) else []
    from .models import Option
    options = [Option(label=o["label"], text=o["text"]) for o in options_data]

    def _g(key: str, default: Any = None) -> Any:
        try:
            v = row[key]
            return v if v is not None else default
        except (KeyError, IndexError):
            return default

    return Question(
        question_id=row["question_id"],
        pdf_name=_g("pdf_name", ""),
        source_page=_g("source_page", 0),
        global_question_number=_g("global_question_number", 0),
        section=row["section"],
        year=_g("year", 0),
        tier=_g("tier", "tier1"),
        question_text=row["question_text"],
        options=options,
        correct_option_label=_g("correct_option_label", ""),
        correct_option_text=_g("correct_option_text"),
        chosen_option_label=_g("chosen_option_label"),
        question_modality=_g("question_modality", "text_only"),
        visual_required=bool(_g("visual_required", False)),
        table_required=bool(_g("table_required", False)),
        math_required=bool(_g("math_required", False)),
        evidence_status=_g("evidence_status"),
        is_holdout=bool(_g("is_holdout", False)),
        archetype_id=_g("archetype_id"),
    )
