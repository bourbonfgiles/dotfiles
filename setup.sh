#!/bin/zsh

# Function to set up Git login
setup_git() {
  echo "Setting up Git..."
  read "email?Enter your GitHub email: "
  read "username?Enter your GitHub username: "

  git config --global user.email "$email"
  git config --global user.name "$username"
  git config --global push.autosetupremote true

  echo "Git configuration set."
}

# Function to set up SSH keys
setup_ssh() {
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

# Create symlinks using Stow
create_symlinks() {
  echo "Creating symlinks..."
  cd ~/repos/personal/dotfiles || { echo "Failed to change directory"; exit 1; }
  stow -t ~ nvim || { echo "Failed to stow nvim"; exit 1; }
  stow -t ~ nushell || { echo "Failed to stow nushell"; exit 1; }
  stow -t ~ starship || { echo "Failed to stow starship"; exit 1; }
  stow -t ~ nixpkgs || { echo "Failed to stow nixpkgs"; exit 1; }
}

# Run Home Manager to apply the configuration
apply_home_manager() {
  echo "Applying Home Manager configuration..."
  home-manager switch || { echo "Failed to apply Home Manager configuration"; exit 1; }
}

# Main script execution
clone_dotfiles
setup_git
setup_ssh
create_symlinks
apply_home_manager

echo "Setup complete!"
