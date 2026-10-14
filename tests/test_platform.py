"""Tests for operating-system detection."""

from __future__ import annotations

import platform as std_platform

import pytest

from dotfiles.utils import platform
from dotfiles.utils.platform import OSKind


def test_os_kind_returns_enum() -> None:
    assert isinstance(platform.os_kind(), OSKind)


def test_is_linux_matches_stdlib() -> None:
    assert platform.is_linux() == (std_platform.system() == "Linux")


def _fake_os(
    monkeypatch: pytest.MonkeyPatch,
    *,
    system: str,
    release: str = "",
    ostree: bool = False,
) -> None:
    """Simulate a host by faking platform.system() and the probed files."""
    monkeypatch.setattr(platform._platform, "system", lambda: system)

    class _FakePath:
        def __init__(self, text: str | None, exists: bool) -> None:
            self._text = text
            self._exists = exists

        def read_text(self, encoding: str = "utf-8") -> str:
            if self._text is None:
                raise OSError("missing")
            return self._text

        def exists(self) -> bool:
            return self._exists

    monkeypatch.setattr(
        platform, "OS_RELEASE_PATH", _FakePath(release or None, bool(release))
    )
    monkeypatch.setattr(platform, "_OSTREE_MARKER", _FakePath(None, ostree))


def test_detects_mac(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_os(monkeypatch, system="Darwin")
    assert platform.os_kind() is OSKind.MAC
    assert platform.is_mac()
    assert not platform.is_linux()
    assert not platform.is_fedora_atomic()


def test_detects_bazzite(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_os(monkeypatch, system="Linux", release="ID=bazzite\n", ostree=True)
    assert platform.os_kind() is OSKind.BAZZITE
    assert platform.is_linux()
    assert platform.is_fedora_atomic()  # Bazzite is atomic


def test_detects_fedora_atomic(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_os(monkeypatch, system="Linux", release="ID=fedora\n", ostree=True)
    assert platform.os_kind() is OSKind.FEDORA_ATOMIC
    assert platform.is_linux()
    assert platform.is_fedora_atomic()


def test_detects_plain_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_os(monkeypatch, system="Linux", release="ID=ubuntu\n", ostree=False)
    assert platform.os_kind() is OSKind.LINUX
    assert platform.is_linux()
    assert not platform.is_fedora_atomic()


def test_unknown_os(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_os(monkeypatch, system="Windows")
    assert platform.os_kind() is OSKind.UNKNOWN
    assert not platform.is_linux()
    assert not platform.is_mac()
