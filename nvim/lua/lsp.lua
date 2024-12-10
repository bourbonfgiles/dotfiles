-- Language server configurations
local lspconfig = require('lspconfig')

-- Enable language servers
local servers = { 'pyright', 'bashls', 'dockerls', 'jsonls', 'yamlls', 'terraformls', 'gopls' }
for _, lsp in ipairs(servers) do
  lspconfig[lsp].setup {}
end

-- Additional language servers for DevOps
lspconfig.terraformls.setup {} -- Terraform
lspconfig.opentofu_ls.setup {} -- OpenTofu
lspconfig.helm_ls.setup {} -- Helm
lspconfig.yamlls.setup {} -- YAML
lspconfig.dockerls.setup {} -- Docker
lspconfig.bashls.setup {} -- Bash
