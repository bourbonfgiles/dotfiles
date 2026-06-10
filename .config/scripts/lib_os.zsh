#!/usr/bin/env zsh
# Platform-detection helpers shared by the setup scripts.
#
# os_kind prints exactly one of:
#   mac            - macOS
#   bazzite        - Bazzite (atomic Fedora, gaming stack built in)
#   fedora-atomic  - other rpm-ostree atomic Fedora (Silverblue/Kinoite/...)
#   linux          - any other Linux
#   unknown        - anything else

os_kind() {
  case "$(uname -s)" in
    Darwin) printf '%s\n' "mac"; return ;;
    Linux)  ;;
    *)      printf '%s\n' "unknown"; return ;;
  esac

  if [[ -r /etc/os-release ]] && grep -qi 'bazzite' /etc/os-release; then
    printf '%s\n' "bazzite"; return
  fi
  if [[ -f /run/ostree-booted ]]; then
    printf '%s\n' "fedora-atomic"; return
  fi
  printf '%s\n' "linux"
}

is_mac()           { [[ "$(uname -s)" == "Darwin" ]]; }
is_linux()         { [[ "$(uname -s)" == "Linux" ]]; }
is_bazzite()       { [[ "$(os_kind)" == "bazzite" ]]; }
is_fedora_atomic() { [[ -f /run/ostree-booted ]]; }   # true on Bazzite too
