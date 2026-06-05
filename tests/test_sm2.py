"""SM-2 algorithm reference tests — canonical SuperMemo 2 (Woźniak 1987).

These tests encode the 6 critical pitfalls documented in the plan:
  P1: EF frozen on failure (q < 3)
  P2: ceil() rounding, not round() or floor()
  P3: No EF upper bound (only lower at 1.3)
  P4: n==0 → 1d, n==1 → 6d distinct cases
  P5: Reset n on failure but keep EF
  P6: Quality scale 0-5 integers only
"""

from __future__ import annotations

from datetime import date

import pytest

from ssc_study.models import SM2State
from ssc_study.sm2 import add_days, compute_sm2, quality_from_performance

TODAY = date.today().isoformat()


# ── Reference table per original SM-2 spec ──────────────────────────────

REFERENCE_CASES: list[tuple] = [
    # (quality, prev_EF, prev_interval, prev_reps, expected_EF, expected_I, expected_reps, description)
    (5, 2.5, 0, 0, 2.6,   1,  1,  "First correct: I=1, EF rises 0.1"),
    (4, 2.5, 0, 0, 2.5,   1,  1,  "First correct q=4: EF unchanged (delta=0)"),
    (3, 2.5, 0, 0, 2.36,  1,  1,  "First correct q=3: EF drops by 0.14"),
    (5, 2.6, 1, 1, 2.7,   6,  2,  "Second correct: I jumps to 6"),
    # P2: ceil — 6 * 2.7 = 16.2 → 17, NOT round=16 or floor=16
    (5, 2.7, 6, 2, 2.8,  17,  3,  "Third correct: I=ceil(6*2.7)=ceil(16.2)=17"),
    # P2: ceil — 17 * 2.8 = 47.6 → 48
    (5, 2.8, 17, 3, 2.9, 48,  4,  "Fourth: I=ceil(17*2.8)=ceil(47.6)=48"),
    # P1 + P5: Failure freezes EF, resets n
    (0, 2.5, 30, 5, 2.5,   1,  0,  "Failed q=0: n→0 I→1 EF stays 2.5"),
    (2, 2.5, 30, 5, 2.5,   1,  0,  "Failed q=2: same — EF unchanged"),
    # P3: EF floor is a LOWER bound — EF rises on q=5 even from floor
    # I uses OLD EF: ceil(8*1.3)=11, then EF rises to 1.4
    (5, 1.3,  8, 3, 1.4,  11,  4,  "EF floor: I=ceil(8*1.3)=11, EF rises 1.3→1.4"),
    # At floor: I=ceil(11*1.3)=15, EF rises 1.3→1.4
    (5, 1.3, 11, 4, 1.4,  15,  5,  "EF floor: I=ceil(11*1.3)=15, EF 1.3→1.4"),
    # P3: No upper bound — EF grows with perfect scores
    # I=ceil(48*2.9)=ceil(139.2)=140, EF 2.9→3.0
    (5, 2.9, 48, 4, 3.0, 140,  5,  "EF grows: I=ceil(48*2.9)=140, EF 2.9→3.0"),
    # I=ceil(140*3.0)=420, EF 3.0→3.1
    (5, 3.0, 140, 5, 3.1, 420, 6,  "EF unbounded: I=ceil(140*3.0)=420, EF 3.0→3.1"),
]


@pytest.mark.parametrize(
    "quality,ef,interval,reps,exp_ef,exp_i,exp_reps,desc",
    REFERENCE_CASES,
)
def test_sm2_reference(
    quality, ef, interval, reps, exp_ef, exp_i, exp_reps, desc
):
    """Each reference case must match the canonical SM-2 spec exactly."""
    prev = SM2State(
        easiness=ef, interval_days=interval, repetitions=reps
    )
    result = compute_sm2(quality, prev, today=TODAY)

    assert result.repetitions == exp_reps, (
        f"{desc}: expected reps={exp_reps}, got {result.repetitions}"
    )
    assert result.interval_days == exp_i, (
        f"{desc}: expected I={exp_i}, got {result.interval_days}"
    )
    assert result.easiness == exp_ef, (
        f"{desc}: expected EF={exp_ef}, got {result.easiness}"
    )
    # next_review must be today + interval
    expected_review = add_days(TODAY, exp_i)
    assert result.next_review == expected_review, (
        f"{desc}: expected next_review={expected_review}, got {result.next_review}"
    )


# ── Pitfall-specific tests ──────────────────────────────────────────────


def test_p1_ef_frozen_on_failure():
    """P1: EF must NOT change when quality < 3."""
    prev = SM2State(easiness=2.8, interval_days=30, repetitions=5)

    for q in (0, 1, 2):
        result = compute_sm2(q, prev, today=TODAY)
        assert result.easiness == 2.8, (
            f"P1 VIOLATION: q={q} changed EF from 2.8 to {result.easiness}"
        )


