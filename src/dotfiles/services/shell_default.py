"""Make Homebrew zsh the default login shell on Linux (chsh, usermod fallback)."""

from __future__ import annotations

import getpass
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("shell_default")


def _login_shell(user: str) -> str:
    entry = shell.run(
        ["getent", "passwd", user], check=False, capture=True
    ).stdout.strip()
    parts = entry.split(":")
    return parts[6] if len(parts) >= 7 else ""


def run(settings: Settings) -> None:
    """Register brew zsh in /etc/shells and set it as the login shell."""
    if platform.is_mac():
        logger.info("macOS already uses zsh as the login shell; nothing to do.")
        return
    zsh = shell.which("zsh")
    if not zsh:
        logger.warning("zsh not found on PATH; skipping default-shell change.")
        return
    shells_file = Path("/etc/shells")
    existing = shells_file.read_text(encoding="utf-8") if shells_file.exists() else ""
    if zsh not in existing.split():
        logger.info("Registering %s in /etc/shells…", zsh)
        shell.run(
            ["sudo", "tee", "-a", str(shells_file)], text_input=f"{zsh}\n", capture=True
        )
    user = getpass.getuser()
    current = _login_shell(user)
    if current == zsh:
        logger.info("Login shell is already %s.", zsh)
        return
    logger.info("Changing login shell: %s -> %s", current or "unknown", zsh)
    if (
        shell.command_exists("chsh")
        and shell.run(["chsh", "-s", zsh], check=False).returncode == 0
    ):
        logger.info("Default shell set via chsh. Log out/in for it to take effect.")
    elif (
        shell.command_exists("usermod")
        and shell.run(["sudo", "usermod", "--shell", zsh, user], check=False).returncode
        == 0
    ):
        logger.info("Default shell set via usermod. Log out/in for it to take effect.")
    else:
        logger.warning(
            "Could not change shell; run: sudo usermod --shell %s %s", zsh, user
        )
