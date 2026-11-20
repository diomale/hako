"""Configuration loading and validation for HAKO.

Only non-secret settings live here. Credentials are handled in Milestone 9.
"""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

from hako import __version__ as package_version
from hako.core.errors import ConfigError
from hako.core.models import Mode
from hako.utils.paths import project_root, resolve_path

_ALLOWED_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


@dataclass(frozen=True)
class AppConfig:
    """Validated, immutable runtime configuration."""

    name: str
    version: str
    description: str
    default_mode: Mode
    log_level: str
    log_file: Path
    history_limit: int
    config_path: Path
    project_root: Path


def default_config_path() -> Path:
    """Return the config path, honouring an optional ``HAKO_CONFIG`` override."""
    override = os.environ.get("HAKO_CONFIG")
    if override:
        return Path(override).expanduser().resolve()
    return project_root() / "config" / "hako.ini"


def _get(parser: configparser.ConfigParser, section: str, option: str) -> str:
    try:
        value = parser.get(section, option).strip()
    except (configparser.NoSectionError, configparser.NoOptionError) as exc:
        raise ConfigError(f"missing configuration value: [{section}] {option}") from exc
    if not value:
        raise ConfigError(f"empty configuration value: [{section}] {option}")
    return value


def load_config(path: Path | None = None) -> AppConfig:
    """Load and validate the INI configuration file."""
    config_path = path.expanduser().resolve() if path is not None else default_config_path()
    parser = configparser.ConfigParser(interpolation=None)

    try:
        loaded = parser.read(config_path, encoding="utf-8")
    except (OSError, configparser.Error) as exc:
        raise ConfigError(f"cannot read configuration {config_path}: {exc}") from exc

    if not loaded:
        raise ConfigError(f"configuration file not found: {config_path}")

    root = project_root()
    name = _get(parser, "app", "name")
    version = _get(parser, "app", "version")
    description = _get(parser, "app", "description")
    mode_raw = _get(parser, "app", "default_mode")
    log_level = _get(parser, "runtime", "log_level").upper()
    log_file_raw = _get(parser, "runtime", "log_file")
    history_raw = _get(parser, "runtime", "history_limit")

    if log_level not in _ALLOWED_LOG_LEVELS:
        raise ConfigError(f"unsupported log_level: {log_level}")

    try:
        default_mode = Mode.from_value(mode_raw)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc

    try:
        history_limit = int(history_raw)
    except ValueError as exc:
        raise ConfigError("history_limit must be an integer") from exc
    if history_limit <= 0:
        raise ConfigError("history_limit must be greater than zero")

    if version != package_version:
        raise ConfigError(
            f"config version {version!r} does not match package version {package_version!r}"
        )

    return AppConfig(
        name=name,
        version=version,
        description=description,
        default_mode=default_mode,
        log_level=log_level,
        log_file=resolve_path(log_file_raw, root),
        history_limit=history_limit,
        config_path=config_path,
        project_root=root,
    )
