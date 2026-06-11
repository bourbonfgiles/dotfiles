#!/usr/bin/env zsh
set -uo pipefail

source "${0:A:h}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# Make Homebrew zsh the default login shell. macOS already defaults to zsh, so
# this targets Linux (Bazzite/Silverblue), where the default is bash.

if is_mac; then
  log "macOS already uses zsh as the login shell; nothing to do."
  exit 0
fi

ZSH_BIN="$(command -v zsh || true)"
if [[ -z "$ZSH_BIN" ]]; then
  warn "zsh not found on PATH; skipping default-shell change (install via brew bundle)."
  exit 0
fi

# chsh only accepts shells listed in /etc/shells.
if ! grep -qxF "$ZSH_BIN" /etc/shells 2>/dev/null; then
  log "Registering $ZSH_BIN in /etc/shells…"
  echo "$ZSH_BIN" | sudo tee -a /etc/shells >/dev/null || warn "Could not write /etc/shells."
fi

current="$(getent passwd "$USER" 2>/dev/null | cut -d: -f7)"
if [[ "$current" == "$ZSH_BIN" ]]; then
  log "Login shell is already $ZSH_BIN."
else
  log "Changing login shell: ${current:-unknown} -> $ZSH_BIN"
  # Bazzite/Silverblue ship no `chsh`; fall back to `usermod` (writes /etc/passwd).
  if command -v chsh >/dev/null 2>&1 && chsh -s "$ZSH_BIN"; then
    log "Default shell set via chsh. Log out/in for it to take effect."
  elif command -v usermod >/dev/null 2>&1 && sudo usermod --shell "$ZSH_BIN" "$USER"; then
    log "Default shell set via usermod. Log out/in for it to take effect."
  else
    warn "Could not change shell automatically. Set it manually: sudo usermod --shell $ZSH_BIN $USER"
  fi
fi
