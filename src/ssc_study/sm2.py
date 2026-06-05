"""Pure SuperMemo 2 (SM-2) spaced repetition algorithm.

Reference: Piotr Woźniak, "Application of a computer to improve the results
obtained in working with the SuperMemo method" (1987/1990).

Key rules (from the original spec):
  - After a CORRECT response (quality >= 3):
      * repetitions += 1
      * If repetitions == 0 (shouldn't happen): interval = 1
      * If repetitions == 1: interval = 6
      * If repetitions >= 2: interval = ceil(previous_interval * easiness)
      * easiness = max(1.3, prev_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
  - After an INCORRECT response (quality < 3):
      * repetitions = 0
      * interval = 1
      * easiness is NOT changed (critical — EF is frozen on failure)
  - Intervals use ceil() (round UP), not round() or floor()
  - No upper bound on easiness factor; only lower bound at 1.3
"""

from __future__ import annotations

from .models import SM2Result, SM2State


def compute_sm2(quality: int, prev: SM2State, today: str | None = None) -> SM2Result:
    """Compute the next SM-2 state after a review of the given quality.

    Args:
        quality: Response quality, 0–5.
            5 = perfect, 4 = correct with hesitation, 3 = correct with difficulty,
            2 = incorrect but answer upon seeing correct, 1 = incorrect but seems familiar,
            0 = complete blackout.
        prev: Previous SM-2 state.
        today: ISO date string (YYYY-MM-DD) for the review date.
               Uses the current local date if omitted.

    Returns:
        The new SM-2 state after this review.

    Raises:
        ValueError: If quality is not in the range 0–5.
    """
    if not isinstance(quality, int) or quality < 0 or quality > 5:
        raise ValueError(f"quality must be an integer 0–5, got {quality!r}")

    if today is None:
        from datetime import date
        today = date.today().isoformat()

    if quality >= 3:
        # Correct response
        n = prev.repetitions + 1

        if n == 1:
            interval = 1
        elif n == 2:
            interval = 6
        else:
            # Use ceil() — round UP, NOT round() or floor()
            raw = prev.interval_days * prev.easiness
            interval = int(raw) if raw == int(raw) else int(raw) + 1

        # Compute new easiness factor
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        delta = 5 - quality
        ef_change = 0.1 - delta * (0.08 + delta * 0.02)
        new_easiness = prev.easiness + ef_change
        if new_easiness < 1.3:
            new_easiness = 1.3
        # No upper bound — easiness can grow unbounded

        return SM2Result(
            easiness=round(new_easiness, 4),
            interval_days=interval,
            repetitions=n,
            next_review=add_days(today, interval),
        )
    else:
        # Incorrect response — EF is FROZEN (critical: do NOT change easiness)
        return SM2Result(
            easiness=prev.easiness,
            interval_days=1,
            repetitions=0,
            next_review=add_days(today, 1),
        )


def quality_from_performance(
    is_correct: bool,
    time_spent_seconds: int,
    threshold_fast: int = 15,
    threshold_slow: int = 60,
) -> int:
    """Heuristic to map quiz performance to SM-2 quality score.

    This is an opinionated mapping — not part of the original SM-2 spec.

    Mapping:
      - Correct + fast (<15s)         → 5 (perfect)
      - Correct + normal (15-60s)     → 4 (correct with hesitation)
      - Correct + slow (>60s)         → 3 (correct with difficulty)
      - Incorrect + slow              → 2 (incorrect; answer was familiar)
      - Incorrect + normal            → 1 (incorrect but seems familiar)
      - Incorrect + fast              → 0 (complete blackout / guess)
    """
    if is_correct:
        if time_spent_seconds < threshold_fast:
            return 5
        elif time_spent_seconds <= threshold_slow:
            return 4
        else:
            return 3
    else:
        if time_spent_seconds > threshold_slow:
            return 2
        elif time_spent_seconds >= threshold_fast:
            return 1
        else:
            return 0


def add_days(iso_date: str, days: int) -> str:
    """Add N days to an ISO date string, returning a new ISO date string."""
    from datetime import date, timedelta
    d = date.fromisoformat(iso_date)
    return (d + timedelta(days=days)).isoformat()
