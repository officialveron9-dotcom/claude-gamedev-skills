---
name: fivem-resource-dev
description: Writes and reviews FiveM (Cfx.re, GTA V Legacy) resources correctly - fxmanifest.lua (fx_version cerulean, game gta5, lua54, shared/client/server scripts, files, ui_page, dependencies, provide, data_file), CfxLua 5.4 specifics (vector3, backtick joaat hashes, CreateThread/Wait, compound operators), net events (RegisterNetEvent vs AddEventHandler, TriggerServerEvent/TriggerClientEvent, capturing source), callbacks, exports, state bags (Entity().state, Player().state, GlobalState, AddStateBagChangeHandler), NUI (SendNUIMessage, RegisterNUICallback, SetNuiFocus), KVP, convars, routing buckets, OneSync entity ownership and server-side spawning, JS/C# runtimes. Use for any FiveM Lua/JS/C# script, __resource.lua migration or NUI work, also when the user writes German like "FiveM Script schreiben", "Resource erstellen", "Event triggern", "NUI Fenster".
---

# FiveM resource development (Legacy platform, state 2026-10)

Applies to FXServer artifacts on the regular (Legacy / Gen8) FiveM platform. For FiveM on GTA V Enhanced (early access since 2026-07-21) differences exist - see the `fivem-gta5-enhanced` skill if present.

## Non-negotiables

1. Server is authoritative. Anything a client sends is an untrusted request (see `fivem-security`).
2. `fxmanifest.lua` only. `__resource.lua` + `resource_manifest_version` is deprecated; the server warns `"<res> has an outdated manifest (__resource.lua instead of fxmanifest.lua)"`.
3. Never block a thread: every `while true do` needs a `Wait(n)`.
4. Capture `source` into a local at the top of every server net-event handler, before any yield.
5. Do not invent natives. Native names exist in two sets: game natives (`citizenfx/natives`) and CFX natives (`citizenfx/fivem` `ext/native-decls`, with `apiset: client|server|shared`). A client-only native called on the server errors with `attempt to call a nil value (global 'X')`.

## Minimal current manifest

```lua
fx_version 'cerulean'          -- current FXv2 version; 'adamant'/'bodacious' are older
game 'gta5'                    -- or games { 'gta5', 'rdr3' }; 'common' = no game natives
lua54 'yes'                    -- no-op since June 2025 (all Lua is 5.4); harmless, many libs still declare it

name 'my_resource'
author 'me'
version '1.0.0'

shared_scripts {
    '@ox_lib/init.lua',        -- only if ox_lib is used; must come first, loaded once
    'shared/*.lua',
}
client_scripts { 'client/*.lua' }
server_scripts {
    '@oxmysql/lib/MySQL.lua',  -- only if oxmysql is used
    'server/*.lua',
}

ui_page 'web/dist/index.html'
files { 'web/dist/index.html', 'web/dist/**/*' }   -- every client-side non-script file must be listed

dependencies {
    '/server:12913',           -- min artifact (12913 = Node 22 available)
    '/onesync',
    'ox_lib',
}
```

Order of entries in `client_scripts`/`server_scripts` is load order. Globs (`*.lua`, `**/*.lua`) load alphabetically. Full directive list incl. `provide`, `data_file`, `this_is_a_map`, `server_only`, `node_version`, `use_experimental_fxv2_oal`, `escrow_ignore`, `loadscreen`: [references/manifest.md](references/manifest.md) - read when writing or reviewing a manifest.

## CfxLua essentials

- Lua 5.4 with extensions: `vector2/3/4`, `quat`, `#(a - b)` for distance, backtick hashes `` `adder` `` (compile-time joaat), `joaat('x')` at runtime, compound ops `+=`, `-=`, safe navigation `t?.x?.y`, `local a, b in t`. Standard luacheck/LuaLS flag these - use the CfxLua IntelliSense / fivem-lls-addon definitions.
- Globals `CreateThread`, `Wait`, `SetTimeout`, `ClearTimeout` alias `Citizen.*`; the `Citizen.` prefix is optional. `RegisterServerEvent` is an alias of `RegisterNetEvent`.
- Libraries in scope: `json` (dkjson), `msgpack`, `promise` (+ `Citizen.Await(p)`).
- `GetPlayers()` (server) returns **strings**; `tonumber()` before arithmetic/comparison.
- `GetHashKey('x')` == `` `x` `` == `joaat('x')`; prefer backticks for literals.

