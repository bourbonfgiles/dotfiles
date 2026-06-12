#!/usr/bin/env zsh
set -euo pipefail

# Logs
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
# Homebrew PATH (macOS + Linux)
# Official method to expose brewed bottles across shells.                      #
# ref: Homebrew formulae/docs (shellenv, bottles)                              #
################################################################################

eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$(~/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true

# Install Homebrew if missing (fresh machine), then reload its shellenv.
if ! command -v brew >/dev/null 2>&1; then
  log "Installing Homebrew…"
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true
fi

################################################################################
# Minimal packages (git + stow). All other tools come from Brewfile.           #
################################################################################

brew update || true
brew install git stow || true

################################################################################
# macOS fallback for Git (Command Line Tools)
################################################################################

if $IS_MAC && ! command -v git >/dev/null 2>&1; then
  log "Installing Xcode Command Line Tools (includes Git)…"
  xcode-select --install || true
fi

################################################################################
# Git & SSH (ed25519)
################################################################################

log "Configuring Git & SSH…"

if [[ -z "$(git config --global user.email 2>/dev/null)" || -z "$(git config --global user.name 2>/dev/null)" ]]; then
  read "email?Enter your GitHub email: "
  read "username?Enter your GitHub username: "
  git config --global user.email "$email"
  git config --global user.name "$username"
else
  email="$(git config --global user.email)"
  log "Git identity already set for $(git config --global user.name) <$email>; skipping prompts."
fi
git config --global init.defaultBranch main
git config --global push.autosetupremote true

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_ed25519 ]; then
  ssh-keygen -t ed25519 -C "$email"
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_ed25519
  if $IS_MAC && command -v pbcopy >/dev/null 2>&1; then
    pbcopy < ~/.ssh/id_ed25519.pub
    log "SSH public key copied to clipboard (macOS)."
  elif $IS_LINUX && command -v wl-copy >/dev/null 2>&1; then
    wl-copy < ~/.ssh/id_ed25519.pub
    log "SSH public key copied to clipboard (Wayland)."
  elif $IS_LINUX && command -v xclip >/dev/null 2>&1; then
    xclip -selection clipboard < ~/.ssh/id_ed25519.pub
    log "SSH public key copied to clipboard (X11)."
  else
    log "Copy this SSH public key into GitHub:"
    cat ~/.ssh/id_ed25519.pub
  fi
  read "dummy?Press Enter after adding the SSH key to GitHub…"
else
  log "SSH key already exists."
fi

################################################################################
# Clone dotfiles & eza-themes
################################################################################

log "Cloning dotfiles & eza-themes…"
mkdir -p ~/repos/personal

clone_or_update() {
  local repo_url="$1"
  local dest="$2"
  if [ -d "$dest/.git" ]; then
    log "Updating $(basename "$dest")…"
    git -C "$dest" pull --ff-only
  else
    log "Cloning $(basename "$dest")…"
    git clone "$repo_url" "$dest" || { err "Failed to clone $repo_url"; exit 1; }
  fi
}

clone_or_update "git@github.com:bourbonfgiles/dotfiles.git"   "$HOME/repos/personal/dotfiles"
clone_or_update "https://github.com/eza-community/eza-themes.git" "$HOME/repos/personal/eza-themes"
clone_or_update "https://github.com/syl20bnr/spacemacs.git" "$HOME/.emacs.d"

################################################################################
# Symlinks via GNU Stow
################################################################################

log "Creating symlinks with stow…"
cd ~/repos/personal/dotfiles || { err "dotfiles directory missing"; exit 1; }
mkdir -p ~/.config

# Self-heal prior stow conflicts: if a target in ~/.config is a real file/dir
# (not a symlink) stow would abort. This happens e.g. when the old
# lazyvim_setup.zsh replaced the stowed ~/.config/nvim with a vanilla starter.
# Move any such path aside (timestamped) so stow can link the repo version.
for _entry in .config/*(DN); do
  _target="$HOME/.config/${_entry:t}"
  if [[ -e "$_target" && ! -L "$_target" ]]; then
    _bak="${_target}.pre-stow.$(date +%Y%m%d-%H%M%S)"
    warn "Backing up ${_target} → ${_bak} so stow can link the repo version."
    mv "$_target" "$_bak"
  fi
done
# Drop the stale ~/.config/nvim.bak symlink left by the old lazyvim_setup.zsh.
if [[ -L "$HOME/.config/nvim.bak" ]]; then
  rm -f "$HOME/.config/nvim.bak"
fi

stow -t ~/.config .config
ln -sf ~/repos/personal/dotfiles/.zshrc ~/.zshrc
ln -sf ~/repos/personal/dotfiles/.spacemacs ~/.spacemacs
log "Symlinks created."

################################################################################
# eza theme path normalization (macOS + Linux)
# Use ~/.config/eza on both platforms; avoids macOS path quirks.               #
# ref: eza-themes README + macOS issue thread                                  #
################################################################################

mkdir -p ~/.config/eza
ln -sf ~/repos/personal/eza-themes/themes/dracula.yml ~/.config/eza/theme.yml
if ! grep -q 'EZA_CONFIG_DIR' ~/.zshrc 2>/dev/null; then
  echo 'export EZA_CONFIG_DIR="$HOME/.config/eza"' >> ~/.zshrc
  log "Added EZA_CONFIG_DIR to ~/.zshrc"
fi

log "Core bootstrap done; running setup scripts in order…"

################################################################################
# Orchestration: run the remaining setup scripts in order.                     #
# brew_setup is critical (aborts on failure). Desktop/optional steps warn and  #
# continue so one failure never blocks the rest.                               #
################################################################################

SCRIPTS="${0:A:h}/.config/scripts"

# Homebrew Bundle: CLI everywhere; GUI casks on macOS. Non-fatal so one bad
# formula can't block the rest of the setup.
zsh "${SCRIPTS}/brew_setup.zsh" || warn "brew_setup had issues."

# Linux GUI apps + terminals (no-op on macOS). Non-fatal individually.
zsh "${SCRIPTS}/flatpak_setup.zsh" || warn "flatpak_setup had issues."
zsh "${SCRIPTS}/ghostty_setup.zsh" || warn "ghostty_setup had issues."
zsh "${SCRIPTS}/warp_setup.zsh"    || warn "warp_setup had issues."
zsh "${SCRIPTS}/albert_setup.zsh"  || warn "albert_setup had issues."
zsh "${SCRIPTS}/gaming_setup.zsh"  || warn "gaming_setup had issues."

# Nerd Fonts (Linux; macOS uses Brewfile casks). Non-fatal.
zsh "${SCRIPTS}/fonts_setup.zsh"   || warn "fonts_setup had issues."

# Make zsh the default login shell (Linux). Non-fatal.
zsh "${SCRIPTS}/shell_setup.zsh"   || warn "shell_setup had issues."

# DNS over TLS (systemd-resolved on Linux; skipped on macOS). Non-fatal.
zsh "${SCRIPTS}/dns_setup.zsh"     || warn "dns_setup had issues."

# GNOME desktop tweaks: Dash to Dock + Tiling Shell (Linux GNOME only). Non-fatal.
zsh "${SCRIPTS}/gnome_setup.zsh"   || warn "gnome_setup had issues."

# Neovim: sync the stowed LazyVim config in place (never clobbers it). Non-fatal.
zsh "${SCRIPTS}/nvim_setup.zsh"    || warn "nvim_setup had issues."

# Post-bootstrap sanity checks.
zsh "${SCRIPTS}/post_bootstrap_checks.zsh" || true

log "Bootstrap complete."
