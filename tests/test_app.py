"""Tests for application lifecycle and resource handling."""

from __future__ import annotations

import io
import signal
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hako.app import Application
from hako.core.errors import HakoError
from hako.core.lifecycle import install_signal_handlers
from hako.core.models import Mode
from tests.helpers import make_config


class DummyResource:
    def __init__(self) -> None:
        self.release_count = 0

    def release(self) -> None:
        self.release_count += 1


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.app = Application(make_config(Path(self._tmp.name)))

    def tearDown(self) -> None:
        self.app.close()
        self._tmp.cleanup()

    def test_run_exits_on_exit_command(self) -> None:
        buffer = io.StringIO()
        with patch("builtins.input", side_effect=["/status", "/exit"]), redirect_stdout(buffer):
            code = self.app.run()
        self.assertEqual(code, 0)
        self.assertFalse(self.app.is_running)
        self.assertTrue(self.app.stop_requested)
        output = buffer.getvalue()
        self.assertIn("HAKO v", output)
        self.assertIn("CLI foundation: READY", output)
        self.assertIn("Goodbye", output)

    def test_run_exits_on_eof(self) -> None:
        with patch("builtins.input", side_effect=EOFError), redirect_stdout(io.StringIO()):
            self.assertEqual(self.app.run(), 0)
        self.assertTrue(self.app.stop_requested)

    def test_pre_stopped_application_consumes_no_input(self) -> None:
        self.app.stop()
        with patch("builtins.input", side_effect=AssertionError("input must not be called")):
            self.assertEqual(self.app.run(), 0)

    def test_cannot_run_twice(self) -> None:
        self.app._running = True
        with self.assertRaises(HakoError):
            self.app.run()

    def test_mode_switch_releases_resources_then_close_is_noop(self) -> None:
        resource = DummyResource()
        self.app.register_resource(resource)
        self.app.set_mode(Mode.TALK)
        self.assertEqual(resource.release_count, 1)
        self.assertEqual(self.app.mode, Mode.TALK)
        self.app.close()
        self.assertEqual(resource.release_count, 1)

    def test_same_mode_does_not_release(self) -> None:
        resource = DummyResource()
        self.app.register_resource(resource)
        self.app.set_mode(Mode.CHAT)
        self.assertEqual(resource.release_count, 0)

    def test_close_is_idempotent(self) -> None:
        resource = DummyResource()
        self.app.register_resource(resource)
        self.app.close()
        self.app.close()
        self.assertEqual(resource.release_count, 1)

    def test_signal_handlers_stop_application(self) -> None:
        with (
            patch("hako.core.lifecycle.signal.getsignal", return_value=None),
            patch("hako.core.lifecycle.signal.signal") as mock_signal,
        ):
            install_signal_handlers(self.app)

        self.assertEqual(mock_signal.call_count, 2)
        handler = mock_signal.call_args_list[0].args[1]
        with self.assertRaises(KeyboardInterrupt):
            handler(signal.SIGINT, None)
        self.assertTrue(self.app.stop_requested)


if __name__ == "__main__":
    unittest.main()
