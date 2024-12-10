-- Dracula theme configuration
require('dracula').setup()
vim.cmd[[colorscheme dracula]]

-- Set custom highlight groups for the floating window and border
vim.cmd [[
  highlight MyFloat guibg=#282a36 guifg=#f8f8f2
  highlight MyFloatBorder guibg=#282a36 guifg=#6272a4
]]
