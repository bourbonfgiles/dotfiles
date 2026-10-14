"""Domain-specific exceptions for the dotfiles bootstrap."""

from __future__ import annotations


class DotfilesError(Exception):
    """Base class for all bootstrap errors; catch this to catch any of ours."""


class UnsupportedPlatformError(DotfilesError):
    """Raised when a step does not support the current operating system."""


class CommandError(DotfilesError):
    """Raised when an external command is missing or exits non-zero."""

    def __init__(
        self,
        message: str,
        *,
        returncode: int | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class StepError(DotfilesError):
    """Raised by a setup step when it cannot complete its work."""
