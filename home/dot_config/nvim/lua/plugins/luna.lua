-- luna.nvim: near-black colorscheme built on greys with four accent hues.
-- Paired with the matching Ghostty theme in .config/ghostty/themes/luna so the
-- terminal chrome and the editor agree.
return {
  {
    "wtfox/luna.nvim",
    lazy = false,
    priority = 1000, -- load before other plugins so highlights aren't clobbered
    opts = {
      -- Ghostty already provides the translucent background; leaving this false
      -- keeps nvim's own bg (#060606) so splits/floats stay distinguishable.
      transparent = false,
      -- 0-1: blends syntax accents toward grey. 1 = full colour.
      accent = 1.0,
      plugins = {
        all = false,
        auto = true, -- autodetect installed plugins via lazy.nvim
      },
    },
  },

  -- Tell LazyVim to actually use it (overrides the default tokyonight).
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "luna",
    },
  },
}
