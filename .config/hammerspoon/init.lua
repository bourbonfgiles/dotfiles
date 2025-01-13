-- Add a pathwatcher function to reload the config
function reloadConfig(files)
    doReload = false
    for _, file in pairs(files) do
        if file:sub(-4) == ".lua" then
            doReload = true
        end
    end
    if doReload then
        hs.reload()
    end
end
myWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.config/hammerspoon/", reloadConfig):start()
hs.alert.show("Config loaded")

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
    end
end

-- Define a function to hide the window
local function hideWindow()
    local win = hs.window.focusedWindow()
    if win then
        win:application():hide()
    end
end

-- Define a function to move window to the left half of the screen
local function leftHalf()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x, screenFrame.y, screenFrame.w / 2, screenFrame.h))
    end
end

-- Define a function to move window to the right half of the screen
local function rightHalf()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x + screenFrame.w / 2, screenFrame.y, screenFrame.w / 2, screenFrame.h))
    end
end

-- Define functions to move window to quarters of the screen
local function topLeft()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x, screenFrame.y, screenFrame.w / 2, screenFrame.h / 2))
    end
end

local function topRight()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x + screenFrame.w / 2, screenFrame.y, screenFrame.w / 2, screenFrame.h / 2))
    end
end

local function bottomLeft()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x, screenFrame.y + screenFrame.h / 2, screenFrame.w / 2, screenFrame.h / 2))
    end
end

local function bottomRight()
    local win = hs.window.focusedWindow()
    if win then
        local screenFrame = win:screen():frame()
        win:setFrame(hs.geometry.rect(screenFrame.x + screenFrame.w / 2, screenFrame.y + screenFrame.h / 2, screenFrame.w / 2, screenFrame.h / 2))
    end
end

-- Bind hotkeys to the functions
hotkey.bind({"alt"}, "Up", maximizeWindow)
hotkey.bind({"alt"}, "Down", hideWindow)
hotkey.bind({"alt"}, "Left", leftHalf)
hotkey.bind({"alt"}, "Right", rightHalf)
hotkey.bind({"alt", "shift"}, "Left", topLeft)
hotkey.bind({"alt", "shift"}, "Right", topRight)
hotkey.bind({"alt", "shift"}, "Down", bottomLeft)
hotkey.bind({"alt", "shift"}, "Up", bottomRight)

-- Load Caffeine spoon
hs.loadSpoon("Caffeine")

-- Function to start Caffeine
local function startCaffeine()
    spoon.Caffeine:start()
    hs.notify.new({title="Hammerspoon", informativeText="Caffeine activated"}):send()
end

-- Function to stop Caffeine
local function stopCaffeine()
    spoon.Caffeine:stop()
    hs.notify.new({title="Hammerspoon", informativeText="Caffeine deactivated"}):send()
end

-- Schedule Caffeine to start at 9am
hs.timer.doAt("09:00", startCaffeine)

-- Schedule Caffeine to stop at 5:30pm
hs.timer.doAt("17:30", stopCaffeine)
