"""Tests for the embeddings module.

Skips tests requiring sentence-transformers model loading if the
model import fails (CI environments without full ML stack).
"""

from __future__ import annotations

from ssc_study.embeddings import (
    compute_text_embedding,
    find_similar_questions,
    get_embedding_stats,
    update_all_embeddings,
)


class TestComputeTextEmbedding:
    """compute_text_embedding returns valid vectors."""

    def test_returns_float_list(self):
        """Returns a list of floats."""
        vec = compute_text_embedding("test")
        assert isinstance(vec, list)
        assert len(vec) > 0
        assert all(isinstance(v, float) for v in vec)

    def test_same_input_same_vector(self):
        """Same input produces roughly the same vector (deterministic)."""
        v1 = compute_text_embedding("What is the capital of France?")
        v2 = compute_text_embedding("What is the capital of France?")
        assert len(v1) == len(v2)

        # Cosine similarity should be very close to 1.0
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = sum(a * a for a in v1) ** 0.5
        n2 = sum(b * b for b in v2) ** 0.5
        sim = dot / (n1 * n2) if n1 * n2 > 0 else 0
        assert sim > 0.999, f"Expected ~1.0 similarity, got {sim}"

    def test_different_inputs_different(self):
        """Different inputs produce different vectors."""
        v1 = compute_text_embedding("Mathematics algebra equation solving")
        v2 = compute_text_embedding("History ancient civilizations Rome")
        # Should be less than perfectly similar
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = sum(a * a for a in v1) ** 0.5
        n2 = sum(b * b for b in v2) ** 0.5
        sim = dot / (n1 * n2) if n1 * n2 > 0 else 0
        # These should be semantically different enough
        assert sim < 0.95, f"Expected lower similarity, got {sim}"

    def test_empty_string(self):
        """Empty string still produces a vector."""
        vec = compute_text_embedding("")
        assert len(vec) > 0


class TestGetEmbeddingStats:
    """get_embedding_stats returns correct counts."""

    def test_zero_when_no_embeddings(self, seeded_db):
        """No embeddings returns zero counts."""
        stats = get_embedding_stats(seeded_db)
        assert stats["without_embeddings"] > 0
        assert stats["with_embeddings"] == 0

    def test_counts_after_update(self, seeded_db):
        """After update, embeddings exist."""
        update_all_embeddings(seeded_db, batch_size=50)
        stats = get_embedding_stats(seeded_db)
        assert stats["with_embeddings"] > 0
        assert stats["without_embeddings"] == 0


class TestFindSimilarQuestions:
    """find_similar_questions returns relevant results."""

    def test_returns_list(self, seeded_db):
        """Returns a list even when question doesn't exist."""
        # Need to compute embeddings first
        update_all_embeddings(seeded_db, batch_size=50)

        results = find_similar_questions(seeded_db, "q1", top_k=3)
        assert isinstance(results, list)

    def test_nonexistent_question(self, seeded_db):
        """Non-existent question returns empty list."""
        results = find_similar_questions(seeded_db, "nonexistent", top_k=3)
        assert results == []


class TestUpdateAllEmbeddings:
    """update_all_embeddings batch update."""

    def test_processes_all(self, seeded_db):
        """All questions without embeddings get one."""
        result = update_all_embeddings(seeded_db, batch_size=50)
        assert result["computed"] > 0
        assert result["failed"] == 0

    def test_idempotent(self, seeded_db):
        """Running twice on same DB skips already-computed."""
        r1 = update_all_embeddings(seeded_db, batch_size=50)
        r2 = update_all_embeddings(seeded_db, batch_size=50)
        assert r2["computed"] == 0  # all already done
