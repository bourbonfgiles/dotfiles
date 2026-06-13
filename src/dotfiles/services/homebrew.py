"""Homebrew: ensure it is on PATH, install git+stow, trust taps, brew bundle."""

from __future__ import annotations

import os  # stdlib: process environment (we edit os.environ['PATH'])
from pathlib import Path

from ..config.settings import Settings
from ..utils import (
    shell,  # import the module, then call shell.run(), shell.command_exists()
)
from ..utils.exceptions import StepError
from ..utils.logging import get_logger

logger = get_logger("homebrew")

# Tuple literal (an immutable list) of candidate Homebrew prefixes per platform.
_PREFIXES = (
    "/opt/homebrew",  # Apple Silicon macOS
    "/usr/local",  # Intel macOS
    "/home/linuxbrew/.linuxbrew",  # Linux (default)
    str(Path.home() / ".linuxbrew"),  # Linux per-user; str() -> tuple holds strings
)


def ensure_on_path() -> None:
    """Prepend a known Homebrew bin dir to PATH when ``brew`` is missing."""
    if shell.command_exists("brew"):  # already callable? then nothing to do
        return
    for prefix in _PREFIXES:  # try each candidate location in turn
        bindir = Path(prefix) / "bin"
        if (bindir / "brew").is_file():  # a brew binary lives here
            # f-string builds a new PATH with brew's dirs ahead of the old value.
            os.environ["PATH"] = f"{bindir}:{prefix}/sbin:{os.environ.get('PATH', '')}"
            os.environ.setdefault("HOMEBREW_PREFIX", prefix)  # set only if not present
            return


def _taps(brewfile: Path) -> list[str]:
    """Extract ``tap "x"`` names declared in the Brewfile."""
    taps: list[str] = []  # annotated empty list we append to
    for raw in brewfile.read_text(encoding="utf-8").splitlines():
        line = raw.strip()  # remove surrounding whitespace
        if line.startswith("tap ") and '"' in line:  # a tap line with a quoted name
            taps.append(line.split('"')[1])  # split on '"'; index [1] is the name
    return taps


def run(settings: Settings) -> None:
    """Install core tools and run ``brew bundle``."""
    ensure_on_path()
    if not shell.command_exists("brew"):  # still missing -> this step can't proceed
        raise StepError("Homebrew not found on PATH")
    shell.run(
        ["brew", "update"], check=False
    )  # check=False: continue even on a warning
    shell.run(["brew", "install", "git", "stow"], check=False)  # tools later steps need
    # Homebrew 6 refuses third-party taps until trusted; trust each declared tap.
    for tap in _taps(settings.brewfile):
        shell.run(["brew", "trust", tap], check=False)
    logger.info("Running brew bundle…")
    shell.run(["brew", "bundle", "--file", str(settings.brewfile)], check=False)
    logger.info("Homebrew bundle complete.")
