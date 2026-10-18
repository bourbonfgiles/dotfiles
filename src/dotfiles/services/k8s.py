"""Local Kubernetes via k3d on every target.

k3d runs k3s nodes as containers through the Docker API, so one tool gives the
same cluster (1 server + 3 agents) on macOS, Bazzite, and Silverblue. The
runtime is rootful Podman everywhere, since eBPF CNIs need to load programs:
the system podman.socket on Linux, the Podman machine on macOS.

The bootstrap step only verifies the runtime is ready; creating or destroying a
cluster is explicit via create_cluster() / delete_cluster(), never automatic.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger

logger = get_logger("k8s")

# Node counts, versions, disabled components, port maps, and the local registry
# all live in the chezmoi-managed config at ~/.config/k3d/config.yaml.
CLUSTER_NAME = "dev"
_PODMAN_MACHINE = "podman-machine-default"
# applehv needs no extra binary (libkrun would require krunkit). Multi-node k3d
# only works on a rootful machine — rootless leaves agents stuck in "Created".
_PODMAN_PROVIDER = "applehv"
# First run pulls the k3s image through Podman, which outlasts k3d's default.
_CREATE_TIMEOUT = "300s"
_CREATE_ATTEMPTS = 3
_CREATE_RETRY_PAUSE_S = 5
# Holds the control plane, Cilium, and a JVM game server at once; 2 GB OOMs.
_MACHINE_MEMORY_MB = 8192
# k3d prepends "k3d-" to the registry name, so this resolves as
# "k3d-registry.localhost" on the cluster network (what the config mirror uses).
_REGISTRY_NAME = "registry.localhost"
_REGISTRY_NODE_HOST = "k3d-registry.localhost"
# Bind the host-published port to loopback only; a dev registry has no reason
# to be reachable from the LAN. 5000 clashes with macOS AirPlay, so use 5050.
_REGISTRY_PORT = "127.0.0.1:5050"
# Podman's default bridge network is "podman", not the "bridge" k3d assumes on
# Docker, so registry create must pass it explicitly.
_PODMAN_NETWORK = "podman"
# Created here rather than by k3d so the bridge name and subnet are stable: the
# cluster's LoadBalancer pool and the host DNS route both depend on them.
_CLUSTER_NETWORK = "k3d-dev"
_CLUSTER_SUBNET = "10.89.0.0/24"
_CLUSTER_BRIDGE = "k3d0"
_LINUX_SOCKET = "/run/podman/podman.sock"
_SOCKET_DROPIN_DIR = "/etc/systemd/system/podman.socket.d"
_SOCKET_DROPIN = "dotfiles-wheel.conf"
_SOCKET_DROPIN_BODY = """\
[Socket]
SocketGroup=wheel
SocketMode=0660
ExecStartPre=/usr/bin/install -d -m 0750 -o root -g wheel /run/podman
"""
# Sends *.kube.internal lookups to the cluster's DNS server (kube_local's BIND
# LoadBalancer) whenever the cluster bridge exists. The link opts out of the
# global DNS-over-TLS and DNSSEC settings, which a local zone can't satisfy.
_KUBE_DNS_DOMAIN = "kube.internal"
_KUBE_DNS_SERVER = "10.89.0.250"
_KUBE_DNS_UNIT = "dotfiles-kube-dns.service"
_KUBE_DNS_UNIT_BODY = f"""\
[Unit]
Description=Resolve {_KUBE_DNS_DOMAIN} via the local k3d cluster
BindsTo=sys-subsystem-net-devices-{_CLUSTER_BRIDGE}.device
After=sys-subsystem-net-devices-{_CLUSTER_BRIDGE}.device systemd-resolved.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/resolvectl dns {_CLUSTER_BRIDGE} {_KUBE_DNS_SERVER}
ExecStart=/usr/bin/resolvectl domain {_CLUSTER_BRIDGE} ~{_KUBE_DNS_DOMAIN}
ExecStart=/usr/bin/resolvectl dnsovertls {_CLUSTER_BRIDGE} no
ExecStart=/usr/bin/resolvectl dnssec {_CLUSTER_BRIDGE} no

