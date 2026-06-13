"""Coloured, prefixed logging that mirrors the old ==> / WARN: / ERROR output."""

from __future__ import annotations

import logging  # stdlib module: Python's standard logging framework

# Module-level constants (UPPER_SNAKE_CASE by convention).
_RESET = "\033[0m"  # string literal: ANSI escape that resets the terminal colour
_COLOURS = {  # dict literal: maps a logging level (int) -> ANSI colour (str)
    logging.DEBUG: "\033[2m",  # logging.DEBUG is an int constant (10)
    logging.INFO: "\033[1;32m",  # green
    logging.WARNING: "\033[1;33m",  # yellow
    logging.ERROR: "\033[1;31m",  # red
    logging.CRITICAL: "\033[1;31m",
}
_PREFIXES = {  # dict literal: level (int) -> line prefix (str)
    logging.DEBUG: "...",
    logging.INFO: "==>",
    logging.WARNING: "WARN:",
    logging.ERROR: "ERROR:",
    logging.CRITICAL: "ERROR:",
}


# Subclassing logging.Formatter to control how each log record becomes text.
class _PrefixFormatter(logging.Formatter):
    """Render records as ``<coloured-prefix> message``."""

    # Same method name as the parent = an override of Formatter.format.
    def format(self, record: logging.LogRecord) -> str:
        # dict.get(key, default): returns the value, or "" if level not present.
        colour = _COLOURS.get(record.levelno, "")  # record.levelno is the int level
        prefix = _PREFIXES.get(record.levelno, "")
        # f-string: the {} parts are evaluated; getMessage() applies any % args.
        return f"{colour}{prefix}{_RESET} {record.getMessage()}"


# 'def name(*, verbose=...)': the bare '*' makes 'verbose' keyword-only.
def setup_logging(*, verbose: bool = False) -> None:
    """Configure the ``dotfiles`` logger to write coloured lines to stderr.

    Args:
        verbose: When True, also emit DEBUG-level messages.
    """
    handler = logging.StreamHandler()  # object: writes records to a stream (stderr)
    handler.setFormatter(_PrefixFormatter())  # attach an instance of our formatter
    root = logging.getLogger("dotfiles")  # fetch (creating if needed) a named logger
    root.handlers.clear()  # list method: drop any previously-attached handlers
    root.addHandler(handler)
    # Ternary expression: <value_if_true> if <condition> else <value_if_false>.
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    root.propagate = False  # attribute: stop messages bubbling up to the root logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``dotfiles`` namespace."""
    return logging.getLogger(f"dotfiles.{name}")  # f-string builds 'dotfiles.<name>'