## Events

| Need | Use |
|---|---|
| Same-side only (client->client, server->server) | `AddEventHandler(name, fn)` - not callable over the network |
| Cross-network | `RegisterNetEvent(name, fn)` - marks it safe for net; still callable locally |
| Client -> server | `TriggerServerEvent(name, ...)` |
| Server -> client(s) | `TriggerClientEvent(name, target, ...)` (`-1` = everyone) |
| Large payloads | `TriggerLatentClientEvent(name, target, bps, ...)` / `TriggerLatentServerEvent(name, bps, ...)` |

A net event without `RegisterNetEvent` prints `event X was not safe for net` and is dropped.

```lua
-- WRONG: source is a global swapped per event; after a yield it belongs to someone else
RegisterNetEvent('shop:buy', function(item)
    local price = MySQL.scalar.await('SELECT price FROM items WHERE name = ?', { item })
    TriggerClientEvent('shop:bought', source, item)
end)

-- RIGHT
RegisterNetEvent('shop:buy', function(item)
    local src = source
    if type(item) ~= 'string' then return end
    local price = MySQL.scalar.await('SELECT price FROM items WHERE name = ?', { item })
    if not price then return end
    TriggerClientEvent('shop:bought', src, item)
end)
```

Client side: events coming from the server have `source == 65535`; to reject local/injected triggers of a server-only client event check `if source ~= 65535 then return end` (not bulletproof - the client is untrusted anyway).

Name events `resource:side:action` (e.g. `garage:server:storeVehicle`) to avoid collisions.

## Callbacks (request/response)

Plain FiveM has none; use ox_lib unless the codebase is pinned to a framework's own API.

```lua
-- server
lib.callback.register('garage:getVehicles', function(source, garageId)
    return MySQL.query.await('SELECT plate, model FROM owned_vehicles WHERE owner = ? AND garage = ?',
        { GetPlayerIdentifierByType(source, 'license'), garageId })
end)
-- client (yields the current thread)
local vehicles = lib.callback.await('garage:getVehicles', false, 'pillbox')
```

Server -> client: `lib.callback.await('name', playerId, ...)`. ESX: `ESX.TriggerServerCallback` / `ESX.RegisterServerCallback`; QBCore: `QBCore.Functions.TriggerCallback` / `CreateCallback`. Treat callback args exactly like net-event args (untrusted).

## Exports

```lua
-- provider (server or client file)
exports('getBalance', function(identifier) return balances[identifier] or 0 end)
-- consumer
local bal = exports.my_bank:getBalance(id)        -- colon syntax required
local x   = exports['my-res']:fn()                -- bracket form for names with '-'
```

`No such export X in resource Y` = provider not started yet, wrong side (client vs server), typo, or the provider crashed during load. Fix ordering with `dependency` + `ensure` order.

## State bags (OneSync)

```lua
Entity(veh).state:set('fuel', 42.0, true)   -- server: replicated to clients
Player(src).state:set('job', 'police', true)
GlobalState.weather = 'RAIN'                 -- server-write, all clients read
LocalPlayer.state.isLoggedIn                 -- client read of own player bag

AddStateBagChangeHandler('fuel', nil, function(bagName, key, value, _, replicated)
    local ent = GetEntityFromStateBagName(bagName)
    if ent == 0 then return end              -- not in scope on this client
end)
```

Rules: assignment via `.state.x = v` replicates from server, not from clients; `:set(key, value, replicate)` controls it. Nested mutation `state.x.y = 1` does **not** replicate - set the whole value or use flat keys `state['x:y']`. Handlers fire with the old value still stored. With `setr sv_stateBagStrictMode true` (server >= 12739) clients cannot write replicated bags at all - prefer it and write state server-side. Details: [references/networking-state.md](references/networking-state.md).

## OneSync, entities, routing buckets