[Install]
WantedBy=sys-subsystem-net-devices-{_CLUSTER_BRIDGE}.device
"""
# Podman's journald log reader intermittently fails while k3d waits for a node's
# "k3s is up" line. Plain log files avoid it; capped so k3s can't fill the disk.
_PODMAN_LOGGING_CONF = "/etc/containers/containers.conf.d/dotfiles-k3d.conf"
_PODMAN_LOGGING_BODY = """\
[containers]
log_driver = "k8s-file"
log_size_max = 52428800
"""


def _machine_field(field: str) -> object | None:
    """Return a top-level field from `podman machine inspect`, or None."""
    out = shell.run(
        ["podman", "machine", "inspect", _PODMAN_MACHINE],
        check=False,
        capture=True,
    ).stdout.strip()
    if not out:
        return None
    try:
        value: object = json.loads(out)[0].get(field)
    except (json.JSONDecodeError, IndexError, KeyError, AttributeError):
        return None
    return value


def _podman_socket() -> str | None:
    """Return the Podman machine's Docker-API socket path, or None."""
    info = _machine_field("ConnectionInfo")
    if not isinstance(info, dict):
        return None
    sock = info.get("PodmanSocket", {}).get("Path")
    return sock or None


def _machine_exists() -> bool:
    return _machine_field("Name") is not None


def _machine_running() -> bool:
    listed = shell.run(
        ["podman", "machine", "list", "--format", "{{.Name}} {{.Running}}"],
        check=False,
        capture=True,
    ).stdout
    return any(
        line.startswith(_PODMAN_MACHINE) and line.endswith("true")
        for line in listed.splitlines()
    )


def _machine_memory_mb() -> int | None:
    value = _machine_field("Resources")
    if not isinstance(value, dict):
        return None
    memory = value.get("Memory")
    return memory if isinstance(memory, int) else None


def _ensure_resources() -> bool:
    """Make the machine rootful and give it enough memory; k3d requires both.

    Both are stopped-machine operations, so they are batched into one
    stop/set/start cycle. Rootful is mandatory for multi-node; the memory bump
    keeps the control plane plus Cilium and workloads off the OOM killer.
    """
    rootful = _machine_field("Rootful") is True
    sized = (_machine_memory_mb() or 0) >= _MACHINE_MEMORY_MB
    if rootful and sized:
        return True
    logger.info("Reconfiguring Podman machine (rootful + %d MB)…", _MACHINE_MEMORY_MB)
    shell.run(["podman", "machine", "stop", _PODMAN_MACHINE], check=False)
    shell.run(
        [
            "podman",
            "machine",
            "set",
            "--rootful",
            "--memory",
            str(_MACHINE_MEMORY_MB),
            _PODMAN_MACHINE,
        ],
        check=False,
    )
    started = shell.run(
        ["podman", "machine", "start", _PODMAN_MACHINE], check=False
    ).returncode
    return (
        started == 0
        and _machine_field("Rootful") is True
        and (_machine_memory_mb() or 0) >= _MACHINE_MEMORY_MB
    )


def _ensure_podman_machine() -> bool:
    """Ensure a running, rootful applehv Podman machine exists."""
    if not _machine_exists():
        logger.info(
            "Creating Podman machine %r (%s)…", _PODMAN_MACHINE, _PODMAN_PROVIDER
        )
        shell.run(
            ["podman", "machine", "init", "--provider", _PODMAN_PROVIDER], check=False
        )
    if not _machine_running():
        logger.info("Starting Podman machine %r…", _PODMAN_MACHINE)
        if (
            shell.run(
                ["podman", "machine", "start", _PODMAN_MACHINE], check=False
            ).returncode
            != 0
        ):
            return False
    return _ensure_resources()


def _linux_socket_ready() -> bool:
    try:
        return Path(_LINUX_SOCKET).is_socket() and os.access(
            _LINUX_SOCKET, os.R_OK | os.W_OK
        )
    except OSError:
        return False


