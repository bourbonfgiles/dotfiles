#!/usr/bin/env zsh
set -euo pipefail

# Backwards-compatible shim. The repo-root bootstrap.zsh is now the single
# orchestrator that runs this repo's setup scripts in order. This file just
# forwards to it so the historical path .config/scripts/bootstrap.zsh (and any
# muscle memory) keeps working without running the whole setup twice.
REPO_ROOT="${0:A:h:h:h}"
exec zsh "${REPO_ROOT}/bootstrap.zsh" "$@"
