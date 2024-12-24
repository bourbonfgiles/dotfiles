{ config, pkgs, ... }:

{
  # User information
  home.username = "giles";
  home.homeDirectory = "/home/giles";
  home.stateVersion = "24.11";  

  # Packages to be installed in the user's environment
  home.packages = with pkgs; [
    bat
    carapace
    cargo
    curl
    direnv
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
    kubectl
    lazydocker
    lazygit
    lua
    neovim
    nodejs
    nushell
    opentofu
    pre-commit
    python3
    ripgrep
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

  # Dock settings for macOS
  programs.dock.enable = true;
  programs.dock.settings = {
    autohide = false;  
    magnification = true;  
    tilesize = 36;  
    largesize = 64;  
    orientation = "bottom";  
    persistent-apps = [  
      "Spotify"
      "Safari"
      "iTerm2"
      "Docker"
      "Calendar"
      "Outlook"
      "Teams"
    ];
  };

  # Environment variables for iTerm2
  home.sessionVariables = {
    TERMINAL = "iterm2";  
    TERM_PROGRAM = "iTerm.app";  
  };

  # Directories to include in the PATH environment variable
  home.sessionPath = [
    "/run/current-system/sw/bin"
    "$HOME/.nix-profile/bin"
  ];
 
  # Enable Home Manager
  programs.home-manager.enable = true;

  # Zsh configuration
  programs.zsh = {
    enable = true;  
    initExtra = ''
      # Additional configurations for Zsh
      export PATH=/run/current-system/sw/bin:$HOME/.nix-profile/bin:$PATH
      if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
        . '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
      fi
    '';
  };

  # Create symlink for Alfred
  home.activation.createAlfredSymlink = lib.mkAfter {
    description = "Create symlink for Alfred";
    script = ''
      ln -sf /opt/homebrew/Caskroom/alfred/*/Alfred.app /Applications/Alfred.app
    '';
  }

  # Nushell configuration
  programs.nushell = {
    enable = true;   
    initExtra = ''
      # Additional configurations for Nushell
      let-env PATH = "$env.PATH:/run/current-system/sw/bin:$HOME/.nix-profile/bin"
      if test -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh {
        source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
      }
    '';
  };

  # Set Nushell as the default shell for iTerm2
  home.activation.setNushellAsDefault = lib.mkAfter {
    description = "Set Nushell as the default shell for iTerm2";
    script = ''
      chsh -s $(which nu)
    '';
  };

  # iTerm2 Quake mode configuration
  programs.iterm2 = {
    enable = true;  
    settings = {
      "New Bookmarks" = [
        {
          "Guid" = "00000000-0000-0000-0000-000000000000";  
          "Name" = "Hotkey Window";  
          "Shortcut" = "Ctrl-`";  
          "Window Type" = "Hotkey";  
          "Screen" = "Screen with Cursor";  
          "Space" = "All Spaces";  
          "Style" = "Full-Width Top of Screen";  
          "Tab Bar" = true;  
        }
      ];
    };
  };
}
