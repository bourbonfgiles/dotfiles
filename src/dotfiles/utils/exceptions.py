"""Domain-specific exceptions for the dotfiles bootstrap."""

# 'from __future__ import annotations' makes every type hint lazy (stored as a
# string), so modern syntax like 'int | None' works on older Pythons too.
from __future__ import annotations


# 'class Name(Base):' defines a new type. Subclassing the built-in 'Exception'
# makes these usable with 'raise'/'except'. This base lets callers catch every
# error of ours with a single 'except DotfilesError'.
class DotfilesError(Exception):
    """Base class for all bootstrap errors."""  # docstring (shown by help())


# Subclassing DotfilesError: inherits its behaviour, just a more specific name.
class UnsupportedPlatformError(DotfilesError):
    """Raised when a step does not support the current operating system."""


class CommandError(DotfilesError):
    """Raised when an external command is missing or exits non-zero."""

    # '__init__' is the constructor (a 'dunder' = double-underscore method) that
    # runs when you create an instance. 'self' is the instance being built.
    def __init__(
        self,
        message: str,  # positional parameter with a type hint (str)
        *,  # bare '*' forces the following parameters to be keyword-only
        returncode: int | None = None,  # type is 'int OR None'; default None
        stderr: str | None = None,
    ) -> None:  # '-> None' means the function returns nothing
        super().__init__(message)  # call the parent Exception's constructor
        self.returncode = returncode  # store as an instance attribute
        self.stderr = stderr


class StepError(DotfilesError):
    """Raised by a setup step when it cannot complete its work."""
