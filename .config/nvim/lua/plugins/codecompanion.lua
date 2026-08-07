-- Kiro AI integration.
--
-- Uses CodeCompanion's built-in `kiro` ACP adapter, which spawns `kiro-cli acp`
-- and talks JSON-RPC over stdio. Preferred over an HTTP/OpenAI-shim provider
-- because the agent is stateful (it owns the conversation context, so we only
-- send new turns), it gets real read/write access to buffers, and its tool
-- calls surface as permission prompts with diff previews instead of silent edits.
--
-- Auth is delegated entirely to the CLI: run `kiro-cli login` once. Until that
-- is done, opening a chat will fail to connect -- nothing else breaks.
return {
  -- Replaced by CodeCompanion. The old config pointed at a local OpenAI-shim on
  -- 127.0.0.1:9091 that no longer runs, and its mappings shadowed LazyVim's LSP
  -- keys (<leader>cf Format, <leader>cd Line Diagnostics, etc).
  { "yetone/avante.nvim", enabled = false },

  {
    "olimorris/codecompanion.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-treesitter/nvim-treesitter",
    },
    opts = {
      interactions = {
        chat = { adapter = "kiro" },
        inline = { adapter = "kiro" },
      },
      display = {
        chat = {
          window = {
            position = "right",
            width = 0.35,
          },
        },
        diff = {
          provider = "default",
        },
      },
    },
    cmd = {
      "CodeCompanion",
      "CodeCompanionChat",
      "CodeCompanionActions",
    },
    keys = {
      { "<leader>aa", "<cmd>CodeCompanionChat Toggle<cr>", mode = { "n", "v" }, desc = "Kiro chat (toggle)" },
      { "<leader>ai", "<cmd>CodeCompanion<cr>", mode = { "n", "v" }, desc = "Kiro inline prompt" },
      { "<leader>ap", "<cmd>CodeCompanionActions<cr>", mode = { "n", "v" }, desc = "Kiro actions palette" },
      { "<leader>an", "<cmd>CodeCompanionChat<cr>", mode = "n", desc = "Kiro chat (new)" },
      { "ga", "<cmd>CodeCompanionChat Add<cr>", mode = "v", desc = "Add selection to Kiro chat" },

      -- The full CLI TUI in a float, for work the ACP bridge doesn't expose:
      -- session resume, agent switching, and the CLI's own tool loop.
      {
        "<leader>ak",
        function()
          Snacks.terminal.toggle("kiro-cli", {
            cwd = LazyVim.root(),
            win = {
              position = "float",
              border = "rounded",
              width = 0.85,
              height = 0.85,
              title = " kiro-cli ",
              title_pos = "center",
            },
          })
        end,
        mode = { "n", "t" },
        desc = "Kiro CLI (float)",
      },
    },
  },
}
