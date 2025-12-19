#!/usr/bin/env bash
set -euo pipefail

# Resolve repo-relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 1) Git + SSH + clone + stow + eza theme path
zsh "${REPO_ROOT}/bootstrap.zsh"

# 2) Homebrew Bundle (taps, brew, casks, and flatpaks directly in Brewfile)
bash "${SCRIPT_DIR}/brew_setup.sh"

# 3) LazyVim (fresh runtime install from upstream)
bash "${SCRIPT_DIR}/lazyvim_setup.sh"

# 4) Post-bootstrap sanity checks
bash "${SCRIPT_DIR}/post_bootstrap_checks.sh"
