-- Pathwatcher to reload config
function reloadConfig(files)
    local doReload = false
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
hs.alert.show("Reconfiguration successful. New settings have been applied.")

-- Load Hammerspoon extensions
local hotkey = require "hs.hotkey"
local window = require "hs.window"
local screen = require "hs.screen"
local alert = require "hs.alert"
local caffeinate = require "hs.caffeinate"

-- Window management functions
local function maximizeWindow()
    local win = hs.window.focusedWindow()
    if win then win:setFrame(win:screen():frame()) end
end

local function hideWindow()
    local win = hs.window.focusedWindow()
    if win then win:application():hide() end
end

local function leftHalf()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x, f.y, f.w / 2, f.h))
    end
end
local function rightHalf()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x + f.w / 2, f.y, f.w / 2, f.h))
    end
end

local function topLeft()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x, f.y, f.w / 2, f.h / 2))
    end
end

local function topRight()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x + f.w / 2, f.y, f.w / 2, f.h / 2))
    end
end

local function bottomLeft()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x, f.y + f.h / 2, f.w / 2, f.h / 2))
    end
end

local function bottomRight()
    local win = hs.window.focusedWindow()
    if win then
        local f = win:screen():frame()
        win:setFrame(hs.geometry.rect(f.x + f.w / 2, f.y + f.h / 2, f.w / 2, f.h / 2))
    end
end

-- Hotkey bindings
hotkey.bind({"alt"}, "Up", maximizeWindow)
hotkey.bind({"alt"}, "Down", hideWindow)
hotkey.bind({"alt"}, "Left", leftHalf)
hotkey.bind({"alt"}, "Right", rightHalf)
hotkey.bind({"alt", "shift"}, "Left", topLeft)
hotkey.bind({"alt", "shift"}, "Right", topRight)
hotkey.bind({"alt", "shift"}, "Down", bottomLeft)
hotkey.bind({"alt", "shift"}, "Up", bottomRight)

-- Jiggler and Caffeinate (Mon–Fri, 08:00–16:30)
local jiggleInterval = 60 -- seconds
local jigglerTimer = nil
local caffeinateActive = false

local function jiggleMouse()
    local point = hs.mouse.absolutePosition()
    hs.mouse.absolutePosition({x = point.x + 1, y = point.y})
    hs.timer.usleep(100000)
    hs.mouse.absolutePosition(point)
end

local function isWithinSchedule()
    local now = os.date("*t")
    local hour, min, wday = now.hour, now.min, now.wday
    return wday >= 2 and wday <= 6 and (hour > 8 or (hour == 8 and min >= 0)) and (hour < 16 or (hour == 16 and min <= 30))
end

local function manageCaffeinate()
    if isWithinSchedule() then
        if not caffeinateActive then
            caffeinate.set("displayIdle", true, true)
            caffeinate.set("systemSleep", true, true)
            caffeinateActive = true
            hs.alert("☕️ Caffeinate enabled (scheduled)")
        end
    else
        if caffeinateActive then
            caffeinate.set("displayIdle", false, true)
            caffeinate.set("systemSleep", false, true)
            caffeinateActive = false
            hs.alert("💤 Caffeinate disabled (outside schedule)")
        end
    end
end

local function scheduledJiggler()
    manageCaffeinate()
    if isWithinSchedule() then
        if not jigglerTimer then
            jigglerTimer = hs.timer.doEvery(jiggleInterval, jiggleMouse)
            hs.alert("✅ Jiggler started (scheduled)")
        end
    else
        if jigglerTimer then
            jigglerTimer:stop()
            jigglerTimer = nil
            hs.alert("🛑 Jiggler stopped (outside schedule)")
        end
    end
end

-- Check every 5 minutes
hs.timer.doEvery(300, scheduledJiggler)
scheduledJiggler() -- Initial check
