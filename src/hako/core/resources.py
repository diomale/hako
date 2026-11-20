"""Resource lifecycle interface used by the application.

Later milestones can register audio or other resources that must be released
on mode switches and shutdown. Milestone 2 registers no concrete resources.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Releaseable(Protocol):
    """Any resource that can be cleanly released."""

    def release(self) -> None:
        """Release the resource. Implementations must be idempotent."""
        ...
