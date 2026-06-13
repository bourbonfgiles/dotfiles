"""Command-line entry point: ``python -m dotfiles``."""

from __future__ import annotations

import argparse
import sys

from . import bootstrap
from .config.settings import Settings
from .utils.exceptions import DotfilesError
from .utils.logging import get_logger, setup_logging


def _build_parser() -> argparse.ArgumentParser:
    # argparse parses sys.argv, validates the flags, and auto-generates --help.
    parser = argparse.ArgumentParser(
        prog="dotfiles",
        description="Cross-platform dotfiles bootstrap (macOS, Bazzite, Silverblue).",
    )
    # action="store_true": a boolean flag — present => True, absent => False.
    parser.add_argument("--verbose", action="store_true", help="enable debug logging")
    parser.add_argument("--list", action="store_true", help="list steps and exit")
    parser.add_argument(
        "--only",
        nargs="+",  # accept one or more values, e.g. --only gnome fonts
        metavar="STEP",  # placeholder name shown in --help
        choices=bootstrap.step_names(),  # only valid step names are accepted
        help="run only the named step(s)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, configure logging, and run the bootstrap."""
    # argv defaults to None so tests can pass a fake list; parse_args(None) reads sys.argv.
    args = _build_parser().parse_args(argv)
    setup_logging(verbose=args.verbose)  # configure logging BEFORE doing any work
    log = get_logger("main")
    if args.list:  # --list: just print the step names and exit (no side effects)
        for name in bootstrap.step_names():
            print(name)
        return 0  # 0 = success exit code
    try:
        settings = Settings.load()  # resolve + validate paths; may raise DotfilesError
    except DotfilesError as exc:
        log.error("%s", exc)  # report cleanly instead of dumping a traceback
        return 1  # 1 = failure exit code
    return bootstrap.run(settings, only=args.only)  # hand off to the orchestrator


# This block runs only when executed as a program (python -m dotfiles), not on import.
# sys.exit() turns main()'s return value into the process exit status (0 ok / 1 fail).
if __name__ == "__main__":
    sys.exit(main())
