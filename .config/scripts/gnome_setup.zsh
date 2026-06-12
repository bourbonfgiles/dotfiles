#!/usr/bin/env zsh
set -uo pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h:h}"
source "${SCRIPT_DIR}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# GNOME desktop customisation for the Linux targets: Dash to Dock + Tiling Shell
# (Windows-like snapping for the ultrawide). No-ops on macOS or non-GNOME.

if is_mac; then
  log "macOS: skipping GNOME setup."
  exit 0
fi
if [[ "${XDG_CURRENT_DESKTOP:-}" != *GNOME* ]]; then
  warn "Not a GNOME session (XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-unset}); skipping GNOME setup."
  exit 0
fi
if ! command -v gnome-extensions >/dev/null 2>&1; then
  warn "gnome-extensions CLI not found; skipping GNOME setup."
  exit 0
fi

DASH="dash-to-dock@micxgx.gmail.com"
TILING="tilingshell@ferrarodomenico.com"
EXT_DIR="${HOME}/.local/share/gnome-shell/extensions"
DCONF_DIR="${REPO_ROOT}/dconf"

# 1) Allow user extensions (already default on Bazzite, required on Silverblue).
gsettings set org.gnome.shell disable-user-extensions false 2>/dev/null || true

# Ensure gext (gnome-extensions-cli) is available to pull from extensions.gnome.org.
ensure_gext() {
  command -v gext >/dev/null 2>&1 && return 0
  if command -v uv >/dev/null 2>&1; then
    log "Installing gnome-extensions-cli (gext) via uv…"
    uv tool install gnome-extensions-cli >/dev/null 2>&1 || warn "Could not install gext via uv."
  fi
  command -v gext >/dev/null 2>&1
}

ext_present() { [[ -d "${EXT_DIR}/$1" ]] || gnome-extensions info "$1" >/dev/null 2>&1; }

install_ext() {
  local uuid="$1"
  if ext_present "$uuid"; then
    log "$uuid already installed."
    return 0
  fi
  if ensure_gext; then
    log "Installing $uuid via gext…"
    gext install "$uuid" >/dev/null 2>&1 && return 0
    warn "gext could not install $uuid (it may not yet support this GNOME version on extensions.gnome.org)."
  fi
  return 1
}

# GNOME 50 fallback for Tiling Shell: build the v18 branch from source.
install_tilingshell_from_github() {
  command -v git >/dev/null 2>&1 || { warn "git missing; cannot build Tiling Shell."; return 1; }
  command -v npm >/dev/null 2>&1 || { warn "npm missing (brew installs node); cannot build Tiling Shell from source."; return 1; }
  local tmp; tmp="$(mktemp -d)"
  log "Building Tiling Shell (v18.0) from GitHub for the current GNOME…"
  if ! git clone --depth 1 --branch v18.0 https://github.com/domferr/tilingshell.git "$tmp" >/dev/null 2>&1; then
    warn "Clone of Tiling Shell v18.0 failed."; rm -rf "$tmp"; return 1
  fi
  if ! ( cd "$tmp" && npm install >/dev/null 2>&1 && npm run build:dist >/dev/null 2>&1 ); then
    warn "Tiling Shell build failed."; rm -rf "$tmp"; return 1
  fi
  local zip; zip="$(ls "$tmp"/*.zip 2>/dev/null | head -n1)"
  if [[ -n "$zip" ]] && gnome-extensions install -f "$zip" >/dev/null 2>&1; then
    rm -rf "$tmp"; return 0
  fi
  warn "Could not install built Tiling Shell zip."; rm -rf "$tmp"; return 1
}

# 2) Dash to Dock.
install_ext "$DASH" || warn "Install Dash to Dock manually: https://extensions.gnome.org/extension/307/dash-to-dock/"

# 3) Tiling Shell (with GNOME 50 source-build fallback).
if ! install_ext "$TILING"; then
  install_tilingshell_from_github || warn "Install Tiling Shell manually: https://extensions.gnome.org/extension/7065/tiling-shell/"
fi

# 4) Enable. On Wayland newly installed extensions only load after logout/login.
for uuid in "$DASH" "$TILING"; do
  ext_present "$uuid" || continue
  if gnome-extensions enable "$uuid" 2>/dev/null; then
    log "Enabled $uuid"
  else
    warn "Could not enable $uuid yet. After logging out/in run: gnome-extensions enable $uuid"
  fi
done

# 5) Apply tracked dconf (layouts, keybindings, dock).
apply_dconf() {
  local path="$1" file="$2"
  [[ -r "$file" ]] || return 0
  log "Loading dconf $path"
  dconf load "$path" < "$file" 2>/dev/null || warn "dconf load failed for $path"
}
apply_dconf "/org/gnome/shell/extensions/tilingshell/" "${DCONF_DIR}/tilingshell.conf"
apply_dconf "/org/gnome/shell/extensions/dash-to-dock/" "${DCONF_DIR}/dash-to-dock.conf"

# Free GNOME's native Super+Up/Down so Tiling Shell's move-window-center and
# span-window-all-tiles bindings (Super+Up/Down) aren't intercepted by maximize.
dconf write /org/gnome/desktop/wm/keybindings/maximize "@as []" 2>/dev/null || true
dconf write /org/gnome/desktop/wm/keybindings/unmaximize "@as []" 2>/dev/null || true

log "GNOME setup done. Log out and back in to load newly installed extensions."
log "If the Tiling Shell layout didn't stick (first run initialises defaults), re-run this script after logging in."
