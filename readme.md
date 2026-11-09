# Dotfiles

One chezmoi setup for macOS, Bazzite and Fedora Silverblue.

## Model

- **Home files → chezmoi** (`home/` source state via `.chezmoiroot`).
- **CLI tools → Homebrew** (`brewfile`), shared across targets with small per-OS sections.
- **GUI apps → Homebrew Casks on macOS, native Flatpak on Linux** (`flatpaks`).
- **Ghostty, Albert, BPF tools** → Homebrew cask (Ghostty) on macOS; the os_build image on Linux.
- **Gaming** → native on Bazzite; Flatpaks (`flatpaks-gaming`) on Silverblue.
- **Containers** → Apple `container` and brew Podman on macOS; the OS's own `podman` on Linux. k3d uses rootful Podman on both.
- **Local Kubernetes** → a 4-node k3d cluster on rootful Podman, empty until the `kube_local` repo bootstraps it. See [kubernetes.md](kubernetes.md).
- **kubectl plugins** → `30-krew` installs `access-matrix` and `rbac-tool` for reading RBAC from the terminal.
- **Linux system config** → the [os_build](https://github.com/bourbonfgiles/os_build) image: DNS over TLS, and k3d's rootful `podman.socket`, logging and `kube.internal` DNS. dotfiles only writes `$HOME` there, plus one `nmcli` setting.
- **GNOME desktop** → Dash to Dock + Tiling Shell on Linux from `dconf/`, no suspend on AC (the KVM keyboard dies after resume); Hammerspoon on macOS.

Flatpak **overrides** are applied by chezmoi under `~/.local/share/flatpak/overrides/`.

## Quick start

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/bourbonfgiles/dotfiles/master/bootstrap.sh)"
```

`bootstrap.sh` installs Homebrew, git and chezmoi, then `chezmoi init --apply` clones this repo to
`~/repos/personal/dotfiles`, saves where the repo is in `~/.config/chezmoi/chezmoi.toml`, and applies everything. After that:

```bash
chezmoi diff     # what would change, scripts included
chezmoi apply
```

## Setup scripts

`home/.chezmoiscripts/`, in name order after files are written.

| Script | OS | Does | Runs again when |
| --- | --- | --- | --- |
| `05-github` | all | SSH key (waits while you add it to GitHub), SSH remote for this repo, clones `kube_local` | never |
| `10-brew` | all | Trusts the taps, `brew bundle` | `brewfile` changes |
| `20-flatpaks` | Linux | Installs `flatpaks`, plus `flatpaks-gaming` off Bazzite; skips apps already installed system-wide | a list changes |
| `30-krew` | all | `access-matrix`, `rbac-tool` | the script changes |
| `40-gnome` | Linux | Enables Dash to Dock, Tiling Shell and Steal My Focus; loads `dconf/`; Albert on Super+Space; fast key repeat; no suspend on AC | `dconf/` changes |
| `50-fonts` | Linux | JetBrainsMono Nerd Font (macOS uses casks) | never |
| `60-neovim` | all | `Lazy! restore` | `lazy-lock.json` changes |
| `70-login-shell` | Linux | brew zsh in `/etc/shells` and as the login shell (`sudo`) | never |
| `80-dns` | macOS, Linux | macOS: Cloudflare DoT profile to approve. Linux: wired connections ignore the router's DNS (`sudo`) | never |
| `90-podman-machine` | macOS | Rootful 8 GB Podman machine for k3d | never |

To run a `run_once_` script again, `chezmoi state delete-bucket --bucket=scriptState`, then `chezmoi apply`.

## Chezmoi layout

`.chezmoiroot` → `home/`:

```
home/
  dot_zshrc              → ~/.zshrc
  dot_gitconfig.tmpl     → ~/.gitconfig   (from .chezmoidata.toml)
  dot_config/…           → ~/.config/…
  dot_local/share/flatpak/overrides/… → flatpak overrides
  dot_config/eza/theme.yml → ~/.config/eza/theme.yml (Smyck)
```

Git identity:

- **Personal** (committed): `home/.chezmoidata.toml` → global `~/.gitconfig`
- **Work** (work machines only, not in git): add `[data.git.work]` `name` and `email` to `~/.config/chezmoi/chezmoi.toml` by hand; `chezmoi init` keeps them. That writes `~/.config/git/config-work`, included only for `~/repos/vitalhub/` via `includeIf`.

## Repository structure

```
home/                 Chezmoi source state
  .chezmoiscripts/    Setup scripts
brewfile              Homebrew packages
flatpaks*             Flathub app ID lists
dconf/                GNOME extension dconf
bootstrap.sh          Fresh-machine entry
```

## Notes (Bazzite / Silverblue)

- chezmoi only writes `$HOME` — install via Homebrew.
- Plain Silverblue lacks what the os_build image adds (DNS over TLS, the k3d socket); rebase onto it or add them by hand.
- Neovim config is chezmoi-managed; `60-neovim` only restores plugins. Neovide's Flatpak sandbox links to `~/.config/nvim`. lazy.nvim's luarocks support is off (its Lua build needs readline headers Bazzite lacks); plugins that ship rockspecs get their dependencies as ordinary plugins instead.

## Notes (brew on macOS)

Tap installs such as `brew install hashicorp/tap/*` can fail with `could not read Username for 'https://github.com'`: brew's git has no stored GitHub credential and won't prompt. Make brew's git (only) use SSH:

```ini
# /opt/homebrew/etc/gitconfig (Linuxbrew: /home/linuxbrew/.linuxbrew/etc/gitconfig)
[credential]
    helper = osxkeychain

[url "git@github.com:"]
    insteadOf = https://github.com/
```

## Ghostty

Config is split under `home/dot_config/ghostty/`:

- `config` — includes the fragments
- `appearance` (Smyck) / `input` / `quake` / `platform`
- `quake` is a template: the quick terminal (``cmd+` ``) on macOS only, because GNOME has no wlr-layer-shell.
