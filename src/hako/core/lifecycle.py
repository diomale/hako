"""Signal handling for graceful shutdown."""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hako.app import Application


def install_signal_handlers(app: "Application") -> dict[signal.Signals, Any]:
    """Route SIGINT/SIGTERM to ``app.stop()`` and return previous handlers."""
    def handle_signal(signum: int, frame: Any) -> None:
        del signum, frame
        app.stop()
        raise KeyboardInterrupt

    previous: dict[signal.Signals, Any] = {}
    for name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, name, None)
        if sig is None:
            continue
        previous[sig] = signal.getsignal(sig)
        signal.signal(sig, handle_signal)
    return previous
