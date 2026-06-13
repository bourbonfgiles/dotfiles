"""Run the setup steps in order: critical steps abort, the rest warn on error."""

from __future__ import annotations

from collections.abc import Callable, Sequence  # abstract types used only in hints
from dataclasses import dataclass, field  # field(): set per-field dataclass options

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


# frozen=True -> immutable; also auto-writes __init__/__repr__/__eq__ for us
@dataclass(frozen=True)
class Step:
    """A single named bootstrap step."""

    name: str  # identifier used by --only and in the logs
    # Callable[[Settings], None] is a TYPE describing a function value: one that
    # takes a single Settings argument and returns None. Each service's `run`
    # function fits this shape, so we can store it here and call it later.
    run: Callable[[Settings], None]
    # field(default=False) gives this field a default value, so most Steps omit it;
    # only the must-not-fail steps pass critical=True in STEPS below.
    critical: bool = field(default=False)


# Order matters: Homebrew provides git/stow before clone/stow run; Neovim's
# plugin sync needs nvim from brew bundle, etc.
# tuple[Step, ...]: a tuple of any length whose items are all Step. The '...' means
# "variadic length" (not "fill this in"); a tuple (vs list) keeps the order fixed.
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
    failures = 0  # counts non-critical steps that errored but didn't abort the run
    for step in STEPS:  # iterate in declared order (STEPS is ordered)
        # --only filter: when given, skip any step whose name isn't in the list.
        if only and step.name not in only:
            continue  # 'continue' jumps straight to the next loop iteration
        logger.info("== %s ==", step.name)
        try:  # guard each step so one failure can't crash the whole bootstrap
            step.run(settings)  # call this service's run() function
        except DotfilesError as exc:  # only catch OUR errors; real bugs still surface
            failures += 1
            if step.critical:  # critical steps (git_ssh, stow) must not continue
                logger.error("%s failed (critical): %s", step.name, exc)
                return 1  # bail out early with a failure exit code
            # non-critical step: warn and carry on to the next step
            logger.warning("%s had issues: %s", step.name, exc)
    logger.info("Bootstrap complete.")
    # Ternary expression: 1 if any non-critical step failed, else 0 (the exit code).
    return 1 if failures else 0
