"""User configuration with JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path

from .models import StudyConfig

DEFAULT_CONFIG_PATH = Path.home() / ".ssc_study" / "config.json"


def load_config(path: Path | None = None) -> StudyConfig:
    """Load user config from JSON, creating with defaults if missing.

    Args:
        path: Config file path (default: ~/.ssc_study/config.json).

    Returns:
        StudyConfig with user values merged over defaults.
    """
    file_path = path or DEFAULT_CONFIG_PATH

    if file_path.exists():
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        # Build from defaults, then overlay any saved values.
        defaults = StudyConfig()
        return StudyConfig(
            db_path=raw.get("db_path", defaults.db_path),
            daily_split_minutes=raw.get("daily_split_minutes", defaults.daily_split_minutes),
            tier1_floor_target=raw.get("tier1_floor_target", defaults.tier1_floor_target),
            tier2_floor_target=raw.get("tier2_floor_target", defaults.tier2_floor_target),
            archetype_probe_count=raw.get("archetype_probe_count", defaults.archetype_probe_count),
            archetype_unlock_accuracy=raw.get("archetype_unlock_accuracy", defaults.archetype_unlock_accuracy),
            holdout_ratio=raw.get("holdout_ratio", defaults.holdout_ratio),
            backup_reminder=raw.get("backup_reminder", defaults.backup_reminder),
        )

    return StudyConfig()


def save_config(config: StudyConfig, path: Path | None = None) -> None:
    """Save config to JSON file, creating parent directories as needed."""
    file_path = path or DEFAULT_CONFIG_PATH
    file_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "db_path": config.db_path,
        "daily_split_minutes": config.daily_split_minutes,
        "tier1_floor_target": config.tier1_floor_target,
        "tier2_floor_target": config.tier2_floor_target,
        "archetype_probe_count": config.archetype_probe_count,
        "archetype_unlock_accuracy": config.archetype_unlock_accuracy,
        "holdout_ratio": config.holdout_ratio,
        "backup_reminder": config.backup_reminder,
    }
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
