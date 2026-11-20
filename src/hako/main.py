"""Entry point for the HAKO terminal application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from hako import __version__
from hako.app import Application
from hako.cli.output import emit_error
from hako.core.config import load_config
from hako.core.errors import HakoError
from hako.core.lifecycle import install_signal_handlers
from hako.core.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Build the small argument parser for the launcher."""
    parser = argparse.ArgumentParser(
        prog="hako",
        description="HAKO — lightweight terminal AI assistant foundation",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="path to an alternative HAKO INI configuration file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"HAKO {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run HAKO and return a process exit code."""
    args = build_parser().parse_args(argv)
    app: Application | None = None
    try:
        config = load_config(args.config)
        configure_logging(config)
        app = Application(config)
        install_signal_handlers(app)
        return app.run()
    except HakoError as exc:
        emit_error(str(exc))
        return 2
    finally:
        if app is not None:
            app.close()


if __name__ == "__main__":
    sys.exit(main())
