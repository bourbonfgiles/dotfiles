-- HTTP client for .http files. Handy for poking tunnel endpoints and HTTPRoutes
-- without leaving the editor.
--
-- rest.nvim probes for four optional deps at load and warns loudly for each one
-- missing. Two of them (nio, fidget) are ordinary Neovim plugins, so we pull
-- them from GitHub rather than relying on luarocks, which only half-installed.
-- The remaining two are pure Lua rocks and only matter for XML bodies and
-- external file bodies -- if hererocks fails to build them, the warnings now
-- appear when you open a .http buffer rather than on every startup.
return {
  {
    "rest-nvim/rest.nvim",
    ft = "http",
    dependencies = {
      "nvim-neotest/nvim-nio", -- async requests; without it the editor blocks
      "j-hui/fidget.nvim", -- request progress messages
      {
        "nvim-treesitter/nvim-treesitter",
        opts = function(_, opts)
          opts.ensure_installed = opts.ensure_installed or {}
          table.insert(opts.ensure_installed, "http")
        end,
      },
    },
    rocks = {
      "mimetypes", -- detect file type of external body files
      "xml2lua", -- XML request bodies
    },
    keys = {
      { "<leader>Rr", "<cmd>Rest run<cr>", ft = "http", desc = "Run request under cursor" },
      { "<leader>Rl", "<cmd>Rest last<cr>", ft = "http", desc = "Re-run last request" },
      { "<leader>Ro", "<cmd>Rest open<cr>", ft = "http", desc = "Open result pane" },
    },
  },
}
