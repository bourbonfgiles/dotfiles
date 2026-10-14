"""Operating-system detection shared by the setup services (ports lib_os.zsh)."""

from __future__ import annotations

import platform as _platform  # 'import X as Y': alias avoids clashing with THIS module
from enum import Enum  # Enum: base class for a set of named constant members
from pathlib import Path  # Path: object-oriented filesystem paths

# Path objects (not plain strings) for the files we probe. Exported (public name)
# so system.py can share the same os-release path instead of redeclaring it.
OS_RELEASE_PATH = Path("/etc/os-release")
_OSTREE_MARKER = Path("/run/ostree-booted")


# 'class OSKind(str, Enum)': an Enum whose members are ALSO strings (the 'str'
# mixin), so OSKind.MAC == "mac" and it serialises/prints nicely.
class OSKind(str, Enum):
    """A coarse classification of the host operating system."""

    MAC = "mac"  # an enum member, referenced as OSKind.MAC
    BAZZITE = "bazzite"
    FEDORA_ATOMIC = "fedora-atomic"
    LINUX = "linux"
    UNKNOWN = "unknown"


def os_kind() -> OSKind:  # the return type is an OSKind member
    """Classify the running operating system."""
    system = _platform.system()  # function call: returns 'Linux'/'Darwin'/'Windows'
    if system == "Darwin":  # '==' tests equality
        return OSKind.MAC
    if system != "Linux":  # '!=' is 'not equal'
        return OSKind.UNKNOWN
    try:  # try/except guards code that might raise
        # Method chain: read the file's text, then .lower() returns a new string.
        release = OS_RELEASE_PATH.read_text(encoding="utf-8").lower()
    except OSError:  # catch filesystem errors (missing/unreadable file)
        release = ""  # fallback so the checks below still work
    if "bazzite" in release:  # 'in' tests substring membership
        return OSKind.BAZZITE
    if _OSTREE_MARKER.exists():  # Path.exists(): bool, is the file present?
        return OSKind.FEDORA_ATOMIC
    return OSKind.LINUX


def is_mac() -> bool:  # '-> bool' returns True/False
    """Return True on macOS."""
    return os_kind() is OSKind.MAC  # 'is' = identity check (safe for enum members)


def is_linux() -> bool:
    """Return True on any Linux (Bazzite and atomic Fedora included)."""
    # Derive from os_kind() so there is a single source of truth: every Linux
    # classification maps to one of these members; UNKNOWN/MAC do not.
    return os_kind() in (OSKind.LINUX, OSKind.BAZZITE, OSKind.FEDORA_ATOMIC)


def is_fedora_atomic() -> bool:
    """Return True on rpm-ostree systems (Bazzite included)."""
    # Bazzite is itself atomic, so it counts here too.
    return os_kind() in (OSKind.FEDORA_ATOMIC, OSKind.BAZZITE)
