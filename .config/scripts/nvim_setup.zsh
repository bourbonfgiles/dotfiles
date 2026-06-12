#!/usr/bin/env zsh
set -uo pipefail

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# The Neovim (LazyVim) config lives in THIS repo and is symlinked into place by
# stow. This script intentionally NEVER moves ~/.config/nvim aside or clones the
# LazyVim starter over it (the old lazyvim_setup.zsh did, which wiped the stowed
# config). It only verifies the link and runs a headless plugin sync.

NVIM_CFG="${HOME}/.config/nvim"
REPO_NVIM="${HOME}/repos/personal/dotfiles/.config/nvim"

if [[ ! -e "$NVIM_CFG" ]]; then
  warn "$NVIM_CFG is missing. From the repo run: stow -t ~/.config .config"
  exit 0
fi

# `:A` fully resolves symlinks to a real absolute path.
if [[ "${NVIM_CFG:A}" != "${REPO_NVIM:A}" ]]; then
  warn "$NVIM_CFG does not resolve to the repo config."
  warn "  resolves to: ${NVIM_CFG:A}"
  warn "  expected:    ${REPO_NVIM:A}"
  warn "This is usually a leftover vanilla LazyVim starter. To restore the stowed config:"
  warn "  rm -rf ~/.config/nvim && rm -f ~/.config/nvim.bak && (cd ~/repos/personal/dotfiles && stow -t ~/.config .config)"
  exit 0
fi

log "Neovim config is the stowed repo config (${NVIM_CFG:A})."

if command -v nvim >/dev/null 2>&1; then
  log "Syncing Lazy plugins (headless)…"
  nvim --headless "+Lazy! sync" +qa 2>/dev/null || warn "Lazy sync reported issues; open nvim and run :Lazy."
  log "Neovim ready. Verify with ':LazyHealth'."
else
  warn "nvim not on PATH yet; skipping plugin sync (brew bundle installs neovim)."
fi

# Neovide on Linux is a Flatpak whose sandbox uses a private XDG config dir, so
# its bundled nvim ignores ~/.config/nvim. Point the sandbox config at the host
# repo config so Neovide looks like terminal Neovim. (Plugins install into the
# flatpak's own data dir on first launch to avoid nvim-version mismatches.)
if command -v flatpak >/dev/null 2>&1 && flatpak info dev.neovide.neovide >/dev/null 2>&1; then
  neovide_cfg="${HOME}/.var/app/dev.neovide.neovide/config"
  mkdir -p "$neovide_cfg"
  rm -rf "$neovide_cfg/nvim"
  ln -sfn "$HOME/.config/nvim" "$neovide_cfg/nvim"
  log "Neovide: linked sandbox config → ~/.config/nvim"
fi
