{ config, pkgs, ... }:

{
  # User information
  home.username = "giles";
  home.homeDirectory = "/home/giles";
  home.stateVersion = "24.11";  # Version of the Home Manager state

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
    autohide = false;  # Dock is always visible
    magnification = true;  # Enable magnification of dock icons
    tilesize = 36;  # Size of dock icons
    largesize = 64;  # Size of magnified dock icons
    orientation = "bottom";  # Position of the dock
    persistent-apps = [  # Apps that will always be in the dock
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
    TERMINAL = "iterm2";  # Set terminal type to iTerm2
    TERM_PROGRAM = "iTerm.app";  # Set terminal program to iTerm2
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
    enable = true;  # Enable Zsh as the default shell
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
    enable = true;  # Enable iTerm2 configuration
    settings = {
      "New Bookmarks" = [
        {
          "Guid" = "00000000-0000-0000-0000-000000000000";  # Unique identifier for the bookmark
          "Name" = "Hotkey Window";  # Name of the bookmark
          "Shortcut" = "Ctrl-`";  # Shortcut to open the hotkey window
          "Window Type" = "Hotkey";  # Type of window
          "Screen" = "Screen with Cursor";  # Screen to display the window on
          "Space" = "All Spaces";  # Display the window in all spaces
          "Style" = "Full-Width Top of Screen";  # Style of the window
          "Tab Bar" = true;  # Enable tabs in the window
        }
      ];
    };
  };
}
