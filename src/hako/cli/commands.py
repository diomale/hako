"""Command handlers for the Milestone 2 CLI foundation.

Commands belonging to later milestones are routed but return explicit
"not implemented" messages. They never perform their future work here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from hako.core.models import Mode
from hako.core.status import collect_status, format_status

if TYPE_CHECKING:
    from hako.app import Application


@dataclass(frozen=True)
class CommandResult:
    """Result returned by a command handler."""

    message: str
    should_exit: bool = False


CommandHandler = Callable[["Application", tuple[str, ...]], CommandResult]


_HELP_LINES: tuple[tuple[str, str], ...] = (
    ("/help", "Show available commands"),
    ("/status", "Show system and subsystem status"),
    ("/chat", "Select text chat mode (chat engine not implemented yet)"),
    ("/talk", "Select voice mode (audio is deferred)"),
    ("/clear", "Clear current conversation (not active yet)"),
    ("/memory", "Show memory status (Milestone 8)"),
    ("/memories", "List saved memories (Milestone 8)"),
    ("/remember <info>", "Save a memory (Milestone 8)"),
    ("/forget <ID>", "Delete a memory (Milestone 8)"),
    ("/clear-memory", "Clear all memories after confirmation (Milestone 8)"),
    ("/apikey", "Show credential status (Milestone 9)"),
    ("/apikey set", "Configure API key (Milestone 9)"),
    ("/apikey remove", "Remove stored API key (Milestone 9)"),
    ("/exit", "Exit HAKO"),
)


def _planned(name: str, milestone: str) -> CommandResult:
    return CommandResult(f"{name} is reserved for {milestone} and is not implemented yet.")


def handle_help(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    width = max(len(command) for command, _ in _HELP_LINES)
    lines = [f"  {command.ljust(width)}  {description}" for command, description in _HELP_LINES]
    lines.append("")
    lines.append("Plain text input is treated as a chat message; chat is not implemented yet.")
    return CommandResult("Available commands:\n" + "\n".join(lines))


def handle_status(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del args
    return CommandResult(format_status(collect_status(app.config, app.mode)))


def handle_chat(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del args
    app.set_mode(Mode.CHAT)
    return CommandResult(
        "Text chat mode selected. Chat responses are not implemented in Milestone 2."
    )


def handle_talk(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del args
    app.set_mode(Mode.TALK)
    return CommandResult(
        "Voice mode selected, but audio is deferred; no microphone or speaker was opened."
    )


def handle_clear(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return CommandResult("No conversation history exists in Milestone 2; nothing to clear.")


def handle_memory(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return _planned("Memory status", "Milestone 8")


def handle_memories(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return _planned("Memory listing", "Milestone 8")


def handle_remember(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return _planned("Saving memories", "Milestone 8")


def handle_forget(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return _planned("Deleting memories", "Milestone 8")


def handle_clear_memory(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return _planned("Clearing memories", "Milestone 8")


def handle_apikey(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app
    if not args:
        return CommandResult(
            "Credential management is reserved for Milestone 9. "
            "No key status was checked."
        )
    subcommand = args[0].lower()
    if subcommand == "set":
        return CommandResult(
            "API key configuration is reserved for Milestone 9; "
            "no prompt was shown and no key was read."
        )
    if subcommand == "remove":
        return CommandResult(
            "API key removal is reserved for Milestone 9; no credentials were touched."
        )
    return CommandResult(f"Unknown /apikey subcommand: {subcommand!r}. Type /help for commands.")


def handle_exit(app: "Application", args: tuple[str, ...]) -> CommandResult:
    del app, args
    return CommandResult("Goodbye.", should_exit=True)


def build_command_registry() -> dict[str, CommandHandler]:
    """Return the command-name to handler mapping."""
    return {
        "help": handle_help,
        "status": handle_status,
        "chat": handle_chat,
        "talk": handle_talk,
        "clear": handle_clear,
        "memory": handle_memory,
        "memories": handle_memories,
        "remember": handle_remember,
        "forget": handle_forget,
        "clear-memory": handle_clear_memory,
        "apikey": handle_apikey,
        "exit": handle_exit,
    }
