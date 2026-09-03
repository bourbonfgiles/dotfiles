-- Smyck colorscheme (palette matches Ghostty built-in Smyck)
local bg = "#1b1b1b"
local fg = "#f7f7f7"
local black = "#000000"
local red = "#b84131"
local green = "#7da900"
local yellow = "#c4a500"
local blue = "#62a3c4"
local magenta = "#ba8acc"
local cyan = "#207383"
local white = "#a1a1a1"
local bright_black = "#7a7a7a"
local bright_red = "#d6837c"
local bright_green = "#c4f137"
local bright_yellow = "#fee14d"
local bright_blue = "#8dcff0"
local bright_magenta = "#f79aff"
local bright_cyan = "#6ad9cf"
local bright_white = "#f7f7f7"
local sel = "#207483"

vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then
  vim.cmd("syntax reset")
end
vim.g.colors_name = "smyck"
vim.o.termguicolors = true
vim.o.background = "dark"

local function hi(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

hi("Normal", { fg = fg, bg = bg })
hi("NormalFloat", { fg = fg, bg = black })
hi("FloatBorder", { fg = bright_black, bg = black })
hi("Comment", { fg = bright_black, italic = true })
hi("Constant", { fg = bright_red })
hi("String", { fg = green })
hi("Character", { fg = green })
hi("Number", { fg = yellow })
hi("Boolean", { fg = yellow })
hi("Identifier", { fg = bright_blue })
hi("Function", { fg = blue })
hi("Statement", { fg = magenta })
hi("Keyword", { fg = magenta })
hi("PreProc", { fg = cyan })
hi("Type", { fg = bright_cyan })
hi("Special", { fg = yellow })
hi("Underlined", { fg = blue, underline = true })
hi("Todo", { fg = yellow, bg = black, bold = true })
hi("Error", { fg = red, bold = true })
hi("ErrorMsg", { fg = red, bold = true })
hi("WarningMsg", { fg = yellow })
hi("LineNr", { fg = bright_black })
hi("CursorLineNr", { fg = yellow, bold = true })
hi("CursorLine", { bg = black })
hi("CursorColumn", { bg = black })
hi("ColorColumn", { bg = black })
hi("Visual", { bg = sel, fg = bright_white })
hi("Search", { bg = yellow, fg = black })
hi("IncSearch", { bg = bright_yellow, fg = black })
hi("MatchParen", { fg = bright_magenta, bold = true })
hi("Pmenu", { fg = fg, bg = black })
hi("PmenuSel", { fg = bright_white, bg = cyan })
hi("PmenuSbar", { bg = black })
hi("PmenuThumb", { bg = bright_black })
hi("StatusLine", { fg = fg, bg = black })
hi("StatusLineNC", { fg = bright_black, bg = black })
hi("TabLine", { fg = white, bg = black })
hi("TabLineSel", { fg = bright_white, bg = cyan })
hi("TabLineFill", { bg = black })
hi("VertSplit", { fg = bright_black, bg = bg })
hi("WinSeparator", { fg = bright_black, bg = bg })
hi("Title", { fg = blue, bold = true })
hi("Directory", { fg = blue })
hi("DiffAdd", { fg = green })
hi("DiffChange", { fg = yellow })
hi("DiffDelete", { fg = red })
hi("DiffText", { fg = bright_blue, bold = true })
hi("DiagnosticError", { fg = red })
hi("DiagnosticWarn", { fg = yellow })
hi("DiagnosticInfo", { fg = blue })
hi("DiagnosticHint", { fg = cyan })
hi("GitSignsAdd", { fg = green })
hi("GitSignsChange", { fg = yellow })
hi("GitSignsDelete", { fg = red })
hi("@keyword", { fg = magenta })
hi("@string", { fg = green })
hi("@function", { fg = blue })
hi("@variable", { fg = fg })
hi("@type", { fg = bright_cyan })
hi("@comment", { fg = bright_black, italic = true })