def _ensure_linux_socket() -> bool:
    """Enable the rootful podman.socket and let wheel use it without sudo.

    Socket access is root-equivalent, like the docker group would be.
    """
    if _linux_socket_ready():
        return True
    logger.info("Enabling rootful podman.socket for wheel (sudo)…")
    shell.run(["sudo", "install", "-d", "-m", "0755", _SOCKET_DROPIN_DIR], check=False)
    system.sudo_write(f"{_SOCKET_DROPIN_DIR}/{_SOCKET_DROPIN}", _SOCKET_DROPIN_BODY)
    shell.run(["sudo", "systemctl", "daemon-reload"], check=False)
    shell.run(["sudo", "systemctl", "enable", "podman.socket"], check=False)
    shell.run(["sudo", "systemctl", "restart", "podman.socket"], check=False)
    return _linux_socket_ready()


def _sudo_install(path: str, body: str) -> bool:
    """Write a root-owned file unless it already matches; return True if written."""
    try:
        if Path(path).read_text(encoding="utf-8") == body:
            return False
    except OSError:
        pass
    shell.run(
        ["sudo", "install", "-d", "-m", "0755", str(Path(path).parent)], check=False
    )
    system.sudo_write(path, body)
    return True


def _ensure_host_dns() -> None:
    """Install the systemd unit that routes kube.internal to the cluster."""
    unit = f"/etc/systemd/system/{_KUBE_DNS_UNIT}"
    if not _sudo_install(unit, _KUBE_DNS_UNIT_BODY):
        return
    logger.info("Routed *.%s to the local cluster.", _KUBE_DNS_DOMAIN)
    shell.run(["sudo", "systemctl", "daemon-reload"], check=False)
    shell.run(["sudo", "systemctl", "enable", "--now", _KUBE_DNS_UNIT], check=False)


def _ensure_podman_logging() -> None:
    """Switch rootful Podman to file logging (applies to new containers)."""
    if _sudo_install(_PODMAN_LOGGING_CONF, _PODMAN_LOGGING_BODY):
        logger.info("Rootful Podman now logs to files; recreate the cluster to use it.")


def _docker_env() -> dict[str, str] | None:
    """Env that points k3d at a rootful Podman Docker-API socket.

    macOS: start the Podman machine and use its socket.
    Linux: enable the system podman.socket and use it.
    Returns None if the runtime could not be made ready.
    """
    if not platform.is_mac():
        if not _ensure_linux_socket():
            return None
        return {"DOCKER_HOST": f"unix://{_LINUX_SOCKET}"}
    if not shell.command_exists("podman") or not _ensure_podman_machine():
        return None
    sock = _podman_socket()
    if not sock:
        return None
    return {"DOCKER_HOST": f"unix://{sock}"}


def _run_env(extra: dict[str, str]) -> dict[str, str]:
    """Merge extra vars onto the current environment for a subprocess."""
    env = dict(os.environ)
    env.update(extra)
    return env


def _config_file() -> Path:
    """Path to the chezmoi-managed k3d cluster config."""
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config_home / "k3d" / "config.yaml"


def _ensure_network(env: dict[str, str]) -> bool:
    """Ensure the cluster network exists with its fixed bridge and subnet."""
    podman = ["podman", "--url", env["DOCKER_HOST"], "network"]
    exists = shell.run([*podman, "exists", _CLUSTER_NETWORK], check=False, capture=True)
    if exists.returncode == 0:
        bridge = shell.run(
            [*podman, "inspect", _CLUSTER_NETWORK, "--format", "{{.NetworkInterface}}"],
            check=False,
            capture=True,
        ).stdout.strip()
        if bridge and bridge != _CLUSTER_BRIDGE:
            logger.warning(
                "Network %r uses bridge %r, not %r, so *.%s won't resolve on the "
                "host. Delete the cluster, then `podman network rm %s` (disconnect "
                "the registry first) and create again.",
                _CLUSTER_NETWORK,
                bridge,
                _CLUSTER_BRIDGE,
                _KUBE_DNS_DOMAIN,
                _CLUSTER_NETWORK,
            )
        return True
    logger.info("Creating cluster network %r (%s)…", _CLUSTER_NETWORK, _CLUSTER_SUBNET)
    cmd = [
        *podman,
        "create",
        "--subnet",
        _CLUSTER_SUBNET,
        "--interface-name",
        _CLUSTER_BRIDGE,
        _CLUSTER_NETWORK,
    ]
    return shell.run(cmd, check=False).returncode == 0


