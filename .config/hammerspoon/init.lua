---------------------------------------------------------
-- CONFIGURATION WATCHER
---------------------------------------------------------
function reloadConfig(files)
	for _, f in ipairs(files) do
		if f:sub(-4) == ".lua" then
			hs.reload()
			return
		end
	end
end

-- Using global variable to prevent garbage collection
-- Standard path: ~/.hammerspoon/
systemWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
hs.alert.show("System Configuration Active")

---------------------------------------------------------
-- WINDOW LAYOUT (25/50/25 Symmetrical Split)
---------------------------------------------------------
hs.window.animationDuration = 0

local function setLayout(pos)
	local win = hs.window.focusedWindow()
	if not win then
		return
	end

	local screenFrame = win:screen():frame()
	local sideWidth = screenFrame.w * 0.25
	local centerWidth = screenFrame.w * 0.50

	if pos == "left" then
		win:setFrame({ x = screenFrame.x, y = screenFrame.y, w = sideWidth, h = screenFrame.h })
	elseif pos == "center" then
		win:setFrame({ x = screenFrame.x + sideWidth, y = screenFrame.y, w = centerWidth, h = screenFrame.h })
	elseif pos == "right" then
		win:setFrame({
			x = screenFrame.x + sideWidth + centerWidth,
			y = screenFrame.y,
			w = sideWidth,
			h = screenFrame.h,
		})
	end
end

hs.hotkey.bind({ "alt" }, "Left", function()
	setLayout("left")
end)
hs.hotkey.bind({ "alt" }, "Up", function()
	setLayout("center")
end)
hs.hotkey.bind({ "alt" }, "Right", function()
	setLayout("right")
end)

---------------------------------------------------------
-- SYSTEM PERSISTENCE (Active State Management)
---------------------------------------------------------
persistenceTimer = persistenceTimer or nil
isSystemActive = isSystemActive or false

local function maintainActiveState()
	-- Substantial cursor movement to register as HID activity
	local currentPos = hs.mouse.absolutePosition()
	hs.mouse.setAbsolutePosition({ x = currentPos.x + 40, y = currentPos.y + 40 })
	hs.timer.usleep(50000)
	hs.mouse.setAbsolutePosition(currentPos)

	-- Register a hardware-level keystroke (Shift)
	hs.eventtap.keyStroke({}, "shift")
end

local function checkSchedule()
	local date = os.date("*t")
	local isWorkDay = date.wday >= 2 and date.wday <= 6
	local timeValue = date.hour * 100 + date.min
	return isWorkDay and (timeValue >= 800 and timeValue <= 1830)
end

function updatePersistence()
	if checkSchedule() then
		if not isSystemActive then
			-- Prevents display sleep and idle timeout
			hs.caffeinate.set("displayIdle", true, true)
			isSystemActive = true
			hs.alert("Persistence: Enabled")
		end
		if not persistenceTimer then
			persistenceTimer = hs.timer.doEvery(60, maintainActiveState)
		end
	else
		if isSystemActive then
			hs.caffeinate.set("displayIdle", false, true)
			isSystemActive = false
			hs.alert("Persistence: Disabled")
		end
		if persistenceTimer then
			persistenceTimer:stop()
			persistenceTimer = nil
		end
	end
end

-- Refresh schedule every minute
scheduleMonitor = hs.timer.doEvery(120, updatePersistence)
updatePersistence()
