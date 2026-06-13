#!/usr/bin/env sh
# Fresh-machine entry point. POSIX sh runs on every target (macOS, Bazzite,
# Silverblue) before anything else is installed. Its only jobs are to make sure
# Homebrew and Python 3 exist, then hand off to the Python bootstrap package
# which does all the real work.
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

# Python 3: prefer an interpreter already present, else install via Homebrew.
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  log "Installing Python via Homebrew…"
  brew install python
  PYTHON=python3
fi

command -v "$PYTHON" >/dev/null 2>&1 || { err "Python 3 unavailable after install."; exit 1; }

log "Starting the Python bootstrap ($("$PYTHON" --version 2>&1))…"
# Run the package straight from the source tree; no install step required.
PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH
exec "$PYTHON" -m dotfiles "$@"
