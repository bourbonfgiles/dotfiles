"""Tests for --yes (non-interactive) and --strict behaviour."""

from __future__ import annotations

import builtins

import pytest

from dotfiles.config import runtime
from dotfiles.config.settings import Settings
from dotfiles.services import checks, git_ssh
from dotfiles.utils import shell
from dotfiles.utils.exceptions import StepError
from tests.conftest import FakeRunner


def _no_input(*_a: object, **_k: object) -> str:
    raise AssertionError("input() must not be called under --yes")


class TestAssumeYes:
    def test_identity_does_not_prompt_when_unset(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        runtime.configure(assume_yes=True)
        # git config returns empty (unset) for both keys via the default match.
        monkeypatch.setattr(builtins, "input", _no_input)
        assert git_ssh._configure_identity() == ""

    def test_identity_prompts_when_interactive(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        runtime.configure(assume_yes=False)
        answers = iter(["me@example.com", "me"])
        monkeypatch.setattr(builtins, "input", lambda _p="": next(answers))
        assert git_ssh._configure_identity() == "me@example.com"
        assert fake_runner.ran("git", "config", "--global", "user.email")


class TestStrictChecks:
    def _settings(self, tmp_path: object) -> Settings:
        from pathlib import Path

        base = Path(str(tmp_path))
        return Settings(home=base, repo_root=base, config_home=base)

    def test_strict_raises_on_missing(
        self, monkeypatch: pytest.MonkeyPatch, settings: Settings
    ) -> None:
        runtime.configure(strict=True)
        monkeypatch.setattr(shell, "command_exists", lambda _n: False)
        with pytest.raises(StepError, match="missing core tools"):
            checks.run(settings)

    def test_non_strict_never_raises(
        self, monkeypatch: pytest.MonkeyPatch, settings: Settings
    ) -> None:
        runtime.configure(strict=False)
        monkeypatch.setattr(shell, "command_exists", lambda _n: False)
        checks.run(settings)
