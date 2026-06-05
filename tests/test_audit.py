"""Tests for notification audit workflow."""

from __future__ import annotations

from ssc_study.audit import (
    NotificationChange,
    complete_audit,
    get_audit_history,
    is_audit_paused,
    trigger_notification_audit,
)


class TestTriggerNotificationAudit:
    """trigger_notification_audit creates audit entries."""

    def test_creates_audit(self, seeded_db):
        """Creates an audit entry in the database."""
        result = trigger_notification_audit(seeded_db)
        assert result["audit_id"] > 0
        assert "message" in result

    def test_major_change_pauses(self, seeded_db):
        """Major change (section_weights) pauses advancement."""
        result = trigger_notification_audit(seeded_db, {
            "changes": ["section_weights"],
        })
        assert result["is_major"] is True
        assert result["paused"] is True

    def test_minor_change_no_pause(self, seeded_db):
        """Minor change does not pause."""
        result = trigger_notification_audit(seeded_db, {
            "changes": ["other"],
        })
        assert result["is_major"] is False
        assert result["paused"] is False


class TestIsAuditPaused:
    """is_audit_paused checks pause state."""

    def test_not_paused_initially(self, seeded_db):
        """No audits means not paused."""
        status = is_audit_paused(seeded_db)
        assert status["paused"] is False


class TestCompleteAudit:
    """complete_audit finalizes an audit."""

    def test_completes_audit(self, seeded_db):
        """Completing an audit returns affected queues."""
        audit = trigger_notification_audit(seeded_db, {
            "changes": ["module"],
        })

        result = complete_audit(seeded_db, audit["audit_id"], [
            NotificationChange("module", "New module added", "major"),
        ])
        assert result["completed"] is True
        assert "affected_queues" in result

    def test_nonexistent_audit(self, seeded_db):
        """Non-existent audit returns error."""
        result = complete_audit(seeded_db, 9999, [])
        assert result["completed"] is False


class TestGetAuditHistory:
    """get_audit_history returns audit records."""

    def test_empty_when_no_audits(self, seeded_db):
        """No audits returns empty list."""
        history = get_audit_history(seeded_db)
        assert history == []

    def test_returns_audits(self, seeded_db):
        """Returns created audits."""
        trigger_notification_audit(seeded_db)
        trigger_notification_audit(seeded_db)
        history = get_audit_history(seeded_db)
        assert len(history) >= 2
