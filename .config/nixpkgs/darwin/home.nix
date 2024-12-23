# darwin/home.nix

{ config, pkgs, ... }:

{
  # Home Manager configuration
  imports = [
    <home-manager/nixos>
  ];

  home.packages = with pkgs; [
    bat
    carapace
    cargo
    curl
    direnv
    dockly
    eza
    fzf
    gh
    git
    glances
    go
    helm
    helmfile
    htop
    ipcalc
    jq
    k9s
    kubecm
    kubernetes-cli
    lazydocker
    lazygit
    lua
    make
    neovim
    nodejs
    nushell
    opentofu
    pre-commit
    python3
    ripgrep
    rust
    starship
    stow
    terraform
    terraform-docs
    tldr
    typescript
    unzip
    yank
    yarn
    yazi
    zip
  ];

  # Homebrew taps
  homebrew.taps = [
    "azure/kubelogin"
    "cloudflare/cloudflare"
    "homebrew/bundle"
    "idoavrah/homebrew"
    "jandedobbeleer/oh-my-posh"
    "julien-cpsn/atac"
    "mk-5/mk-5"
    "vladimirvivien/oss-tools"
  ];

  # Homebrew packages managed via Nix
  homebrew.packages = [
    "azure/kubelogin/kubelogin"
    "cloudflare/cloudflare/cf-terraforming"
    "idoavrah/homebrew/tftui"
    "jandedobbeleer/oh-my-posh/oh-my-posh"
    "julien-cpsn/atac/atac"
    "mk-5/mk-5/fjira"
    "vladimirvivien/oss-tools/ktop"
  ];

  # macOS native apps
  homebrew.casks = [
    "alfred",
    "docker",
    "iterm2",
    "signal",
    "slack",
    "spotify"
  ];

  # Create symlink for Alfred
  home.activation = {
    createAlfredSymlink = lib.mkAfter {
      description = "Create symlink for Alfred";
      script = ''
        ln -sf /opt/homebrew/Caskroom/alfred/*/Alfred.app /Applications/Alfred.app
      '';
    };
  };

  # Dock settings
  programs.dock.enable = true;
  programs.dock.settings = {
    autohide = false;
    magnification = true;
    tilesize = 36;
    largesize = 64;
    orientation = "bottom";
    persistent-apps = [
      "Spotify",
      "Safari",
      "iTerm2",
      "Docker",
      "Calendar",
      "Outlook",
      "Teams"
    ];
  };

  # Environment variables for iTerm2
  home.sessionVariables = {
    TERMINAL = "iterm2";
    TERM_PROGRAM = "iTerm.app";
  };

  # Set Nushell as the default shell for iTerm2
  home.activation = {
    setNushellAsDefault = lib.mkAfter {
      description = "Set Nushell as the default shell for iTerm2";
      script = ''
        chsh -s $(which nu)
      '';
    };
  };
}
