"""Local Kubernetes: k3d on Linux, Apple `container k8s` on macOS.

Both launchers run k3s/kind nodes, so the resulting cluster and the standard
`kubectl`/`k9s`/`helm` workflow behave the same across targets. The bootstrap
step only verifies the launcher is installed; creating or destroying a cluster
is explicit via `create_cluster()` / `delete_cluster()`, never automatic.
"""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger
from ..utils.platform import OSKind

logger = get_logger("k8s")

# "Classic 3-node": one control plane + two workers on every target.
CLUSTER_NAME = "dev"
_WORKERS = 2


def _launcher() -> tuple[str, str] | None:
    """Return (command, human label) for the current OS, or None if missing."""
    kind = platform.os_kind()
    if kind is OSKind.MAC:
        return (
            ("container", "Apple container k8s")
            if shell.command_exists("container")
            else None
        )
    if platform.is_linux():
        return ("k3d", "k3d") if shell.command_exists("k3d") else None
    return None


def _create_argv(launcher: str, name: str, workers: int) -> list[str]:
    """Build the per-launcher create command for a 1 + ``workers`` cluster."""
    if launcher == "container":
        return ["container", "k8s", "create", "--name", name, "--workers", str(workers)]
    return [
        "k3d",
        "cluster",
        "create",
        name,
        "--servers",
        "1",
        "--agents",
        str(workers),
    ]


def _delete_argv(launcher: str, name: str) -> list[str]:
    if launcher == "container":
        return ["container", "k8s", "delete", "--name", name]
    return ["k3d", "cluster", "delete", name]


def create_cluster(name: str = CLUSTER_NAME, workers: int = _WORKERS) -> bool:
    """Create a 1-control-plane + ``workers`` cluster; return True on success."""
    launcher = _launcher()
    if launcher is None:
        logger.warning("No Kubernetes launcher available for this OS.")
        return False
    cmd, label = launcher
    logger.info("Creating %s cluster %r (1 + %d nodes)…", label, name, workers)
    return shell.run(_create_argv(cmd, name, workers), check=False).returncode == 0


def delete_cluster(name: str = CLUSTER_NAME) -> bool:
    """Delete the named cluster; return True on success."""
    launcher = _launcher()
    if launcher is None:
        return False
    cmd, _ = launcher
    return shell.run(_delete_argv(cmd, name), check=False).returncode == 0


def run(settings: Settings) -> None:
    """Verify the local Kubernetes launcher is installed (no cluster created)."""
    launcher = _launcher()
    if launcher is None:
        if platform.is_mac():
            logger.warning("Apple `container` not found; k8s launcher unavailable.")
        else:
            logger.warning("k3d not found; k8s launcher unavailable.")
        return
    _, label = launcher
    logger.info(
        "%s ready. Create a 3-node cluster with the k8s service's create_cluster().",
        label,
    )


__all__ = ["create_cluster", "delete_cluster", "run", "CLUSTER_NAME"]
