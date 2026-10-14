"""Mutable run-time options set once from the CLI, read by services.

Settings holds immutable filesystem paths; these are the per-invocation
behaviour switches (``--yes``, ``--strict``). Keeping them in one tiny module
avoids threading extra parameters through every service's ``run(settings)``
signature — services import and read these flags directly, the same way they
use the shell runner seam.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Options:
    """Per-run behaviour switches."""

    assume_yes: bool = False  # --yes
    strict: bool = False  # --strict


_options = Options()


def configure(*, assume_yes: bool = False, strict: bool = False) -> None:
    """Set the process-wide options (called once from bootstrap.run)."""
    global _options
    _options = Options(assume_yes=assume_yes, strict=strict)


def current() -> Options:
    """Return the active options."""
    return _options
