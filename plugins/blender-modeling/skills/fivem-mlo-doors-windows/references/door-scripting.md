# Door scripting: own resource, ox_doorlock, qb-doorlock

Read when writing Lua for MLO doors or configuring a doorlock resource. Conventions: CfxLua 5.4, server-authoritative
state, `local src = source` first (see `fivem-resource-dev`, `fivem-security`).

## Facts the code relies on

- Door natives are **client-only** game natives. Calling them on the server gives `attempt to call a nil value (global 'AddDoorToSystem')`.
- `AddDoorToSystem(hash, model, x, y, z, false, false, false)` creates a local entry. The natives doc says a
  "localized" door system with hundreds or thousands of doors is fine this way, provided you sync the states yourself.
  `scriptDoor = true` registers on the script host and has a hard cap on script IDs.
- A state set before the door streams in is kept and applied once `DoorSystemGetIsPhysicsLoaded` is true.
- Map/MLO doors are not networked entities. There is no `Entity(door).state` across clients, so use **GlobalState**
  (bag name `global`) or events. With `sv_stateBagStrictMode true`, only the server writes it, which is what you want.
- Use a stable hash per door: `joaat('mlodoor_<id>_<n>')`. Never register the same physical door in two resources
  (for example ox_doorlock and your script), or the states fight. Check `DoorSystemFindExistingDoor` first.
- ox_doorlock and qb-doorlock both call `DoorSystemSetDoorState(h, 4)` once before the real state, to snap the door to
  its closed pose. ox_doorlock also does this when you add a door with `/doorlock`, so the stored coords are from the closed pose.

## Own resource (doors, double doors, garage with keypad + remote)

```
mlo_doors/
  fxmanifest.lua
  shared/config.lua
  client/main.lua
  server/main.lua
```

```lua
-- fxmanifest.lua
fx_version 'cerulean'
games { 'gta5', 'gta5enhanced' }     -- cross-platform manifest (see fivem-gta5-enhanced)
lua54 'yes'
shared_scripts { '@ox_lib/init.lua', 'shared/config.lua' }
client_script 'client/main.lua'
server_script 'server/main.lua'
dependencies { 'ox_lib', 'ox_target' }
```

```lua
-- shared/config.lua (clients can read this file: no PINs here)
Config = {}

-- coords = world position of each door OBJECT in its closed pose (read in game, never from Blender)
Config.Doors = {
    office = {
        parts = { { model = `my_mlo_door_01`, coords = vec3(-551.32, -191.88, 38.22) } },
        locked = true, jobs = { police = 0 }, maxDistance = 2.0,
    },
    lobby = {                                         -- double door: one state, two leaves
        parts = {
            { model = `my_mlo_door_l`, coords = vec3(-548.10, -195.02, 38.22) },
            { model = `my_mlo_door_r`, coords = vec3(-546.30, -195.02, 38.22) },
        },
        locked = false, jobs = { police = 0 }, maxDistance = 2.5,
    },
    garage = {
        parts = { { model = `my_mlo_garage_01`, coords = vec3(-560.40, -180.12, 37.95) } },
        garage = true, rate = 1.0, locked = true, jobs = { mechanic = 0 },
        keypad = vec3(-557.80, -181.60, 38.90), maxDistance = 2.0,
        remoteItem = 'garage_remote', remoteDistance = 25.0,
        pinProtected = true,                          -- the PIN itself is a server convar
    },
}
```

```lua
-- server/main.lua
local Doors = Config.Doors
local PINS = { garage = GetConvar('mlodoors_pin_garage', '') }   -- server.cfg: set mlodoors_pin_garage "4711" (set, NOT setr)
local nextUse = {}

for id, door in pairs(Doors) do
    GlobalState['mlodoor:' .. id] = door.locked and 1 or 0       -- 1 locked/closed, 0 unlocked/open
end

local ESX = GetResourceState('es_extended') == 'started' and exports.es_extended:getSharedObject()

local function getJob(src)                                         -- full bridge: fivem-frameworks
    if GetResourceState('qbx_core') == 'started' then
        local p = exports.qbx_core:GetPlayer(src)
        if p then return p.PlayerData.job.name, p.PlayerData.job.grade.level end
    elseif ESX then
        local x = ESX.GetPlayerFromId(src)
        if x then return x.job.name, x.job.grade end
    end
end

local function hasAccess(src, door)
    if IsPlayerAceAllowed(src, 'mlodoors.admin') then return true end
    local job, grade = getJob(src)
    local min = job and door.jobs and door.jobs[job]
    return min ~= nil and grade >= min
end

RegisterNetEvent('mlodoors:server:toggle', function(id, via, pin)
    local src = source
    local now = GetGameTimer()
    if (nextUse[src] or 0) > now then return end                   -- also slows PIN brute force
    nextUse[src] = now + 1000

    local door = type(id) == 'string' and Doors[id]
    if not door then return end
    local pos = GetEntityCoords(GetPlayerPed(src))

    if via == 'remote' then
        if not door.remoteItem then return end
        if #(pos - door.parts[1].coords) > door.remoteDistance then return end
        if exports.ox_inventory:Search(src, 'count', door.remoteItem) < 1 then return end
    else
        if #(pos - (door.keypad or door.parts[1].coords)) > door.maxDistance + 1.0 then return end
        if not hasAccess(src, door) then
            local real = PINS[id]
            if not (door.pinProtected and real and real ~= '' and pin == real) then return end
        end
    end

    local key = 'mlodoor:' .. id
    GlobalState[key] = GlobalState[key] == 1 and 0 or 1
end)

AddEventHandler('playerDropped', function() nextUse[source] = nil end)
```

