"""Local Kubernetes via k3d on every target.

k3d runs k3s nodes as containers through the Docker API, so one tool gives the
same classic 3-node cluster (1 server + 2 agents) on macOS, Bazzite, and
Silverblue. On Linux k3d talks to docker/podman directly; on macOS it talks to
the Podman machine's Docker-compatible socket via DOCKER_HOST.

The bootstrap step only verifies the runtime is ready; creating or destroying a
cluster is explicit via create_cluster() / delete_cluster(), never automatic.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("k8s")

# Node counts, versions, disabled components, and port maps live in the
# chezmoi-managed config at ~/.config/k3d/config.yaml.
CLUSTER_NAME = "dev"
_PODMAN_MACHINE = "podman-machine-default"
# applehv needs no extra binary (libkrun would require krunkit). Multi-node k3d
# only works on a rootful machine — rootless leaves agents stuck in "Created".
_PODMAN_PROVIDER = "applehv"
# First run pulls the k3s image through Podman, which outlasts k3d's default.
_CREATE_TIMEOUT = "300s"
# Holds the control plane, Cilium, and a JVM game server at once; 2 GB OOMs.
_MACHINE_MEMORY_MB = 8192
_REGISTRY_NAME = "k3d-registry.localhost"
_REGISTRY_PORT = "5000"


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


def _docker_env() -> dict[str, str] | None:
    """Env that points k3d at a Docker API.

    macOS: start the Podman machine and set DOCKER_HOST to its socket.
    Linux: None — k3d uses the ambient docker/podman socket as-is.
    Returns an empty dict on Linux-with-nothing-extra, or None if the macOS
    runtime could not be made ready.
    """
    if not platform.is_mac():
        return {}
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


def _ensure_registry(env: dict[str, str]) -> bool:
    """Ensure the shared local registry the cluster config mirrors exists."""
    listed = shell.run(
        ["k3d", "registry", "list", "--output", "json"],
        check=False,
        capture=True,
        env=_run_env(env),
    ).stdout
    if _REGISTRY_NAME in listed or f"k3d-{_REGISTRY_NAME}" in listed:
        return True
    logger.info("Creating k3d registry %r…", _REGISTRY_NAME)
    return (
        shell.run(
            ["k3d", "registry", "create", _REGISTRY_NAME, "--port", _REGISTRY_PORT],
            check=False,
            env=_run_env(env),
        ).returncode
        == 0
    )


def create_cluster(name: str = CLUSTER_NAME) -> bool:
    """Create the k3d cluster from the tracked config; return True on success.

    The config pins the k3s version, disables Traefik, servicelb, Flannel, the
    default network policy, and kube-proxy, and maps the host ports. A CNI is
    expected to be installed afterwards (handled outside this step).
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
    if not _ensure_registry(extra):
        logger.warning("Could not ensure the local registry; aborting create.")
        return False
    logger.info("Creating k3d cluster %r from %s…", name, config)
    return (
        shell.run(
            [
                "k3d",
                "cluster",
                "create",
                name,
                "--config",
                str(config),
                "--timeout",
                _CREATE_TIMEOUT,
            ],
            check=False,
            env=_run_env(extra),
        ).returncode
        == 0
    )


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
    if platform.is_mac():
        if _docker_env() is None:
            logger.warning(
                "k3d present but Podman machine not ready; "
                "run `podman machine start` before creating a cluster."
            )
            return
        logger.info("k3d ready (via Podman). create_cluster() makes a 3-node cluster.")
        return
    logger.info("k3d ready. create_cluster() makes a 3-node cluster.")


__all__ = ["create_cluster", "delete_cluster", "run", "CLUSTER_NAME"]
