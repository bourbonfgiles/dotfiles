#!/bin/zsh

# Function to install Nix and Home Manager
install_nix_and_home_manager() {
  echo "Installing Nix..."
  curl -L https://nixos.org/nix/install | sh
  . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

  echo "Installing Home Manager..."
  nix-channel --add https://github.com/nix-community/home-manager/archive/release-23.05.tar.gz home-manager
  nix-channel --update
  nix-shell '<home-manager>' -A install
}

# Function to install Nix-Darwin and Home Manager
install_nix_darwin_and_home_manager() {
  echo "Installing Nix-Darwin..."
  nix-build https://github.com/LnL7/nix-darwin/archive/master.tar.gz -A installer
  ./result/bin/darwin-installer

  echo "Installing Home Manager..."
  nix-channel --add https://github.com/nix-community/home-manager/archive/release-23.05.tar.gz home-manager
  nix-channel --update
  nix-shell '<home-manager>' -A install
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
  stow -t ~ nvim || { echo "Failed to stow nvim"; exit 1; }
  stow -t ~ nushell || { echo "Failed to stow nushell"; exit 1; }
  stow -t ~ starship || { echo "Failed to stow starship"; exit 1; }
  stow -t ~ nixpkgs || { echo "Failed to stow nixpkgs"; exit 1; }

  # macOS specific configuration
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Configuring eza theme for macOS..."
    mkdir -p ~/Library/Application\ Support/eza
    ln -sf ~/repos/personal/eza-themes/themes/dracula.yml ~/Library/Application\ Support/eza/theme.yml || { echo "Failed to configure eza theme for macOS"; exit 1; }
  else
    echo "Configuring the eza theme..."
    mkdir -p ~/.config/eza
    ln -sf ~/repos/personal/eza-themes/themes/dracula.yml ~/.config/eza/theme.yml || { echo "Failed to configure eza theme"; exit 1; }
  fi
}

# Run Home Manager to apply the configuration
apply_home_manager() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Applying Home Manager configuration from ~/repos/personal/dotfiles/.config/nixpkgs/darwin/home.nix..."
    home-manager switch -f ~/repos/personal/dotfiles/.config/nixpkgs/darwin/home.nix || { echo "Failed to apply Home Manager configuration"; exit 1; }
  else
    echo "Applying Home Manager configuration from ~/repos/personal/dotfiles/.config/nixpkgs/home.nix..."
    home-manager switch -f ~/repos/personal/dotfiles/.config/nixpkgs/home.nix || { echo "Failed to apply Home Manager configuration"; exit 1; }
  fi
}

# Install Nu plugins
install_nu_plugins() {
  echo "Installing Nu plugins..."
  nu_plugins=(
    nu_plugin_inc
    nu_plugin_polars
    nu_plugin_gstat
    nu_plugin_formats
    nu_plugin_query
  )
  for plugin in "${nu_plugins[@]}"; do
    cargo install "$plugin" --locked || { echo "Failed to install $plugin"; exit 1; }
  done
 
  # Add plugins to Nushell
  echo "Adding plugins to Nushell..."
  nu -c 'for plugin in nu_plugin_inc nu_plugin_polars nu_plugin_gstat nu_plugin_formats nu_plugin_query { plugin add ~/.cargo/bin/$plugin }' || { echo "Failed to add plugins to Nushell"; exit 1; }
}

# Main script execution
if [[ "$OSTYPE" == "darwin"* ]]; then
  install_nix_darwin_and_home_manager
else
  install_nix_and_home_manager
fi

apply_home_manager
setup_git_and_ssh
clone_dotfiles
clone_eza_themes
install_astrovim
create_symlinks
install_nu_plugins

echo "Setup complete!"
