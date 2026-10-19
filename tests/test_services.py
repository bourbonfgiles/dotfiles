"""Service tests exercised through the FakeRunner (no real processes)."""

from __future__ import annotations

from pathlib import Path

import pytest

from dotfiles.config.settings import Settings
from dotfiles.services import bpf, chezmoi_apply, flatpak, homebrew, k8s, krew
from dotfiles.utils import platform, shell
from dotfiles.utils.exceptions import StepError
from dotfiles.utils.platform import OSKind
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


@pytest.fixture
def no_system_files(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make _sudo_install see no existing file, whatever this host has in /etc."""

    def missing(self: object, *args: object, **kwargs: object) -> str:
        raise FileNotFoundError

    monkeypatch.setattr(Path, "read_text", missing)


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
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: True)
        monkeypatch.setattr(shell, "command_exists", lambda n: n == "k3d")
        assert k8s.create_cluster("dev") is True
        assert fake_runner.ran("k3d", "registry", "create", "registry.localhost")
        assert fake_runner.ran(
            "k3d", "cluster", "create", "dev", "--config", str(config)
        )

    def test_create_cluster_pins_server_ip(
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
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: True)
        monkeypatch.setattr(shell, "command_exists", lambda n: n == "k3d")
        sock = "unix:///run/podman/podman.sock"
        fake_runner.script(
            ["podman", "--url", sock, "inspect", "k3d-dev-server-0"],
            stdout="10.89.0.20\n",
        )
        assert k8s.create_cluster("dev") is True
        assert fake_runner.ran(
            "podman",
            "--url",
            sock,
            "network",
            "connect",
            "--ip",
            "10.89.0.20",
            "k3d-dev",
            "k3d-dev-server-0",
        )

    def test_create_cluster_retries(
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
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: True)
        monkeypatch.setattr(shell, "command_exists", lambda n: n == "k3d")
        monkeypatch.setattr(k8s, "_CREATE_RETRY_PAUSE_S", 0)
        fake_runner.script(["k3d", "cluster", "create"], returncode=1)
        assert k8s.create_cluster("dev") is False
        creates = [
            c for c in fake_runner.calls if c[:3] == ["k3d", "cluster", "create"]
        ]
        assert len(creates) == 3

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

    def test_network_created_with_fixed_subnet_and_bridge(
        self, fake_runner: FakeRunner
    ) -> None:
        sock = {"DOCKER_HOST": "unix:///run/podman/podman.sock"}
        podman = ["podman", "--url", "unix:///run/podman/podman.sock", "network"]
        fake_runner.script([*podman, "exists"], returncode=1)
        assert k8s._ensure_network(sock) is True
        assert fake_runner.ran(
            *podman,
            "create",
            "--subnet",
            "10.89.0.0/24",
            "--interface-name",
            "k3d0",
            "k3d-dev",
        )

    def test_existing_network_is_reused(self, fake_runner: FakeRunner) -> None:
        assert k8s._ensure_network({"DOCKER_HOST": "unix:///s"}) is True
        assert not fake_runner.ran("podman", "--url", "unix:///s", "network", "create")

    def test_host_dns_unit_routes_domain_on_cluster_bridge(
        self, fake_runner: FakeRunner, no_system_files: None
    ) -> None:
        body = k8s._KUBE_DNS_UNIT_BODY
        assert "BindsTo=sys-subsystem-net-devices-k3d0.device" in body
        assert "resolvectl dns k3d0 10.89.0.250" in body
        assert "resolvectl domain k3d0 ~kube.internal" in body
        assert "resolvectl dnsovertls k3d0 no" in body
        k8s._ensure_host_dns()
        assert fake_runner.ran(
            "sudo", "tee", "/etc/systemd/system/dotfiles-kube-dns.service"
        )
        assert fake_runner.ran(
            "sudo", "systemctl", "enable", "--now", "dotfiles-kube-dns.service"
        )

    def test_podman_logging_drop_in_uses_capped_files(
        self, fake_runner: FakeRunner, no_system_files: None
    ) -> None:
        assert 'log_driver = "k8s-file"' in k8s._PODMAN_LOGGING_BODY
        assert "log_size_max" in k8s._PODMAN_LOGGING_BODY
        k8s._ensure_podman_logging()
        assert fake_runner.ran(
            "sudo", "tee", "/etc/containers/containers.conf.d/dotfiles-k3d.conf"
        )

    def test_registry_create_uses_podman_network(self, fake_runner: FakeRunner) -> None:
        assert k8s._ensure_registry({}) is True
        assert fake_runner.ran(
            "k3d",
            "registry",
            "create",
            "registry.localhost",
            "--port",
            "127.0.0.1:5050",
            "--default-network",
            "podman",
        )

    def test_linux_points_docker_host_at_rootful_podman(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: False)
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: True)
        assert k8s._docker_env() == {"DOCKER_HOST": "unix:///run/podman/podman.sock"}
        assert fake_runner.calls == []

    def test_linux_enables_socket_for_wheel_when_unreachable(
        self, monkeypatch: pytest.MonkeyPatch, fake_runner: FakeRunner
    ) -> None:
        monkeypatch.setattr(platform, "is_mac", lambda: False)
        monkeypatch.setattr(k8s, "_linux_socket_ready", lambda: False)
        assert k8s._docker_env() is None
        assert fake_runner.ran(
            "sudo", "tee", "/etc/systemd/system/podman.socket.d/dotfiles-wheel.conf"
        )
        assert fake_runner.ran("sudo", "systemctl", "restart", "podman.socket")


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


class TestBpf:
    def test_noop_on_mac(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(platform, "os_kind", lambda: OSKind.MAC)
        bpf.run(settings)
        assert fake_runner.calls == []

    def test_layers_all_packages_on_atomic_fedora(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_runner: FakeRunner,
        settings: Settings,
    ) -> None:
        monkeypatch.setattr(platform, "os_kind", lambda: OSKind.BAZZITE)
        fake_runner.script(["rpm", "-q"], returncode=1)
        bpf.run(settings)
        for package in ("bpftrace", "bcc-tools", "bpftool", "perf"):
            assert fake_runner.ran(
                "sudo", "rpm-ostree", "install", "--idempotent", package
            )
