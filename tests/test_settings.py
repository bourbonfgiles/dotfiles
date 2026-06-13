"""Tests for settings resolution."""

from __future__ import annotations

from dotfiles.config.settings import Settings


def test_load_finds_repo_root() -> None:
    settings = Settings.load()
    assert (settings.repo_root / "pyproject.toml").is_file()
    assert settings.brewfile.name == "brewfile"
