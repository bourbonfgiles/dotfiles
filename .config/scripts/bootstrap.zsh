#!/usr/bin/env zsh
set -euo pipefail

# Resolve repo-relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# 1) Git + SSH + clone + stow + eza theme path
zsh "${REPO_ROOT}/bootstrap.zsh"

# 2) Homebrew Bundle (taps, brew, casks, and flatpaks directly in Brewfile)
zsh "${SCRIPT_DIR}/brew_setup.zsh"

# 3) DNS over TLS configuration (WARP for macOS, systemd-resolved for Linux)
zsh "${SCRIPT_DIR}/dns_setup.zsh"

# 4) LazyVim (fresh runtime install from upstream)
zsh "${SCRIPT_DIR}/lazyvim_setup.zsh"

# 5) Post-bootstrap sanity checks
zsh "${SCRIPT_DIR}/post_bootstrap_checks.zsh"
