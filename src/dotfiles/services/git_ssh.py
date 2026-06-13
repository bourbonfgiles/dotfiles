"""Configure Git identity, ensure an ed25519 SSH key, and clone repos."""

from __future__ import annotations

from pathlib import Path

from ..config.settings import Settings
from ..utils import shell
from ..utils.logging import get_logger

logger = get_logger("git_ssh")

# Tuple of (url, destination-relative-to-home) pairs to clone or update.
_REPOS = (
    ("git@github.com:bourbonfgiles/dotfiles.git", "repos/personal/dotfiles"),
    ("https://github.com/eza-community/eza-themes.git", "repos/personal/eza-themes"),
    ("https://github.com/syl20bnr/spacemacs.git", ".emacs.d"),
)


def _git_config(key: str) -> str:
    # Read a global git setting; check=False so an unset key just yields "".
    return shell.run(
        ["git", "config", "--global", key], check=False, capture=True
    ).stdout.strip()


def _configure_identity() -> str:
    """Prompt for Git identity only if unset; return the configured email."""
    email = _git_config("user.email")
    name = _git_config("user.name")
    if not email or not name:  # 'not x' is True for an empty string
        email = input(
            "Enter your GitHub email: "
        ).strip()  # input(): read one stdin line
        name = input("Enter your GitHub username: ").strip()
        shell.run(["git", "config", "--global", "user.email", email])
        shell.run(["git", "config", "--global", "user.name", name])
    else:
        logger.info(
            "Git identity already set for %s <%s>; skipping prompts.", name, email
        )
    shell.run(["git", "config", "--global", "init.defaultBranch", "main"])
    shell.run(["git", "config", "--global", "push.autosetupremote", "true"])
    return email


def _copy_to_clipboard(text: str) -> bool:
    """Best-effort copy of ``text`` to the system clipboard."""
    # Each candidate tool is itself a list (an argv); we try them in order.
    for tool in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"]):
        if shell.command_exists(tool[0]):  # tool[0] is the program name
            shell.run(tool, text_input=text, check=False)
            return True
    return False


def _ensure_ssh_key(email: str) -> None:
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(
        mode=0o700, exist_ok=True
    )  # 0o700 = octal perms; exist_ok avoids error
    key = ssh_dir / "id_ed25519"
    if key.exists():
        logger.info("SSH key already exists.")
        return
    shell.run(["ssh-keygen", "-t", "ed25519", "-C", email])
    pub = key.with_suffix(".pub").read_text(
        encoding="utf-8"
    )  # with_suffix swaps extension
    if _copy_to_clipboard(pub):
        logger.info("SSH public key copied to clipboard.")
    else:
        logger.info("Add this SSH public key to GitHub:\n%s", pub)
    input("Press Enter after adding the SSH key to GitHub… ")  # pause for the user


def _clone_or_update(url: str, dest: Path) -> None:
    if (dest / ".git").is_dir():  # already a clone -> update it
        logger.info("Updating %s…", dest.name)  # Path.name = final path component
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
    for url, rel in _REPOS:  # tuple unpacking: url, rel come from each pair
        _clone_or_update(url, settings.home / rel)
