"""Install Albert via OBS repo (rpm-ostree); podman-docker compat; seed config."""

from __future__ import annotations

import shutil

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger
from ..utils.platform import OSKind

logger = get_logger("albert")

_OBS_BASE = "https://download.opensuse.org/repositories/home:/manuelschneid3r"
_REPO_FILE = "/etc/yum.repos.d/home:manuelschneid3r.repo"


def _obs_target() -> str:
    """Map the running Fedora to an OBS build target (Rawhide for 44+)."""
    try:
        version = int(system.fedora_version_id())
    except ValueError:
        version = 40
    return "Fedora_Rawhide" if version >= 44 else f"Fedora_{version}"


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


def seed_config(settings: Settings) -> None:
    """Seed ~/.config/albert/config from the repo template on fresh machines."""
    if platform.is_mac():
        return
    dest = settings.config_home / "albert" / "config"
    if settings.albert_template.is_file() and not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(settings.albert_template, dest)
        logger.info("Seeded Albert config (enabled plugins) from repo template.")


def run(settings: Settings) -> None:
    """Install Albert and its docker compat + seed plugin config."""
    if platform.is_mac():
        logger.info("macOS: Albert is Linux-only (use Raycast/Alfred); skipping.")
        return
    seed_config(settings)
    ensure_podman_docker()
    kind = platform.os_kind()
    target = _obs_target()
    base = f"{_OBS_BASE}/{target}/"
    if kind in (OSKind.BAZZITE, OSKind.FEDORA_ATOMIC):
        from pathlib import Path

        if not Path(_REPO_FILE).exists():
            logger.info("Adding Albert's OBS repo (%s)…", target)
            system.sudo_write(_REPO_FILE, _repo_body(base))
        shell.run(["rpm-ostree", "refresh-md"], check=False)
        if system.rpm_installed("albert"):
            if system.rpm_ostree_local_package("albert"):
                logger.info("Migrating Albert from a local RPM to the repo package…")
                shell.run(["sudo", "rpm-ostree", "uninstall", "albert"], check=False)
                shell.run(["sudo", "rpm-ostree", "install", "albert"], check=False)
            else:
                logger.info("Albert already layered from the repo; nothing to do.")
            return
        logger.info("Layering Albert (rpm-ostree). A reboot is needed to use it.")
        result = shell.run(
            ["sudo", "rpm-ostree", "install", "--idempotent", "albert"], check=False
        )
        if result.returncode != 0:
            logger.warning(
                "rpm-ostree install albert failed — OBS may lack %s.", target
            )
        return
    if shell.command_exists("dnf"):
        from pathlib import Path

        if not Path(_REPO_FILE).exists():
            system.sudo_write(_REPO_FILE, _repo_body(base))
        shell.run(["sudo", "dnf", "-y", "install", "albert"], check=False)
    else:
        logger.warning(
            "No known Albert install path; see https://albertlauncher.github.io/"
        )
