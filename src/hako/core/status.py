"""Basic status reporting for the Milestone 2 CLI foundation."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from hako.core.models import Mode

if TYPE_CHECKING:
    from hako.core.config import AppConfig


@dataclass(frozen=True)
class SubsystemStatus:
    """State of one HAKO subsystem."""

    name: str
    state: str
    note: str = ""


@dataclass(frozen=True)
class SystemStatus:
    """Snapshot of the running application and its planned subsystems."""

    app_name: str
    version: str
    description: str
    mode: Mode
    python_version: str
    platform: str
    architecture: str
    config_path: Path
    log_path: Path
    subsystems: tuple[SubsystemStatus, ...]


def collect_status(config: "AppConfig", mode: Mode) -> SystemStatus:
    """Build a status snapshot from configuration and current mode."""
    return SystemStatus(
        app_name=config.name,
        version=config.version,
        description=config.description,
        mode=mode,
        python_version=platform.python_version(),
        platform=platform.system(),
        architecture=platform.machine(),
        config_path=config.config_path,
        log_path=config.log_file,
        subsystems=(
            SubsystemStatus("CLI foundation", "READY", "Command routing and lifecycle active"),
            SubsystemStatus("Configuration", "READY", str(config.config_path)),
            SubsystemStatus("Logging", "READY", "File logging with redaction active"),
            SubsystemStatus("OpenRouter client", "PLANNED", "Milestone 3; no requests made"),
            SubsystemStatus("Text chat", "PLANNED", "Milestone 4; no conversation engine yet"),
            SubsystemStatus("Speech recognition", "DEFERRED", "Audio work deferred by user decision"),
            SubsystemStatus("Text-to-speech", "DEFERRED", "Audio work deferred by user decision"),
            SubsystemStatus("Voice modes", "DEFERRED", "No audio resources opened"),
            SubsystemStatus("Persistent memory", "PLANNED", "Milestone 8; no database opened"),
            SubsystemStatus("Credential management", "PLANNED", "Milestone 9; key status not queried"),
            SubsystemStatus("Schedule / Google Calendar", "NOT IN SCOPE", "Not part of current roadmap"),
        ),
    )


def format_status(status: SystemStatus) -> str:
    """Render a status snapshot for terminal output."""
    lines = [
        f"{status.app_name} v{status.version} — {status.description}",
        f"Mode: {status.mode.value}",
        f"Python: {status.python_version}",
        f"Platform / architecture: {status.platform} / {status.architecture}",
        f"Configuration: {status.config_path}",
        f"Log file: {status.log_path}",
        "",
        "Subsystems:",
    ]
    for subsystem in status.subsystems:
        suffix = f" — {subsystem.note}" if subsystem.note else ""
        lines.append(f"  {subsystem.name}: {subsystem.state}{suffix}")
    return "\n".join(lines)
