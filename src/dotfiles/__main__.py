"""Command-line entry point: ``python -m dotfiles``."""

from __future__ import annotations

import argparse
import sys

from . import bootstrap
from .config.settings import Settings
from .utils.exceptions import DotfilesError
from .utils.logging import get_logger, setup_logging


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dotfiles",
        description="Cross-platform dotfiles bootstrap (macOS, Bazzite, Silverblue).",
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug logging")
    parser.add_argument("--list", action="store_true", help="list steps and exit")
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="STEP",
        choices=bootstrap.step_names(),
        help="run only the named step(s)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, configure logging, and run the bootstrap."""
    args = _build_parser().parse_args(argv)
    setup_logging(verbose=args.verbose)
    log = get_logger("main")
    if args.list:
        for name in bootstrap.step_names():
            print(name)
        return 0
    try:
        settings = Settings.load()
    except DotfilesError as exc:
        log.error("%s", exc)
        return 1
    return bootstrap.run(settings, only=args.only)


if __name__ == "__main__":
    sys.exit(main())
