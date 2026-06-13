"""Install Ghostty: COPR via rpm-ostree on atomic Fedora; cask note on macOS."""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger
from ..utils.platform import OSKind  # import the enum to compare against its members

logger = get_logger("ghostty")

_REPO_FILE = "/etc/yum.repos.d/_copr:copr.fedorainfracloud.org:scottames:ghostty.repo"


def run(settings: Settings) -> None:
    """Ensure Ghostty is installed for the current platform."""
    if shell.command_exists("ghostty"):
        logger.info("Ghostty already installed.")
        return
    kind = platform.os_kind()  # one of the OSKind members
    if kind is OSKind.MAC:
        logger.info("macOS: Ghostty is installed via the Homebrew cask.")
        return
    if kind in (OSKind.BAZZITE, OSKind.FEDORA_ATOMIC):  # 'in' tests tuple membership
        if system.rpm_installed("ghostty"):
            logger.info("Ghostty rpm already layered (reboot pending?).")
            return
        version = system.fedora_version_id()
        url = (  # adjacent string literals are concatenated automatically
            "https://copr.fedorainfracloud.org/coprs/scottames/ghostty/repo/"
            f"fedora-{version}/scottames-ghostty-fedora-{version}.repo"
        )
        logger.info("Adding scottames/ghostty COPR for Fedora %s…", version)
        system.sudo_write(
            _REPO_FILE, shell.capture(["curl", "-fsSL", url])
        )  # download then write
        shell.run(["rpm-ostree", "refresh-md"], check=False)
        result = shell.run(
            ["sudo", "rpm-ostree", "install", "--idempotent", "ghostty"], check=False
        )
        if result.returncode == 0:
            logger.info("Ghostty layered. Reboot to finish: systemctl reboot")
        else:
            logger.warning("rpm-ostree install ghostty failed.")
        return
    if shell.command_exists("dnf"):  # non-atomic Fedora fallback
        shell.run(
            ["sudo", "dnf", "-y", "copr", "enable", "scottames/ghostty"], check=False
        )
        shell.run(["sudo", "dnf", "-y", "install", "ghostty"], check=False)
    else:
        logger.warning(
            "No known Ghostty install path; see https://ghostty.org/docs/install."
        )
