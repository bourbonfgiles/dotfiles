# dotfiles

Personal repo for setting up Linux or Mac to be a relatively reproducible environment for DevOps tooling utilising a shell script and nixpkgs.  

```
    .config  - Modern .config files for neovim, nixpgkgs, Starship and NuShell  
      nushell - NuShell configuration  
        config.nu - NuShell config  
        env.nu   - NuShell env vars  
      nvim    - AstroVim with customisations.   
    wsl      - Config for Ubuntu on WSL.  
    .zshrc   - For ZSH, now superseded by NuShell.  
    brewfile - For Homebrew, now superseded by nixpgkgs.  
```

Source this script and run `zsh ~/repos/personal/dotfiles/setup.sh`  
This will perform the following actions:   

```
setup_git_and_ssh  
clone_dotfiles  
clone_eza_themes  
install_astrovim  
create_symlinks  
apply_home_manager  
install_nu_plugins 
```  

if/fi statements determine if it's being sourced on Mac or Linux and adjust accordingly.  

Once inside Neovim, handle LSP and linter installation using :LspInstall  
