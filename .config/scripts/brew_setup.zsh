#!/usr/bin/env zsh
set -euo pipefail

BREWFILE="${HOME}/repos/personal/dotfiles/brewfile"

# Ensure brew is on PATH in non-login shells (quietly; not all prefixes exist).
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$(~/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true

# Homebrew 6.0 refuses formulae from third-party taps until they are trusted.
# Trust every tap declared in the Brewfile so `brew bundle` can install them.
echo "Trusting third-party taps from the Brewfile…"
grep -E '^[[:space:]]*tap[[:space:]]+"' "$BREWFILE" \
  | sed -E 's/.*tap[[:space:]]+"([^"]+)".*/\1/' \
  | while read -r _tap; do
      brew trust "$_tap" >/dev/null 2>&1 || true
    done

echo "Running brew bundle…"
brew bundle --file "$BREWFILE"
echo "brew bundle complete."
# Brew Bundle supports flatpak DSL in Brewfiles (docs).
