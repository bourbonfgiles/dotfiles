-- Load Hammerspoon extensions
local hotkey = require "hs.hotkey"
local window = require "hs.window"
local screen = require "hs.screen"
local alert = require "hs.alert"

-- Define a function to maximize the window minus the dock
local function maximizeWindow()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(screenFrame)
        alert.show("Maximized (minus dock)")
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
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x, screenFrame.y, screenFrame.w / 2, screenFrame.h))
        alert.show("Left Half")
    end
end

-- Define a function to move window to the right half of the screen
local function rightHalf()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x + screenFrame.w / 2, screenFrame.y, screenFrame.w / 2, screenFrame.h))
        alert.show("Right Half")
    end
end

-- Bind hotkeys to the functions
hotkey.bind({"alt"}, "Up", maximizeWindow)
hotkey.bind({"alt"}, "Down", minimizeWindow)
hotkey.bind({"alt"}, "Left", leftHalf)
hotkey.bind({"alt"}, "Right", rightHalf)