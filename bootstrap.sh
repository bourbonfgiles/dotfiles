#!/bin/sh
# Fresh machine: Homebrew, then chezmoi clones this repo and applies it, scripts included.
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/bourbonfgiles/dotfiles/master/bootstrap.sh)"
set -eu

brew_env() {
  for prefix in /opt/homebrew /usr/local /home/linuxbrew/.linuxbrew; do
    if [ -x "$prefix/bin/brew" ]; then
      eval "$("$prefix/bin/brew" shellenv)"
      return
    fi
  done
}

brew_env
if ! command -v brew >/dev/null; then
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew_env
fi
brew install git chezmoi
chezmoi init --apply --source "$HOME/repos/personal/dotfiles" https://github.com/bourbonfgiles/dotfiles.git
