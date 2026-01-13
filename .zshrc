
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
# Warp often starts non‑login shells; pull in ~/.zprofile where brew shellenv lives.
[[ -r "$HOME/.zprofile" ]] && source "$HOME/.zprofile"

################################################################################
# Zsh completion system (must be before any compdef/completion usage)
################################################################################
autoload -Uz compinit
compinit -i

################################################################################
# Aliases
################################################################################
alias ll='eza -l --group-directories-first --icons --color=always --header'
alias z='zoxide'
alias top='btm'
alias dotfiles-check='zsh ~/.config/scripts/health_check.zsh'
if command -v xclip >/dev/null; then
  alias xclip='xclip -selection clipboard'
fi

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
if command -v brew >/dev/null; then
  FZF_PREFIX="$(brew --prefix)"
  [[ -f "${FZF_PREFIX}/opt/fzf/shell/key-bindings.zsh" ]] && source "${FZF_PREFIX}/opt/fzf/shell/key-bindings.zsh"
  [[ -f "${FZF_PREFIX}/opt/fzf/shell/completion.zsh"    ]] && source "${FZF_PREFIX}/opt/fzf/shell/completion.zsh"
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
# Editor
################################################################################
if command -v nvim >/dev/null; then
  export EDITOR="nvim"
  export VISUAL="nvim"
elif command -v vim >/dev/null; then
  export EDITOR="vim"
  export VISUAL="vim"
fi

################################################################################
# Terraform version management (tenv)
################################################################################
export TENV_AUTO_INSTALL=true

################################################################################
# Secrets (not tracked in git)
################################################################################
[[ -f "$HOME/.zshrc.secrets" ]] && source "$HOME/.zshrc.secrets"
export PATH="$HOME/bin:$PATH"
