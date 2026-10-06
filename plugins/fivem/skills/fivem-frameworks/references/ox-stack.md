# ox_lib, ox_inventory, ox_target, oxmysql - traps

Read when using the ox stack. Current upstream: github.com/overextended (ox_lib 3.40.0, ox_inventory 2.48.0, ox_target 1.18.1, oxmysql 2.14.3; docs overextended.dev). If a server still runs CommunityOx builds (ox_lib <= 3.32.x, docs coxdocs.dev), APIs added after early 2026 (e.g. ox_lib "replication modes", event hooks API, DataView) are missing.

## Install / start order

```
ensure oxmysql
ensure ox_lib
ensure <framework core>     # es_extended / qbx_core / ox_core
ensure ox_target
ensure ox_inventory
```
- Download the **release zip** (`.../releases/latest/download/ox_lib.zip`). Cloning the repo gives no built `web/build` -> NUI broken (`ui_page` 404) unless you build with bun.
- Minimum artifacts: ox_lib `/server:7290` + OneSync, ox_inventory `/server:6116` + OneSync, oxmysql `/server:12913` (Node 22).

## ox_lib

```lua
-- fxmanifest
shared_script '@ox_lib/init.lua'
ox_libs { 'locale', 'math' }      -- optional preload

-- lazy modules: first access of lib.x loads imports/x
local zone = lib.zones.box({ coords = vec3(0, 0, 0), size = vec3(4, 4, 3), rotation = 0,
    onEnter = function() lib.showTextUI('[E] Open') end,
    onExit = function() lib.hideTextUI() end,
    inside = function() if IsControlJustReleased(0, 38) then openMenu() end end })

local point = lib.points.new({ coords = shopCoords, distance = 30 })
function point:nearby() DrawMarker(...) end         -- runs every frame only while near

lib.onCache('vehicle', function(veh) end)          -- cache.vehicle changes
```

Traps:
- Client `lib.callback.await(name, delay, ...)`: `delay` is a throttle (ms or `false`). Passing data as 2nd arg silently eats it.
- Server `lib.callback.register(name, function(source, ...) return ... end)` - return values are sent back; errors print `SCRIPT ERROR` and return nothing. Default timeout `ox:callbackTimeout` 300000 ms.
- `require` (ox_lib) loads `@resource.path.module` style modules: `require '@qbx_core.modules.lib'` or relative `require 'client.utils'` (dots, no `.lua`). Files must be listed in `files` for client-side require.
- `lib.addCommand` with `restricted = 'group.admin'` uses ACE; ox_lib needs `add_ace resource.ox_lib command.add_ace allow` (+ `remove_ace`, `add_principal`, `remove_principal`) or permissions silently fail.
- Notify from server: `TriggerClientEvent('ox_lib:notify', src, { title = 'x', type = 'success' })`. Server-side `lib.notify(src, data)` is marked deprecated.
- `zone.inside` / `point:nearby` run per frame while active - keep them cheap.
- Strict-mode warning on start (3.37+): set `setr sv_stateBagStrictMode true` or `set ox:ignoreSecurityAdvisory ["stateBagStrictMode"]`.
- UI theme convars: `setr ox:primaryColor blue`, `setr ox:primaryShade 8`, `setr ox:userLocales 1`; locale `setr ox:locale de`.

## ox_inventory (server API)

```lua
local ox = exports.ox_inventory
if not ox:CanCarryItem(src, 'water', 2) then return end
local ok, resp = ox:AddItem(src, 'water', 2, { quality = 100 })   -- ok=false, resp='inventory_full' etc.
local removed = ox:RemoveItem(src, 'money', price)                 -- false + 'not_enough_items'
local count = ox:GetItemCount(src, 'lockpick')
local slots = ox:Search(src, 'slots', 'weapon_pistol')
ox:RegisterStash('police_evidence', 'Evidence', 100, 100000, nil, { police = 0 })
-- server item callback (items.lua: server = { export = 'myres.useBandage' }):
exports('useBandage', function(event, item, inventory, slot, data)
    if event == 'usingItem' then return true end   -- return false to cancel; also called with 'usedItem', 'buying'
end)
ox:registerHook('swapItems', function(payload) return true end, { itemFilter = { money = true } })
```
Traps:
- `setr inventory:framework` must be `esx`, `qbx`, `ox` or `nd` - no `qb`. Plain qb-core is unsupported.
- Items are defined in `ox_inventory/data/items.lua` (+ weapons.lua). Adding them only to the framework's items table/DB does nothing.
- Money is an item (`money`) by default (`inventory:accounts`); framework cash and ox `money` are synced by the bridge - don't modify both.
- Client UI image path: `nui://ox_inventory/web/images/<item>.png` (`inventory:imagepath`).
- Weapons are items; ESX loadouts / `GiveWeaponToPed` from scripts get stripped. Give weapons via `AddItem(src, 'WEAPON_PISTOL', 1)`.
- Convert old data once: `convertinventory esx` / `convertinventory esxproperty` (ESX), Qbox recipe handles qb data.

## ox_target (client)

```lua
exports.ox_target:addBoxZone({
    coords = vec3(441.0, -981.0, 30.7), size = vec3(1.5, 1.5, 2.0), rotation = 0,
    options = {{
        name = 'mdt', label = 'Open MDT', icon = 'fa-solid fa-laptop', distance = 2.0,
        groups = { police = 0 },                       -- framework job/gang check (client-side only!)
        onSelect = function(data) TriggerServerEvent('mdt:server:open') end,
    }},
})
exports.ox_target:addGlobalVehicle({{ name = 'trunk', label = 'Trunk', bones = { 'boot' }, onSelect = fn }})
exports.ox_target:addLocalEntity(ped, options)        -- non-networked entity
exports.ox_target:addEntity(netIds, options)          -- networked, by net id
exports.ox_target:addModel(`prop_atm_01`, options)
exports.ox_target:removeZone(id)
```
Traps:
- `groups`/`items`/`canInteract` only hide options client-side. The server handler must re-check job, distance and items.
- `serverEvent` options send `data.entity` as a **net ID**, other actions get the local handle.
- Compat: ox_target provides only `qtarget`; `exports['qb-target']` calls break - convert to ox_target exports.
- ox_target removes a stopped resource's zones/options itself (`onClientResourceStop`); manual `remove*` is only needed when options change at runtime. Give options a `name` so they can be removed.

## oxmysql details

- Connection string: `set mysql_connection_string "mysql://user:pass@127.0.0.1:3306/db?charset=utf8mb4"` or `"user=...;password=...;host=...;port=3306;database=..."`. Avoid `; , / ? : @ & = + $ #` in the password or switch format. Use `set`, never `setr`/`sets`.
- MariaDB recommended over MySQL 8 (MySQL 8 reserves words like `group`/`stored`, no defaults on LONGTEXT/JSON) - quote columns with backticks.
- Errors print `Unable to establish a connection to the database (CODE)!` (see fivem-performance-debugging common errors).
- `MySQL.prepare` = server-side prepared statements, `?` only; fastest for hot queries. `MySQL.rawExecute` returns raw result.
- `MySQL.Sync.*`/`MySQL.Async.*` aliases exist for compatibility only.
