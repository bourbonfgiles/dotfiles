"""Thin subprocess wrapper with logging, dry-run, and uniform error handling."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Mapping, Sequence
from typing import Protocol

from .exceptions import CommandError
from .logging import get_logger

logger = get_logger("shell")


def which(name: str) -> str | None:
    """Return the absolute path to ``name`` on PATH, or None."""
    return shutil.which(name)


def command_exists(name: str) -> bool:
    """Return True if ``name`` is found on PATH."""
    return shutil.which(name) is not None


# Making the executor swappable (rather than calling subprocess directly) is the
# seam that unlocks both --dry-run and unit testing.
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
            return subprocess.run(
                list(cmd),
                check=check,
                text=True,
                capture_output=capture,
                input=text_input,
                env=dict(env) if env is not None else None,
                cwd=cwd,
            )
        except FileNotFoundError as exc:
            raise CommandError(f"command not found: {cmd[0]}") from exc
        except subprocess.CalledProcessError as exc:
            raise CommandError(
                f"command failed ({exc.returncode}): {' '.join(cmd)}",
                returncode=exc.returncode,
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
        # Success-shaped result so callers proceed as if the command had run.
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
    "rpm-ostree": frozenset({"status"}),
    "brew": frozenset({"list"}),
}
# Read-only git subcommands (judged after any leading `-C <dir>`).
_GIT_READ_ONLY = frozenset({"config", "status", "rev-parse", "remote", "log"})


def _git_subcommand(cmd: Sequence[str]) -> str | None:
    """Return git's real subcommand, skipping a leading ``-C <dir>``."""
    i = 1
    while i < len(cmd) and cmd[i] == "-C":
        i += 2  # skip the flag and its directory argument
    return cmd[i] if i < len(cmd) else None


def _is_read_only(cmd: Sequence[str], *, capture: bool, text_input: str | None) -> bool:
    """Best-effort guess at whether ``cmd`` only reads state."""
    if not cmd:
        return False
    program = cmd[0]
    if program in _READ_ONLY_PROGRAMS:
        return True
    if program == "git":
        # Judge the real subcommand, not `-C` — `git -C dir pull` MUTATES.
        sub = _git_subcommand(cmd)
        if sub not in _GIT_READ_ONLY:
            return False
        if sub == "config":
            # `git config key` reads; `git config key value` writes.
            return capture and text_input is None
        return True
    subs = _READ_ONLY_SUBCOMMANDS.get(program)
    if subs is not None and len(cmd) > 1 and cmd[1] in subs:
        return True
    return False


# The active runner, swapped by set_runner() for dry-run or tests. Everything
# calls the module-level run()/capture() below, so this one switch changes
# command execution everywhere at once.
_runner: Runner = SubprocessRunner()


def set_runner(runner: Runner) -> Runner:
    """Install ``runner`` as the active executor; return the previous one."""
    global _runner
    previous = _runner
    _runner = runner
    return previous


def get_runner() -> Runner:
    """Return the active runner."""
    return _runner


def run(
    cmd: Sequence[str],
    *,
    check: bool = True,
    capture: bool = False,
    text_input: str | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:
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
    logger.debug("run: %s", " ".join(cmd))
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
    return run(cmd, capture=True).stdout.strip()
