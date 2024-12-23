# History settings
HISTSIZE=10000  # Set the maximum number of history entries
SAVEHIST=20000  # Set the number of history entries to save

# Aliases for common commands
alias ll='eza'
alias z='zoxide'

# Initialize Homebrew and Oh My Posh
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"  # Initialize Homebrew
eval "$(oh-my-posh init zsh --config ~/.oh-my-posh/themes/catppuccin_mocha.omp.json)"  # Initialize Oh My Posh with a specific theme

if command -v zoxide > /dev/null; then
  eval "$(zoxide init zsh)"
fi

eval "$(starship init zsh)"eval
eval "$(carapace _carapace)"

# Uncomment the following line to start kubectl proxy for WSL with specific settings
# kubectl proxy --port=8001 --reject-paths="^/api/./pods/./attach"

echo "Sourced .zshrc"

