"""Parse terminal input and route commands to their handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hako.cli.commands import CommandHandler, CommandResult, build_command_registry
from hako.core.errors import HakoError

if TYPE_CHECKING:
    from hako.app import Application


class CommandRouter:
    """Dispatch slash commands and classify plain text input."""

    def __init__(self, registry: dict[str, CommandHandler] | None = None) -> None:
        self._registry = registry if registry is not None else build_command_registry()

    def dispatch(self, raw: str, app: "Application") -> CommandResult:
        """Route one line of terminal input."""
        text = raw.strip()
        if not text:
            return CommandResult("")

        if not text.startswith("/"):
            return CommandResult(
                "Plain text chat is not implemented in Milestone 2. Type /help for commands."
            )

        parts = text[1:].split()
        name = parts[0].lower() if parts else ""
        args = tuple(parts[1:])
        handler = self._registry.get(name)
        if handler is None:
            return CommandResult(f"Unknown command: /{name}. Type /help for commands.")

        try:
            return handler(app, args)
        except HakoError as exc:
            return CommandResult(f"Error: {exc}")
