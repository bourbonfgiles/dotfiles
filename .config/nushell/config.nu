echo "NuShell has loaded successfully!"

# Aliases
alias ll = eza
alias lvim = /home/giles/.local/bin/lvim
alias pbcopy = xclip -selection clipboard
alias pbpaste = xclip -selection clipboard -o
alias cps = gh copilot suggest
alias cpe = gh copilot explain

# Source external scripts
#source-env ~/.config/nvim-Lazyman/.lazymanrc
#source-env ~/.config/nvim-Lazyman/.nvimsbind

source ~/.zoxide.nu

$env.STARSHIP_SHELL = "nu"
source ~/.cache/carapace/init.nu
use ~/.cache/starship/init.nu

#source ~/.config/starship.toml
