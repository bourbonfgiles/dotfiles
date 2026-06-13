"""DNS over TLS: a Cloudflare profile on macOS; systemd-resolved on Linux."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell, system
from ..utils.logging import get_logger

logger = get_logger("dns")

_RESOLVED_CONF = "/etc/systemd/resolved.conf"
_RESOLVED_BODY = (
    "[Resolve]\n"
    "DNS=1.1.1.1 1.0.0.1 2606:4700:4700::1111 2606:4700:4700::1001\n"
    "FallbackDNS=8.8.8.8 8.8.4.4\n"
    "Domains=~.\n"
    "DNSOverTLS=yes\n"
    "DNSSEC=allow-downgrade\n"
    "DNSStubListener=yes\n"
    "Cache=yes\n"
    "CacheFromLocalhost=no\n"
)
_NM_DNS = "[main]\ndns=systemd-resolved\nsystemd-resolved=true\n"


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


def _linux_resolved() -> None:
    """Point systemd-resolved at Cloudflare DNS over TLS."""
    logger.info("Configuring systemd-resolved for DNS over TLS…")
    system.sudo_write(_RESOLVED_CONF, _RESOLVED_BODY)
    if shell.command_exists("nmcli"):
        shell.run(["sudo", "mkdir", "-p", "/etc/NetworkManager/conf.d"], check=False)
        system.sudo_write("/etc/NetworkManager/conf.d/dns.conf", _NM_DNS)
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
    logger.info("Linux DNS over TLS configured (Cloudflare 1.1.1.1).")


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
        _linux_resolved()
