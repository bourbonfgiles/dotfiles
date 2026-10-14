"""Homebrew: ensure it is on PATH, install git+chezmoi, trust taps, brew bundle."""

from __future__ import annotations

import os
from pathlib import Path

from ..config.settings import Settings
from ..utils import shell
from ..utils.exceptions import StepError
from ..utils.logging import get_logger

logger = get_logger("homebrew")

# Candidate Homebrew prefixes, in priority order per platform.
_PREFIXES = (
    "/opt/homebrew",  # Apple Silicon macOS
    "/usr/local",  # Intel macOS
    "/home/linuxbrew/.linuxbrew",  # Linux (default)
    str(Path.home() / ".linuxbrew"),  # Linux per-user
)


def ensure_on_path() -> None:
    """Prepend a known Homebrew bin dir to PATH when ``brew`` is missing."""
    if shell.command_exists("brew"):
        return
    for prefix in _PREFIXES:
        bindir = Path(prefix) / "bin"
        if (bindir / "brew").is_file():
            os.environ["PATH"] = f"{bindir}:{prefix}/sbin:{os.environ.get('PATH', '')}"
            os.environ.setdefault("HOMEBREW_PREFIX", prefix)
            return


def _taps(brewfile: Path) -> list[str]:
    """Extract ``tap "x"`` names declared in the Brewfile."""
    taps: list[str] = []
    for raw in brewfile.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("tap ") and '"' in line:
            taps.append(line.split('"')[1])
    return taps


def run(settings: Settings) -> None:
    """Install core tools and run ``brew bundle``."""
    ensure_on_path()
    if not shell.command_exists("brew"):
        raise StepError("Homebrew not found on PATH")
    shell.run(["brew", "update"], check=False)
    shell.run(["brew", "install", "git", "chezmoi"], check=False)
    # Homebrew refuses third-party taps until trusted.
    for tap in _taps(settings.brewfile):
        shell.run(["brew", "trust", tap], check=False)
    logger.info("Running brew bundle…")
    # A failed bundle is a real (non-critical) failure, not a silent exit 0;
    # the calls above stay best-effort (advisory or recoverable).
    result = shell.run(
        ["brew", "bundle", "--file", str(settings.brewfile)], check=False
    )
    if result.returncode != 0:
        raise StepError(
            f"brew bundle failed (exit {result.returncode}); some packages "
            "may not be installed"
        )
    logger.info("Homebrew bundle complete.")
