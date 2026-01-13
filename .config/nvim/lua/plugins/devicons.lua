return {
  {
    "nvim-tree/nvim-web-devicons",
    config = function()
      require("nvim-web-devicons").setup({
        override = {
          tf = {
            icon = "",
            color = "#7b42bc",
            name = "Terraform",
          },
          hcl = {
            icon = "",
            color = "#7b42bc",
            name = "HCL",
          },
          yaml = {
            icon = "",
            color = "#ff6188",
            name = "Yaml",
          },
          yml = {
            icon = "",
            color = "#ff6188",
            name = "Yml",
          },
          md = {
            icon = "",
            color = "#519aba",
            name = "Markdown",
          },
          sh = {
            icon = "",
            color = "#89e051",
            name = "Shell",
          },
          zsh = {
            icon = "",
            color = "#89e051",
            name = "Zsh",
          },
          py = {
            icon = "",
            color = "#ffbc03",
            name = "Python",
          },
          go = {
            icon = "",
            color = "#00add8",
            name = "Go",
          },
          dockerfile = {
            icon = "",
            color = "#0db7ed",
            name = "Dockerfile",
          },
          json = {
            icon = "",
            color = "#f1c40f",
            name = "Json",
          },
        },
        color_icons = true,
        default = true,
      })
    end,
  },
}
