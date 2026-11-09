"""Install Albert via OBS repo (rpm-ostree); podman-docker compat."""

from __future__ import annotations

from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger
from ..utils.platform import OSKind

logger = get_logger("albert")

_OBS_BASE = "https://download.opensuse.org/repositories/home:/manuelschneid3r"
_REPO_FILE = "/etc/yum.repos.d/home:manuelschneid3r.repo"
# $releasever is resolved from the image being deployed, so the repo follows
# Fedora upgrades. Never Rawhide: its builds need a newer Qt than the release has.
_BASE = f"{_OBS_BASE}/Fedora_$releasever/"


def _repo_body(base: str) -> str:
    return (
        "[home_manuelschneid3r]\n"
        "name=home_manuelschneid3r\n"
        f"baseurl={base}\n"
        "enabled=1\n"
        "gpgcheck=1\n"
        f"gpgkey={base}repodata/repomd.xml.key\n"
    )


def ensure_podman_docker() -> None:
    """Provide a ``docker`` shim via podman so Albert's docker plugin works."""
    if platform.is_mac() or shell.command_exists("docker"):
        return
    if not shell.command_exists("podman"):
        return
    if platform.is_fedora_atomic():
        logger.info("Adding podman-docker (docker -> podman) via rpm-ostree…")
        shell.run(
            ["sudo", "rpm-ostree", "install", "--idempotent", "podman-docker"],
            check=False,
        )
    elif shell.command_exists("dnf"):
        shell.run(["sudo", "dnf", "-y", "install", "podman-docker"], check=False)


def run(settings: Settings) -> None:
    """Install Albert and its docker compat (config via chezmoi → ~/.config/albert)."""
    if platform.is_mac():
        logger.info("macOS: Albert is Linux-only (use Raycast/Alfred); skipping.")
        return
    ensure_podman_docker()
    kind = platform.os_kind()
    if kind in (OSKind.BAZZITE, OSKind.FEDORA_ATOMIC):
        system.ensure_repo_file(_REPO_FILE, _repo_body(_BASE), label="Albert")
        system.rpmostree_install_or_migrate("albert", label="Albert")
        return
    if shell.command_exists("dnf"):
        if not Path(_REPO_FILE).exists():
            system.sudo_write(_REPO_FILE, _repo_body(_BASE))
        shell.run(["sudo", "dnf", "-y", "install", "albert"], check=False)
    else:
        logger.warning(
            "No known Albert install path; see https://albertlauncher.github.io/"
        )
