"""Tests for Phase 4 Guardian Planner."""

from __future__ import annotations

from datetime import date
import pytest
from ssc_study.db import Database
from ssc_study.guardian import build_guardian_plan, GuardianPlan
from ssc_study.audit import trigger_notification_audit


def test_default_plan_180_min(seeded_db):
    """Verify that default plan totals exactly 180 minutes and contains standard blocks."""
    # Seed a recent mock so that mock is not due
    conn = seeded_db.connect()
    conn.execute(
        """INSERT INTO external_mocks (mock_name, source, taken_at, tier, raw_score, calibrated_score)
           VALUES ('Mock Recent', 'External', '2026-07-07', 'tier1', 100, 100)"""
    )
    conn.commit()

    # We choose a normal day that is not a first Monday, e.g. 2026-07-08 (Wednesday)
    today = date(2026, 7, 8)
    plan = build_guardian_plan(seeded_db, today=today)

    assert plan.total_minutes == 180
    assert len(plan.blocks) == 6

    names = [b.name for b in plan.blocks]
    assert "SM-2 Review" in names
    assert "Tier-1 Boss Fights" in names
    assert "Tier-2 Module Queue" in names
    assert "GK/GA Memory Queue" in names
    assert "English" in names
    assert "Analysis" in names


def test_tier1_floor_shift(seeded_db):
    """Verify that Tier-1 floor shift updates the boss fights and module queue blocks."""
    # Seed 2 external mocks in the DB with tier1 and calibrated_score >= 135.
    # One must be very recent (yesterday) to prevent mock due condition.
    conn = seeded_db.connect()
    conn.execute(
        """INSERT INTO external_mocks (mock_name, source, taken_at, tier, raw_score, calibrated_score)
           VALUES ('Mock A', 'External', '2026-07-01', 'tier1', 140, 140)"""
    )
    conn.execute(
        """INSERT INTO external_mocks (mock_name, source, taken_at, tier, raw_score, calibrated_score)
           VALUES ('Mock B', 'External', '2026-07-07', 'tier1', 140, 140)"""
    )
    conn.commit()

    today = date(2026, 7, 8)
    plan = build_guardian_plan(seeded_db, today=today)

    assert plan.total_minutes == 180
    # Tier-1 boss fights should be 25 min, Tier-2 module queue should be 70 min
    t1_boss = next(b for b in plan.blocks if b.name == "Tier-1 Boss Fights")
    t2_module = next(b for b in plan.blocks if b.name == "Tier-2 Module Queue")

    assert t1_boss.minutes == 25
    assert t2_module.minutes == 70


def test_first_monday_pulses(seeded_db):
    """Verify that first Monday recommends foundation and CK pulses replacing boss fights."""
    # First Monday of July 2026 is 2026-07-06
    today = date(2026, 7, 6)
    plan = build_guardian_plan(seeded_db, today=today)

    assert plan.total_minutes == 180
    assert plan.pulse_recommendation == "both"

    names = [b.name for b in plan.blocks]
    assert "Foundation Pulse" in names
    assert "CK Pulse" in names
    assert "Tier-1 Boss Fights" not in names
    assert "Tier-2 Module Queue" not in names
    assert "SM-2 Review" in names  # SM-2 review must not be removed


def test_mock_day_does_not_remove_sm2(seeded_db):
    """Verify that a mock day recommendation replaces boss fight blocks and keeps SM-2."""
    # Insert a dummy mock taken more than 7 days ago to force weekly mock to be due
    conn = seeded_db.connect()
    conn.execute(
        """INSERT INTO external_mocks (mock_name, source, taken_at, tier, raw_score, calibrated_score)
           VALUES ('Mock Old', 'External', '2026-06-01', 'tier1', 100, 100)"""
    )
    conn.commit()

    # Wednesday 2026-07-08 (mock is due because last mock was in June)
    today = date(2026, 7, 8)
    plan = build_guardian_plan(seeded_db, today=today)

    assert plan.mock_recommendation == "weekly mock"
    names = [b.name for b in plan.blocks]
    assert "Mock Test" in names
    assert "SM-2 Review" in names
    assert "Tier-1 Boss Fights" not in names
    assert "Tier-2 Module Queue" not in names


def test_pulse_mock_collision(seeded_db):
    """Verify that collision of mock and pulse days defers the mock recommendation."""
    # Insert a dummy mock taken more than 7 days ago
    conn = seeded_db.connect()
    conn.execute(
        """INSERT INTO external_mocks (mock_name, source, taken_at, tier, raw_score, calibrated_score)
           VALUES ('Mock Old', 'External', '2026-06-01', 'tier1', 100, 100)"""
    )
    conn.commit()

    # First Monday (2026-07-06)
    today = date(2026, 7, 6)
    plan = build_guardian_plan(seeded_db, today=today)

    # Recommends pulses, mock is deferred (none)
    assert plan.pulse_recommendation == "both"
    assert plan.mock_recommendation == "none"
    assert any("deferred" in w.lower() for w in plan.warnings)


def test_notification_audit_pause(seeded_db):
    """Verify active major notification audit pauses advancement blocks."""
    # Trigger major audit
    trigger_notification_audit(seeded_db, {"changes": ["section_weights"]})

    today = date(2026, 7, 8)
    plan = build_guardian_plan(seeded_db, today=today)

    assert plan.audit_mode in ("notification_pause", "recalibration")
    names = [b.name for b in plan.blocks]
    assert "Advancement Paused" in names
    assert "Tier-1 Boss Fights" not in names
    assert "Tier-2 Module Queue" not in names
