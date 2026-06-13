"""Install Nerd Fonts on Linux (macOS gets them from Brewfile casks)."""

from __future__ import annotations

import tarfile
import tempfile
import urllib.request
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("fonts")

_FONTS = ("JetBrainsMono",)
_FONT_DIR = Path.home() / ".local/share/fonts"
_RELEASE = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download"


def _installed(name: str) -> bool:
    listing = shell.run(["fc-list"], check=False, capture=True).stdout.lower()
    return f"{name} nerd font".lower() in listing


def _install(name: str) -> None:
    url = f"{_RELEASE}/{name}.tar.xz"
    logger.info("Installing %s Nerd Font…", name)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / f"{name}.tar.xz"
        urllib.request.urlretrieve(url, archive)  # noqa: S310 (trusted host)
        dest = _FONT_DIR / f"{name}NerdFont"
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive, "r:xz") as tar:
            tar.extractall(dest, filter="data")


def run(settings: Settings) -> None:
    """Ensure the referenced Nerd Fonts exist in ~/.local/share/fonts."""
    if platform.is_mac():
        logger.info("macOS: Nerd Fonts come from Brewfile casks; skipping.")
        return
    _FONT_DIR.mkdir(parents=True, exist_ok=True)
    for name in _FONTS:
        if _installed(name):
            logger.info("%s Nerd Font already installed.", name)
            continue
        try:
            _install(name)
        except (OSError, tarfile.TarError) as exc:
            logger.warning("Failed to install %s Nerd Font: %s", name, exc)
    if shell.command_exists("fc-cache"):
        shell.run(["fc-cache", "-f"], check=False)
    logger.info("Fonts setup complete.")
