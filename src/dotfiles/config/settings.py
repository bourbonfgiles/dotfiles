"""Resolved filesystem paths, validated once on startup."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ..utils.exceptions import DotfilesError


@dataclass(frozen=True)
class Settings:
    """Filesystem locations the bootstrap operates on."""

    home: Path
    repo_root: Path
    config_home: Path

    @property
    def chezmoi_home(self) -> Path:
        """Chezmoi source state (``home/`` via ``.chezmoiroot``)."""
        return self.repo_root / "home"

    @property
    def system_dir(self) -> Path:
        """Tracked system drop-ins (resolved, NetworkManager) for Linux."""
        return self.repo_root / "system"

    @property
    def brewfile(self) -> Path:
        """Homebrew Brewfile."""
        return self.repo_root / "brewfile"

    @property
    def flatpaks_file(self) -> Path:
        """Flathub application-id list installed on every Linux target."""
        return self.repo_root / "flatpaks"

    @property
    def gaming_flatpaks_file(self) -> Path:
        """Gaming Flathub list (Silverblue; native on Bazzite)."""
        return self.repo_root / "flatpaks-gaming"

    @property
    def dconf_dir(self) -> Path:
        """Tracked GNOME dconf snippets."""
        return self.repo_root / "dconf"

    @classmethod
    def load(cls) -> Settings:
        """Resolve settings from the environment and package location."""
        home = Path.home()
        # config -> dotfiles -> src -> repo
        repo_root = Path(__file__).resolve().parents[3]
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
        settings = cls(home=home, repo_root=repo_root, config_home=config_home)
        settings.validate()
        return settings

    def validate(self) -> None:
        """Fail fast if the repo layout is not where we expect it.

        Raises:
            DotfilesError: If the resolved repo root does not exist.
        """
        if not self.repo_root.is_dir():
            raise DotfilesError(f"repo root not found: {self.repo_root}")


__all__ = ["Settings"]
