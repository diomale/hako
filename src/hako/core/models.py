"""Small value types shared across HAKO modules."""

from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    """Terminal interaction modes.

    Only the mode state exists in Milestone 2. No chat engine or audio backend
    is attached to these modes yet.
    """

    CHAT = "chat"
    TALK = "talk"

    @classmethod
    def from_value(cls, value: str) -> "Mode":
        """Return a Mode from a configuration or command value."""
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"unknown mode: {value!r}")