```lua
-- client/main.lua
local registered = {}                                              -- id -> { doorHash, ... }

local function apply(id, state)
    local door, hashes = Config.Doors[id], registered[id]
    if not door or not hashes then return end
    for i = 1, #hashes do
        local h = hashes[i]
        if door.garage then
            DoorSystemSetAutomaticRate(h, door.rate or 1.0, false, true)
            DoorSystemSetOpenRatio(h, state == 0 and 1.0 or 0.0, false, true)   -- target (verify per model)
            DoorSystemSetDoorState(h, 1, false, true)                            -- locked = held at the ratio
        else
            DoorSystemSetDoorState(h, state, false, false)
        end
    end
end

local function register(id, door)
    local hashes = {}
    for i, part in ipairs(door.parts) do
        local h = joaat(('mlodoor_%s_%d'):format(id, i))
        if not IsDoorRegisteredWithSystem(h) then
            AddDoorToSystem(h, part.model, part.coords.x, part.coords.y, part.coords.z, false, false, false)
        end
        DoorSystemSetDoorState(h, 4, false, false)                 -- snap closed once
        hashes[i] = h
    end
    registered[id] = hashes
    apply(id, GlobalState['mlodoor:' .. id] or 1)                  -- late joiners get the current state
end

CreateThread(function()
    for id, door in pairs(Config.Doors) do register(id, door) end
end)

AddStateBagChangeHandler(nil, 'global', function(_, key, value)
    local id = key:match('^mlodoor:(.+)$')
    if id then apply(id, value) end
end)

-- keypad (ox_target zone; groups/canInteract would only be UX - the server re-checks)
for id, door in pairs(Config.Doors) do
    if door.keypad then
        exports.ox_target:addSphereZone({
            coords = door.keypad, radius = 0.35,
            options = {{
                name = 'mlodoor_keypad_' .. id, icon = 'fa-solid fa-keyboard', label = 'Keypad',
                distance = door.maxDistance,
                onSelect = function()
                    local pin
                    if door.pinProtected then
                        local input = lib.inputDialog('Keypad', { { type = 'input', label = 'PIN', password = true } })
                        if not input then return end
                        pin = input[1]
                    end
                    TriggerServerEvent('mlodoors:server:toggle', id, 'keypad', pin)
                end,
            }},
        })
    end
end

-- vehicle remote (user-rebindable key)
RegisterCommand('garageremote', function()
    local pos = GetEntityCoords(cache.ped)
    for id, door in pairs(Config.Doors) do
        if door.remoteItem and #(pos - door.parts[1].coords) <= door.remoteDistance then
            return TriggerServerEvent('mlodoors:server:toggle', id, 'remote')
        end
    end
end, false)
RegisterKeyMapping('garageremote', 'Garage remote', 'keyboard', 'G')

AddEventHandler('onResourceStop', function(res)
    if res ~= cache.resource then return end
    for _, hashes in pairs(registered) do
        for i = 1, #hashes do
            DoorSystemSetDoorState(hashes[i], 0, false, false)
            RemoveDoorFromSystem(hashes[i])
        end
    end
end)
```

If the garage model ignores the ratio + lock pattern, replace the garage branch with the qb-doorlock pattern:
`state 0` → `DoorSystemSetAutomaticDistance(h, 15.0, false, true)` + `DoorSystemSetDoorState(h, 0, ...)`;
`state 1` → distance `0.0` + state `1`. That door then opens for anyone near it while unlocked.

## ox_doorlock (overextended, 1.22.1, 2026-07)

