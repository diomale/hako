"""Terminal output helpers for the HAKO CLI."""

from __future__ import annotations

from hako.core.models import Mode


def prompt(mode: Mode) -> str:
    """Return the input prompt for the active mode."""
    return f"hako[{mode.value}]> "


def emit(message: str) -> None:
    """Write a normal message to stdout."""
    print(message)


def emit_error(message: str) -> None:
    """Write an error message to stdout without exposing secrets."""
    print(f"Error: {message}")


def emit_welcome(name: str, version: str) -> None:
    """Print the startup banner."""
    print(f"{name} v{version} — type /help for commands, /exit to quit.")