def test_p2_ceil_rounding():
    """P2: Interval uses ceil(), never round() or floor()."""
    # 16.2 → 17, NOT 16
    prev = SM2State(easiness=2.7, interval_days=6, repetitions=2)
    result = compute_sm2(5, prev, today=TODAY)
    assert result.interval_days == 17, (
        f"P2 VIOLATION: ceil(6*2.7)=17, got {result.interval_days}"
    )

    # 47.6 → 48, NOT 47
    prev2 = SM2State(easiness=2.8, interval_days=17, repetitions=3)
    result2 = compute_sm2(5, prev2, today=TODAY)
    assert result2.interval_days == 48, (
        f"P2 VIOLATION: ceil(17*2.8)=48, got {result2.interval_days}"
    )

    # Exact integer: 4.0 → 4, NOT 5
    prev3 = SM2State(easiness=2.0, interval_days=2, repetitions=3)
    result3 = compute_sm2(5, prev3, today=TODAY)
    assert result3.interval_days == 4, (
        f"P2 VIOLATION: ceil(2*2.0)=4, got {result3.interval_days}"
    )


def test_p3_no_ef_upper_bound():
    """P3: EF has no upper bound — only lower at 1.3."""
    # After 12 perfect reviews, EF should be above 3.5
    ef = 2.5
    interval = 0
    reps = 0
    for _ in range(12):
        prev = SM2State(easiness=ef, interval_days=interval, repetitions=reps)
        result = compute_sm2(5, prev, today=TODAY)
        ef = result.easiness
        interval = result.interval_days
        reps = result.repetitions

    # After 12 perfect reviews, EF should be above 3.5 (no cap)
    assert ef > 3.5, f"P3 VIOLATION: EF capped — got {ef} after 12 perfect reviews"


def test_p3_ef_lower_bound():
    """P3: EF floor at 1.3 — never goes below."""
    # Worst case: quality 3 repeatedly (EF drops each time)
    ef = 2.5
    interval = 0
    reps = 0
    for i in range(5):
        prev = SM2State(easiness=ef, interval_days=interval, repetitions=reps)
        result = compute_sm2(3, prev, today=TODAY)
        ef = result.easiness
        interval = result.interval_days
        reps = result.repetitions
        if ef == 1.3:
            break

    assert ef >= 1.3, f"P3 VIOLATION: EF={ef} went below floor 1.3"


def test_p4_distinct_n0_n1():
    """P4: n==0 → 1d, n==1 → 6d (distinct, don't collapse)."""
    # n==0 → 1
    r1 = compute_sm2(5, SM2State(easiness=2.5, interval_days=0, repetitions=0), today=TODAY)
    assert r1.interval_days == 1, f"P4: n=0 should give I=1, got {r1.interval_days}"
    assert r1.repetitions == 1

    # n==1 → 6
    r2 = compute_sm2(5, SM2State(easiness=2.6, interval_days=1, repetitions=1), today=TODAY)
    assert r2.interval_days == 6, f"P4: n=1 should give I=6, got {r2.interval_days}"
    assert r2.repetitions == 2


def test_p5_reset_n_keep_ef():
    """P5: On failure, n resets to 0 but EF persists."""
    prev = SM2State(easiness=2.9, interval_days=40, repetitions=6)
    result = compute_sm2(0, prev, today=TODAY)

    assert result.repetitions == 0, (
        f"P5 VIOLATION: n should reset to 0, got {result.repetitions}"
    )
    assert result.easiness == 2.9, (
        f"P5 VIOLATION: EF should stay 2.9, got {result.easiness}"
    )
    assert result.interval_days == 1


def test_p6_quality_validation():
    """P6: Quality must be integer 0–5, else ValueError."""
    with pytest.raises(ValueError):
        compute_sm2(-1, SM2State(), today=TODAY)
    with pytest.raises(ValueError):
        compute_sm2(6, SM2State(), today=TODAY)
    with pytest.raises(ValueError):
        compute_sm2(3.5, SM2State(), today=TODAY)  # type: ignore[arg-type]


# ── quality_from_performance tests ──────────────────────────────────────


def test_quality_perfect():
    """Correct + fast → quality 5."""
    assert quality_from_performance(True, 10) == 5


def test_quality_normal_correct():
    """Correct + normal → quality 4."""
    assert quality_from_performance(True, 30) == 4


def test_quality_slow_correct():
    """Correct + slow → quality 3."""
    assert quality_from_performance(True, 90) == 3


def test_quality_slow_wrong():
    """Wrong + slow → quality 2."""
    assert quality_from_performance(False, 90) == 2


def test_quality_normal_wrong():
    """Wrong + normal → quality 1."""
    assert quality_from_performance(False, 30) == 1


def test_quality_fast_wrong():
    """Wrong + fast → quality 0."""
    assert quality_from_performance(False, 5) == 0
