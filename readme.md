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

Making use of Nix package manager to do the bulk of the work:  
  ```
  xcode-select --install   
  sh <(curl -L https://nixos.org/nix/install)   
  nix-channel --add https://github.com/nix-community/home-manager/archive/release-23.05.tar.gz home-manager  
  nix-channel --update  
  nix-shell <home-manager> -A install  
  home-manager switch
  ``` 

Run `zsh ~/repos/personal/dotfiles/setup.sh` in order to auth to git, gen an SSH key and create your config.

To get `NuShell` plug-ins working, perform the following:  
```
 [ nu_plugin_inc  
  nu_plugin_polars  
  nu_plugin_gstat  
  nu_plugin_formats  
  nu_plugin_query  
] | each { cargo install $in --locked } | ignore
```  

Once done, check in `~/.cargo/bin/`  

From here you can run `plugin add ~/.cargo/bin/nu_plugin_gstat`.  
If you run into issues with `libgit2.so.1.8`, just curl and compile the version showing in the error. 

Once inside Neovim, handle LSP and linter installation using :LspInstall  

Configure the eza theme:  
`ln -sf "/home/giles/repos/personal/eza-themes/themes/tokyonight.yml" ~/.config/eza/theme.yml`  
