"""Install Flathub apps listed in the repo's ``flatpaks`` file (Linux only)."""

from __future__ import annotations

from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("flatpak")

_FLATHUB = "https://flathub.org/repo/flathub.flatpakrepo"


def read_ids(path: Path) -> list[str]:
    """Return the application ids in ``path`` (one per line, ``#`` comments)."""
    ids: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        app = raw.split("#", 1)[0].strip()  # drop an inline '# comment', then trim
        if app:  # skip blank lines
            ids.append(app)
    return ids


def install_all(ids: list[str]) -> None:
    """Add the user Flathub remote and install/skip each id."""
    shell.run(
        ["flatpak", "remote-add", "--if-not-exists", "--user", "flathub", _FLATHUB],
        check=False,
    )
    for app in ids:
        installed = shell.run(["flatpak", "info", app], check=False, capture=True)
        if installed.returncode == 0:  # 0 means it is already installed
            logger.info("already installed: %s", app)
            continue  # skip to the next id
        logger.info("installing: %s", app)
        shell.run(
            [
                "flatpak",
                "install",
                "--user",
                "--noninteractive",
                "--or-update",
                "flathub",
                app,
            ],
            check=False,
        )


def run(settings: Settings) -> None:
    """Install the Linux GUI flatpaks (no-op on macOS)."""
    if platform.is_mac():
        logger.info("macOS: GUI apps come from Brewfile casks; skipping Flatpaks.")
        return
    if not platform.is_linux() or not shell.command_exists("flatpak"):
        logger.warning("flatpak unavailable; skipping Flatpak setup.")
        return
    install_all(read_ids(settings.flatpaks_file))
    logger.info("Flatpak setup complete.")
