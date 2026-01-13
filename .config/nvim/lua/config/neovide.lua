-- Neovide specific configuration
if vim.g.neovide then
  -- Font size
  vim.o.guifont = "JetBrainsMono Nerd Font:h14"
  
  -- Window blur
  vim.g.neovide_window_blurred = true
  
  -- Floating blur
  vim.g.neovide_floating_blur_amount_x = 2.0
  vim.g.neovide_floating_blur_amount_y = 2.0
  
  -- Animations
  vim.g.neovide_cursor_animation_length = 0.08
  vim.g.neovide_cursor_trail_size = 0.4
  vim.g.neovide_cursor_antialiasing = true
  vim.g.neovide_cursor_animate_in_insert_mode = true
  vim.g.neovide_cursor_animate_command_line = true
  
  -- Cursor particles (choose one or comment all out)
  -- vim.g.neovide_cursor_vfx_mode = "railgun"
  -- vim.g.neovide_cursor_vfx_mode = "torpedo"
  vim.g.neovide_cursor_vfx_mode = "pixiedust"
  -- vim.g.neovide_cursor_vfx_mode = "sonicboom"
  -- vim.g.neovide_cursor_vfx_mode = "ripple"
  -- vim.g.neovide_cursor_vfx_mode = "wireframe"
  
  vim.g.neovide_cursor_vfx_opacity = 200.0
  vim.g.neovide_cursor_vfx_particle_lifetime = 1.2
  vim.g.neovide_cursor_vfx_particle_density = 7.0
  vim.g.neovide_cursor_vfx_particle_speed = 10.0
  
  -- Refresh rate
  vim.g.neovide_refresh_rate = 60
  vim.g.neovide_refresh_rate_idle = 5
  
  -- Scroll animation
  vim.g.neovide_scroll_animation_length = 0.3
  
  -- Padding
  vim.g.neovide_padding_top = 0
  vim.g.neovide_padding_bottom = 0
  vim.g.neovide_padding_right = 0
  vim.g.neovide_padding_left = 0
  
  -- Remember window size
  vim.g.neovide_remember_window_size = true
  
  -- Fullscreen
  vim.g.neovide_fullscreen = false
  
  -- Input settings
  vim.g.neovide_input_use_logo = true -- Use Command key on macOS
  
  -- Hide mouse when typing
  vim.g.neovide_hide_mouse_when_typing = true
  
  -- Confirm quit
  vim.g.neovide_confirm_quit = true
end
