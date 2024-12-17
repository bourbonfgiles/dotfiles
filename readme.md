# dotfiles

Personal repo (open to all), for setting up Linux or Mac to be a relatively reproduceable environment for DevOps tooling.  

Structure:  
    .config  - Modern .config files for `LunarVim`, `nixpgkgs`, `Starship` and `NuShell`  
    nvim     - Own customised version of `neovim`. Superseded by `LunarVim`.  
    wsl      - Config for Ubuntu on WSL.  
    .zshrc   - For ZSH, now superseded by NuShell.  
    brewfile - For Homebrew, now superseded by nixpgkgs.  

Making use of Nix package manager to do the bulk of the work:  
  `xcode-select --install`  
  `sh <(curl -L https://nixos.org/nix/install)`  
  `nix-channel --add https://github.com/nix-community/home-manager/archive/release-23.05.tar.gz home-manager`  
  `nix-channel --update`  
  `nix-shell '<home-manager>' -A install`  
  `home-manager switch` #Grabs your .conf  
  
Once nixpgkgs has installed the contents of home.nix, copy the .config files for `LunarVim`, `Starship`, and `NuShell`.  

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
  
Configure the eza theme: `ln -sf "/home/giles/repos/personal/eza-themes/themes/tokyonight.yml" ~/.config/eza/theme.yml`  
  
For terminal history, grab atuin via package manager and run `mkdir ~/.local/share/atuin/` followed by `atuin init nu | save ~/.local/share/atuin/init.nu`.  
Then add `source ~/.local/share/atuin/init.nu` to your `config.nu`

Grab anything on the GUI.  
