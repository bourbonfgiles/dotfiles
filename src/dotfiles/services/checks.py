"""Post-bootstrap sanity checks."""

from __future__ import annotations

from ..config.data import CORE_TOOLS, LINKED_CONFIGS
from ..config.runtime import current as _options
from ..config.settings import Settings
from ..utils import shell
from ..utils.exceptions import StepError
from ..utils.logging import get_logger

logger = get_logger("checks")


def run(settings: Settings) -> None:
    """Report which core tools and applied configs are present."""
    logger.info("Post-bootstrap checks…")
    missing = [tool for tool in CORE_TOOLS if not shell.command_exists(tool)]
    for tool in CORE_TOOLS:
        if shell.command_exists(tool):
            logger.info("ok: %s", tool)
        else:
            logger.warning("missing: %s", tool)
    for name in LINKED_CONFIGS:
        path = settings.config_home / name
        if path.exists():
            logger.info("ok: ~/.config/%s", name)
        else:
            logger.warning("missing: ~/.config/%s", name)
    if missing:
        logger.warning("Missing tools: %s", ", ".join(missing))
        if _options().strict:
            # --strict turns checks into a gate: a missing core tool fails the
            # step (non-critical, so the run still finishes with exit 1).
            raise StepError(f"missing core tools: {', '.join(missing)}")
    else:
        logger.info("All core tools present.")
