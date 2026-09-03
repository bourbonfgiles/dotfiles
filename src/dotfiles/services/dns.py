"""DNS over TLS: Cloudflare profile on macOS; resolved drop-ins on Linux."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger

logger = get_logger("dns")


def _macos_profile() -> None:
    """Generate a Cloudflare DNS-over-TLS profile and open it for approval."""
    payload, profile = uuid.uuid4(), uuid.uuid4()
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>DNSSettings</key>
      <dict>
        <key>DNSProtocol</key><string>TLS</string>
        <key>ServerName</key><string>one.one.one.one</string>
        <key>ServerAddresses</key>
        <array><string>1.1.1.1</string><string>1.0.0.1</string></array>
      </dict>
      <key>PayloadType</key><string>com.apple.dnsSettings.managed</string>
      <key>PayloadIdentifier</key><string>com.bourbonfgiles.dotfiles.dns.{payload}</string>
      <key>PayloadUUID</key><string>{payload}</string>
      <key>PayloadVersion</key><integer>1</integer>
      <key>PayloadDisplayName</key><string>Cloudflare DNS over TLS</string>
    </dict>
  </array>
  <key>PayloadDisplayName</key><string>Cloudflare DNS over TLS</string>
  <key>PayloadIdentifier</key><string>com.bourbonfgiles.dotfiles.dns.{profile}</string>
  <key>PayloadType</key><string>Configuration</string>
  <key>PayloadUUID</key><string>{profile}</string>
  <key>PayloadVersion</key><integer>1</integer>
</dict>
</plist>
"""
    path = Path(tempfile.mkdtemp()) / "Cloudflare-DoT.mobileconfig"
    path.write_text(plist, encoding="utf-8")
    if shell.run(["open", str(path)], check=False).returncode == 0:
        logger.info(
            "Approve 'Cloudflare DNS over TLS' in System Settings > VPN & Device Management."
        )
    else:
        logger.warning("Could not open the profile; install it manually: %s", path)


def _install_dropins(settings: Settings) -> None:
    """Copy tracked resolved/NetworkManager drop-ins into /etc."""
    resolved_src = settings.system_dir / "resolved.conf.d"
    nm_src = settings.system_dir / "NetworkManager" / "conf.d"

    if resolved_src.is_dir():
        shell.run(["sudo", "mkdir", "-p", "/etc/systemd/resolved.conf.d"], check=False)
        for conf in sorted(resolved_src.glob("*.conf")):
            logger.info("Installing %s", conf.name)
            system.sudo_write(
                f"/etc/systemd/resolved.conf.d/{conf.name}",
                conf.read_text(encoding="utf-8"),
            )

    if nm_src.is_dir() and shell.command_exists("nmcli"):
        shell.run(["sudo", "mkdir", "-p", "/etc/NetworkManager/conf.d"], check=False)
        for conf in sorted(nm_src.glob("*.conf")):
            logger.info("Installing NetworkManager %s", conf.name)
            system.sudo_write(
                f"/etc/NetworkManager/conf.d/{conf.name}",
                conf.read_text(encoding="utf-8"),
            )


def _linux_resolved(settings: Settings) -> None:
    """Point systemd-resolved at Cloudflare DNS over TLS via drop-in files."""
    logger.info("Configuring systemd-resolved for DNS over TLS…")
    _install_dropins(settings)
    shell.run(
        [
            "sudo",
            "ln",
            "-sf",
            "/run/systemd/resolve/stub-resolv.conf",
            "/etc/resolv.conf",
        ],
        check=False,
    )
    shell.run(["sudo", "systemctl", "restart", "systemd-resolved"], check=False)
    shell.run(["sudo", "systemctl", "enable", "systemd-resolved"], check=False)
    if shell.command_exists("nmcli"):
        shell.run(["sudo", "systemctl", "restart", "NetworkManager"], check=False)
    logger.info("Linux DNS over TLS configured (Cloudflare 1.1.1.1 drop-ins).")


def run(settings: Settings) -> None:
    """Enable DNS over TLS appropriately for the platform."""
    if platform.is_mac():
        _macos_profile()
        return
    if platform.is_linux():
        if not (
            shell.command_exists("resolvectl")
            or shell.command_exists("systemd-resolve")
        ):
            logger.warning("systemd-resolved not found; skipping DNS setup.")
            return
        _linux_resolved(settings)
