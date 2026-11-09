"""DNS over TLS: a Cloudflare profile on macOS; on Linux, keep DHCP resolvers out."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from ..config.settings import Settings
from ..utils import platform, shell
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


def _ignore_lan_dns() -> None:
    """Stop wired profiles taking DHCP's resolvers.

    NetworkManager gives the default-route link `~.`, so resolved would send
    every lookup to the router in plain text alongside Cloudflare. Wi-Fi keeps
    them for captive portals.
    """
    out = shell.capture(["nmcli", "-t", "-f", "UUID,TYPE,DEVICE", "connection", "show"])
    for line in out.splitlines():
        uuid_, kind, device = line.split(":", 2)
        if kind != "802-3-ethernet":
            continue
        shell.run(
            [
                "sudo",
                "nmcli",
                "connection",
                "modify",
                uuid_,
                "ipv4.ignore-auto-dns",
                "yes",
                "ipv6.ignore-auto-dns",
                "yes",
            ],
            check=False,
        )
        if device:
            shell.run(["sudo", "nmcli", "device", "reapply", device], check=False)
            # NetworkManager pushes nothing when it has no DNS, so resolved
            # would keep the router's servers from before.
            shell.run(["sudo", "resolvectl", "revert", device], check=False)


def run(settings: Settings) -> None:
    """DNS over TLS: a profile on macOS; on Linux the image has the drop-ins."""
    if platform.is_mac():
        _macos_profile()
    elif shell.command_exists("nmcli"):
        _ignore_lan_dns()
