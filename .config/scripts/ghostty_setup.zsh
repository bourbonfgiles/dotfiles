#!/usr/bin/env zsh
set -uo pipefail

source "${0:A:h}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

if command -v ghostty >/dev/null 2>&1; then
  log "Ghostty already installed: $(ghostty --version 2>/dev/null | head -n1)"
  exit 0
fi

case "$(os_kind)" in
  mac)
    log "macOS: Ghostty is installed via the Homebrew cask (see Brewfile)."
    ;;

  bazzite|fedora-atomic)
    # Official method for Fedora Atomic: scottames COPR layered with rpm-ostree.
    # (Ghostty is not on Flathub and has no official Linux Homebrew formula.)
    if rpm -q ghostty >/dev/null 2>&1; then
      log "Ghostty rpm already layered (reboot pending?)."
      exit 0
    fi
    . /etc/os-release
    repo="/etc/yum.repos.d/_copr:copr.fedorainfracloud.org:scottames:ghostty.repo"
    log "Adding scottames/ghostty COPR for Fedora ${VERSION_ID}..."
    curl -fsSL "https://copr.fedorainfracloud.org/coprs/scottames/ghostty/repo/fedora-${VERSION_ID}/scottames-ghostty-fedora-${VERSION_ID}.repo" \
      | sudo tee "$repo" >/dev/null
    log "Layering Ghostty (rpm-ostree). A reboot is needed to use it."
    rpm-ostree refresh-md >/dev/null 2>&1 || true
    if sudo rpm-ostree install --idempotent ghostty; then
      log "Ghostty layered. Reboot to finish: systemctl reboot"
    else
      warn "rpm-ostree install ghostty failed (see output above)."
      exit 1
    fi
    ;;

  *)
    # Non-atomic Fedora / other distros.
    if command -v dnf >/dev/null 2>&1; then
      log "Fedora (non-atomic): enabling scottames/ghostty COPR via dnf..."
      sudo dnf -y copr enable scottames/ghostty || true
      sudo dnf -y install ghostty || warn "dnf install ghostty failed."
    else
      warn "No known Ghostty install path here; see https://ghostty.org/docs/install."
    fi
    ;;
esac
