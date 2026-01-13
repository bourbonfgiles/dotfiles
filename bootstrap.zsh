#!/usr/bin/env zsh
set -euo pipefail

# Logs
log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31mERROR:\033[0m %s\n" "$*"; }

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

eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(~/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true

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

read "email?Enter your GitHub email: "
read "username?Enter your GitHub username: "
git config --global user.email "$email"
git config --global user.name "$username"
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
  elif $IS_LINUX && command -v xclip >/dev/null 2>&1; then
    xclip -selection clipboard < ~/.ssh/id_ed25519.pub
    log "SSH public key copied to clipboard (Linux)."
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

log "Bootstrap complete."
