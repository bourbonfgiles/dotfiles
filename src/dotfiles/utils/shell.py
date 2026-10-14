"""Thin subprocess wrapper with logging, dry-run, and uniform error handling."""

from __future__ import annotations

import shutil  # stdlib: high-level helpers (shutil.which finds programs on PATH)
import subprocess  # stdlib: spawn and manage external programs
from collections.abc import Mapping, Sequence  # abstract types used in hints only
from typing import Protocol  # Protocol: structural ("duck") typing for the runner

from .exceptions import CommandError  # relative import: '.' = this package (utils)
from .logging import get_logger

logger = get_logger("shell")  # one module-level logger instance


def which(name: str) -> str | None:  # returns a path string, or None if not found
    """Return the absolute path to ``name`` on PATH, or None."""
    return shutil.which(name)


def command_exists(name: str) -> bool:
    """Return True if ``name`` is found on PATH."""
    return shutil.which(name) is not None  # 'is not None' = explicit None test


# A Runner is anything with a run() method of this shape. Making the executor a
# swappable object (rather than calling subprocess directly) is the single seam
# that unlocks both --dry-run (DryRunner) and unit testing (a fake in tests).
class Runner(Protocol):
    """Structural type: an object that can execute a command."""

    def run(
        self,
        cmd: Sequence[str],
        *,
        check: bool,
        capture: bool,
        text_input: str | None,
        env: Mapping[str, str] | None,
        cwd: str | None,
    ) -> subprocess.CompletedProcess[str]: ...


class SubprocessRunner:
    """The real runner: actually spawns the process via ``subprocess``."""

    def run(
        self,
        cmd: Sequence[str],
        *,
        check: bool,
        capture: bool,
        text_input: str | None,
        env: Mapping[str, str] | None,
        cwd: str | None,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(  # the call that actually starts the process
                list(cmd),  # list(): copy/normalise the sequence into a list
                check=check,  # if True, a non-zero exit raises CalledProcessError
                text=True,  # decode stdout/stderr as str (not raw bytes)
                capture_output=capture,
                input=text_input,
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


class DryRunner:
    """A runner that executes read-only probes but only logs mutating commands.

    Pure queries (``capture=True`` with no ``text_input``) still run so that
    detection logic — ``git config``, ``rpm -q``, ``flatpak info`` — keeps
    working under ``--dry-run``. Anything that could change the system is logged
    and skipped, returning a success-shaped result so callers proceed as if it
    had worked.
    """

    def __init__(self) -> None:
        self._real = SubprocessRunner()

    def run(
        self,
        cmd: Sequence[str],
        *,
        check: bool,
        capture: bool,
        text_input: str | None,
        env: Mapping[str, str] | None,
        cwd: str | None,
    ) -> subprocess.CompletedProcess[str]:
        if _is_read_only(cmd, capture=capture, text_input=text_input):
            return self._real.run(
                cmd,
                check=check,
                capture=capture,
                text_input=text_input,
                env=env,
                cwd=cwd,
            )
        logger.info("[dry-run] would run: %s", " ".join(cmd))
        # Fabricate a success result so callers treat the step as having worked.
        return subprocess.CompletedProcess(
            list(cmd), returncode=0, stdout="", stderr=""
        )


# Commands whose first token is purely informational — safe to execute even in
# dry-run because they never mutate state.
_READ_ONLY_PROGRAMS = frozenset(
    {"rpm", "flatpak", "fc-list", "getent", "defaults", "scutil"}
)
# Subcommands that are read-only for programs that are otherwise mutating.
_READ_ONLY_SUBCOMMANDS = {
    "git": frozenset({"config", "-C"}),
    "rpm-ostree": frozenset({"status"}),
    "brew": frozenset({"list"}),
}


def _is_read_only(cmd: Sequence[str], *, capture: bool, text_input: str | None) -> bool:
    """Best-effort guess at whether ``cmd`` only reads state."""
    if not cmd:
        return False
    program = cmd[0]
    if program in _READ_ONLY_PROGRAMS:
        return True
    subs = _READ_ONLY_SUBCOMMANDS.get(program)
    if subs is not None and len(cmd) > 1 and cmd[1] in subs:
        # `git config key` reads; `git config key value` writes. Treat a bare
        # read (capture with no stdin) as safe, otherwise assume a mutation.
        if program == "git" and cmd[1] == "config":
            return capture and text_input is None
        return True
    return False


# The active runner. Swapped by set_runner() for dry-run or tests; everything
# in the codebase calls the module-level run()/capture() below, never a runner
# object directly, so this single switch changes behaviour everywhere at once.
_runner: Runner = SubprocessRunner()


def set_runner(runner: Runner) -> Runner:
    """Install ``runner`` as the active executor; return the previous one."""
    global _runner  # rebind the module-level name (not a local)
    previous = _runner
    _runner = runner
    return previous


def get_runner() -> Runner:
    """Return the active runner."""
    return _runner


def run(
    cmd: Sequence[str],  # a sequence (list/tuple) of argument strings
    *,  # everything below is keyword-only (caller must name it)
    check: bool = True,
    capture: bool = False,
    text_input: str | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:  # returns the finished-process object
    """Run an external command through the active runner.

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
    return _runner.run(
        cmd,
        check=check,
        capture=capture,
        text_input=text_input,
        env=env,
        cwd=cwd,
    )


def capture(cmd: Sequence[str]) -> str:
    """Run ``cmd`` and return its stripped stdout."""
    # .stdout is a CompletedProcess attribute; .strip() trims surrounding whitespace.
    return run(cmd, capture=True).stdout.strip()
