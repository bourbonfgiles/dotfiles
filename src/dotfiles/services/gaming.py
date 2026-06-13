"""Gaming apps: native on Bazzite; Flatpaks on Silverblue (+ rebase note)."""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger
from ..utils.platform import OSKind
from . import flatpak

logger = get_logger("gaming")

_REBASE_NOTE = (
    "Installed the portable gaming Flatpaks. Bazzite's deeper gaming features "
    "(custom kernel/HDR, gamescope-session, mesa-freeworld, controller drivers) "
    "are baked into the Bazzite image. To get them all, rebase to Bazzite:\n"
    "  rpm-ostree rebase "
    "ostree-unverified-registry:ghcr.io/ublue-os/bazzite-gnome:stable\n"
    "(then reboot). Optional and intentionally NOT run automatically."
)


def run(settings: Settings) -> None:
    """Install gaming Flatpaks on Silverblue; no-op on Bazzite/macOS."""
    kind = platform.os_kind()
    if kind is OSKind.MAC:
        logger.info("macOS: gaming setup not applicable; skipping.")
        return
    if kind is OSKind.BAZZITE:
        logger.info("Bazzite ships the gaming stack natively; nothing to do.")
        return
    if not shell.command_exists("flatpak"):
        logger.warning("flatpak not found; skipping gaming setup.")
        return
    flatpak.install_all(flatpak.read_ids(settings.gaming_flatpaks_file))
    if kind is OSKind.FEDORA_ATOMIC:
        logger.info("%s", _REBASE_NOTE)
    logger.info("Gaming setup complete.")