def _ensure_registry(env: dict[str, str]) -> bool:
    """Ensure the persistent standalone registry the config references exists.

    The config uses registries.use (not create), so the registry must outlive
    any single cluster — this keeps the image cache across rebuilds. k3d
    prepends "k3d-" to the name, so "registry.localhost" resolves as
    "k3d-registry.localhost:5000" from the nodes, matching the mirror.
    """
    listed = shell.run(
        ["k3d", "registry", "list", "--output", "json"],
        check=False,
        capture=True,
        env=_run_env(env),
    ).stdout
    if _REGISTRY_NODE_HOST in listed:
        return True
    logger.info("Creating persistent registry %r…", _REGISTRY_NODE_HOST)
    cmd = [
        "k3d",
        "registry",
        "create",
        _REGISTRY_NAME,
        "--port",
        _REGISTRY_PORT,
        "--default-network",
        _PODMAN_NETWORK,
    ]
    return shell.run(cmd, check=False, env=_run_env(env)).returncode == 0


def create_cluster(name: str = CLUSTER_NAME) -> bool:
    """Create the k3d cluster from the tracked config; return True on success.

    The config pins the k3s version, disables Traefik, servicelb, Flannel, the
    default network policy, and kube-proxy, maps the host ports, and attaches
    the persistent registry. A CNI is installed afterwards, outside this step.
    """
    if not shell.command_exists("k3d"):
        logger.warning("k3d not found; cannot create a cluster.")
        return False
    extra = _docker_env()
    if extra is None:
        logger.warning("No Docker API runtime available (Podman machine?).")
        return False
    config = _config_file()
    if not config.is_file():
        logger.warning("k3d config not found at %s; run chezmoi apply.", config)
        return False
    if not _ensure_network(extra):
        logger.warning("Could not ensure the cluster network; aborting.")
        return False
    if not _ensure_registry(extra):
        logger.warning("Could not ensure the persistent registry; aborting.")
        return False
    cmd = [
        "k3d",
        "cluster",
        "create",
        name,
        "--config",
        str(config),
        "--timeout",
        _CREATE_TIMEOUT,
    ]
    # Podman's journald log reader intermittently fails while k3d waits for the
    # server (see _PODMAN_LOGGING_BODY for the fix); k3d rolls back cleanly.
    for attempt in range(1, _CREATE_ATTEMPTS + 1):
        logger.info("Creating k3d cluster %r from %s…", name, config)
        if shell.run(cmd, check=False, env=_run_env(extra)).returncode == 0:
            return True
        if attempt < _CREATE_ATTEMPTS:
            logger.warning("k3d cluster create failed; retrying.")
            time.sleep(_CREATE_RETRY_PAUSE_S)
    return False


def delete_cluster(name: str = CLUSTER_NAME) -> bool:
    """Delete the named k3d cluster; return True on success."""
    if not shell.command_exists("k3d"):
        return False
    extra = _docker_env()
    if extra is None:
        return False
    return (
        shell.run(
            ["k3d", "cluster", "delete", name],
            check=False,
            env=_run_env(extra),
        ).returncode
        == 0
    )


def run(settings: Settings) -> None:
    """Verify the k3d runtime is ready (no cluster created)."""
    if not shell.command_exists("k3d"):
        logger.warning("k3d not found; local Kubernetes unavailable.")
        return
    if _docker_env() is None:
        hint = (
            "run `podman machine start`"
            if platform.is_mac()
            else f"check `systemctl status podman.socket` and {_LINUX_SOCKET}"
        )
        logger.warning("k3d present but Podman not ready; %s.", hint)
        return
    if platform.is_linux():
        _ensure_podman_logging()
        if shell.command_exists("resolvectl"):
            _ensure_host_dns()
    logger.info("k3d ready (via Podman). create_cluster() makes the dev cluster.")


__all__ = ["create_cluster", "delete_cluster", "run", "CLUSTER_NAME"]
