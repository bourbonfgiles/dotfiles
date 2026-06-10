#!/usr/bin/env zsh
set -uo pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h:h}"
source "${SCRIPT_DIR}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

kind="$(os_kind)"
case "$kind" in
  mac)
    log "macOS: gaming setup not applicable; skipping."
    exit 0 ;;
  bazzite)
    log "Bazzite ships Steam, Lutris and the gaming stack natively; nothing to do."
    exit 0 ;;
esac

if ! command -v flatpak >/dev/null 2>&1; then
  warn "flatpak not found; skipping gaming setup."
  exit 0
fi

LIST="${REPO_ROOT}/flatpaks-gaming"
if [[ -r "$LIST" ]]; then
  flatpak remote-add --if-not-exists --user flathub \
    https://flathub.org/repo/flathub.flatpakrepo >/dev/null 2>&1 || true

  log "Installing gaming Flatpaks from $(basename "$LIST")..."
  while IFS= read -r line; do
    app="${line%%#*}"
    app="${app//[[:space:]]/}"
    [[ -z "$app" ]] && continue

    if flatpak info "$app" >/dev/null 2>&1; then
      log "already installed: $app"
      continue
    fi
    log "installing: $app"
    flatpak install --user --noninteractive --or-update flathub "$app" \
      || warn "failed: $app"
  done < "$LIST"
else
  warn "Gaming list not found at $LIST; skipping installs."
fi

if [[ "$kind" == "fedora-atomic" ]]; then
  cat <<'EOS'

------------------------------------------------------------------------
Installed the portable gaming apps (Steam, Lutris, Heroic, Bottles,
ProtonUp-Qt) as Flatpaks. Bazzite's deeper gaming features (custom
kernel/HDR, gamescope-session, mesa-freeworld, controller drivers,
ujust tooling) are baked into the Bazzite image and cannot be fully
replicated on stock Silverblue. To get all of them, rebase to Bazzite:

  rpm-ostree rebase ostree-unverified-registry:ghcr.io/ublue-os/bazzite-gnome:stable

(then reboot). Optional and intentionally NOT run automatically.
------------------------------------------------------------------------
EOS
fi

log "Gaming setup complete."
