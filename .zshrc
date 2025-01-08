# History settings
HISTIGNORE='cps*:cps *:cps:cpe*:cpe: cpe *:history:ll:ls:z:exit:k9s'  # Ignore specific commands in history
HISTSIZE=10000  # Set the maximum number of history entries
SAVEHIST=20000  # Set the number of history entries to save

# Aliases for common commands
alias ll='eza -l --group-directories-first --icons --color=always --header'
alias z='zoxide'

if command -v zoxide > /dev/null; then
  eval "$(zoxide init zsh)"
fi

eval "$(starship init zsh)"eval
eval "$(carapace _carapace)"

echo "Sourced .zshrc"

