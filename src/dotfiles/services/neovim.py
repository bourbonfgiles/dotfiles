"""Sync the stowed LazyVim config; never clobber it; link Neovide's sandbox."""

from __future__ import annotations

import shutil

from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("neovim")

_NEOVIDE = "dev.neovide.neovide"


def _link_neovide(settings: Settings) -> None:
    """Point the Neovide flatpak sandbox config at the host nvim config."""
    if not shell.command_exists("flatpak"):
        return
    if (
        shell.run(["flatpak", "info", _NEOVIDE], check=False, capture=True).returncode
        != 0
    ):
        return
    sandbox = settings.home / ".var/app" / _NEOVIDE / "config"
    sandbox.mkdir(parents=True, exist_ok=True)
    link = sandbox / "nvim"
    if link.is_symlink():
        link.unlink()
    elif link.is_dir():
        shutil.rmtree(link)
    elif link.exists():
        link.unlink()
    link.symlink_to(settings.config_home / "nvim")
    logger.info("Neovide: linked sandbox config -> ~/.config/nvim")


def run(settings: Settings) -> None:
    """Verify the stowed nvim config and run a headless Lazy sync."""
    nvim_cfg = settings.config_home / "nvim"
    repo_nvim = settings.repo_config / "nvim"
    if not nvim_cfg.exists():
        logger.warning("%s missing; run stow first.", nvim_cfg)
        return
    if nvim_cfg.resolve() != repo_nvim.resolve():
        logger.warning(
            "%s does not resolve to the repo config (%s); leftover starter?",
            nvim_cfg,
            repo_nvim,
        )
    elif shell.command_exists("nvim"):
        logger.info("Syncing Lazy plugins (headless)…")
        shell.run(["nvim", "--headless", "+Lazy! sync", "+qa"], check=False)
    _link_neovide(settings)


__all__ = ["run"]
