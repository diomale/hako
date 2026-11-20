"""Application lifecycle for HAKO.

Milestone 2 owns startup, the input loop, mode state, resource release hooks,
and shutdown. No backend services are started here.
"""

from __future__ import annotations

import logging as std_logging
from typing import TYPE_CHECKING

from hako.cli.output import emit, emit_welcome, prompt
from hako.cli.router import CommandRouter
from hako.core.errors import HakoError
from hako.core.models import Mode
from hako.core.resources import Releaseable

if TYPE_CHECKING:
    from hako.core.config import AppConfig


class Application:
    """Top-level terminal application object."""

    def __init__(self, config: "AppConfig", router: CommandRouter | None = None) -> None:
        self.config = config
        self.router = router if router is not None else CommandRouter()
        self.mode = config.default_mode
        self._running = False
        self._stop_requested = False
        self._closed = False
        self._resources: list[Releaseable] = []
        self.logger = std_logging.getLogger("hako")

    @property
    def is_running(self) -> bool:
        """Whether the main loop is active."""
        return self._running

    @property
    def stop_requested(self) -> bool:
        """Whether a clean stop has been requested."""
        return self._stop_requested

    def register_resource(self, resource: Releaseable) -> None:
        """Register a future resource that must be released on switch/shutdown."""
        self._resources.append(resource)

    def set_mode(self, mode: Mode) -> None:
        """Switch interaction mode, releasing registered resources first."""
        if mode == self.mode:
            return
        self._release_resources()
        self.mode = mode
        self.logger.info("mode switched to %s", mode.value)

    def stop(self) -> None:
        """Request a clean stop of the main loop."""
        self._stop_requested = True

    def run(self) -> int:
        """Run the terminal loop until stop/exit/EOF/interrupt."""
        if self._running:
            raise HakoError("application is already running")
        if self._stop_requested:
            return 0

        self._running = True
        self.logger.info("HAKO %s started in %s mode", self.config.version, self.mode.value)
        emit_welcome(self.config.name, self.config.version)

        try:
            while not self._stop_requested:
                try:
                    raw = input(prompt(self.mode))
                except (EOFError, KeyboardInterrupt):
                    emit("")
                    self.stop()
                    break

                result = self.router.dispatch(raw, self)
                if result.message:
                    emit(result.message)
                if result.should_exit:
                    self.stop()
        finally:
            self._running = False
            self.close()

        return 0

    def close(self) -> None:
        """Release resources. Safe to call more than once."""
        if self._closed:
            return
        self._release_resources()
        self._closed = True
        self.logger.info("HAKO stopped")

    def _release_resources(self) -> None:
        for resource in self._resources:
            try:
                resource.release()
            except Exception:
                self.logger.exception("failed to release a registered resource")
        self._resources.clear()
