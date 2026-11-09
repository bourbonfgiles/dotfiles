"""Service tests exercised through the FakeRunner (no real processes)."""

from __future__ import annotations

from pathlib import Path

import pytest

from dotfiles.config.settings import Settings
from dotfiles.services import chezmoi_apply, dns, flatpak, homebrew, k8s, krew
from dotfiles.utils import platform, shell
from dotfiles.utils.exceptions import StepError
from tests.conftest import FakeRunner


class TestDns:
    def test_wired_profiles_ignore_dhcp_resolvers(
        self, fake_runner: FakeRunner
    ) -> None:
        fake_runner.script(
            ["nmcli", "-t", "-f", "UUID,TYPE,DEVICE", "connection", "show"],
            stdout="aaa:802-3-ethernet:enp5s0\nbbb:802-11-wireless:\nccc:802-3-ethernet:\n",
        )
        dns._ignore_lan_dns()
        for uuid_ in ("aaa", "ccc"):
            assert fake_runner.ran(
                "sudo",
                "nmcli",
                "connection",
                "modify",
                uuid_,
                "ipv4.ignore-auto-dns",
                "yes",
                "ipv6.ignore-auto-dns",
                "yes",
            )
        assert not fake_runner.ran("sudo", "nmcli", "connection", "modify", "bbb")
        assert fake_runner.ran("sudo", "nmcli", "device", "reapply", "enp5s0")
        assert fake_runner.ran("sudo", "resolvectl", "revert", "enp5s0")
        assert not fake_runner.ran("sudo", "nmcli", "device", "reapply", "")


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


@pytest.fixture
def no_system_files(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make _sudo_install see no existing file, whatever this host has in /etc."""

    def missing(self: object, *args: object, **kwargs: object) -> str:
        raise FileNotFoundError

    monkeypatch.setattr(Path, "read_text", missing)


class TestK8s:
    def test_linux_only_checks_the_image_socket(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: False)
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: False)
        k8s.run(settings)
        assert fake_runner.calls == []

    def test_mac_makes_machine_rootful_with_memory(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: True)
        monkeypatch.setattr(shell, "command_exists", lambda _n: True)
        fake_runner.script(
            ["podman", "machine", "inspect", "podman-machine-default"],
            stdout='[{"Name": "podman-machine-default", "Rootful": false, "Resources": {"Memory": 2048}}]',
        )
        fake_runner.script(
            ["podman", "machine", "list", "--format", "{{.Name}} {{.Running}}"],
            stdout="podman-machine-default true\n",
        )
        k8s.run(settings)
        assert fake_runner.ran(
            "podman", "machine", "set", "--rootful", "--memory", "8192"
        )
        assert not fake_runner.ran("podman", "machine", "init")


class TestKrew:
    def test_skips_without_krew(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda name: False)
        krew.run(settings)
        assert fake_runner.calls == []

    def test_installs_only_missing_plugins(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda name: True)
        fake_runner.script(["kubectl", "krew", "list"], stdout="krew\naccess-matrix\n")
        krew.run(settings)
        assert fake_runner.ran("kubectl", "krew", "install", "rbac-tool")
        assert not fake_runner.ran("kubectl", "krew", "install", "access-matrix")

    def test_noop_when_all_installed(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(shell, "command_exists", lambda name: True)
        fake_runner.script(
            ["kubectl", "krew", "list"], stdout="access-matrix\nrbac-tool\n"
        )
        krew.run(settings)
        assert not fake_runner.ran("kubectl", "krew", "update")
