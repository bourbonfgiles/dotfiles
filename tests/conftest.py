"""Shared pytest fixtures: a fake command runner and a temp Settings.

The whole point of the runner seam in ``utils.shell`` is this file: tests
install a :class:`FakeRunner` so service/orchestrator code can be exercised
without ever spawning a real process.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

import pytest

from dotfiles.config import runtime
from dotfiles.config.settings import Settings
from dotfiles.utils import shell


class FakeRunner:
    """Records every command and returns scripted results instead of running.

    Scripting: map a command *prefix* (tuple of the first N argv tokens) to a
    ``(returncode, stdout, stderr)`` triple via :meth:`script`. Unmatched
    commands return a success/empty result. Every call is appended to
    :attr:`calls` for assertions.
    """

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self._scripts: dict[tuple[str, ...], tuple[int, str, str]] = {}

    def script(
        self,
        prefix: Sequence[str],
        *,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Make commands starting with ``prefix`` return this result."""
        self._scripts[tuple(prefix)] = (returncode, stdout, stderr)

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
        argv = list(cmd)
        self.calls.append(argv)
        returncode, stdout, stderr = self._match(argv)
        if check and returncode != 0:
            from dotfiles.utils.exceptions import CommandError

            raise CommandError(
                f"command failed ({returncode}): {' '.join(argv)}",
                returncode=returncode,
                stderr=stderr,
            )
        return subprocess.CompletedProcess(argv, returncode, stdout, stderr)

    def _match(self, argv: list[str]) -> tuple[int, str, str]:
        # Prefer the longest matching prefix so specific scripts win over broad ones.
        best: tuple[int, str, str] | None = None
        best_len = -1
        for prefix, result in self._scripts.items():
            n = len(prefix)
            if argv[:n] == list(prefix) and n > best_len:
                best, best_len = result, n
        return best if best is not None else (0, "", "")

    def ran(self, *tokens: str) -> bool:
        """Return True if some recorded call starts with ``tokens``."""
        n = len(tokens)
        return any(call[:n] == list(tokens) for call in self.calls)


@pytest.fixture
def fake_runner() -> Iterator[FakeRunner]:
    """Install a FakeRunner for the duration of a test, then restore the real one."""
    runner = FakeRunner()
    previous = shell.set_runner(runner)
    try:
        yield runner
    finally:
        shell.set_runner(previous)


@pytest.fixture(autouse=True)
def reset_runtime_options() -> Iterator[None]:
    """Reset process-wide run options before and after every test."""
    runtime.configure(assume_yes=False, strict=False)
    yield
    runtime.configure(assume_yes=False, strict=False)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """A Settings pointing at a throwaway repo layout under tmp_path."""
    repo = tmp_path / "repo"
    (repo / "home").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("", encoding="utf-8")
    (repo / "brewfile").write_text('tap "example/tap"\nbrew "git"\n', encoding="utf-8")
    (repo / "flatpaks").write_text("# comment\norg.example.App\n", encoding="utf-8")
    config_home = tmp_path / "config"
    config_home.mkdir()
    return Settings(home=tmp_path, repo_root=repo, config_home=config_home)
