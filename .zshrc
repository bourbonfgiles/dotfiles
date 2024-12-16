# History settings
HISTIGNORE='cps*:cps *:cps:cpe*:cpe: cpe *:history:ll:ls:exit:k9s'  # Ignore specific commands in history
HISTFILE=~/.histfile  # Set the history file location
HISTSIZE=10000  # Set the maximum number of history entries
SAVEHIST=20000  # Set the number of history entries to save

# Aliases for common commands
alias ll='eza'
alias z='zoxide'
alias history='bat ~/.histfile'  # Display history file with 'bat' for syntax highlighting
alias lvim='/home/giles/.local/bin/lvim'

# Initialize Homebrew and Oh My Posh
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"  # Initialize Homebrew
eval "$(oh-my-posh init zsh --config ~/.oh-my-posh/themes/catppuccin_mocha.omp.json)"  # Initialize Oh My Posh with a specific theme

# Aliases for clipboard operations
alias pbcopy='xclip -selection clipboard'  # Copy to clipboard
alias pbpaste='xclip -selection clipboard -o'  # Paste from clipboard

# GitHub Copilot aliases
alias cps='gh copilot suggest'  # Alias for GitHub Copilot suggest
alias cpe='gh copilot explain'  # Alias for GitHub Copilot explain

# Key bindings for word navigation
bindkey "^[[1;5D" backward-word  # Move cursor backward by word
bindkey "^[[1;5C" forward-word  # Move cursor forward by word

if command -v zoxide > /dev/null; then
  eval "$(zoxide init zsh)"
fi

eval "$(carapace _carapace)"

# Source the Lazyman shell initialization for aliases and nvims selector
# shellcheck source=.config/nvim-Lazyman/.lazymanrc
[ -f ~/.config/nvim-Lazyman/.lazymanrc ] && source ~/.config/nvim-Lazyman/.lazymanrc
# Source the Lazyman .nvimsbind for nvims key binding
# shellcheck source=.config/nvim-Lazyman/.nvimsbind
[ -f ~/.config/nvim-Lazyman/.nvimsbind ] && source ~/.config/nvim-Lazyman/.nvimsbind

# Uncomment the following line to start kubectl proxy for WSL with specific settings
# kubectl proxy --port=8001 --reject-paths="^/api/./pods/./attach"

echo "Sourced .zshrc"

eval "$(starship init zsh)"eval
