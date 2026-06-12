#!/usr/bin/env zsh
set -uo pipefail

source "${0:A:h}/lib_os.zsh"

log()  { printf "\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33mWARN:\033[0m %s\n" "$*"; }

# Albert (keyboard launcher) is Linux-only and NOT on Flathub. On atomic Fedora
# we layer the maintainer's openSUSE Build Service (OBS) repo with rpm-ostree,
# mirroring warp_setup.zsh. OBS frequently lags new Fedora releases, so the
# install may fail until builds exist (handled non-fatally).
# refs: https://albertlauncher.github.io/installing/

OBS_BASE="https://download.opensuse.org/repositories/home:/manuelschneid3r"
REPO_FILE="/etc/yum.repos.d/home:manuelschneid3r.repo"

obs_target() {
  . /etc/os-release 2>/dev/null
  local v="${VERSION_ID:-40}"
  # OBS often has no build for a brand-new Fedora; fall back to Rawhide.
  if (( v >= 44 )); then
    printf 'Fedora_Rawhide'
  else
    printf 'Fedora_%s' "$v"
  fi
}

write_repo() {
  local base="$1"
  sudo tee "$REPO_FILE" >/dev/null <<EOF
[home_manuelschneid3r]
name=home_manuelschneid3r
baseurl=${base}
enabled=1
gpgcheck=1
gpgkey=${base}repodata/repomd.xml.key
EOF
}

case "$(os_kind)" in
  mac)
    log "macOS: Albert is Linux-only (use Raycast/Alfred); skipping."
    ;;

  bazzite|fedora-atomic)
    target="$(obs_target)"
    base="${OBS_BASE}/${target}/"
    if [[ ! -f "$REPO_FILE" ]]; then
      log "Adding Albert's OBS repo (${target})…"
      # No `rpm --import` here: the rpmdb is read-only on rpm-ostree, and the key
      # is referenced via gpgkey= in the repo file, so rpm-ostree imports it.
      write_repo "$base"
    else
      log "Albert repo already present."
    fi

    rpm-ostree refresh-md >/dev/null 2>&1 || true

    if rpm -q albert >/dev/null 2>&1; then
      # Already installed. If it is a hand-installed LOCAL package, migrate it to
      # the repo-tracked package so future updates come from the repo.
      if rpm-ostree status 2>/dev/null | grep -q 'LocalPackages:.*albert'; then
        log "Migrating Albert from a local RPM to the repo-tracked package…"
        if sudo rpm-ostree uninstall albert && sudo rpm-ostree install albert; then
          log "Albert migrated. Reboot to finish: systemctl reboot"
        else
          warn "Albert migration failed (see output above)."
          exit 1
        fi
      else
        log "Albert already layered from the repo; nothing to do."
      fi
      exit 0
    fi

    log "Layering Albert (rpm-ostree). A reboot is needed to use it."
    if sudo rpm-ostree install --idempotent albert; then
      log "Albert layered. Reboot to finish: systemctl reboot"
    else
      warn "rpm-ostree install albert failed — OBS may not build for ${target} yet."
      exit 1
    fi
    ;;

  *)
    # Non-atomic Fedora / RHEL / openSUSE: same official repo via dnf.
    if command -v dnf >/dev/null 2>&1; then
      target="$(obs_target)"
      base="${OBS_BASE}/${target}/"
      [[ -f "$REPO_FILE" ]] || { log "Adding Albert's OBS repo (dnf, ${target})…"; write_repo "$base"; }
      sudo dnf -y install albert || warn "dnf install albert failed (OBS may not build for ${target})."
    else
      warn "No known Albert install path here; see https://albertlauncher.github.io/installing/"
    fi
    ;;
esac
