#!/usr/bin/env bash
set -euo pipefail

# Ensure brew is on PATH in non-login shells
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(~/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true

echo "Running brew bundle…"
brew bundle --file "${HOME}/repos/personal/dotfiles/Brewfile"
echo "brew bundle complete."
# Brew Bundle supports flatpak DSL in Brewfiles (docs).
