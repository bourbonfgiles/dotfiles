# home.nix

{ config, pkgs, ... }:

{
  # Home Manager configuration
  imports = [
    <home-manager/nixos>
  ];

  home.packages = with pkgs; [
    bat
    carapace
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
    "alfred"
    # Add other macOS native apps here
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
}
