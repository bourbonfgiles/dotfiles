"""Apply home-directory dotfiles with chezmoi."""

from __future__ import annotations

from ..config.settings import Settings
from ..utils import shell
from ..utils.exceptions import StepError
from ..utils.logging import get_logger

logger = get_logger("chezmoi")


def run(settings: Settings) -> None:
    """Run ``chezmoi apply`` against this repo's source tree.

    The repo root contains ``.chezmoiroot`` pointing at ``home/``, which holds
    the chezmoi source state (``dot_config``, ``dot_zshrc``, templates, etc.).
    Conflict backups and the eza theme symlink are handled by chezmoi itself.
    """
    if not shell.command_exists("chezmoi"):
        raise StepError("chezmoi not found on PATH (install via Homebrew first)")

    source = settings.repo_root
    if not (source / ".chezmoiroot").is_file() and not (source / "home").is_dir():
        raise StepError(f"chezmoi source not found under {source}")

    logger.info("Applying dotfiles with chezmoi (source=%s)…", source)
    # --force replaces existing plain files/dirs the way our old stow reconcile did.
    shell.run(
        [
            "chezmoi",
            "apply",
            "--source",
            str(source),
            "--force",
        ]
    )
    logger.info("chezmoi apply complete.")
