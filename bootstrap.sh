#!/usr/bin/env sh
# Fresh machine: ensure Homebrew and uv, then run the bootstrap package.
#   sh ~/repos/personal/dotfiles/bootstrap.sh
set -eu

log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
err() { printf '\033[1;31mERROR:\033[0m %s\n' "$*"; }

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)

for prefix in /opt/homebrew /usr/local /home/linuxbrew/.linuxbrew "$HOME/.linuxbrew"; do
  if [ -x "$prefix/bin/brew" ]; then
    eval "$("$prefix/bin/brew" shellenv)"
    break
  fi
done

if ! command -v brew >/dev/null 2>&1; then
  log "Installing Homebrew…"
  NONINTERACTIVE=1 /bin/bash -c \
    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  for prefix in /opt/homebrew /home/linuxbrew/.linuxbrew; do
    if [ -x "$prefix/bin/brew" ]; then
      eval "$("$prefix/bin/brew" shellenv)"
      break
    fi
  done
fi

PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH

if ! command -v uv >/dev/null 2>&1; then
  log "Installing uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  for prefix in "$HOME/.local/bin" "$HOME/.cargo/bin"; do
    [ -x "$prefix/uv" ] && PATH="$prefix:$PATH" && export PATH && break
  done
fi

command -v uv >/dev/null 2>&1 || { err "uv install failed"; exit 1; }
log "Starting the bootstrap via uv…"
exec uv run --python 3.13 python -m dotfiles "$@"
