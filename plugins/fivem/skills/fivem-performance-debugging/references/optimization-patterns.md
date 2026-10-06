# Optimisation recipes

Read when rewriting a hot loop or a resource shows high ms in resmon / the server profiler.

## 1. Vehicle HUD / speedometer (per-frame only while in a vehicle)

```lua
-- WRONG: Wait(0) forever, natives every frame even on foot, NUI message every frame
CreateThread(function()
    while true do
        Wait(0)
        local veh = GetVehiclePedIsIn(PlayerPedId(), false)
        SendNUIMessage({ speed = GetEntitySpeed(veh) * 3.6 })
    end
end)

-- RIGHT (ox_lib): start a loop only when entering a vehicle, send only changes, ~10 Hz
lib.onCache('vehicle', function(veh)
    if not veh then return SendNUIMessage({ action = 'hud', show = false }) end
    CreateThread(function()
        local last
        while cache.vehicle == veh do
            local speed = math.floor(GetEntitySpeed(veh) * 3.6)
            if speed ~= last then
                last = speed
                SendNUIMessage({ action = 'speed', value = speed })
            end
            Wait(100)
        end
    end)
end)
```
Without ox_lib: one thread polls `GetVehiclePedIsIn(PlayerPedId(), false)` every 500 ms and starts the fast loop when it changes. (`baseevents:enteredVehicle`/`leftVehicle` are **server** events sent by the client - useless for client HUDs and spoofable.)

## 2. Markers / interaction points

- `lib.points.new({ coords = c, distance = 20 })` + `function point:nearby() DrawMarker(...) end` - only near points tick per frame.
- Without ox_lib: one thread, distance-sorted check every 500-1000 ms, a separate per-frame draw loop only while `closest` is within range.

## 3. Disabling controls while UI open

Per-frame `DisableControlAction` is required while open; stop the loop when closed:
```lua
local function holdControls()
    CreateThread(function()
        while isOpen do
            DisableControlAction(0, 24, true)   -- attack
            DisableControlAction(0, 25, true)   -- aim
            Wait(0)
        end
    end)
end
```

## 4. Player iteration

- Client: `for _, ply in ipairs(GetActivePlayers()) do` (only players in scope).
- Server: keep your own `players[src] = data` table maintained via `playerJoining`/framework loaded events and `playerDropped`; don't call `GetPlayers()` + per-player natives every tick.
- Need "who is near X" on the server: `GetEntityCoords(GetPlayerPed(src))` per player at low frequency, or ox_lib `lib.getNearbyPlayers(coords, radius)` server-side.

## 5. Entity enumeration

`GetGamePool('CVehicle')` returns all vehicle handles; filter with `#(coords - GetEntityCoords(v))`. Run on demand (button press) or at <= 1 Hz, never per frame. `lib.getClosestVehicle(coords, maxDist)` wraps this.

## 6. Model / dict loading

```lua
local function loadModel(model)
    if not IsModelInCdimage(model) then return false end
    RequestModel(model)
    local timeout = GetGameTimer() + 5000
    while not HasModelLoaded(model) do
        if GetGameTimer() > timeout then return false end
        Wait(0)
    end
    return true
end
-- after creating the entity:
SetModelAsNoLongerNeeded(model)
```
ox_lib: `lib.requestModel(model, timeout)`, `lib.requestAnimDict(dict)`.

## 7. Database

- Cache static tables at boot; avoid per-request `SELECT` of config-like data.
- Hot write paths: keep in memory, flush on interval and on `playerDropped`; use `MySQL.prepare.await(query, { {..}, {..} })` with multiple parameter sets for batches, or `MySQL.transaction`.
- Add indexes for `WHERE` columns (`identifier`, `citizenid`, `owner`, `plate`).
- Never run queries in client-triggered loops without a rate limit.

## 8. State bags instead of polling events

Replace "server sends update every second to everyone" with a state bag set on change; clients react in `AddStateBagChangeHandler` only for entities in scope.

## 9. Threads hygiene

- One thread per concern; exit loops when the feature is inactive (`while active do ... end`).
- `SetTimeout(ms, fn)` for one-shot delays instead of a thread with `Wait`.
- Don't create a new thread per event in high-frequency events; queue work.

## 10. NUI

- Unmount hidden views; avoid CSS `backdrop-filter`, large box-shadows, infinite animations.
- Batch `SendNUIMessage` (one message with all HUD values) and send only on change.
- Prefer local assets in the resource over remote URLs.
