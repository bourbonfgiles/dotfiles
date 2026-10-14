"""Operating-system detection shared by the setup services (ports lib_os.zsh)."""

from __future__ import annotations

import platform as _platform
from enum import Enum
from pathlib import Path

# Public so system.py can share it instead of redeclaring the path.
OS_RELEASE_PATH = Path("/etc/os-release")
_OSTREE_MARKER = Path("/run/ostree-booted")


class OSKind(str, Enum):
    """A coarse classification of the host operating system."""

    MAC = "mac"
    BAZZITE = "bazzite"
    FEDORA_ATOMIC = "fedora-atomic"
    LINUX = "linux"
    UNKNOWN = "unknown"


def os_kind() -> OSKind:
    """Classify the running operating system."""
    system = _platform.system()
    if system == "Darwin":
        return OSKind.MAC
    if system != "Linux":
        return OSKind.UNKNOWN
    try:
        release = OS_RELEASE_PATH.read_text(encoding="utf-8").lower()
    except OSError:
        release = ""
    if "bazzite" in release:
        return OSKind.BAZZITE
    if _OSTREE_MARKER.exists():
        return OSKind.FEDORA_ATOMIC
    return OSKind.LINUX


def is_mac() -> bool:
    """Return True on macOS."""
    return os_kind() is OSKind.MAC


def is_linux() -> bool:
    """Return True on any Linux (Bazzite and atomic Fedora included)."""
    # Derived from os_kind() so there is a single source of truth.
    return os_kind() in (OSKind.LINUX, OSKind.BAZZITE, OSKind.FEDORA_ATOMIC)


def is_fedora_atomic() -> bool:
    """Return True on rpm-ostree systems (Bazzite is atomic, so counts too)."""
    return os_kind() in (OSKind.FEDORA_ATOMIC, OSKind.BAZZITE)
