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
git clone https://github.com/bourbonfgiles/dotfiles.git ~/repos/personal/dotfiles

# Set up Git login
setup_git

# Set up SSH keys
setup_ssh

# Create symlinks using Stow
cd ~/repos/personal/dotfiles
stow -t ~ git
stow -t ~ nvim
stow -t ~ nushell
stow -t ~ starship
stow -t ~ nixpkgs

# Run Home Manager to apply the configuration
home-manager switch
