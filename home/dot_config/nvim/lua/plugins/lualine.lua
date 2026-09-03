return {
  {
    "nvim-lualine/lualine.nvim",
    opts = {
      options = {
        -- "auto" resolves lualine/themes/<colors_name>, so the statusline follows
        -- whatever colorscheme is active. follows active colorscheme (smyck).
        theme = "auto",
        globalstatus = true,
      },
    },
  },
}
