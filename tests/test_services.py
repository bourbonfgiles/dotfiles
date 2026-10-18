"""Service tests exercised through the FakeRunner (no real processes)."""

from __future__ import annotations

from pathlib import Path

import pytest

from dotfiles.config.settings import Settings
from dotfiles.services import chezmoi_apply, flatpak, homebrew, k8s
from dotfiles.utils import platform, shell
from dotfiles.utils.exceptions import StepError
from tests.conftest import FakeRunner


class TestFlatpak:
    def test_read_ids_strips_comments_and_blanks(self, settings: Settings) -> None:
        path = settings.flatpaks_file
        path.write_text(
            "# header\n\norg.a.App\norg.b.App  # inline\n   \n",
            encoding="utf-8",
        )
        assert flatpak.read_ids(path) == ["org.a.App", "org.b.App"]

    def test_install_all_skips_already_installed(self, fake_runner: FakeRunner) -> None:
        # `flatpak info org.a.App` returns 0 => installed => must be skipped.
        fake_runner.script(["flatpak", "info", "org.a.App"], returncode=0)
        fake_runner.script(["flatpak", "info", "org.b.App"], returncode=1)
        flatpak.install_all(["org.a.App", "org.b.App"])
        assert not fake_runner.ran(
            "flatpak",
            "install",
            "--user",
            "--noninteractive",
            "--or-update",
            "flathub",
            "org.a.App",
        )
        assert fake_runner.ran(
            "flatpak",
            "install",
            "--user",
            "--noninteractive",
            "--or-update",
            "flathub",
            "org.b.App",
        )

    def test_run_noop_on_mac(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
        fake_runner: FakeRunner,
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: True)
        flatpak.run(settings)
        assert fake_runner.calls == []


class TestHomebrew:
    def test_taps_parsed_from_brewfile(self, settings: Settings) -> None:
        settings.brewfile.write_text(
            'tap "a/b"\nbrew "x"\ntap "c/d"\n# tap "ignored/commented"\n',
            encoding="utf-8",
        )
        assert homebrew._taps(settings.brewfile) == ["a/b", "c/d"]

    def test_run_raises_when_brew_absent(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
        fake_runner: FakeRunner,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: False)
        with pytest.raises(StepError, match="Homebrew not found"):
            homebrew.run(settings)

    def test_run_trusts_taps_and_bundles(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
        fake_runner: FakeRunner,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        settings.brewfile.write_text('tap "a/b"\nbrew "git"\n', encoding="utf-8")
        homebrew.run(settings)
        assert fake_runner.ran("brew", "trust", "a/b")
        assert fake_runner.ran("brew", "bundle", "--file", str(settings.brewfile))

    def test_run_raises_when_bundle_fails(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
        fake_runner: FakeRunner,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        fake_runner.script(["brew", "bundle"], returncode=1)
        with pytest.raises(StepError, match="brew bundle failed"):
            homebrew.run(settings)
        assert fake_runner.ran("brew", "bundle", "--file", str(settings.brewfile))


class TestChezmoiApply:
    def test_raises_when_chezmoi_absent(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: False)
        with pytest.raises(StepError, match="chezmoi not found"):
            chezmoi_apply.run(settings)

    def test_applies_with_force(
        self,
        monkeypatch: pytest.MonkeyPatch,
        settings: Settings,
        fake_runner: FakeRunner,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        (settings.repo_root / ".chezmoiroot").write_text("home\n", encoding="utf-8")
        chezmoi_apply.run(settings)
        assert fake_runner.ran(
            "chezmoi", "apply", "--source", str(settings.repo_root), "--force"
        )


class TestConfigData:
    def test_checks_use_central_data(self) -> None:
        from dotfiles.config import data
        from dotfiles.services import checks

        # checks must read from the central lists, not re-declare its own.
        assert checks.CORE_TOOLS is data.CORE_TOOLS
        assert checks.LINKED_CONFIGS is data.LINKED_CONFIGS

    def test_git_ssh_uses_central_repos(self) -> None:
        from dotfiles.config import data
        from dotfiles.services import git_ssh

        assert git_ssh.REPOS is data.REPOS

    def test_fonts_use_central_data(self) -> None:
        from dotfiles.config import data
        from dotfiles.services import fonts

        assert fonts.NERD_FONTS is data.NERD_FONTS


class TestK8s:
    def test_create_cluster_runs_k3d_on_linux(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        tmp_path: Path,
    ) -> None:
        config = tmp_path / "k3d" / "config.yaml"
        config.parent.mkdir(parents=True)
        config.write_text("apiVersion: k3d.io/v1alpha5\n", encoding="utf-8")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(platform, "is_mac", lambda: False)
        monkeypatch.setattr(shell, "command_exists", lambda n: n == "k3d")
        assert k8s.create_cluster("dev") is True
        assert fake_runner.ran(
            "k3d", "registry", "create", "registry.localhost", "--port", "5050"
        )
        assert fake_runner.ran(
            "k3d", "cluster", "create", "dev", "--config", str(config)
        )

    def test_create_cluster_sets_docker_host_on_mac(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "k3d" / "config.yaml"
        config.parent.mkdir(parents=True)
        config.write_text("apiVersion: k3d.io/v1alpha5\n", encoding="utf-8")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(platform, "is_mac", lambda: True)
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        monkeypatch.setattr(k8s, "_ensure_podman_machine", lambda: True)
        monkeypatch.setattr(k8s, "_podman_socket", lambda: "/tmp/p.sock")
        seen: dict[str, str] = {}

        def fake_run(cmd, *, check, env=None, **kw):  # type: ignore[no-untyped-def]
            seen.update(env or {})
            import subprocess

            return subprocess.CompletedProcess(cmd, 0, "", "")

        monkeypatch.setattr(shell, "run", fake_run)
        assert k8s.create_cluster("dev") is True
        assert seen["DOCKER_HOST"] == "unix:///tmp/p.sock"

    def test_create_cluster_noop_without_k3d(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda _n: False)
        assert k8s.create_cluster() is False
        assert fake_runner.calls == []

    def test_create_cluster_noop_when_mac_runtime_missing(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: True)
        # k3d exists, but podman does not -> no Docker API available.
        monkeypatch.setattr(shell, "command_exists", lambda n: n == "k3d")
        assert k8s.create_cluster() is False
        assert not fake_runner.ran("k3d", "cluster", "create")
