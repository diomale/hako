"""Tests for logging setup and credential redaction."""

from __future__ import annotations

import logging as std_logging
import tempfile
import unittest
from pathlib import Path

from hako.core.logging import RedactingFilter, configure_logging
from tests.helpers import make_config


class LoggingTests(unittest.TestCase):
    def tearDown(self) -> None:
        logger = std_logging.getLogger("hako")
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

    def test_redacting_filter_masks_credential_shapes(self) -> None:
        record = std_logging.LogRecord(
            "hako",
            std_logging.INFO,
            __file__,
            1,
            "api_key: sk-abcdefgh1234 Authorization: Bearer token-123",
            (),
            None,
        )
        self.assertTrue(RedactingFilter().filter(record))
        rendered = record.getMessage()
        self.assertNotIn("sk-abcdefgh1234", rendered)
        self.assertNotIn("token-123", rendered)
        self.assertIn("[REDACTED]", rendered)

    def test_configure_logging_writes_redacted_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_config(Path(tmp))
            logger = configure_logging(config)
            logger.info("startup %s", "ok")
            logger.info("candidate key sk-abcdefgh1234")
            for handler in logger.handlers:
                handler.flush()
            content = config.log_file.read_text(encoding="utf-8")
            self.assertIn("startup ok", content)
            self.assertIn("[REDACTED]", content)
            self.assertNotIn("sk-abcdefgh1234", content)


if __name__ == "__main__":
    unittest.main()
