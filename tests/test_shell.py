"""Tests for the shell runner seam: error translation and dry-run behaviour."""

from __future__ import annotations

import pytest

from dotfiles.utils import shell
from dotfiles.utils.exceptions import CommandError
from tests.conftest import FakeRunner


def test_run_delegates_to_active_runner(fake_runner: FakeRunner) -> None:
    shell.run(["echo", "hi"], check=False)
    assert fake_runner.ran("echo", "hi")


def test_capture_returns_stripped_stdout(fake_runner: FakeRunner) -> None:
    fake_runner.script(["git", "config"], stdout="  value\n")
    assert shell.capture(["git", "config", "user.name"]) == "value"


def test_check_true_raises_command_error(fake_runner: FakeRunner) -> None:
    fake_runner.script(["false"], returncode=1, stderr="nope")
    with pytest.raises(CommandError) as excinfo:
        shell.run(["false"])
    assert excinfo.value.returncode == 1


def test_real_runner_reports_missing_command() -> None:
    # No fake installed here: SubprocessRunner should translate ENOENT.
    with pytest.raises(CommandError, match="command not found"):
        shell.run(["this-command-does-not-exist-xyz"], check=False)


def test_set_runner_returns_previous(fake_runner: FakeRunner) -> None:
    other = FakeRunner()
    previous = shell.set_runner(other)
    try:
        assert previous is fake_runner
        assert shell.get_runner() is other
    finally:
        shell.set_runner(previous)


class TestDryRunner:
    def test_mutating_command_is_skipped(self) -> None:
        runner = shell.DryRunner()
        result = runner.run(
            ["sudo", "rm", "-rf", "/tmp/x"],
            check=True,
            capture=False,
            text_input=None,
            env=None,
            cwd=None,
        )
        assert result.returncode == 0  # fabricated success, nothing executed

    def test_read_only_probe_still_runs(self) -> None:
        runner = shell.DryRunner()
        # `rpm -q` is a pure query; under dry-run it must still execute so
        # detection logic stays correct. A skipped command returns 0, so either
        # outcome proves it ran: on a Mac rpm is absent -> ENOENT; on Fedora it
        # exists and reports the package as not installed (non-zero).
        try:
            result = runner.run(
                ["rpm", "-q", "something"],
                check=False,
                capture=True,
                text_input=None,
                env=None,
                cwd=None,
            )
        except CommandError:
            return
        assert result.returncode != 0

    def test_git_config_read_vs_write(self) -> None:
        # read form: `git config key` (capture, no stdin) -> read-only
        assert shell._is_read_only(
            ["git", "config", "user.name"], capture=True, text_input=None
        )
        # write form: `git config key value` -> not read-only
        assert not shell._is_read_only(
            ["git", "config", "user.name", "Ben"], capture=False, text_input=None
        )

    def test_git_pull_is_mutating(self) -> None:
        # `git pull` and `git -C <dir> pull` both mutate -> must be skipped.
        assert not shell._is_read_only(
            ["git", "pull", "--ff-only"], capture=False, text_input=None
        )
        assert not shell._is_read_only(
            ["git", "-C", "/some/repo", "pull", "--ff-only"],
            capture=False,
            text_input=None,
        )

    def test_git_c_prefix_still_reads_config(self) -> None:
        # `git -C <dir> config key` is a read behind the -C prefix.
        assert shell._is_read_only(
            ["git", "-C", "/some/repo", "config", "user.name"],
            capture=True,
            text_input=None,
        )

    def test_git_clone_is_mutating(self) -> None:
        assert not shell._is_read_only(
            ["git", "clone", "url", "/dest"], capture=False, text_input=None
        )
