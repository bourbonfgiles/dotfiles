"""BPF tracing tools (bpftrace, BCC, bpftool, perf) for the BPF Performance Tools book; Linux only."""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger
from ..utils.platform import OSKind

logger = get_logger("bpf")

# Fedora's own repos; BCC's tools install under /usr/share/bcc/tools.
_PACKAGES = ("bpftrace", "bcc-tools", "bpftool", "perf")


def run(settings: Settings) -> None:
    """Layer the BPF tracing tools (no-op on macOS, which has no BPF)."""
    kind = platform.os_kind()
    if kind is OSKind.MAC:
        logger.info("macOS: BPF tracing is Linux-only; run the tools in a Linux VM.")
        return
    if kind in (OSKind.BAZZITE, OSKind.FEDORA_ATOMIC):
        for package in _PACKAGES:
            system.rpmostree_install_or_migrate(package, label=package)
        return
    if shell.command_exists("dnf"):
        shell.run(["sudo", "dnf", "-y", "install", *_PACKAGES], check=False)
    else:
        logger.warning("No known install path for %s.", ", ".join(_PACKAGES))
