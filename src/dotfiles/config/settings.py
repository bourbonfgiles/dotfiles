"""Resolved filesystem paths, validated once on startup."""

from __future__ import annotations

import os  # stdlib: environment access (os.environ)
from dataclasses import dataclass  # decorator that auto-generates __init__/__repr__
from pathlib import Path

from ..utils.exceptions import DotfilesError  # '..' = parent package (dotfiles)


# '@dataclass(frozen=True)' is a decorator: it writes the boilerplate __init__,
# __repr__, __eq__ for us. 'frozen=True' makes instances read-only (immutable).
@dataclass(frozen=True)
class Settings:
    """Filesystem locations the bootstrap operates on."""

    # These class-level annotations become the dataclass fields (and __init__ args).
    home: Path
    repo_root: Path
    config_home: Path

    # '@property' lets you call this like an attribute (settings.repo_config) with
    # no parentheses; it computes a value on access.
    @property
    def repo_config(self) -> Path:
        """The repo's ``.config`` tree (stowed into ``~/.config``)."""
        return self.repo_root / ".config"  # Path overloads '/' to join path parts

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

    @property
    def albert_template(self) -> Path:
        """Tracked Albert config seeded onto fresh machines."""
        return self.repo_root / "albert" / "config"

    # '@classmethod' receives the class itself ('cls'), not an instance. It's a
    # factory: a tidy way to build and return a configured Settings.
    @classmethod
    def load(cls) -> Settings:  # 'from __future__ import annotations' lets us name
        # the still-unfinished class here (a forward reference) without quotes.
        """Resolve settings from the environment and package location."""
        home = Path.home()  # Path classmethod: the current user's home directory
        # __file__ is this file's path. .resolve() makes it absolute (following
        # symlinks). .parents[3] climbs 4 levels: config -> dotfiles -> src -> repo.
        repo_root = Path(__file__).resolve().parents[3]
        # os.environ.get(key, default): read an env var, falling back if unset.
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
        settings = cls(home=home, repo_root=repo_root, config_home=config_home)
        settings.validate()  # run our own check before handing the object back
        return settings

    def validate(self) -> None:
        """Fail fast if the repo layout is not where we expect it.

        Raises:
            DotfilesError: If the resolved repo root does not exist.
        """
        if not self.repo_root.is_dir():  # Path.is_dir(): bool
            raise DotfilesError(f"repo root not found: {self.repo_root}")


__all__ = ["Settings"]  # names exported by 'from settings import *'
