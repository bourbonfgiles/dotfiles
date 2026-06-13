"""Post-bootstrap sanity checks."""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("checks")

_CORE_TOOLS = (
    "git",
    "stow",
    "zsh",
    "nvim",
    "starship",
    "eza",
    "zoxide",
    "fzf",
    "rg",
    "fd",
    "bat",
)
_LINKED = ("nvim", "ghostty", "starship", "k9s")


def run(settings: Settings) -> None:
    """Report which core tools and stowed configs are present."""
    logger.info("Post-bootstrap checks…")
    missing = [tool for tool in _CORE_TOOLS if not shell.command_exists(tool)]
    for tool in _CORE_TOOLS:
        if shell.command_exists(tool):
            logger.info("ok: %s", tool)
        else:
            logger.warning("missing: %s", tool)
    for name in _LINKED:
        path = settings.config_home / name
        if path.exists():
            logger.info("ok: ~/.config/%s", name)
        else:
            logger.warning("missing: ~/.config/%s", name)
    if missing:
        logger.warning("Missing tools: %s", ", ".join(missing))
    else:
        logger.info("All core tools present.")
