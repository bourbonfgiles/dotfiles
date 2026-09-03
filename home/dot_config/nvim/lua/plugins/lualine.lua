return {
  {
    "nvim-lualine/lualine.nvim",
    opts = {
      options = {
        -- "auto" resolves lualine/themes/<colors_name>, so the statusline follows
        -- whatever colorscheme is active. luna ships its own matching theme.
        theme = "auto",
        globalstatus = true,
      },
    },
  },
}
