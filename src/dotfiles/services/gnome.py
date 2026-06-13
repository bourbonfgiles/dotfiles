"""GNOME desktop: extensions, dconf, native-keybind clears, Albert hotkey, keys."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
from ..utils.logging import get_logger

logger = get_logger("gnome")

DASH = "dash-to-dock@micxgx.gmail.com"
TILING = "tilingshell@ferrarodomenico.com"
FOCUS = "steal-my-focus-window@steal-my-focus-window"
_EXT_DIR = Path.home() / ".local/share/gnome-shell/extensions"
_MEDIA_KEYS = "org.gnome.settings-daemon.plugins.media-keys"
_ALBERT_KB = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/albert/"


def _gset(schema: str, key: str, value: str) -> None:
    shell.run(["gsettings", "set", schema, key, value], check=False)


def _ensure_gext() -> bool:
    if shell.command_exists("gext"):
        return True
    if shell.command_exists("uv"):
        logger.info("Installing gnome-extensions-cli (gext) via uv…")
        shell.run(["uv", "tool", "install", "gnome-extensions-cli"], check=False)
    return shell.command_exists("gext")


def _ext_present(uuid: str) -> bool:
    if (_EXT_DIR / uuid).is_dir():
        return True
    return (
        shell.run(
            ["gnome-extensions", "info", uuid], check=False, capture=True
        ).returncode
        == 0
    )


def _install_ext(uuid: str) -> bool:
    if _ext_present(uuid):
        logger.info("%s already installed.", uuid)
        return True
    if _ensure_gext():
        logger.info("Installing %s via gext…", uuid)
        shell.run(["gext", "install", uuid], check=False)
    return _ext_present(uuid)


def _install_tilingshell_github() -> bool:
    """Build Tiling Shell's v18 branch from source (GNOME 50 fallback)."""
    if not (shell.command_exists("git") and shell.command_exists("npm")):
        return False
    tmp = Path(tempfile.mkdtemp())
    cloned = shell.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            "v18.0",
            "https://github.com/domferr/tilingshell.git",
            str(tmp / "src"),
        ],
        check=False,
    )
    if cloned.returncode != 0:
        return False
    src = tmp / "src"
    shell.run(["npm", "install"], check=False, cwd=str(src))
    shell.run(["npm", "run", "build:dist"], check=False, cwd=str(src))
    zips = list(src.glob("*.zip"))
    if (
        zips
        and shell.run(
            ["gnome-extensions", "install", "-f", str(zips[0])], check=False
        ).returncode
        == 0
    ):
        return True
    return False


def _apply_dconf(path: str, file: Path) -> None:
    if not file.is_file():
        return
    logger.info("Loading dconf %s", path)
    shell.run(
        ["dconf", "load", path],
        text_input=file.read_text(encoding="utf-8"),
        check=False,
    )


def _albert_hotkey() -> None:
    """Bind Super+Space to ``albert toggle`` (Wayland-safe global shortcut)."""
    if not shell.command_exists("albert"):
        return
    _gset("org.gnome.desktop.wm.keybindings", "switch-input-source", "[]")
    _gset("org.gnome.desktop.wm.keybindings", "switch-input-source-backward", "[]")
    current = shell.run(
        ["gsettings", "get", _MEDIA_KEYS, "custom-keybindings"],
        check=False,
        capture=True,
    ).stdout.strip()
    if _ALBERT_KB not in current:
        if not current or "[]" in current:
            new = f"['{_ALBERT_KB}']"
        else:
            new = f"{current[:-1]}, '{_ALBERT_KB}']"
        _gset(_MEDIA_KEYS, "custom-keybindings", new)
    shell.run(["dconf", "write", f"{_ALBERT_KB}name", "'Albert'"], check=False)
    shell.run(
        ["dconf", "write", f"{_ALBERT_KB}command", "'albert toggle'"], check=False
    )
    shell.run(["dconf", "write", f"{_ALBERT_KB}binding", "'<Super>space'"], check=False)


def _keyboard_repeat() -> None:
    """Fast key repeat (e.g. StarCraft II rapid-fire)."""
    base = "org.gnome.desktop.peripherals.keyboard"
    _gset(base, "repeat", "true")
    _gset(base, "delay", "200")
    _gset(base, "repeat-interval", "8")


def run(settings: Settings) -> None:
    """Install/enable GNOME extensions and apply tracked dconf + tweaks."""
    if platform.is_mac():
        logger.info("macOS: skipping GNOME setup.")
        return
    if "GNOME" not in os.environ.get("XDG_CURRENT_DESKTOP", ""):
        logger.warning("Not a GNOME session; skipping GNOME setup.")
        return
    if not shell.command_exists("gnome-extensions"):
        logger.warning("gnome-extensions CLI not found; skipping GNOME setup.")
        return

    _gset("org.gnome.shell", "disable-user-extensions", "false")
    _install_ext(DASH)
    if not _install_ext(TILING):
        _install_tilingshell_github()
    _install_ext(FOCUS)
    for uuid in (DASH, TILING, FOCUS):
        if _ext_present(uuid):
            shell.run(["gnome-extensions", "enable", uuid], check=False)

    _apply_dconf(
        "/org/gnome/shell/extensions/tilingshell/",
        settings.dconf_dir / "tilingshell.conf",
    )
    _apply_dconf(
        "/org/gnome/shell/extensions/dash-to-dock/",
        settings.dconf_dir / "dash-to-dock.conf",
    )
    # Free native Super+Up/Down so Tiling Shell's bindings win.
    shell.run(
        ["dconf", "write", "/org/gnome/desktop/wm/keybindings/maximize", "@as []"],
        check=False,
    )
    shell.run(
        ["dconf", "write", "/org/gnome/desktop/wm/keybindings/unmaximize", "@as []"],
        check=False,
    )
    _albert_hotkey()
    _keyboard_repeat()
    logger.info("GNOME setup done. Log out/in to load newly installed extensions.")
