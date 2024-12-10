-- Function to create a floating window with Neovim commands
_G.open_command_window = function()
  local ui = vim.api.nvim_list_uis()[1]
  local width = math.floor(ui.width * 0.25)
  local height = ui.height
  local col = ui.width - width
  local row = 0

  local buf = vim.api.nvim_create_buf(false, true)
  local win = vim.api.nvim_open_win(buf, false, {
    relative = 'editor',
    width = width,
    height = height,
    row = row,
    col = col,
    border = 'single',
    style = 'minimal',
    noautocmd = true,
  })

  -- Set custom colors for the floating window and border
  vim.api.nvim_win_set_option(win, 'winhl', 'NormalFloat:MyFloat,FloatBorder:MyFloatBorder')

  vim.api.nvim_buf_set_lines(buf, 0, -1, false, {
    'Command Table:',
    'Navigation:',
    'h - Move left',
    'j - Move down',
    'k - Move up',
    'l - Move right',
    'w - Move to the start of the next word',
    'b - Move to the start of the previous word',
    'e - Move to the end of the current word',
    'gg - Move to the beginning of the file',
    'G - Move to the end of the file',
    '0 - Move to the beginning of the line',
    '$ - Move to the end of the line',
    ':{line number} - Move to the specified line number',
    '',
    'Editing:',
    'i - Insert mode at cursor',
    'I - Insert mode at the beginning of the line',
    'a - Insert mode after cursor',
    'A - Insert mode at the end of the line',
    'o - Open a new line below',
    'O - Open a new line above',
    'r - Replace character under cursor',
    'R - Replace mode',
    'x - Delete character under cursor',
    'X - Delete character before cursor',
    'd{motion} - Delete text with motion (e.g., dw)',
    'dd - Delete current line',
    'y{motion} - Yank (copy) text with motion',
    'yy - Yank (copy) current line',
    'p - Paste after cursor',
    'P - Paste before cursor',
    '',
    'Visual Mode:',
    'v - Visual mode',
    'V - Visual line mode',
    'Ctrl+v - Visual block mode',
    'Esc - Exit visual mode',
    '',
    'Undo/Redo:',
    'u - Undo',
    'Ctrl+r - Redo',
    '',
    'Search:',
    '/{pattern} - Search for pattern',
    'n - Next match',
    'N - Previous match',
    '',
    'Saving and Quitting:',
    ':w - Save file',
    ':wq - Save and quit',
    ':q - Quit',
    ':q! - Quit without saving',
    '',
    'Splitting Windows:',
    ':split - Horizontal split',
    ':vsplit - Vertical split',
    'Ctrl+w h - Move to left window',
    'Ctrl+w j - Move to bottom window',
    'Ctrl+w k - Move to top window',
    'Ctrl+w l - Move to right window',
    ':q - Close current window',
    '',
    'Tabs:',
    ':tabnew - New tab',
    'gt - Next tab',
    'gT - Previous tab',
    ':tabclose - Close tab',
    '',
    'File Management:',
    ':e {file} - Open file',
    ':ls - List open buffers',
    ':b {buffer} - Switch to buffer',
    ':bd - Close buffer',
    '',
    'Help:',
    ':help {topic} - Help for topic',
    ':help user-manual - Open user manual',
  })
end

-- Automatically open the command window when Neovim starts
vim.api.nvim_exec([[
  augroup CommandWindow
    autocmd!
    autocmd VimEnter * lua _G.open_command_window()
  augroup END
]], false)
