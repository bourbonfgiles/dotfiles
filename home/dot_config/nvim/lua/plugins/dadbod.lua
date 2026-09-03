return {
  {
    "tpope/vim-dadbod",
  },
  {
    "kristijanhusak/vim-dadbod-ui",
    dependencies = { "tpope/vim-dadbod" },
    cmd = { "DBUI", "DBUIToggle", "DBUIAddConnection" },
    keys = {
      { "<leader>db", "<cmd>DBUIToggle<cr>", desc = "Toggle DBUI" },
    },
    init = function()
      vim.g.db_ui_use_nerd_fonts = 1
      vim.g.db_ui_save_location = vim.fn.stdpath("data") .. "/db_ui_queries"
      
      vim.g.dbs = {
        -- Development Tools
        {
          name = "devtools-puregym-ne",
          url = function()
            return string.format(
              "postgresql://%s:%s@devtools-postgres-ne.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("DEVTOOLS_PG_PASSWORD") or ""
            )
          end,
        },
        {
          name = "sftp-puregym-ne",
          url = function()
            return string.format(
              "postgresql://%s:%s@sftp-puregym-ne.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("SFTP_PG_PASSWORD") or ""
            )
          end,
        },
        {
          name = "devtools-dependency-tracker",
          url = function()
            return string.format(
              "postgresql://%s:%s@devtools-dependency-tracker.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("DEPTRACK_PG_PASSWORD") or ""
            )
          end,
        },
        
        -- Pico Development
        {
          name = "pico-dev-azdb-uks",
          url = function()
            return string.format(
              "postgresql://%s:%s@env-dev-azdb-uks.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("PICO_DEV_PG_PASSWORD") or ""
            )
          end,
        },
        
        -- Pico Production
        {
          name = "pico-prod-azdb-uks",
          url = function()
            return string.format(
              "postgresql://%s:%s@env-prod-azdb-uks.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("PICO_PROD_PG_PASSWORD") or ""
            )
          end,
        },
        
        -- Pico Base
        {
          name = "pico-base-psql",
          url = function()
            return string.format(
              "postgresql://%s:%s@pico-psql.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("PICO_BASE_PG_PASSWORD") or ""
            )
          end,
        },
        
        -- Pico Shared
        {
          name = "pico-noreprod-shared-azdb-psql",
          url = function()
            return string.format(
              "postgresql://%s:%s@pico-noreprod-shared-azdb-psql.postgres.database.azure.com:5432/postgres?sslmode=require",
              os.getenv("PGUSER") or "pgadmin",
              os.getenv("PICO_SHARED_PG_PASSWORD") or ""
            )
          end,
        },
      }
    end,
  },
  {
    "kristijanhusak/vim-dadbod-completion",
    dependencies = { "vim-dadbod" },
    ft = { "sql", "mysql", "plsql" },
    init = function()
      vim.api.nvim_create_autocmd("FileType", {
        pattern = { "sql", "mysql", "plsql" },
        callback = function()
          require("cmp").setup.buffer({
            sources = {
              { name = "vim-dadbod-completion" },
              { name = "buffer" },
            },
          })
        end,
      })
    end,
  },
}
