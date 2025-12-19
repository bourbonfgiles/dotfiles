#!/usr/bin/env bash
set -euo pipefail

echo "[check] brew …" && brew --version
echo "[check] git …" && git --version
echo "[check] stow …" && stow --version
echo "[check] neovim …" && nvim --version | head -n1
echo "[check] eza …" && eza --version

# Flatpak presence (Linux)
if [[ "$(uname -s)" == "Linux" ]]; then
  echo "[check] flatpak …" && flatpak --version
fi

echo "All good!"