- Spawn persistent/important entities on the server: `CreateVehicleServerSetter(model, type, x, y, z, h)` (reliable; `type` from vehicles.meta: `automobile`, `bike`, `boat`, `heli`, `plane`, `submarine`, `trailer`, `train`), server `CreatePed`/`CreateObjectNoOffset`; then `SetEntityOrphanMode(ent, 2)` to stop server cleanup.
- Pass entities across the network as **net IDs** (`NetworkGetNetworkIdFromEntity`); on the client check `NetworkDoesEntityExistWithNetworkId(netId)` before `NetworkGetEntityFromNetworkId` (entities outside ~424 units are culled).
- The owner client simulates an entity; server `NetworkGetEntityOwner(ent)`. Do not rely on `NetworkRequestControlOfEntity` - with `sv_filterRequestControl` it is blocked.
- Routing buckets (server): `SetPlayerRoutingBucket(src, b)`, `SetEntityRoutingBucket(ent, b)`, `SetRoutingBucketEntityLockdownMode(b, 'strict')`, `SetRoutingBucketPopulationEnabled(b, false)`. Use for instances/char-select, not interiors.

## NUI quick rules

- `SendNUIMessage({ action = 'open', data = t })` -> page `window.addEventListener('message', e => ...)`.
- Page -> Lua: `fetch(\`https://${GetParentResourceName()}/close\`, { method: 'POST', body: JSON.stringify(x) })` + `RegisterNUICallback('close', function(data, cb) ... cb({ ok = true }) end)`. **Always call `cb`**, else the fetch hangs.
- Asset URLs inside the page: `https://cfx-nui-<resource>/path` (old `nui://` is not a secure context). That prefix is for files, not for callbacks.
- `SetNuiFocus(true, true)` to take keyboard+mouse; always release on close/resource stop. Devtools: `nui_devTools` (F8) or `http://localhost:13172`.
More in [references/nui.md](references/nui.md).

## KVP and convars

- `SetResourceKvp`/`GetResourceKvpString`/`...Int`/`...Float`, `DeleteResourceKvp`, prefix scan with `StartFindKvp`/`FindKvp`/`EndFindKvp`. Per resource. Client KVP lives on the player's PC (player-editable): only preferences. Server KVP file name via `sv_kvsName`; `*NoSync` + `FlushResourceKvp` for bulk writes.
- `GetConvar(name, default)` (string), `GetConvarInt`, `GetConvarFloat`, `GetConvarBool`. `set` = server only, `setr` = replicated to clients, `sets` = public server info. Never put secrets in `setr`/`sets`. `add_convar_permission res read name` restricts reads.

## Sandbox (server Lua/JS, since late 2024)

`io.open`/`SaveResourceFile` may write only inside the own resource; `..` traversal, symlinks, the server root and other resources are blocked (`Permission denied`, code 13). `os.execute`, `io.popen` (except emulated ls/dir) and child processes/workers are blocked unless `add_unsafe_child_process_permission` / `add_unsafe_worker_permission` / `add_filesystem_permission` are set in server.cfg. Use `@resource/path` mount paths and `io.readdir`.

## Commands and keybinds

```lua
RegisterCommand('engine', function(source, args, raw) ... end, false)      -- true = needs ACE command.engine
RegisterKeyMapping('engine', 'Toggle engine', 'keyboard', 'Y')            -- client, user-rebindable
```
Prefer `RegisterKeyMapping` over polling `IsControlJustPressed` in a `Wait(0)` loop.

## Other runtimes

JS (V8 client / Node server, Node 16 default, `node_version '22'` opt-in) and C# (`.net.dll`, CitizenFX.Core) are supported: [references/runtimes-js-csharp.md](references/runtimes-js-csharp.md).

## Review checklist

- [ ] `fx_version 'cerulean'`, `game` set, every NUI/meta file in `files`.
- [ ] Every client->server event: `local src = source`, type/range checks, server-side lookups, rate limit.
- [ ] No `Wait(0)` loop without a reason; distance-based sleeps.
- [ ] Entities spawned server-side when persistence/ownership matters; net IDs over the wire.
- [ ] State bags written by the server; no nested mutation.
- [ ] NUI callbacks always `cb(...)`; focus released.
- [ ] Exports/dependencies declared; start order in server.cfg matches.

Sources and versions: [references/sources.md](references/sources.md).
