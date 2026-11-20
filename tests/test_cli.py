"""Tests for command routing and placeholder responses."""

from __future__ import annotations

import getpass
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hako.app import Application
from hako.cli.router import CommandRouter
from hako.core.models import Mode
from tests.helpers import make_config


class CommandRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.app = Application(make_config(Path(self._tmp.name)))
        self.router = CommandRouter()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_help_lists_all_documented_commands(self) -> None:
        result = self.router.dispatch("/help", self.app)
        self.assertIn("Available commands", result.message)
        for command in (
            "/help", "/status", "/chat", "/talk", "/clear", "/memory",
            "/memories", "/remember", "/forget", "/clear-memory",
            "/apikey", "/apikey set", "/apikey remove", "/exit",
        ):
            self.assertIn(command, result.message)

    def test_status_reports_milestone_state_without_secrets(self) -> None:
        result = self.router.dispatch("/status", self.app)
        self.assertIn("Mode: chat", result.message)
        self.assertIn("CLI foundation: READY", result.message)
        self.assertIn("OpenRouter client: PLANNED", result.message)
        self.assertIn("key status not queried", result.message)
        self.assertNotIn("sk-", result.message)

    def test_chat_and_talk_change_mode_state_only(self) -> None:
        result = self.router.dispatch("/talk", self.app)
        self.assertEqual(self.app.mode, Mode.TALK)
        self.assertIn("no microphone or speaker was opened", result.message)
        result = self.router.dispatch("/chat", self.app)
        self.assertEqual(self.app.mode, Mode.CHAT)
        self.assertIn("not implemented", result.message)

    def test_plain_text_is_not_sent_to_any_backend(self) -> None:
        result = self.router.dispatch("hello there", self.app)
        self.assertIn("not implemented", result.message)
        self.assertNotIn("hello there", result.message)

    def test_unknown_command(self) -> None:
        result = self.router.dispatch("/bogus", self.app)
        self.assertIn("Unknown command", result.message)

    def test_later_milestone_commands_are_placeholder_only(self) -> None:
        cases = {
            "/clear": "nothing to clear",
            "/memory": "Milestone 8",
            "/memories": "Milestone 8",
            "/remember anything": "Milestone 8",
            "/forget 1": "Milestone 8",
            "/clear-memory": "Milestone 8",
            "/apikey": "Milestone 9",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertIn(expected, self.router.dispatch(command, self.app).message)

    def test_apikey_subcommands_do_not_prompt_or_touch_credentials(self) -> None:
        with patch.object(getpass, "getpass", side_effect=AssertionError("must not prompt")):
            set_result = self.router.dispatch("/apikey set", self.app)
            remove_result = self.router.dispatch("/apikey remove", self.app)
        self.assertIn("no prompt was shown", set_result.message)
        self.assertIn("no credentials were touched", remove_result.message)

    def test_bad_apikey_subcommand(self) -> None:
        result = self.router.dispatch("/apikey list", self.app)
        self.assertIn("Unknown /apikey subcommand", result.message)

    def test_exit_requests_shutdown(self) -> None:
        result = self.router.dispatch("/exit", self.app)
        self.assertTrue(result.should_exit)
        self.assertIn("Goodbye", result.message)


if __name__ == "__main__":
    unittest.main()
