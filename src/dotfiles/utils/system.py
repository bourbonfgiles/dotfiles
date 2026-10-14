"""rpm-ostree / Fedora helpers shared by the layered-package services."""

from __future__ import annotations

import re  # stdlib: regular expressions
from pathlib import Path

from .logging import get_logger
from .platform import OS_RELEASE_PATH
from .shell import run

logger = get_logger("system")


def fedora_version_id(default: str = "40") -> str:
    """Return the Fedora ``VERSION_ID`` (e.g. ``"44"``), or ``default``."""
    try:
        # .splitlines() returns a list of lines; 'for ... in' walks them.
        for line in OS_RELEASE_PATH.read_text(encoding="utf-8").splitlines():
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


def ensure_repo_file(path: str, body: str, *, label: str) -> None:
    """Write a yum ``.repo`` file via sudo if it is not already present.

    ``label`` is used only for the log line (e.g. "Warp", "Albert").
    """
    if Path(path).exists():
        logger.info("%s repo already present.", label)
        return
    logger.info("Adding %s's RPM repo…", label)
    sudo_write(path, body)


def rpmostree_install_or_migrate(package: str, *, label: str) -> None:
    """Layer ``package`` with rpm-ostree, migrating a stray local RPM if needed.

    Covers the shared atomic-Fedora flow used by multiple services:

    * if the package is already installed as a one-off ``LocalPackages`` entry,
      uninstall it and reinstall from the (now configured) repo so updates flow;
    * if it is already layered from a repo, do nothing;
    * otherwise layer it idempotently.

    A reboot is required before a newly layered package is usable.
    """
    run(["rpm-ostree", "refresh-md"], check=False)
    if rpm_installed(package):
        if rpm_ostree_local_package(package):
            logger.info("Migrating %s from a local RPM to the repo package…", label)
            run(["sudo", "rpm-ostree", "uninstall", package], check=False)
            run(["sudo", "rpm-ostree", "install", package], check=False)
            logger.info("%s migrated. Reboot to finish: systemctl reboot", label)
        else:
            logger.info("%s already layered from the repo; nothing to do.", label)
        return
    logger.info("Layering %s (rpm-ostree). A reboot is needed to use it.", label)
    run(["sudo", "rpm-ostree", "install", "--idempotent", package], check=False)
