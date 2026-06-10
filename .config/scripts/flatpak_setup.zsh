#!/usr/bin/env zsh
set -uo pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h:h}"
source "${SCRIPT_DIR}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

if is_mac; then
  log "macOS: GUI apps come from Brewfile casks; skipping Flatpaks."
  exit 0
fi
if ! is_linux; then
  warn "Unsupported OS for Flatpak setup; skipping."
  exit 0
fi
if ! command -v flatpak >/dev/null 2>&1; then
  warn "flatpak not found; skipping Flatpak setup."
  exit 0
fi

LIST="${REPO_ROOT}/flatpaks"
if [[ ! -r "$LIST" ]]; then
  warn "Flatpak list not found at $LIST; skipping."
  exit 0
fi

# User-scoped Flathub remote so installs need no root/polkit.
flatpak remote-add --if-not-exists --user flathub \
  https://flathub.org/repo/flathub.flatpakrepo >/dev/null 2>&1 || true

typeset -a failed
log "Installing Flatpaks from $(basename "$LIST")..."
while IFS= read -r line; do
  app="${line%%#*}"            # strip inline comment
  app="${app//[[:space:]]/}"  # trim whitespace
  [[ -z "$app" ]] && continue

  if flatpak info "$app" >/dev/null 2>&1; then
    log "already installed: $app"
    continue
  fi

  log "installing: $app"
  if ! flatpak install --user --noninteractive --or-update flathub "$app"; then
    warn "failed: $app"
    failed+=("$app")
  fi
done < "$LIST"

if (( ${#failed} )); then
  warn "Flatpaks that did not install: ${failed[*]}"
fi
log "Flatpak setup complete."
