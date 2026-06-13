"""rpm-ostree / Fedora helpers shared by the layered-package services."""

from __future__ import annotations

import re  # stdlib: regular expressions
from pathlib import Path

from .shell import run

_OS_RELEASE = Path("/etc/os-release")


def fedora_version_id(default: str = "40") -> str:
    """Return the Fedora ``VERSION_ID`` (e.g. ``"44"``), or ``default``."""
    try:
        # .splitlines() returns a list of lines; 'for ... in' walks them.
        for line in _OS_RELEASE.read_text(encoding="utf-8").splitlines():
            if line.startswith("VERSION_ID="):  # str method: prefix test
                # split("=", 1) -> 2 parts on the first '='; [1] is the value,
                # then strip whitespace and surrounding double quotes.
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass  # 'pass': do nothing, fall through to the default below
    return default


def sudo_write(path: str, content: str) -> None:
    """Write ``content`` to a root-owned file via ``sudo tee``."""
    # 'tee' copies stdin to the file; text_input feeds our content to its stdin.
    run(["sudo", "tee", path], text_input=content, capture=True)


def rpm_installed(name: str) -> bool:
    """Return True if rpm package ``name`` is installed."""
    # check=False: a 'not installed' exit code returns normally (no exception).
    return run(["rpm", "-q", name], check=False, capture=True).returncode == 0


def rpm_ostree_local_package(name: str) -> bool:
    """Return True if ``name`` is layered as a one-off LocalPackages entry."""
    result = run(["rpm-ostree", "status"], check=False, capture=True)
    # re.search returns a Match object or None; bool() turns that into True/False.
    # rf"..." is a raw f-string; re.escape() neutralises any regex-special chars.
    return bool(re.search(rf"LocalPackages:.*{re.escape(name)}", result.stdout))
