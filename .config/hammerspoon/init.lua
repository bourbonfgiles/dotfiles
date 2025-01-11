-- Load Hammerspoon extensions
local hotkey = require "hs.hotkey"
local window = require "hs.window"
local grid = require "hs.grid"
local alert = require "hs.alert"

-- Set grid size
hs.grid.setGrid('2x2')
hs.grid.setMargins('0x0')

-- Define a function to maximize the window
local function maximizeWindow()
    local win = hs.window.focusedWindow()
    if win then
        win:maximize()
        alert.show("Maximized")
    end
end

-- Define a function to minimize the window
local function minimizeWindow()
    local win = hs.window.focusedWindow()
    if win then
        win:minimize()
        alert.show("Minimized")
    end
end

-- Define a function to move window to the left half of the screen
local function leftHalf()
    local win = hs.window.focusedWindow()
    if win then
        hs.grid.set(win, '0,0 1x2')
        alert.show("Left Half")
    end
end

-- Define a function to move window to the right half of the screen
local function rightHalf()
    local win = hs.window.focusedWindow()
    if win then
        hs.grid.set(win, '1,0 1x2')
        alert.show("Right Half")
    end
end

-- Bind hotkeys to the functions
hotkey.bind({"opt"}, "Up", maximizeWindow)
hotkey.bind({"opt"}, "Down", minimizeWindow)
hotkey.bind({"opt"}, "Left", leftHalf)
hotkey.bind({"opt"}, "Right", rightHalf)
