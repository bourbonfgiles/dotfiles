"""Tests for operating-system detection."""

from __future__ import annotations

import platform as std_platform

from dotfiles.utils import platform
from dotfiles.utils.platform import OSKind


def test_os_kind_returns_enum() -> None:
    assert isinstance(platform.os_kind(), OSKind)


def test_is_linux_matches_stdlib() -> None:
    assert platform.is_linux() == (std_platform.system() == "Linux")
