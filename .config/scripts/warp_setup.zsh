#!/usr/bin/env zsh
set -uo pipefail

source "${0:A:h}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# Warp is NOT on Flathub, so it is handled here rather than in flatpaks.
# On atomic Fedora we layer the official Warp RPM repo with rpm-ostree, exactly
# like Ghostty's COPR — so updates arrive with the system instead of needing a
# hand-downloaded .rpm.
# refs: https://docs.warp.dev/getting-started/quickstart/installation-and-setup

REPO_FILE="/etc/yum.repos.d/warpdotdev.repo"
KEY_URL="https://releases.warp.dev/linux/keys/warp.asc"
BASE_URL="https://releases.warp.dev/linux/rpm/stable"

write_repo() {
  sudo tee "$REPO_FILE" >/dev/null <<EOF
[warpdotdev]
name=warpdotdev
baseurl=${BASE_URL}
enabled=1
gpgcheck=1
gpgkey=${KEY_URL}
EOF
}

case "$(os_kind)" in
  mac)
    log "macOS: Warp is installed via the Homebrew cask (see Brewfile)."
    ;;

  bazzite|fedora-atomic)
    if [[ ! -f "$REPO_FILE" ]]; then
      log "Adding Warp's official RPM repo…"
      # No `rpm --import` here: the rpmdb is read-only on rpm-ostree, and the key
      # is referenced via gpgkey= in the repo file, so rpm-ostree imports it.
      write_repo
    else
      log "Warp repo already present."
    fi

    rpm-ostree refresh-md >/dev/null 2>&1 || true

    if rpm -q warp-terminal >/dev/null 2>&1; then
      # Already installed. If it is a hand-installed LOCAL package, migrate it to
      # the repo-tracked package so future updates come from the repo. A plain
      # `rpm-ostree install --idempotent` would otherwise leave the local one.
      if rpm-ostree status 2>/dev/null | grep -q 'LocalPackages:.*warp-terminal'; then
        log "Migrating Warp from a local RPM to the repo-tracked package…"
        if sudo rpm-ostree uninstall warp-terminal && sudo rpm-ostree install warp-terminal; then
          log "Warp migrated. Reboot to finish: systemctl reboot"
        else
          warn "Warp migration failed (see output above)."
          exit 1
        fi
      else
        log "Warp already layered from the repo; nothing to do."
      fi
      exit 0
    fi

    log "Layering Warp (rpm-ostree). A reboot is needed to use it."
    if sudo rpm-ostree install --idempotent warp-terminal; then
      log "Warp layered. Reboot to finish: systemctl reboot"
    else
      warn "rpm-ostree install warp-terminal failed (see output above)."
      exit 1
    fi
    ;;

  *)
    # Non-atomic Fedora / RHEL / openSUSE: same official repo via dnf.
    if command -v dnf >/dev/null 2>&1; then
      if [[ ! -f "$REPO_FILE" ]]; then
        log "Adding Warp's official RPM repo (dnf)…"
        sudo rpm --import "$KEY_URL" || true
        write_repo
      fi
      sudo dnf -y install warp-terminal || warn "dnf install warp-terminal failed."
    else
      warn "No known Warp install path here; see https://docs.warp.dev/getting-started/quickstart/installation-and-setup"
    fi
    ;;
esac
