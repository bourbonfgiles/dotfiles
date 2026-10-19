"""Policy data for the bootstrap: lists, URLs, and version pins.

Values most likely to change over time (a new repo to clone, a bumped
extension tag, another font), kept in one place so there is one obvious edit
point and tests can assert against a single source. Plain stdlib only.
"""

from __future__ import annotations

# (clone URL, destination relative to $HOME)
REPOS: tuple[tuple[str, str], ...] = (
    ("git@github.com:bourbonfgiles/dotfiles.git", "repos/personal/dotfiles"),
    ("git@github.com:bourbonfgiles/kube_local.git", "repos/personal/kube_local"),
    ("https://github.com/eza-community/eza-themes.git", "repos/personal/eza-themes"),
    ("https://github.com/syl20bnr/spacemacs.git", ".emacs.d"),
)

GNOME_EXT_DASH = "dash-to-dock@micxgx.gmail.com"
GNOME_EXT_TILING = "tilingshell@ferrarodomenico.com"
GNOME_EXT_FOCUS = "steal-my-focus-window@steal-my-focus-window"
# Build-from-source fallback tag; bump when a newer release supports a newer GNOME.
TILINGSHELL_TAG = "v18.0"
TILINGSHELL_REPO = "https://github.com/domferr/tilingshell.git"

NERD_FONTS: tuple[str, ...] = ("JetBrainsMono",)
NERD_FONTS_RELEASE = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download"

# Tools expected on PATH after a successful run.
CORE_TOOLS: tuple[str, ...] = (
    "git",
    "chezmoi",
    "zsh",
    "nvim",
    "starship",
    "eza",
    "zoxide",
    "fzf",
    "rg",
    "fd",
    "bat",
)
# kubectl plugins installed through krew: RBAC access matrices.
KREW_PLUGINS: tuple[str, ...] = ("access-matrix", "rbac-tool")
# ~/.config/<name> directories expected after chezmoi apply.
LINKED_CONFIGS: tuple[str, ...] = ("nvim", "ghostty", "starship", "k9s", "k3d")
