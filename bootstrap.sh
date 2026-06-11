#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Fresh-machine entry point.                                                   #
#                                                                              #
# A zsh script cannot install zsh before zsh exists, so this thin bash wrapper #
# guarantees Homebrew + zsh are present and then hands off to bootstrap.zsh,   #
# which orchestrates the rest of the setup.                                    #
#                                                                              #
# Usage (Linux or macOS):                                                      #
#   bash ~/repos/personal/dotfiles/bootstrap.sh                                #
################################################################################

log() { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
err() { printf "\033[1;31mERROR:\033[0m %s\n" "$*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Homebrew on PATH (macOS + Linux). Harmless if a given prefix does not exist.
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
eval "$("${HOME}/.linuxbrew/bin/brew" shellenv 2>/dev/null)" 2>/dev/null || true

# Install Homebrew on a fresh machine, then reload its shellenv.
if ! command -v brew >/dev/null 2>&1; then
  log "Installing Homebrew…"
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" 2>/dev/null || true
fi

command -v brew >/dev/null 2>&1 || { err "Homebrew is unavailable after install."; exit 1; }

# zsh is required to run bootstrap.zsh; install it via Homebrew if missing.
# (macOS ships zsh; Bazzite/Silverblue do not.)
if ! command -v zsh >/dev/null 2>&1; then
  log "Installing zsh via Homebrew…"
  brew install zsh
fi

ZSH_BIN="$(command -v zsh)"
log "Handing off to bootstrap.zsh (${ZSH_BIN})…"
exec "${ZSH_BIN}" "${SCRIPT_DIR}/bootstrap.zsh" "$@"
