"""Install Warp via its official RPM repo (rpm-ostree on atomic Fedora)."""

from __future__ import annotations

from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger
from ..utils.platform import OSKind

logger = get_logger("warp")

_REPO_FILE = "/etc/yum.repos.d/warpdotdev.repo"
_KEY_URL = "https://releases.warp.dev/linux/keys/warp.asc"
_BASE_URL = "https://releases.warp.dev/linux/rpm/stable"
# Implicit concatenation of adjacent string literals builds the .repo body.
_REPO_BODY = (
    "[warpdotdev]\n"
    "name=warpdotdev\n"
    f"baseurl={_BASE_URL}\n"
    "enabled=1\n"
    "gpgcheck=1\n"
    f"gpgkey={_KEY_URL}\n"
)


def _ensure_repo() -> None:
    if not Path(_REPO_FILE).exists():
        logger.info("Adding Warp's official RPM repo…")
        system.sudo_write(_REPO_FILE, _REPO_BODY)
    else:
        logger.info("Warp repo already present.")


def run(settings: Settings) -> None:
    """Install/migrate Warp from the official repo (no-op on the macOS cask)."""
    kind = platform.os_kind()
    if kind is OSKind.MAC:
        logger.info("macOS: Warp is installed via the Homebrew cask.")
        return
    if kind in (OSKind.BAZZITE, OSKind.FEDORA_ATOMIC):
        _ensure_repo()
        shell.run(["rpm-ostree", "refresh-md"], check=False)
        if system.rpm_installed("warp-terminal"):
            # Migrate a hand-installed local RPM to the repo-tracked package so
            # future updates flow from the repo instead of a one-off file.
            if system.rpm_ostree_local_package("warp-terminal"):
                logger.info("Migrating Warp from a local RPM to the repo package…")
                shell.run(
                    ["sudo", "rpm-ostree", "uninstall", "warp-terminal"], check=False
                )
                shell.run(
                    ["sudo", "rpm-ostree", "install", "warp-terminal"], check=False
                )
                logger.info("Warp migrated. Reboot to finish: systemctl reboot")
            else:
                logger.info("Warp already layered from the repo; nothing to do.")
            return
        logger.info("Layering Warp (rpm-ostree). A reboot is needed to use it.")
        shell.run(
            ["sudo", "rpm-ostree", "install", "--idempotent", "warp-terminal"],
            check=False,
        )
        return
    if shell.command_exists("dnf"):  # non-atomic Fedora fallback
        if not Path(_REPO_FILE).exists():
            shell.run(["sudo", "rpm", "--import", _KEY_URL], check=False)
            system.sudo_write(_REPO_FILE, _REPO_BODY)
        shell.run(["sudo", "dnf", "-y", "install", "warp-terminal"], check=False)
    else:
        logger.warning("No known Warp install path; see https://docs.warp.dev/")
