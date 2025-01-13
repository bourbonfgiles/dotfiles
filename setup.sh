#!/bin/zsh

# Function to install Git
install_git() {
  if command -v git >/dev/null 2>&1; then
    echo "Git is already installed. Skipping Git installation."
  else
    echo "Installing Git..."
    xcode-select --install
  fi
}

# Function to set up Git and SSH keys
setup_git_and_ssh() {
  echo "Setting up Git..."
  read "email?Enter your GitHub email: "
  read "username?Enter your GitHub username: "

  git config --global user.email "$email"
  git config --global user.name "$username"
  git config --global push.autosetupremote true

  echo "Git configuration set."

  echo "Setting up SSH keys..."
  if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "$email"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519

    echo "Copy the following SSH key to your GitHub account:"
    cat ~/.ssh/id_ed25519.pub
    read "dummy?Press Enter after adding the SSH key to GitHub..."
  else
    echo "SSH key already exists."
  fi
}

# Function to install Nix
install_nix() {
  if command -v nix >/dev/null 2>&1; then
    echo "Nix is already installed. Skipping Nix installation."
  else
    echo "Installing Nix using the Determinate Nix Installer..."
    curl -L https://install.determinate.systems/nix | sh -s -- install
  fi
}

# Function to install Nix-Darwin
install_nix_darwin() {
  echo "Installing Nix-Darwin..."
  nix-build https://github.com/LnL7/nix-darwin/archive/release-24.11.tar.gz -A installer
  ./result/bin/darwin-installer
}

# Create necessary directories
create_directories() {
  echo "Creating required directories..."
  mkdir -p ~/repos/personal || { echo "Failed to create directories"; exit 1; }
}

# Clone the dotfiles repository
clone_dotfiles() {
  echo "Cloning dotfiles repository..."
  git clone https://github.com/bourbonfgiles/dotfiles.git ~/repos/personal/dotfiles || { echo "Failed to clone repository"; exit 1; }
}

# Clone the eza-themes repository
clone_eza_themes() {
  echo "Cloning eza-themes repository..."
  git clone https://github.com/eza-community/eza-themes.git ~/repos/personal/eza-themes || { echo "Failed to clone eza-themes repository"; exit 1; }
}

# Install AstroVim
install_astrovim() {
  echo "Installing AstroVim..."

  # Clone AstroVim template
  git clone --depth 1 https://github.com/AstroNvim/AstroNvim ~/.config/nvim

  # Remove template's git connection
  rm -rf ~/.config/nvim/.git
}

# Create symlinks using Stow
create_symlinks() {
  echo "Creating symlinks..."
  cd ~/repos/personal/dotfiles || { echo "Failed to change directory"; exit 1; }
  rm -rf ~/.config 
  stow -t ~/.config .config
  mkdir -p ~/Library/Application\ Support/eza
  ln -sf ~/repos/personal/eza-themes/themes/dracula.yml ~/Library/Application\ Support/eza/theme.yml || { echo "Failed to configure eza theme for macOS"; exit 1; }
  ln -sf ~/repos/personal/dotfiles/.zshrc ~/.zshrc || { echo "Failed to symlink .zshrc"; exit 1; }
}

# Function to install Home Manager
install_home_manager() {
  if nix-channel --list | grep -q home-manager; then
    echo "Home Manager is already installed. Skipping Home Manager installation."
  else
    echo "Installing Home Manager..."
    nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager
    nix-channel --update
    nix-shell '<home-manager>' --attr install
  fi
}

#apply_home_manager() {
    echo "Applying Home Manager configuration using flake.nix..."
    home-manager switch --flake ~/repos/personal/dotfiles/.config/nixpkgs/darwin/flake.nix || { echo "Failed to apply Home Manager configuration using flake.nix"; exit 1; }

    echo "Applying additional Home Manager configuration using home.nix..."
    home-manager switch -f ~/repos/personal/dotfiles/.config/nixpkgs/darwin/home.nix || { echo "Failed to apply Home Manager configuration using home.nix"; exit 1; }
}

# Install Nu plugins
install_nu_plugins() {
  echo "Installing Nu plugins..."
[ nu_plugin_inc
  nu_plugin_polars
  nu_plugin_gstat
  nu_plugin_formats
  nu_plugin_query
] | each { cargo install $in --locked } | ignore
}
 
  # Add plugins to Nushell
  echo "Adding plugins to Nushell..."
  nu -c 'for plugin in nu_plugin_inc nu_plugin_polars nu_plugin_gstat nu_plugin_formats nu_plugin_query { plugin add ~/.cargo/bin/$plugin }' || { echo "Failed to add plugins to Nushell"; exit 1; }
}

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

echo "Setup complete!"
