"""Root-owned file helper shared by services."""

from __future__ import annotations

from .shell import run


def sudo_write(path: str, content: str) -> None:
    """Write ``content`` to a root-owned file via ``sudo tee``."""
    run(["sudo", "tee", path], text_input=content, capture=True)
