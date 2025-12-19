################################################################################
# History
################################################################################
HISTIGNORE='cps*:cps *:cps:cpe*:cpe: cpe *:history:ll:ls:z:exit:k9s'
HISTSIZE=10000
SAVEHIST=20000

################################################################################
# Homebrew PATH (macOS + Linux)
# Ensure brewed tools are on PATH across shells (official shellenv method).     #
################################################################################
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true
eval "$(~/.linuxbrew/bin/brew shellenv)" 2>/dev/null || true

################################################################################
# Aliases
################################################################################
alias ll='eza -l --group-directories-first --icons --color=always --header'
alias z='zoxide'
# alias xclip='xclip -selection clipboard'  # add after Brewfile installs xclip

################################################################################
# zoxide
################################################################################
if command -v zoxide >/dev/null; then
  eval "$(zoxide init zsh)"
fi

################################################################################
# Starship Prompt
################################################################################
if command -v starship >/dev/null; then
  eval "$(starship init zsh)"
fi

################################################################################
# Carapace Completions
################################################################################
if command -v carapace >/dev/null; then
  eval "$(carapace _carapace)"
fi

################################################################################
# fzf (key-bindings + completion)
################################################################################
if [[ -f "$(brew --prefix)/opt/fzf/shell/key-bindings.zsh" ]]; then
  source "$(brew --prefix)/opt/fzf/shell/key-bindings.zsh"
fi
if [[ -f "$(brew --prefix)/opt/fzf/shell/completion.zsh" ]]; then
  source "$(brew --prefix)/opt/fzf/shell/completion.zsh"
fi

################################################################################
# gh / kubectl / helm completions
################################################################################
if command -v gh >/dev/null; then
  eval "$(gh completion -s zsh)"
fi
if command -v kubectl >/dev/null; then
  source <(kubectl completion zsh)
fi
if command -v helm >/dev/null; then
  source <(helm completion zsh)
fi

################################################################################
# eza Theme Path (cross‑platform)
################################################################################
export EZA_CONFIG_DIR="$HOME/.config/eza"

################################################################################
# Prompt & Editor
################################################################################
export EDITOR="nvim"
export VISUAL="$EDITOR"

echo "Sourced .zshrc"
