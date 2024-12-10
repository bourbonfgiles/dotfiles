-- NvimTree configuration
require'nvim-tree'.setup {
  disable_netrw = true,
  hijack_netrw = true,
  update_cwd = true,
  update_focused_file = {
    enable = true,
    update_cwd = true,
  },
  view = {
    width = 50,  -- Set the width to 50 columns
    side = 'left',
  },
  git = {
    enable = true,
    ignore = false,
  },
  filters = {
    dotfiles = false,
    custom = {},
  },
  actions = {
    open_file = {
      resize_window = true,
      quit_on_open = false, -- Ensure the tree doesn't close when opening a file
    },
  },
}

-- Key mappings for NvimTree
vim.keymap.set("", "<Leader>n", function() require('nvim-tree.api').tree.toggle() end)
vim.keymap.set("", "<Leader>N", function() require('nvim-tree.api').tree.toggle() end)

-- Automatically open nvim-tree when Neovim starts
vim.api.nvim_exec([[
  augroup NvimTree
    autocmd!
    autocmd VimEnter * NvimTreeOpen
  augroup END
]], false)
