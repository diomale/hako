"""Tests for configuration loading and validation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hako import __version__
from hako.core.config import load_config
from hako.core.errors import ConfigError
from hako.core.models import Mode
from hako.utils.paths import project_root


def write_config(
    root: Path,
    *,
    version: str | None = None,
    mode: str = "chat",
    log_level: str = "INFO",
    log_file: str | None = None,
    history_limit: str = "12",
) -> Path:
    """Write a temporary valid-ish config file and return its path."""
    path = root / "config" / "hako.ini"
    path.parent.mkdir(parents=True, exist_ok=True)
    log_value = log_file or str(root / "logs" / "hako.log")
    path.write_text(
        "[app]\n"
        "name = HAKO\n"
        f"version = {version or __version__}\n"
        "description = test config\n"
        f"default_mode = {mode}\n"
        "\n"
        "[runtime]\n"
        f"log_level = {log_level}\n"
        f"log_file = {log_value}\n"
        f"history_limit = {history_limit}\n",
        encoding="utf-8",
    )
    return path


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_load_valid_config(self) -> None:
        path = write_config(self.root)
        config = load_config(path)
        self.assertEqual(config.name, "HAKO")
        self.assertEqual(config.version, __version__)
        self.assertEqual(config.default_mode, Mode.CHAT)
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.history_limit, 12)
        self.assertEqual(config.config_path, path.resolve())
        self.assertEqual(config.log_file, self.root / "logs" / "hako.log")

    def test_hako_config_environment_override(self) -> None:
        path = write_config(self.root)
        with patch.dict(os.environ, {"HAKO_CONFIG": str(path)}):
            config = load_config()
        self.assertEqual(config.config_path, path.resolve())

    def test_relative_log_path_uses_project_root(self) -> None:
        path = write_config(self.root, log_file="logs/custom.log")
        config = load_config(path)
        self.assertEqual(config.log_file, project_root() / "logs" / "custom.log")

    def test_missing_file_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config(self.root / "does-not-exist.ini")

    def test_invalid_mode_raises_config_error(self) -> None:
        path = write_config(self.root, mode="voice")
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_log_level_raises_config_error(self) -> None:
        path = write_config(self.root, log_level="TRACE")
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_history_limit_raises_config_error(self) -> None:
        path = write_config(self.root, history_limit="zero")
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_version_mismatch_raises_config_error(self) -> None:
        path = write_config(self.root, version="9.9.9")
        with self.assertRaises(ConfigError):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
