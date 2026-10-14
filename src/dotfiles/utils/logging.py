"""Coloured, prefixed logging that mirrors the old ==> / WARN: / ERROR output."""

from __future__ import annotations

import logging

_RESET = "\033[0m"
_COLOURS = {
    logging.DEBUG: "\033[2m",
    logging.INFO: "\033[1;32m",
    logging.WARNING: "\033[1;33m",
    logging.ERROR: "\033[1;31m",
    logging.CRITICAL: "\033[1;31m",
}
_PREFIXES = {
    logging.DEBUG: "...",
    logging.INFO: "==>",
    logging.WARNING: "WARN:",
    logging.ERROR: "ERROR:",
    logging.CRITICAL: "ERROR:",
}


class _PrefixFormatter(logging.Formatter):
    """Render records as ``<coloured-prefix> message``."""

    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelno, "")
        prefix = _PREFIXES.get(record.levelno, "")
        return f"{colour}{prefix}{_RESET} {record.getMessage()}"


def setup_logging(*, verbose: bool = False) -> None:
    """Configure the ``dotfiles`` logger to write coloured lines to stderr.

    Args:
        verbose: When True, also emit DEBUG-level messages.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(_PrefixFormatter())
    root = logging.getLogger("dotfiles")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    root.propagate = False  # don't double-log through the root logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``dotfiles`` namespace."""
    return logging.getLogger(f"dotfiles.{name}")
