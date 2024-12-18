$env.PATH = "/home/linuxbrew/.linuxbrew/bin"
echo "NuShell has loaded successfully!"

# Aliases
alias ll = eza
alias lvim = /home/giles/.local/bin/lvim
alias pbcopy = xclip -selection clipboard
alias pbpaste = xclip -selection clipboard -o
alias cps = gh copilot suggest
alias cpe = gh copilot explain

#source ~/.zoxide.nu

$env.STARSHIP_SHELL = "nu"
source ~/.cache/carapace/init.nu
#config set CARAPACE_THEME "Dracula"
use ~/.cache/starship/init.nu
#source ~/.config/starship.toml
