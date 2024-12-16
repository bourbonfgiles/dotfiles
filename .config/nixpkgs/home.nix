#Install
#nix-shell '<home-manager>' -A install

{ pkgs, ... }:
{
  home.packages = with pkgs; [
    bash-language-server
    carapace
    devhints
    dockerfile-language-server
    dockly
    eza
    git
    go
    helm
    helmfile
    htop
    k9s
    kubecm
    kubelogin
    kubernetes-cli
    lazydocker
    lazygit
    lua
    make
    neovim
    nodejs
    opentofu
    pre-commit
    python3
    rust
    starship
    terraform
    terraform-docs
    terraform-ls
    tldr
    typescript
    unzip
    yaml-language-server
    yank
    yarn
    zoxide
    jq
    fzf
    bat
    ripgrep
    curl
    curlie
    ipcalc
  ];
}

#Activate
#home-manager switch
