-- HTTP client for .http files. Handy for poking tunnel endpoints and HTTPRoutes
-- without leaving the editor.
--
-- rest.nvim ships a rockspec, and lazy's luarocks support builds Lua 5.1 with
-- readline to install it. Bazzite has no readline headers, so that build
-- failed and lazy looped on it ("Too many rounds of missing plugins"). Rocks
-- are off in config/lazy.lua; every dependency comes from GitHub instead. Two
-- of them are plain Lua modules at their repo root, so they go on package.path.
local function on_package_path(plugin)
  package.path = plugin.dir .. "/?.lua;" .. package.path
end

return {
  {
    "rest-nvim/rest.nvim",
    ft = "http",
    dependencies = {
      "nvim-neotest/nvim-nio", -- async requests; without it the editor blocks
      "j-hui/fidget.nvim", -- request progress messages
      { "manoelcampos/xml2lua", config = on_package_path }, -- XML bodies
      { "lunarmodules/lua-mimetypes", config = on_package_path }, -- external file bodies
      {
        "nvim-treesitter/nvim-treesitter",
        opts = function(_, opts)
          opts.ensure_installed = opts.ensure_installed or {}
          table.insert(opts.ensure_installed, "http")
        end,
      },
    },
    keys = {
      { "<leader>Rr", "<cmd>Rest run<cr>", ft = "http", desc = "Run request under cursor" },
      { "<leader>Rl", "<cmd>Rest last<cr>", ft = "http", desc = "Re-run last request" },
      { "<leader>Ro", "<cmd>Rest open<cr>", ft = "http", desc = "Open result pane" },
    },
  },
}
