#!/usr/bin/env zsh
set -euo pipefail

###############################################################################
# Dotfiles Health Check
# Verifies current system state matches expected dotfiles configuration
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

OS="$(uname -s)"
IS_MAC=false
IS_LINUX=false

case "$OS" in
  Darwin) IS_MAC=true ;;
  Linux)  IS_LINUX=true ;;
esac

pass() { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
info() { echo -e "${BLUE}ℹ${NC} $*"; }

ISSUES=0

echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Dotfiles Health Check${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

###############################################################################
# Check Homebrew
###############################################################################
echo -e "${BLUE}[Homebrew]${NC}"
if command -v brew >/dev/null 2>&1; then
  pass "Homebrew installed: $(brew --version | head -n1)"
else
  fail "Homebrew not found"
  ((ISSUES++))
fi

###############################################################################
# Check Core Tools
###############################################################################
echo -e "\n${BLUE}[Core Tools]${NC}"
CORE_TOOLS=(git stow zsh nvim starship eza zoxide fzf rg fd bat btm)

for tool in $CORE_TOOLS; do
  if command -v "$tool" >/dev/null 2>&1; then
    pass "$tool"
  else
    fail "$tool not found"
    ((ISSUES++))
  fi
done

###############################################################################
# Check DevOps Tools
###############################################################################
echo -e "\n${BLUE}[DevOps Tools]${NC}"
DEVOPS_TOOLS=(kubectl helm argocd k9s lazygit lazydocker az gh)

for tool in $DEVOPS_TOOLS; do
  if command -v "$tool" >/dev/null 2>&1; then
    pass "$tool"
  else
    warn "$tool not found (optional)"
  fi
done

###############################################################################
# Check Symlinks
###############################################################################
echo -e "\n${BLUE}[Symlinks]${NC}"

if [[ -L "$HOME/.zshrc" ]]; then
  target=$(readlink "$HOME/.zshrc")
  if [[ "$target" == *"dotfiles/.zshrc"* ]]; then
    pass ".zshrc → $target"
  else
    warn ".zshrc links to unexpected location: $target"
  fi
else
  fail ".zshrc not a symlink"
  ((ISSUES++))
fi

if [[ -d "$HOME/.config/nvim" ]]; then
  if [[ -L "$HOME/.config/nvim" ]] || [[ -d "$HOME/.config/nvim/.git" ]]; then
    pass "nvim config exists"
  else
    warn "nvim config exists but may not be LazyVim"
  fi
else
  fail "nvim config missing"
  ((ISSUES++))
fi

EXPECTED_CONFIGS=(k9s starship)
for config in $EXPECTED_CONFIGS; do
  if [[ -e "$HOME/.config/$config" ]]; then
    pass ".config/$config exists"
  else
    warn ".config/$config missing"
  fi
done

###############################################################################
# Check eza theme
###############################################################################
echo -e "\n${BLUE}[eza Theme]${NC}"

if [[ -n "${EZA_CONFIG_DIR:-}" ]]; then
  pass "EZA_CONFIG_DIR set to: $EZA_CONFIG_DIR"
  
  if [[ -f "$EZA_CONFIG_DIR/theme.yml" ]]; then
    pass "eza theme file exists"
  else
    fail "eza theme file missing at $EZA_CONFIG_DIR/theme.yml"
    ((ISSUES++))
  fi
else
  fail "EZA_CONFIG_DIR not set in environment"
  ((ISSUES++))
fi

###############################################################################
# Check Git Configuration
###############################################################################
echo -e "\n${BLUE}[Git Configuration]${NC}"

GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_BRANCH=$(git config --global init.defaultBranch 2>/dev/null || echo "")

if [[ -n "$GIT_EMAIL" ]]; then
  pass "Git email: $GIT_EMAIL"
else
  fail "Git email not configured"
  ((ISSUES++))
fi

if [[ -n "$GIT_NAME" ]]; then
  pass "Git name: $GIT_NAME"
else
  fail "Git name not configured"
  ((ISSUES++))
fi

if [[ "$GIT_BRANCH" == "main" ]]; then
  pass "Default branch: main"
else
  warn "Default branch not set to 'main' (current: ${GIT_BRANCH:-not set})"
fi

###############################################################################
# Check SSH Keys
###############################################################################
echo -e "\n${BLUE}[SSH Keys]${NC}"

if [[ -f "$HOME/.ssh/id_ed25519" ]]; then
  pass "SSH key exists: id_ed25519"
else
  fail "SSH key missing: id_ed25519"
  ((ISSUES++))
fi

if [[ -f "$HOME/.ssh/id_ed25519.pub" ]]; then
  pass "SSH public key exists"
else
  fail "SSH public key missing"
  ((ISSUES++))
fi

###############################################################################
# Check Shell Configuration
###############################################################################
echo -e "\n${BLUE}[Shell Configuration]${NC}"

if [[ -n "${EDITOR:-}" ]]; then
  pass "EDITOR set to: $EDITOR"
else
  warn "EDITOR environment variable not set"
fi

if [[ -n "${VISUAL:-}" ]]; then
  pass "VISUAL set to: $VISUAL"
else
  warn "VISUAL environment variable not set"
fi

###############################################################################
# macOS Specific Checks
###############################################################################
if $IS_MAC; then
  echo -e "\n${BLUE}[macOS Specific]${NC}"
  
  MACOS_CASKS=(alfred ghostty hammerspoon warp)
  for cask in $MACOS_CASKS; do
    if brew list --cask "$cask" >/dev/null 2>&1; then
      pass "$cask installed"
    else
      warn "$cask not installed (optional)"
    fi
  done
fi

###############################################################################
# Linux Specific Checks
###############################################################################
if $IS_LINUX; then
  echo -e "\n${BLUE}[Linux Specific]${NC}"
  
  if command -v flatpak >/dev/null 2>&1; then
    pass "flatpak installed"
    
    FLATPAKS=(org.mozilla.firefox com.spotify.Client org.openrgb.OpenRGB)
    for pkg in $FLATPAKS; do
      if flatpak list | grep -q "$pkg"; then
        pass "$pkg installed"
      else
        warn "$pkg not installed (optional)"
      fi
    done
  else
    warn "flatpak not found"
  fi
fi

###############################################################################
# Summary
###############################################################################
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
if [[ $ISSUES -eq 0 ]]; then
  echo -e "${GREEN}All critical checks passed!${NC}"
  exit 0
else
  echo -e "${RED}Found $ISSUES critical issue(s)${NC}"
  echo -e "Run: ${YELLOW}zsh ~/repos/personal/dotfiles/.config/scripts/bootstrap.zsh${NC}"
  exit 1
fi
