# dotfiles

Personal repo for setting up Linux or Mac to be a relatively reproducible environment for DevOps tooling utilising a shell script and nixpkgs.  

```
    .config  - Modern .config files for neovim, nixpgkgs, Starship and NuShell  
      hammerspoons - OS customisations.  
      k9s          - Kubernetes TUI.  
      nixpgkgs     - Nix package manager config.  
      nushell      - NuShell configuration  
      nvim         - AstroVim with customisations.  
      starship     - Starship config.  
    wsl      - Config for Ubuntu on WSL.  
    .zshrc   - For ZSH.  
    brewfile - For Homebrew.  
    setup.sh - Setup script.  
```

Source this script and run `zsh ~/repos/personal/dotfiles/setup.sh`  
This will perform the following actions:   

```
install_git
setup_git_and_ssh
install_nix
install_nix_darwin
create_directories
clone_dotfiles
clone_eza_themes
install_astrovim
create_symlinks
install_home_manager
apply_home_manager
install_nu_plugins
```  

Once inside Neovim, handle LSP and linter installation using :LspInstall  
