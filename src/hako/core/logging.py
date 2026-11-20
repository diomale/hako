"""Logging setup with defensive secret redaction."""

from __future__ import annotations

import logging as std_logging
import logging.handlers as std_logging_handlers
import re
from typing import TYPE_CHECKING

from hako.utils.paths import ensure_parent_dir

if TYPE_CHECKING:
    from hako.core.config import AppConfig


class RedactingFilter(std_logging.Filter):
    """Mask credential-shaped text before it reaches a log handler."""

    _PATTERNS = (
        re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
        re.compile(r"(?i)\b(?:authorization|api[_-]?key)\s*[:=]\s*\S+"),
    )

    def filter(self, record: std_logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern in self._PATTERNS:
            message = pattern.sub("[REDACTED]", message)
        record.msg = message
        record.args = ()
        return True


def configure_logging(config: "AppConfig") -> std_logging.Logger:
    """Configure the ``hako`` logger to write to the configured file."""
    logger = std_logging.getLogger("hako")
    logger.setLevel(config.log_level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    ensure_parent_dir(config.log_file)
    handler = std_logging_handlers.RotatingFileHandler(
        config.log_file,
        maxBytes=256 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    handler.setLevel(config.log_level)
    handler.setFormatter(
        std_logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    handler.addFilter(RedactingFilter())
    logger.addHandler(handler)
    return logger
