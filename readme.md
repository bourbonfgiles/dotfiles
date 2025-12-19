################################################################################

# Dotfiles

################################################################################

This repository provides a reproducible setup for **macOS**, **Linux**, and
**Bazzite** environments using:

- **Homebrew + Brewfile** for CLI tools, macOS casks, and Flatpaks
- **Bootstrap scripts** for Git/SSH setup, dotfiles cloning, and symlink management
- **LazyVim** for a modern Neovim experience (optional)

---

################################################################################

# What You Get

################################################################################

✔ Automated Git + SSH key setup (ed25519, GitHub-ready)  
✔ Dotfiles cloned and symlinked via GNU Stow  
✔ Unified eza theme configuration across macOS and Linux  
✔ Homebrew taps, CLI tools, macOS casks, and Flatpaks installed declaratively  
✔ Optional LazyVim installation for Neovim  
✔ Post-bootstrap sanity checks for critical tools  

---

################################################################################

# Quick Start

################################################################################

Clone the repo and run the orchestrator script:

```bash
git clone git@github.com:bourbonfgiles/dotfiles.git ~/repos/personal/dotfiles
bash ~/repos/personal/dotfiles/scripts/bootstrap.sh
```

This will:

- Configure Git & SSH keys
- Clone dotfiles and eza-themes
- Create symlinks via GNU Stow
- Normalize eza theme path across macOS/Linux
- Install all tools via `brew bundle` (including Flatpaks on Linux)
- Optionally install LazyVim for Neovim
- Run post-bootstrap checks

---

################################################################################

# Repository Structure

################################################################################

```
    .config    - Modern configs for Neovim (LazyVim), Starship, etc.
      hammerspoons - macOS customisations
      k9s          - Kubernetes TUI
      nvim         - LazyVim starter + customisations
      starship     - Starship prompt config
    .zshrc     - ZSH configuration
    Brewfile   - Homebrew taps, formulae, casks, and Flatpaks
    bootstrap.zsh - Core bootstrap (Git, SSH, clone, stow)
    scripts/
      bootstrap.sh          - Orchestrator (calls all sub-scripts)
      brew_setup.sh         - Runs `brew bundle` against Brewfile
      lazyvim_setup.sh      - Installs LazyVim fresh from upstream
      post_bootstrap_checks.sh - Sanity checks after setup
```

---

################################################################################

# Brewfile Overview

################################################################################

Your Brewfile installs:

- **Taps**: Azure, Cloudflare, custom taps for DevOps tooling
- **CLI Tools**:
  `argocd`, `azure-cli`, `kubectl`, `helm`, `helmfile`, `lazygit`,
  `eza`, `fzf`, `starship`, `ripgrep`, `direnv`, `carapace`, `go`, `node`,
  `python`, `rust`, `terraform-docs`, `pre-commit`, `podman`, `postgresql`, etc.
- **macOS Casks**:
  Alfred, Ghostty, Hammerspoon, Slack, fonts, Postman, Warp, Zoom
- **Flatpaks** (Linux):
  Discord, Firefox, Signal, Spotify, LibreOffice
  *(Gaming apps like Steam/Lutris skipped on Bazzite)*

Run manually if needed:

```bash
cd ~/repos/personal/dotfiles
brew bundle
```

---

################################################################################

# LazyVim Setup (Optional)

################################################################################

If you skip the script, install manually:

```bash
mv ~/.config/nvim{,.bak}
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim
```

Inside Neovim:

```
:LazyHealth
```

---

################################################################################

# Why This Approach?

################################################################################

- **Homebrew** is cross-platform and works seamlessly on macOS and Linux (including Bazzite)
- **brew bundle** supports taps, formulae, casks, and Flatpaks in one declarative file
- **Scripts call scripts** for modularity and reproducibility
- **LazyVim** provides a modern Neovim experience with minimal manual setup
- **GNU Stow** ensures safe, reversible symlink management for dotfiles
