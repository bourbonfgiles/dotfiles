#!/usr/bin/env zsh
set -uo pipefail

source "${0:A:h}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# macOS installs Nerd Fonts via Homebrew casks (see Brewfile). On Linux they are
# not packaged, so fetch the ones the configs reference into ~/.local/share/fonts
# — Flatpaks (Neovide) and native terminals both read that path.

if is_mac; then
  log "macOS: Nerd Fonts come from Brewfile casks; skipping."
  exit 0
fi

# nerd-fonts release archive base names (family becomes "<name> Nerd Font").
typeset -a FONTS
FONTS=(JetBrainsMono)

FONT_DIR="${HOME}/.local/share/fonts"
mkdir -p "$FONT_DIR"

for f in $FONTS; do
  if fc-list 2>/dev/null | grep -qi "${f} Nerd Font"; then
    log "${f} Nerd Font already installed."
    continue
  fi
  log "Installing ${f} Nerd Font…"
  tmp="$(mktemp -d)"
  if curl -fsSL -o "${tmp}/${f}.tar.xz" \
      "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/${f}.tar.xz"; then
    mkdir -p "${FONT_DIR}/${f}NerdFont"
    tar -xf "${tmp}/${f}.tar.xz" -C "${FONT_DIR}/${f}NerdFont" \
      || warn "Failed to extract ${f} Nerd Font."
  else
    warn "Failed to download ${f} Nerd Font."
  fi
  rm -rf "$tmp"
done

command -v fc-cache >/dev/null 2>&1 && fc-cache -f >/dev/null 2>&1 || true
log "Fonts setup complete."
