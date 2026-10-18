"""kubectl plugins via krew (Homebrew installs krew itself)."""

from __future__ import annotations

from ..config.data import KREW_PLUGINS
from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("krew")


def run(settings: Settings) -> None:
    """Install any missing krew plugins."""
    if not shell.command_exists("kubectl-krew"):
        logger.warning("krew not found; install it with brew bundle first.")
        return
    listed = shell.run(["kubectl", "krew", "list"], capture=True, check=False)
    installed = set(listed.stdout.split())
    missing = [p for p in KREW_PLUGINS if p not in installed]
    if not missing:
        logger.info("krew plugins already installed.")
        return
    shell.run(["kubectl", "krew", "update"], check=False)
    shell.run(["kubectl", "krew", "install", *missing], check=False)
