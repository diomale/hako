"""Shared test helpers."""

from __future__ import annotations

from pathlib import Path

from hako import __version__
from hako.core.config import AppConfig
from hako.core.models import Mode


def make_config(base: Path, **overrides: object) -> AppConfig:
    """Build a valid AppConfig for tests without touching real files."""
    values: dict[str, object] = {
        "name": "HAKO",
        "version": __version__,
        "description": "test config",
        "default_mode": Mode.CHAT,
        "log_level": "INFO",
        "log_file": base / "logs" / "hako-test.log",
        "history_limit": 10,
        "config_path": base / "config" / "hako.ini",
        "project_root": base,
    }
    values.update(overrides)
    return AppConfig(**values)  # type: ignore[arg-type]
