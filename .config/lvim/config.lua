-- Read the docs: https://www.lunarvim.org/docs/configuration
-- Example configs: https://github.com/LunarVim/starter.lvim
-- Video Tutorials: https://www.youtube.com/watch?v=sFA9kX-Ud_c&list=PLhoH5vyxr6QqGu0i7tt_XoVK9v-KvZ3m6
-- Forum: https://www.reddit.com/r/lunarvim/
-- Discord: https://discord.com/invite/Xb9B4Ny

-- Keep nvim-tree open
local function open_nvim_tree()
  require("nvim-tree.api").tree.open()
end

vim.api.nvim_create_autocmd({ "VimEnter" }, { callback = open_nvim_tree })

-- Set the colorscheme to Dracula
lvim.colorscheme = "dracula"

-- Add plugins
lvim.plugins = {
  { "Mofiqul/dracula.nvim" },  -- Dracula theme
  { "hashivim/vim-terraform" },  -- Terraform support
  { "tpope/vim-fugitive" },  -- Git integration
  { "folke/which-key.nvim" },  -- Keybinding hints
  { "numToStr/Comment.nvim" },  -- Commenting
  { "ahmedkhalf/project.nvim" },  -- Project management
  { "folke/tokyonight.nvim" },  -- Additional theme option
  { "akinsho/bufferline.nvim" },  -- Buffer line
  { "SmiteshP/nvim-navic" },  -- Code context
  { 'towolf/vim-helm',       ft = 'helm' },
  { "neovim/nvim-lspconfig", event = { "BufReadPre", "BufNewFile", "BufEnter" } },
  { "vim-tutor-mode" }
}

-- Optional: Customize the Dracula theme
local dracula = require("dracula")
dracula.setup({
  colors = {
    bg = "#282A36",
    fg = "#F8F8F2",
    selection = "#44475A",
    comment = "#6272A4",
    red = "#FF5555",
    orange = "#FFB86C",
    yellow = "#F1FA8C",
    green = "#50fa7b",
    purple = "#BD93F9",
    cyan = "#8BE9FD",
    pink = "#FF79C6",
    bright_red = "#FF6E6E",
    bright_green = "#69FF94",
    bright_yellow = "#FFFFA5",
    bright_blue = "#D6ACFF",
    bright_magenta = "#FF92DF",
    bright_cyan = "#A4FFFF",
    bright_white = "#FFFFFF",
    menu = "#21222C",
    visual = "#3E4452",
    gutter_fg = "#4B5263",
    nontext = "#3B4048",
    white = "#ABB2BF",
    black = "#191A21",
  },
  show_end_of_buffer = true,
  transparent_bg = true,
  lualine_bg_color = "#44475a",
  italic_comment = true,
  overrides = {},
})
