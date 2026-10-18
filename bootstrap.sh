#!/usr/bin/env sh
# Fresh-machine entry point. POSIX sh runs on every target (macOS, Bazzite,
# Silverblue) before anything else is installed. Its only jobs are to make sure
# Homebrew and uv exist, then hand off to the bootstrap package (run through uv,
# which supplies its own Python) which does all the real work.
#
# Usage:
#   sh ~/repos/personal/dotfiles/bootstrap.sh
set -eu

log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
err() { printf '\033[1;31mERROR:\033[0m %s\n' "$*"; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# Put an existing Homebrew on PATH (mac: /opt/homebrew or Intel /usr/local;
# Linux: /home/linuxbrew or ~/.linuxbrew).
for prefix in /opt/homebrew /usr/local /home/linuxbrew/.linuxbrew "$HOME/.linuxbrew"; do
  if [ -x "$prefix/bin/brew" ]; then
    eval "$("$prefix/bin/brew" shellenv)"
    break
  fi
done

# Install Homebrew on a fresh machine, then reload its shellenv.
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

# Interpreter: run the stdlib-only bootstrap package with uv, which manages its
# own Python (downloading one if the host has none). uv is the single Python
# toolchain across every target; a system python3 is only a last-resort fallback.
PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH

if ! command -v uv >/dev/null 2>&1; then
  log "Installing uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  for prefix in "$HOME/.local/bin" "$HOME/.cargo/bin"; do
    [ -x "$prefix/uv" ] && PATH="$prefix:$PATH" && export PATH && break
  done
fi

if command -v uv >/dev/null 2>&1; then
  log "Starting the bootstrap via uv…"
  exec uv run --python 3.13 python -m dotfiles "$@"
fi

# Fallback: no uv and its install failed — use any system python3.
if command -v python3 >/dev/null 2>&1; then
  log "uv unavailable; falling back to system python3…"
  exec python3 -m dotfiles "$@"
fi

err "Neither uv nor python3 is available to run the bootstrap."
exit 1
