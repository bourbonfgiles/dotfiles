"""Tests for the shared rpm-ostree helpers in utils.system."""

from __future__ import annotations

import pytest

from dotfiles.utils import system
from tests.conftest import FakeRunner


class TestEnsureRepoFile:
    def test_writes_when_absent(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(system.Path, "exists", lambda _self: False)
        system.ensure_repo_file("/etc/yum.repos.d/x.repo", "body", label="X")
        # sudo_write shells out to `sudo tee <path>`
        assert fake_runner.ran("sudo", "tee", "/etc/yum.repos.d/x.repo")

    def test_skips_when_present(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(system.Path, "exists", lambda _self: True)
        system.ensure_repo_file("/etc/yum.repos.d/x.repo", "body", label="X")
        assert not fake_runner.ran("sudo", "tee")


class TestInstallOrMigrate:
    def test_fresh_install_layers_package(self, fake_runner: FakeRunner) -> None:
        fake_runner.script(
            ["rpm", "-q", "warp-terminal"], returncode=1
        )  # not installed
        system.rpmostree_install_or_migrate("warp-terminal", label="Warp")
        assert fake_runner.ran(
            "sudo", "rpm-ostree", "install", "--idempotent", "warp-terminal"
        )
        assert not fake_runner.ran("sudo", "rpm-ostree", "uninstall")

    def test_migrates_local_package(self, fake_runner: FakeRunner) -> None:
        fake_runner.script(["rpm", "-q", "warp-terminal"], returncode=0)  # installed
        fake_runner.script(
            ["rpm-ostree", "status"], stdout="LocalPackages: warp-terminal-1\n"
        )
        system.rpmostree_install_or_migrate("warp-terminal", label="Warp")
        assert fake_runner.ran("sudo", "rpm-ostree", "uninstall", "warp-terminal")
        assert fake_runner.ran("sudo", "rpm-ostree", "install", "warp-terminal")

    def test_already_repo_layered_is_noop(self, fake_runner: FakeRunner) -> None:
        fake_runner.script(["rpm", "-q", "warp-terminal"], returncode=0)  # installed
        fake_runner.script(["rpm-ostree", "status"], stdout="no local packages here\n")
        system.rpmostree_install_or_migrate("warp-terminal", label="Warp")
        assert not fake_runner.ran("sudo", "rpm-ostree", "uninstall")
        assert not fake_runner.ran("sudo", "rpm-ostree", "install", "warp-terminal")