- Requires oxmysql + ox_lib (>= 3.30.4). Doors live in the `ox_doorlock` table (`id`, `name`, `data` JSON). There is
  no config list; old nui_doorlock files can go in `convert/`.
- Add doors in game: `/doorlock` (restricted to `Config.CommandPrincipal`, default `group.admin`) > fill the form >
  aim at the door(s) and press LMB. Only object entities (type 3) can be picked. A model that is not streamed
  (`IsModelValid` false) is silently ignored.
- Players press E (control 38) within `maxDistance` (`Config.DrawTextUI` / `DrawSprite` for prompts). Lockpicking
  goes through an ox_target global object option (`Config.LockpickItems`).

```lua
-- server: create once (each call INSERTs a row)
if not exports.ox_doorlock:getDoorFromName('mlo lobby') then
    exports.ox_doorlock:createDoor({
        name = 'mlo lobby',
        doors = {                                                   -- double door
            { model = `my_mlo_door_l`, coords = vec3(-548.10, -195.02, 38.22), heading = 90 },
            { model = `my_mlo_door_r`, coords = vec3(-546.30, -195.02, 38.22), heading = 270 },
        },
        state = 1, maxDistance = 2.5,
        groups = { police = 0 },                                    -- { job = minGrade }
        items = { { name = 'keycard', remove = false } },
        autolock = 30,                                              -- seconds
    })
end
```

| Field | Notes |
|---|---|
| `model`, `coords`, `heading` / `doors = {{model, coords, heading}, {...}}` | single vs double; door hashes become `ox_door_<id>` / `ox_door_<id>_<n>` |
| `state` | 1 locked (default), 0 unlocked |
| `maxDistance` | interact distance; the UI defaults to 2, the export has no default, so always set it |
| `auto`, `doorRate`, `holdOpen` | automatic doors (garage/sliding/barrier) |
| `autolock` | seconds until it relocks |
| `groups`, `items`, `characters`, `passcode` | authorization (server-side) |
| `lockpick`, `lockpickDifficulty`, `hideUi`, `lockSound`, `unlockSound` | |

Server API: `getDoor(id)`, `getAllDoors()`, `getDoorFromName(name)`, `editDoor(id, data)`, `createDoor(data)` → id,
`removeDoor(id)`, `setDoorState(id, state, lockpick?)`. Event `ox_doorlock:stateChanged(source, doorId, isLocked, usedItem)`.
Client exports: `useClosestDoor()`, `pickClosestDoor()`, `getClosestDoor()`, `getClosestDoorId()`,
`getDoorIdFromEntity(entity)` (same as `Entity(entity).state.doorId`).

ACE per door: `add_ace group.police "doorlock.mlo lobby" allow`. With `Config.PlayerAceAuthorised = true`, holders of
`command.doorlock` can use every door.

Security traps (read in the 1.22.1 source):
- `ox_doorlock:setState` checks authorization, but **not the player's distance** to the door.
- `registerHook('doorAuthorization', fn, { nameFilter = '^vault' })` can return `true` to grant, but returning `false`
  does not revoke access already granted by groups/items (`return authorised or hookResult == nil or hookResult`).
- Server-side `TriggerEvent('ox_doorlock:setState', id, state)` runs with an empty `source` and skips authorization.
  Validate in your own handler first.

## qb-doorlock (qbcore-framework, 2026-08)

```lua
Config.DoorList['mlo-office'] = {
    objName = 'my_mlo_door_01', objCoords = vec3(-551.32, -191.88, 38.22), objYaw = 90.0,
    doorType = 'door',                -- 'door' | 'double' | 'sliding' | 'doublesliding' | 'garage'
    authorizedJobs = { ['police'] = 0 }, locked = true, distance = 2.0, doorRate = 1.0,
    -- also: authorizedGangs, authorizedCitizenIDs, items, pickable, autoLock (ms), hideLabel, audioLock/audioUnlock
}
```
- Doors are registered within 30 m and removed from the system beyond that. `GetClosestObjectOfType` uses a 1.0 m
  radius (5.0 m for sliding/garage), so the coords must be close.
- Security (source commit `4a8e911`, 2026-08-24): the net event `qb-doorlock:server:updateState(doorID, locked,
  src, usedLockpick, unlockAnyway, enableSounds, enableAnimation, sentSource)` trusts several client arguments.
  `unlockAnyway = true` skips authorization, `usedLockpick = true` passes on pickable doors, and `sentSource`
  replaces `source`. It has no distance check either. Do not protect valuables with it unless you patch the handler
  (see `fivem-security`).
