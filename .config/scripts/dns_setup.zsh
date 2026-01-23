#!/usr/bin/env zsh
set -euo pipefail

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31mERROR:\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

OS="$(uname -s)"
IS_MAC=false
IS_LINUX=false

case "$OS" in
  Darwin) IS_MAC=true ;;
  Linux)  IS_LINUX=true ;;
  *)      err "Unsupported OS: $OS"; exit 1 ;;
esac

################################################################################
# macOS DNS Configuration (Cloudflare WARP)
################################################################################

if $IS_MAC; then
  log "Configuring macOS DNS with Cloudflare WARP..."
  
  # Check if WARP is installed
  if [ ! -d "/Applications/Cloudflare WARP.app" ]; then
    warn "Cloudflare WARP not installed. Install via: brew install --cask cloudflare-warp"
    warn "After installation, enable WARP and set mode to 'WARP' (not just DNS-only)"
    exit 1
  fi
  
  # Check if WARP is running
  if ! pgrep -x "Cloudflare WARP" > /dev/null; then
    warn "Cloudflare WARP is not running. Starting..."
    open -a "Cloudflare WARP"
    sleep 3
  fi
  
  # Verify WARP status
  if command -v warp-cli >/dev/null 2>&1; then
    WARP_STATUS=$(warp-cli status 2>/dev/null | head -1 || echo "Unknown")
    log "WARP Status: $WARP_STATUS"
    
    if [[ "$WARP_STATUS" != *"Connected"* ]]; then
      warn "WARP is not connected. Connecting..."
      warp-cli connect || warn "Failed to connect WARP. Please connect manually."
    fi
  else
    warn "warp-cli not found. Verify WARP is connected manually in the menu bar."
  fi
  
  log "macOS DNS configuration complete."
  log "Safari will automatically use WARP's encrypted DNS."
  log "To verify WARP is working, visit: https://1.1.1.1/help"
  
fi

################################################################################
# Linux DNS Configuration (systemd-resolved with DNS over TLS)
################################################################################

if $IS_LINUX; then
  log "Configuring Linux DNS over TLS with systemd-resolved..."
  
  # Check if running on Bazzite
  IS_BAZZITE=false
  if [ -f /etc/os-release ] && grep -q "Bazzite" /etc/os-release; then
    IS_BAZZITE=true
    log "Detected Bazzite (immutable OS)"
  fi
  
  # Check if systemd-resolved is available
  if ! command -v systemd-resolve >/dev/null 2>&1 && ! command -v resolvectl >/dev/null 2>&1; then
    err "systemd-resolved not found. This script requires systemd-resolved."
    err "Install with: sudo apt install systemd-resolved (Debian/Ubuntu) or equivalent"
    exit 1
  fi
  
  # Create systemd-resolved configuration
  RESOLVED_CONF="/etc/systemd/resolved.conf"
  
  log "Creating systemd-resolved configuration for DNS over TLS..."
  
  # Backup existing config
  if [ -f "$RESOLVED_CONF" ]; then
    sudo cp "$RESOLVED_CONF" "${RESOLVED_CONF}.backup.$(date +%Y%m%d-%H%M%S)"
    log "Backed up existing resolved.conf"
  fi
  
  # Write new configuration
  sudo tee "$RESOLVED_CONF" > /dev/null << 'EOF'
[Resolve]
DNS=1.1.1.1 1.0.0.1 2606:4700:4700::1111 2606:4700:4700::1001
FallbackDNS=8.8.8.8 8.8.4.4
Domains=~.
DNSOverTLS=yes
DNSSEC=allow-downgrade
DNSStubListener=yes
Cache=yes
CacheFromLocalhost=no
EOF
  
  log "systemd-resolved configuration written."
  
  # Handle NetworkManager if present
  if command -v nmcli >/dev/null 2>&1; then
    log "Configuring NetworkManager to use systemd-resolved..."
    
    NM_CONF_DIR="/etc/NetworkManager/conf.d"
    sudo mkdir -p "$NM_CONF_DIR"
    
    sudo tee "${NM_CONF_DIR}/dns.conf" > /dev/null << 'EOF'
[main]
dns=systemd-resolved
systemd-resolved=true
EOF
    
    log "NetworkManager configured to use systemd-resolved."
    
    # Remove any old DNS configuration that might conflict
    if [ -f "${NM_CONF_DIR}/dns-servers.conf" ]; then
      sudo rm -f "${NM_CONF_DIR}/dns-servers.conf"
      log "Removed old DNS servers configuration."
    fi
  fi
  
  # Ensure /etc/resolv.conf is symlinked correctly
  if [ ! -L /etc/resolv.conf ] || [ "$(readlink /etc/resolv.conf)" != "/run/systemd/resolve/stub-resolv.conf" ]; then
    log "Fixing /etc/resolv.conf symlink..."
    sudo rm -f /etc/resolv.conf
    sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
  fi
  
  # Restart services
  log "Restarting systemd-resolved..."
  sudo systemctl restart systemd-resolved
  sudo systemctl enable systemd-resolved
  
  if command -v nmcli >/dev/null 2>&1; then
    log "Restarting NetworkManager..."
    sudo systemctl restart NetworkManager
  fi
  
  # Verify DNS over TLS is working
  sleep 2
  log "Verifying DNS over TLS configuration..."
  
  if command -v resolvectl >/dev/null 2>&1; then
    resolvectl status | grep -A 5 "DNS Servers"
    resolvectl query cloudflare.com > /dev/null && log "✓ DNS resolution working"
  elif command -v systemd-resolve >/dev/null 2>&1; then
    systemd-resolve --status | grep -A 5 "DNS Servers"
    systemd-resolve cloudflare.com > /dev/null && log "✓ DNS resolution working"
  fi
  
  log "Linux DNS over TLS configuration complete."
  log "System DNS now uses Cloudflare DNS over TLS (1.1.1.1)"
  log "Firefox with NordVPN extension will use NordVPN's DNS for browser traffic."
  log ""
  
  if $IS_BAZZITE; then
    log "Bazzite Note: These settings persist across updates."
    log "If DNS resets after a system update, re-run: zsh ~/.config/scripts/dns_setup.zsh"
  fi
  
  log "To verify DNS over TLS is working:"
  log "  resolvectl status"
  log "  resolvectl query example.com"
  
fi

log "DNS configuration complete for $OS!"
