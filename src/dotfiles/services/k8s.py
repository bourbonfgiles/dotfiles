"""k3d's runtime: rootful Podman, which eBPF CNIs need.

On Linux the os_build image provides the socket, logging and kube.internal DNS,
so this only checks it. On macOS it makes the Podman machine rootful and big
enough. Creating the cluster is `kube-create` in .zshrc.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("k8s")

_PODMAN_MACHINE = "podman-machine-default"
# applehv needs no extra binary (libkrun would require krunkit). Multi-node k3d
# only works on a rootful machine; rootless leaves agents stuck in "Created".
_PODMAN_PROVIDER = "applehv"
# Holds the control plane, Cilium, and a JVM game server at once; 2 GB OOMs.
_MACHINE_MEMORY_MB = 8192
_LINUX_SOCKET = "/run/podman/podman.sock"


def _machine_field(field: str) -> object | None:
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


def _machine_ready() -> bool:
    resources = _machine_field("Resources")
    memory = resources.get("Memory") if isinstance(resources, dict) else None
    return (
        _machine_field("Rootful") is True
        and isinstance(memory, int)
        and memory >= _MACHINE_MEMORY_MB
    )


def _ensure_podman_machine() -> bool:
    """Create and start the machine, then make it rootful with enough memory."""
    if _machine_field("Name") is None:
        logger.info(
            "Creating Podman machine %r (%s)…", _PODMAN_MACHINE, _PODMAN_PROVIDER
        )
        shell.run(
            ["podman", "machine", "init", "--provider", _PODMAN_PROVIDER], check=False
        )
    if not _machine_running():
        logger.info("Starting Podman machine %r…", _PODMAN_MACHINE)
        if shell.run(
            ["podman", "machine", "start", _PODMAN_MACHINE], check=False
        ).returncode:
            return False
    if _machine_ready():
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
    shell.run(["podman", "machine", "start", _PODMAN_MACHINE], check=False)
    return _machine_ready()


def _linux_socket_ready() -> bool:
    try:
        return Path(_LINUX_SOCKET).is_socket() and os.access(
            _LINUX_SOCKET, os.R_OK | os.W_OK
        )
    except OSError:
        return False


def run(settings: Settings) -> None:
    """Check (Linux) or prepare (macOS) the runtime; never creates a cluster."""
    if not shell.command_exists("k3d"):
        logger.warning("k3d not found; local Kubernetes unavailable.")
        return
    if platform.is_mac():
        if not shell.command_exists("podman") or not _ensure_podman_machine():
            logger.warning("Podman machine not ready; try `podman machine start`.")
            return
    elif not _linux_socket_ready():
        logger.warning(
            "%s unreachable: it comes from the os_build image. Check "
            "`systemctl status podman.socket` and that you are in wheel.",
            _LINUX_SOCKET,
        )
        return
    logger.info("k3d runtime ready; `kube-create` makes the dev cluster.")


__all__ = ["run"]
