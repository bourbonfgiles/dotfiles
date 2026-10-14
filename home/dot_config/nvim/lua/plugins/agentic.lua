-- agentic.nvim: thin ACP bridge. The plugin is the interface, the CLI is the
-- brain. Kiro is the chosen backend today; everything that's true for Kiro
-- (sessions, MCP servers, agent configs, tools, sub-agents, slash commands)
-- lives in kiro-cli itself, not here.
--
-- Auto-picks the first ACP CLI on $PATH. Installing a new backend (kiro,
-- opencode, claude-agent-acp, codex-acp, gemini-acp) just works. Auth is
-- handled by the CLI -- agentic.nvim never touches credentials.
--
-- Sessions are interchangeable across nvim and the CLI: start in nvim, resume
-- in kiro-cli, hand back to nvim. That's the workflow feature.
return {
  -- Previous: CodeCompanion, before that avante over a now-dead 127.0.0.1:9091
  -- shim. Disabled rather than removed so a rollback is one edit on each.
  { "olimorris/codecompanion.nvim", enabled = false },
  { "yetone/avante.nvim",          enabled = false },

  {
    "carlos-algms/agentic.nvim",

    -- Default to the first ACP CLI on $PATH. Order matters: kiro first so a
    -- commercial licence takes priority. Add more rows to widen the picker.
    opts = function()
      local providers = {
        ["kiro-cli"]         = "kiro-acp",
        ["opencode"]         = "opencode-acp",
        ["claude-agent-acp"] = "claude-agent-acp",
        ["gemini"]           = "gemini-acp",
        ["codex-acp"]        = "codex-acp",
      }
      for bin, prov in pairs(providers) do
        if vim.fn.executable(bin) == 1 then
          return { provider = prov }
        end
      end
      return nil -- no CLI installed; the plugin won't load
    end,

    -- Keys avoid LazyVim-blessed `a*` reservations (avante.lua and
    -- claudecode.lua claim `ap`, `ar`, `aA`, `ac`, `aC`).
    -- Mnemonics copied from rlees85's plain-nvim setup since they match the
    -- plugin's actual API surface rather than inventing new verbs.
    keys = {
      { "<leader>ao", function()
          require("agentic").toggle()
        end, mode = { "n", "v", "i" }, desc = "Agentic chat (toggle)" },

      { "<leader>an", function()
          require("agentic").new_session()
        end, mode = { "n", "v", "i" }, desc = "Agentic new session" },

      { "<leader>aR", function()
          require("agentic").restore_session()
        end, mode = { "n", "v", "i" }, desc = "Agentic restore CLI session" },

      { "<leader>ai", function()
          require("agentic").add_selection_or_file_to_context()
        end, mode = { "n", "v" }, desc = "Agentic add selection to context" },

      { "<leader>ad", function()
          require("agentic").add_buffer_diagnostics()
        end, mode = "n", desc = "Agentic add buffer diagnostics" },
    },
  },
}
