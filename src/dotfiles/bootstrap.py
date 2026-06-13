"""Run the setup steps in order: critical steps abort, the rest warn on error."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from .config.settings import Settings
from .services import (
    albert,
    checks,
    dns,
    flatpak,
    fonts,
    gaming,
    ghostty,
    git_ssh,
    gnome,
    homebrew,
    neovim,
    shell_default,
    stow,
    warp,
)
from .utils.exceptions import DotfilesError
from .utils.logging import get_logger

logger = get_logger("bootstrap")


@dataclass(frozen=True)
class Step:
    """A single named bootstrap step."""

    name: str
    run: Callable[[Settings], None]
    critical: bool = field(default=False)


# Order matters: Homebrew provides git/stow before clone/stow run; Neovim's
# plugin sync needs nvim from brew bundle, etc.
STEPS: tuple[Step, ...] = (
    Step("homebrew", homebrew.run),
    Step("git_ssh", git_ssh.run, critical=True),
    Step("stow", stow.run, critical=True),
    Step("flatpak", flatpak.run),
    Step("ghostty", ghostty.run),
    Step("warp", warp.run),
    Step("albert", albert.run),
    Step("gaming", gaming.run),
    Step("shell_default", shell_default.run),
    Step("dns", dns.run),
    Step("gnome", gnome.run),
    Step("fonts", fonts.run),
    Step("neovim", neovim.run),
    Step("checks", checks.run),
)


def step_names() -> list[str]:
    """Return the ordered step names."""
    return [step.name for step in STEPS]


def run(settings: Settings, only: Sequence[str] | None = None) -> int:
    """Execute the steps and return a process exit code.

    Args:
        settings: Resolved filesystem settings.
        only: When given, run only these step names (in declared order).

    Returns:
        ``0`` on success, ``1`` if a critical step failed.
    """
    failures = 0
    for step in STEPS:
        if only and step.name not in only:
            continue
        logger.info("== %s ==", step.name)
        try:
            step.run(settings)
        except DotfilesError as exc:
            failures += 1
            if step.critical:
                logger.error("%s failed (critical): %s", step.name, exc)
                return 1
            logger.warning("%s had issues: %s", step.name, exc)
    logger.info("Bootstrap complete.")
    return 1 if failures else 0
