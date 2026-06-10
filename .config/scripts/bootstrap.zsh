#!/usr/bin/env zsh
set -euo pipefail

# Resolve repo-relative paths
SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h:h}"

warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# 1) Git + SSH + clone + stow + eza theme path
zsh "${REPO_ROOT}/bootstrap.zsh"

# 2) Homebrew Bundle: CLI on every OS; GUI casks on macOS only
zsh "${SCRIPT_DIR}/brew_setup.zsh"

# 3) Linux GUI apps (Flatpak), Ghostty, and gaming.
#    These no-op on macOS (casks cover it) and are non-fatal individually.
zsh "${SCRIPT_DIR}/flatpak_setup.zsh" || warn "flatpak_setup had issues."
zsh "${SCRIPT_DIR}/ghostty_setup.zsh" || warn "ghostty_setup had issues."
zsh "${SCRIPT_DIR}/gaming_setup.zsh"  || warn "gaming_setup had issues."

# 4) DNS over TLS (systemd-resolved on Linux; skipped on macOS)
zsh "${SCRIPT_DIR}/dns_setup.zsh" || warn "dns_setup had issues."

# 5) LazyVim (fresh runtime install from upstream)
zsh "${SCRIPT_DIR}/lazyvim_setup.zsh" || warn "lazyvim_setup had issues."

# 6) Post-bootstrap sanity checks
zsh "${SCRIPT_DIR}/post_bootstrap_checks.zsh" || true
