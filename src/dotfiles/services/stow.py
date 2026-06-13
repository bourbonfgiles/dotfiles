"""Symlink dotfiles with GNU stow, healing prior non-symlink conflicts."""

from __future__ import annotations

from datetime import datetime  # stdlib: timestamps for backup names
from pathlib import Path

from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("stow")


def _symlink_force(src: Path, dst: Path) -> None:
    """Create ``dst`` as a symlink to ``src``, replacing any existing link."""
    if dst.is_symlink() or dst.exists():  # 'or' short-circuits; also catches dead links
        dst.unlink()  # remove whatever is there first
    dst.symlink_to(src)  # then create the symlink


def _reconcile(settings: Settings) -> None:
    """Move real (non-symlink) ~/.config entries aside so stow can link them.

    Heals e.g. a leftover vanilla LazyVim starter at ``~/.config/nvim``.
    """
    for entry in settings.repo_config.iterdir():  # iterate the repo .config children
        target = settings.config_home / entry.name
        if target.exists() and not target.is_symlink():  # a real file/dir is in the way
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")  # format current time
            backup = target.with_name(f"{target.name}.pre-stow.{stamp}")  # sibling name
            logger.warning("Backing up %s -> %s", target, backup)
            target.rename(backup)  # move it aside
    stale = settings.config_home / "nvim.bak"  # leftover from the old lazyvim_setup
    if stale.is_symlink():
        stale.unlink()


def run(settings: Settings) -> None:
    """Stow ``.config`` and link ``.zshrc``/``.spacemacs`` + the eza theme."""
    logger.info("Creating symlinks with stow…")
    settings.config_home.mkdir(parents=True, exist_ok=True)
    _reconcile(settings)
    shell.run(  # stow links the repo's .config tree into ~/.config
        ["stow", "-t", str(settings.config_home), ".config"],
        cwd=str(settings.repo_root),  # run from the repo so '.config' resolves
    )
    _symlink_force(settings.repo_root / ".zshrc", settings.home / ".zshrc")
    _symlink_force(settings.repo_root / ".spacemacs", settings.home / ".spacemacs")
    eza_dir = settings.config_home / "eza"
    eza_dir.mkdir(parents=True, exist_ok=True)
    theme = settings.home / "repos/personal/eza-themes/themes/dracula.yml"
    _symlink_force(theme, eza_dir / "theme.yml")
    logger.info("Symlinks created.")
