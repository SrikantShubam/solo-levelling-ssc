"""GK/GA fact card generator — extracts factual knowledge from questions.

Fact cards are concise front/back pairs for memory recall, generated
from GK/GA questions in the corpus. Uses heuristics and pattern matching
to extract:
  - Who/What/Which questions → entity → answer
  - Capital/country facts
  - Event → year/date facts
  - Person → achievement facts
  - Terminology → definition facts
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .db import Database


@dataclass
class FactExtraction:
    """A single fact extracted from a question."""
    front_text: str
    back_text: str
    depth_level: str  # 'basic' or 'deep'
    source_question_id: str
    tier_scope: str  # 'tier1', 'tier2', 'both'
    cbic_relevance: bool = False


# ── Pattern extractors ────────────────────────────────────────────────
# Each returns (front, back) or None.


def _capital_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract capital-of-X facts."""
    m = re.search(
        r"what\s+is\s+the\s+capital\s+of\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        country = m.group(1).strip().rstrip(".")
        return (f"Capital of {country}", correct_answer)
    return None


def _who_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract person-related facts."""
    # "Who is X?" → Person description
    m = re.search(
        r"who\s+(?:is|was)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        person = m.group(1).strip().rstrip(".")
        return (f"Who is {person}?", correct_answer)

    # "Who discovered/invented/founded X?"
    verb_match = re.search(
        r"who\s+(discovered|invented|founded|built|wrote|authored|composed|designed|created)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if verb_match:
        verb = verb_match.group(1).lower()
        thing = verb_match.group(2).strip().rstrip(".")
        return (f"Who {verb} {thing}?", correct_answer)

    # "Who is known as/famous for X"
    m = re.search(
        r"who\s+is\s+(?:known\s+as|famous\s+for|called)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        alias = m.group(1).strip().rstrip(".")
        return (f"Who is known as {alias}?", correct_answer)

    # "X is the first person to Y"
    m = re.search(
        r"(?:first|only)\s+(?:person|man|woman|indian|president|prime\s*minister)\s+(?:to|in)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        achievement = m.group(1).strip().rstrip(".")
        return (f"Who was the first {achievement}?", correct_answer)

    return None


def _when_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract date/year facts."""

    # Verb-specific patterns: "When was X established/founded/formed?"
    verb_map = {
        "founded": "founded",
        "established": "established",
        "formed": "formed",
        "set up": "set up",
        "created": "created",
        "discovered": "discovered",
        "invented": "invented",
        "introduced": "introduced",
        "launched": "launched",
        "born": "born",
        "died": "died",
        "elected": "elected",
        "appointed": "appointed",
    }
    verbs_alt = "|".join(verb_map.keys())
    m = re.search(
        rf"when\s+(?:was|were|did)\s+(.+?)\s+(?:{verbs_alt})\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        entity = m.group(1).strip().rstrip(".")
        # Determine verb from the original text
        for v_pattern, v_display in verb_map.items():
            if re.search(rf"\b{v_pattern}\b", text, re.IGNORECASE):
                return (f"When was {entity} {v_display}?", correct_answer)
        return (f"When was {entity}?", correct_answer)

    # "X was established/founded in which year"
    m = re.search(
        r"(.+?)\s+(?:was\s+)?(?:established|founded|formed|set\s*up|created)\s+in\s+(?:which|what)\s+year\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        entity = m.group(1).strip().rstrip(".")
        return (f"In which year was {entity} established?", correct_answer)

    # "X was born in which year"
    m = re.search(
        r"(.+?)\s+(?:was\s+)?born\s+(?:in\s+)?(?:which|what)\s+year\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        person = m.group(1).strip().rstrip(".")
        return (f"In which year was {person} born?", correct_answer)

    # "In which year did X happen?" — preserve original wording
    m = re.search(
        r"in\s+which\s+year\s+(did|was)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        aux = m.group(1).lower()
        event = m.group(2).strip().rstrip(".")
        # Only append "happen" if the event phrase doesn't already have a verb
        if not re.search(r"\b(get|become|take\s*place|occur|happen)\b", event, re.IGNORECASE):
            return (f"In which year did {event} happen?", correct_answer)
        return (f"In which year {aux} {event}?", correct_answer)

    # "When did X happen?" — use the original wording
    m = re.search(
        r"when\s+(did|was|were)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        aux = m.group(1).lower()
        event = m.group(2).strip().rstrip(".")
        return (f"When {aux} {event}?", correct_answer)

    return None


def _where_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract location facts."""
    m = re.search(
        r"where\s+(?:is|are|was|were)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        thing = m.group(1).strip().rstrip(".")
        return (f"Where is {thing}?", correct_answer)

    # "X is located in?"
    m = re.search(
        r"(.+?)\s+is\s+(?:located\s+in|situated\s+in)\s+(?:which|what)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        thing = m.group(1).strip().rstrip(".")
        return (f"Where is {thing} located?", correct_answer)

    return None


def _what_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract definition and terminology facts."""
    # "What is X?" → definition
    m = re.search(
        r"what\s+is\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        term = m.group(1).strip().rstrip(".")
        return (f"Define: {term}", correct_answer)

    # "What does X stand for?" → acronym
    m = re.search(
        r"what\s+(?:does|is)\s+(.+?)\s+(?:stand\s+for|the\s+abbreviation\s+of)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        acronym = m.group(1).strip().rstrip(".")
        return (f"What does {acronym} stand for?", correct_answer)

    # "What is the name of X?"
    m = re.search(
        r"what\s+is\s+the\s+name\s+of\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        thing = m.group(1).strip().rstrip(".")
        return (f"Name of {thing}", correct_answer)

    return None


def _which_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract 'which of the following' facts."""
    # "Which of the following is X?"
    m = re.search(
        r"which\s+of\s+the\s+following\s+(?:is|are|was|were)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        category = m.group(1).strip().rstrip(".").lower()
        return (f"Which is {category}?", correct_answer)

    # "Which country/state/city X?"
    m = re.search(
        r"which\s+(country|state|city|river|mountain|lake|national\s*park|temple)\s+(?:is|was|has|does|of)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        kind = m.group(1).strip()
        desc = m.group(2).strip().rstrip(".")
        return (f"Which {kind} {desc}?", correct_answer)

    return None


def _how_many_fact(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract quantitative facts."""
    m = re.search(
        r"how\s+many\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        subject = m.group(1).strip().rstrip(".")
        return (f"How many {subject}?", correct_answer)
    return None


def _largest_longest_highest(text: str, correct_answer: str) -> tuple[str, str] | None:
    """Extract superlative facts."""
    m = re.search(
        r"(?:largest|longest|highest|biggest|tallest|deepest|oldest|newest|smallest|shortest)\s+(.+?)\??\s*$",
        text, re.IGNORECASE,
    )
    if m:
        subject = m.group(1).strip().rstrip(".")
        # Determine the superlative type from the question
        superlative = re.search(
            r"(largest|longest|highest|biggest|tallest|deepest|oldest|newest|smallest|shortest)",
            text, re.IGNORECASE,
        ).group(1).capitalize()  # type: ignore[union-attr]
        return (f"{superlative} {subject}", correct_answer)
    return None


# Ordered list of extractors to try (first match wins)
_EXTRACTORS = [
    ("capital", _capital_fact),
    ("who", _who_fact),
    ("when", _when_fact),
    ("where", _where_fact),
    ("what", _what_fact),
    ("which", _which_fact),
    ("how_many", _how_many_fact),
    ("superlative", _largest_longest_highest),
]


# ── Public API ────────────────────────────────────────────────────────


def extract_fact(
    question_text: str,
    correct_answer: str,
    section: str = "GK/GA",
) -> FactExtraction | None:
    """Try to extract a fact from a question.

    Args:
        question_text: The question text to extract from.
        correct_answer: The correct answer text (not just label).
        section: The section (only GK/GA questions produce fact cards).

    Returns:
        FactExtraction if a fact was extracted, None otherwise.
    """
    if section != "GK/GA":
        return None

    clean_text = _clean_text(question_text)

    for name, extractor in _EXTRACTORS:
        result = extractor(clean_text, correct_answer)
        if result:
            front, back = result
            depth = "basic" if len(back) < 100 else "deep"
            return FactExtraction(
                front_text=front,
                back_text=back,
                depth_level=depth,
                source_question_id="",
                tier_scope="both",
            )

    # Fallback: use first sentence as a statement
    first_sentence = clean_text.split(".")[0].strip()
    if first_sentence and len(correct_answer) > 1:
        # Try "A is B" pattern
        m = re.match(
            r"^(.+?)\s+(?:is\s+(?:a|an|the|also\s+)?(?:known\s+as\s+)?|refers?\s+to\s+|means?\s+)+\s*(.+)",
            first_sentence, re.IGNORECASE,
        )
        if m:
            return FactExtraction(
                front_text=m.group(1).strip(),
                back_text=correct_answer,
                depth_level="basic",
                source_question_id="",
                tier_scope="both",
            )

    return None


def generate_fact_cards(
    db: Database,
    section: str = "GK/GA",
    max_cards: int = 500,
) -> dict[str, int]:
    """Generate fact cards from GK/GA questions in the database.

    Args:
        db: Database instance.
        section: Section to extract facts from (default: GK/GA).
        max_cards: Maximum number of fact cards to generate.

    Returns:
        Dict with keys: generated, skipped, duplicate (already existed).
    """
    conn = db.connect()

    # Get questions from the given section that don't already have a fact card
    rows = conn.execute(
        """SELECT q.question_id, q.question_text, q.correct_option_text,
                  q.correct_option_label, q.options_json, q.tier
           FROM questions q
           LEFT JOIN fact_cards f ON f.question_id = q.question_id
           WHERE q.section = ?
             AND f.card_id IS NULL
           LIMIT ?""",
        (section, max_cards * 2),  # request more to account for extraction failures
    ).fetchall()

    import json
    from .models import Option

    generated = 0
    skipped = 0
    duplicate = 0

    for row in rows:
        if generated >= max_cards:
            break

        question_text = row["question_text"]
        tier = row["tier"]

        # Get correct answer text
        correct_text = row["correct_option_text"]
        if not correct_text:
            # Parse from options_json
            options_data = json.loads(row["options_json"])
            for opt in options_data:
                if opt["label"] == row["correct_option_label"]:
                    correct_text = opt["text"]
                    break

        if not correct_text:
            skipped += 1
            continue

        fact = extract_fact(question_text, correct_text, section)
        if fact is None:
            skipped += 1
            continue

        # Check for duplicate by front_text similarity
        existing = conn.execute(
            "SELECT card_id FROM fact_cards WHERE front_text = ? AND back_text = ?",
            (fact.front_text, fact.back_text),
        ).fetchone()

        if existing:
            duplicate += 1
            continue

        # Insert
        conn.execute(
            """INSERT INTO fact_cards
               (question_id, front_text, back_text, tier_scope, depth_level,
                cbic_relevance, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (row["question_id"], fact.front_text, fact.back_text,
             tier, fact.depth_level, int(fact.cbic_relevance), "corpus"),
        )
        generated += 1

    conn.commit()

    return {"generated": generated, "skipped": skipped, "duplicate": duplicate}


def get_due_fact_cards(
    db: Database,
    count: int = 10,
    tier: str | None = None,
) -> list[dict[str, Any]]:
    """Get fact cards due for SM-2 review.

    Args:
        db: Database instance.
        count: Number of cards to return.
        tier: Optional tier filter.

    Returns:
        List of dicts with card_id, front_text, back_text, and SM-2 state.
    """
    conn = db.connect()
    today = __import__("datetime").date.today().isoformat()

    conditions = ["1=1"]
    params: list[Any] = []

    if tier:
        conditions.append("(f.tier_scope = ? OR f.tier_scope = 'both')")
        params.append(tier)

    where = " AND ".join(conditions)

    rows = conn.execute(
        f"""SELECT f.*, s.next_review, s.easiness, s.interval_days, s.repetitions
            FROM fact_cards f
            LEFT JOIN sm2_state s ON s.entity_type = 'fact_card' AND s.entity_id = CAST(f.card_id AS TEXT)
            WHERE {where}
              AND (s.next_review IS NULL OR s.next_review <= ?)
            ORDER BY
              CASE WHEN s.next_review IS NULL THEN 0 ELSE 1 END,
              s.next_review ASC
            LIMIT ?""",
        params + [today, count],
    ).fetchall()

    return [
        {
            "card_id": r["card_id"],
            "front_text": r["front_text"],
            "back_text": r["back_text"],
            "depth_level": r["depth_level"],
            "next_review": r["next_review"],
        }
        for r in rows
    ]


def get_fact_card_stats(db: Database) -> dict[str, int]:
    """Return summary stats about fact cards in the database.

    Returns:
        Dict with keys: total, by_tier, by_depth.
    """
    conn = db.connect()
    total = conn.execute("SELECT COUNT(*) as c FROM fact_cards").fetchone()["c"]

    tier_counts: dict[str, int] = {}
    for row in conn.execute(
        "SELECT tier_scope, COUNT(*) as c FROM fact_cards GROUP BY tier_scope"
    ).fetchall():
        tier_counts[row["tier_scope"]] = row["c"]

    depth_counts: dict[str, int] = {}
    for row in conn.execute(
        "SELECT depth_level, COUNT(*) as c FROM fact_cards GROUP BY depth_level"
    ).fetchall():
        depth_counts[row["depth_level"]] = row["c"]

    return {"total": total, "by_tier": tier_counts, "by_depth": depth_counts}


# ── Internal helpers ──────────────────────────────────────────────────


def _clean_text(text: str) -> str:
    """Clean question text for fact extraction."""
    # Remove option labels like "1." "2." "(a)" etc at start
    text = re.sub(r"^\s*(?:\d+[.)]|\([a-d]\))\s*", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
