"""Tests for user configuration persistence."""

from __future__ import annotations

import json
from pathlib import Path

from ssc_study.config import load_config, save_config
from ssc_study.models import StudyConfig


class TestLoadConfig:
    """load_config returns correct config in various states."""

    def test_loads_defaults_when_no_file(self, tmp_path: Path):
        """Missing config file returns default StudyConfig."""
        fake_path = tmp_path / "nonexistent_config.json"
        assert not fake_path.exists()

        config = load_config(fake_path)
        assert isinstance(config, StudyConfig)
        assert config.db_path == "~/.ssc_study/study.db"
        assert config.tier1_floor_target == 140

    def test_loads_existing_config(self, tmp_path: Path):
        """Existing config file merges correctly."""
        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps({"db_path": "/custom/path.db", "tier1_floor_target": 150}),
            encoding="utf-8",
        )

        config = load_config(config_path)
        assert config.db_path == "/custom/path.db"
        assert config.tier1_floor_target == 150
        assert config.tier2_floor_target == 110  # default remains


class TestSaveConfig:
    """save_config persists config correctly."""

    def test_saves_and_reloads(self, tmp_path: Path):
        """Save then load returns same values."""
        config_path = tmp_path / "test_config.json"

        original = StudyConfig(
            db_path="/test/path.db",
            daily_split_minutes={"sm2_review": 30, "mock": 45},
            tier1_floor_target=150,
        )
        save_config(original, config_path)

        assert config_path.exists()

        loaded = load_config(config_path)
        assert loaded.db_path == "/test/path.db"
        assert loaded.daily_split_minutes["sm2_review"] == 30
        assert loaded.daily_split_minutes["mock"] == 45
        assert loaded.tier1_floor_target == 150
