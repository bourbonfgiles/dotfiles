"""Configure Git identity, ensure an ed25519 SSH key, and clone repos."""

from __future__ import annotations

from pathlib import Path

from ..config.data import REPOS
from ..config.runtime import current as _options
from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("git_ssh")


def _git_config(key: str) -> str:
    return shell.run(
        ["git", "config", "--global", key], check=False, capture=True
    ).stdout.strip()


def _configure_identity() -> str:
    """Return a Git email for SSH key comments; identity lives in chezmoi.

    ``~/.gitconfig`` is applied by the chezmoi step from ``dot_gitconfig.tmpl``
    + ``home/.chezmoidata.toml``. This only prompts when nothing is set yet so
    ssh-keygen still has an email comment on a brand-new machine.
    """
    email = _git_config("user.email")
    name = _git_config("user.name")
    if email and name:
        logger.info(
            "Git identity already set for %s <%s>; chezmoi manages ~/.gitconfig.",
            name,
            email,
        )
        return email
    if _options().assume_yes:
        # chezmoi apply seeds the real identity later; an empty email here only
        # affects the ssh-keygen comment on a brand-new machine.
        logger.warning(
            "Non-interactive (--yes): git identity unset; "
            "chezmoi will apply it from .chezmoidata.toml."
        )
        return email
    email = input("Enter your GitHub email: ").strip()
    name = input("Enter your GitHub username: ").strip()
    # Seed config so SSH works before chezmoi apply overwrites it.
    shell.run(["git", "config", "--global", "user.email", email])
    shell.run(["git", "config", "--global", "user.name", name])
    logger.info(
        "Seeded git identity; update home/.chezmoidata.toml if this should persist."
    )
    return email


def _copy_to_clipboard(text: str) -> bool:
    """Best-effort copy of ``text`` to the system clipboard."""
    for tool in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"]):
        if shell.command_exists(tool[0]):
            shell.run(tool, text_input=text, check=False)
            return True
    return False


def _ensure_ssh_key(email: str) -> None:
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    key = ssh_dir / "id_ed25519"
    if key.exists():
        logger.info("SSH key already exists.")
        return
    shell.run(["ssh-keygen", "-t", "ed25519", "-C", email])
    pub = key.with_suffix(".pub").read_text(encoding="utf-8")
    if _copy_to_clipboard(pub):
        logger.info("SSH public key copied to clipboard.")
    else:
        logger.info("Add this SSH public key to GitHub:\n%s", pub)
    if _options().assume_yes:
        logger.warning(
            "Non-interactive (--yes): not pausing for key upload; "
            "clones over SSH may fail until the key is added to GitHub."
        )
        return
    input("Press Enter after adding the SSH key to GitHub… ")


def _clone_or_update(url: str, dest: Path) -> None:
    if (dest / ".git").is_dir():
        logger.info("Updating %s…", dest.name)
        shell.run(["git", "-C", str(dest), "pull", "--ff-only"], check=False)
    else:
        logger.info("Cloning %s…", dest.name)
        shell.run(["git", "clone", url, str(dest)])


def run(settings: Settings) -> None:
    """Configure Git/SSH and clone the dotfiles + companion repos."""
    logger.info("Configuring Git & SSH…")
    email = _configure_identity()
    _ensure_ssh_key(email)
    (settings.home / "repos" / "personal").mkdir(parents=True, exist_ok=True)
    for url, rel in REPOS:
        _clone_or_update(url, settings.home / rel)
