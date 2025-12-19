#!/usr/bin/env bash
set -euo pipefail

# Backup any existing Neovim config/state (recommended by docs)
mv ~/.config/nvim{,.bak} 2>/dev/null || true
mv ~/.local/share/nvim{,.bak} 2>/dev/null || true
mv ~/.local/state/nvim{,.bak} 2>/dev/null || true
mv ~/.cache/nvim{,.bak} 2>/dev/null || true

# Clone the latest LazyVim starter and detach from upstream history
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git

# First launch will bootstrap plugins
if command -v nvim >/dev/null 2>&1; then
  nvim +qall || true
fi

echo "LazyVim installed. Open Neovim and run ':LazyHealth' to verify."
# refs: LazyVim installation page + starter repository.
