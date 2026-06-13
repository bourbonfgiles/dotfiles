"""Thin subprocess wrapper with logging and uniform error handling."""

from __future__ import annotations

import shutil  # stdlib: high-level helpers (shutil.which finds programs on PATH)
import subprocess  # stdlib: spawn and manage external programs
from collections.abc import Mapping, Sequence  # abstract types used in hints only

from .exceptions import CommandError  # relative import: '.' = this package (utils)
from .logging import get_logger

logger = get_logger("shell")  # one module-level logger instance


def which(name: str) -> str | None:  # returns a path string, or None if not found
    """Return the absolute path to ``name`` on PATH, or None."""
    return shutil.which(name)


def command_exists(name: str) -> bool:
    """Return True if ``name`` is found on PATH."""
    return shutil.which(name) is not None  # 'is not None' = explicit None test


def run(
    cmd: Sequence[str],  # a sequence (list/tuple) of argument strings
    *,  # everything below is keyword-only (caller must name it)
    check: bool = True,
    capture: bool = False,
    text_input: str | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:  # returns the finished-process object
    """Run an external command.

    Args:
        cmd: Program and arguments.
        check: Raise :class:`CommandError` on a non-zero exit.
        capture: Capture stdout/stderr instead of streaming them.
        text_input: Optional text fed to the process's stdin.
        env: Optional full environment for the child process.
        cwd: Optional working directory.

    Returns:
        The completed process.

    Raises:
        CommandError: If the program is missing or (when ``check``) it fails.
    """
    logger.debug(
        "run: %s", " ".join(cmd)
    )  # %s is lazy formatting; str.join builds text
    try:
        return subprocess.run(  # the call that actually starts the process
            list(cmd),  # list(): copy/normalise the sequence into a list
            check=check,  # if True, a non-zero exit raises CalledProcessError
            text=True,  # decode stdout/stderr as str (not raw bytes)
            capture_output=capture,
            input=text_input,
            # Conditional expression deciding the env argument:
            env=dict(env) if env is not None else None,
            cwd=cwd,
        )
    except FileNotFoundError as exc:  # 'as exc' binds the caught exception object
        # 'raise NEW from exc' chains exceptions, preserving the original cause.
        raise CommandError(f"command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise CommandError(
            f"command failed ({exc.returncode}): {' '.join(cmd)}",
            returncode=exc.returncode,  # attribute read off the caught exception
            stderr=exc.stderr,
        ) from exc


def capture(cmd: Sequence[str]) -> str:
    """Run ``cmd`` and return its stripped stdout."""
    # .stdout is a CompletedProcess attribute; .strip() trims surrounding whitespace.
    return run(cmd, capture=True).stdout.strip()
