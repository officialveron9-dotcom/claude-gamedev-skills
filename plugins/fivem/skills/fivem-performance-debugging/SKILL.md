---
name: fivem-performance-debugging
description: Diagnoses and fixes FiveM resource errors and performance problems - reading SCRIPT ERROR stack traces and server/F8 console messages ("attempt to index a nil value", "No such export", "Couldn't start resource", "Could not find dependency", "was not safe for net", "server thread hitch warning", "Oversized assets", "Failed to verify protected resource", "You lack the required entitlement", "Reliable network event overflow", database connection errors, game build mismatch), and optimising client/server CPU with resmon, profiler record/view, Wait(0) loop removal, distance-based sleeps, caching, expensive natives and NUI costs. Use when a resource errors, does not start, hitches or shows high ms in resmon, or when the user writes German like "Server Fehler", "Resource startet nicht", "F8 Fehler", "Lags", "Ruckler", "hohe ms", "Performance verbessern".
---

# FiveM debugging and performance

## Error triage workflow

1. Get the **first** error, not the last. `Couldn't start resource X.` is a summary - the cause is printed above it.
2. Identify side: server console / txAdmin Live Console (server) vs F8 (client). Same file can run on both sides - `IsDuplicityVersion()` is true on the server.
3. Read the stack trace: `SCRIPT ERROR: @res/client/main.lua:42: attempt to index a nil value (field 'job')` -> file, line, and *which name* was nil. The lines below (`> fn (@res/...:42)`) show the call chain; the top frame from your resource is the place to fix.
4. Look up the message in [references/common-errors.md](references/common-errors.md) (exact text -> cause -> fix). Read it for any console/F8 error.
5. Reproduce with `restart res` (or `ensure res`); for client issues reconnect, because some state (NUI focus, entities) survives a resource restart.

## nil-index errors: what was nil

| Message part | Usually means |
|---|---|
| `(global 'ESX')`, `(global 'QBCore')`, `(global 'lib')`, `(global 'MySQL')` | Missing manifest include / framework getter / start order |
| `(global 'Config')` | config.lua not loaded on this side (server_script vs shared_script) or loaded after the file using it |
| `(local 'xPlayer')`, `(local 'Player')` | Player not loaded or wrong `source` (captured after a `Wait`, or string ID) |
| `(field '?')` | Indexing with a key that doesn't exist, e.g. `Config.Shops[shopId]` with client-supplied/stringified key (`'1'` vs `1`) |
| `attempt to call a nil value (global 'PlayerPedId')` on server | Client native used server-side |
| `attempt to call a nil value (field 'X')` | API removed/renamed (e.g. `Player.Functions.AddItem`) or method on wrong object |
| `attempt to compare number with string` / `string with number` | `GetPlayers()` IDs, convars, JSON keys are strings - `tonumber()` |

## Performance tools

| Tool | Where | Use |
|---|---|---|
| `resmon 1` (or `resmon true`) | F8 (client) | Per-resource client CPU ms and memory. Targets: idle resource ~0.00-0.02 ms; anything consistently > 0.1-0.2 ms while idle deserves a look. Auto-warning when a resource averages > 6 ms: `<res> is taking N ms (or -X FPS @ 60 Hz)`. |
| `profiler record 500` -> `profiler view` | F8 and server console | Records N frames (`record start`/`stop` also work). `profiler saveJSON file.json` / `profiler save file` to keep it; `profiler status`. On the server `view` prints a Chrome DevTools URL loading `/profileData.json`. Look for wide script blocks under your resource. |
| txAdmin Dashboard -> server performance chart | txAdmin | Server tick time history vs player count. |
| `svgui` | server console | Server debug GUI (removed on Enhanced). |
| `set mysql_debug ["res"]`, `set mysql_slow_query_warning 150`, `set mysql_ui true` | server.cfg | oxmysql query logging / slow queries / in-game UI (`/mysql`, restricted: needs ACE `command.mysql`). |
| `nui_devTools` / `http://localhost:13172` | client | NUI performance panel (CEF). |
| F8 > Tools > Streaming > Pool Monitor | client | Pool exhaustion (map/vehicle packs). |

## Client CPU: the patterns that matter

```lua
-- WRONG: per-frame work for something used near one location
CreateThread(function()
    while true do
        Wait(0)
        local coords = GetEntityCoords(PlayerPedId())
        for _, shop in pairs(Config.Shops) do
            if GetDistanceBetweenCoords(coords, shop.coords, true) < 2.0 then
                DrawText3D(shop.coords, '[E] Shop')
                if IsControlJustReleased(0, 38) then openShop(shop) end
            end
        end
    end
end)

-- RIGHT: sleep by distance, vector math, cache the ped, only draw when close
CreateThread(function()
    while true do
        local sleep = 1000
        local ped = PlayerPedId()                  -- or cache.ped with ox_lib
        local coords = GetEntityCoords(ped)
        for i = 1, #Config.Shops do
            local shop = Config.Shops[i]
            local dist = #(coords - shop.coords)
            if dist < 20.0 then
                sleep = 0
                if dist < 2.0 then
                    DrawText3D(shop.coords, '[E] Shop')
                    if IsControlJustReleased(0, 38) then openShop(shop) end
                end
            end
        end
        Wait(sleep)
    end
end)
```

Better still: `lib.points.new({ coords, distance })` with `nearby()` (runs only near the point), `lib.zones.*` with `onEnter/onExit`, or ox_target zones instead of draw loops; `RegisterKeyMapping` instead of polling keys.

Rules:
- `Wait(0)` only while something must happen every frame (drawing, disabling controls). Everything else: event-driven (state bag handlers, `gameEventTriggered`, `lib.onCache`, framework loaded/job events) or timed (`Wait(500+)`).
- `#(a - b)` instead of `GetDistanceBetweenCoords`/`Vdist` (avoids a native call).
- Hoist `PlayerPedId()`, `GetEntityCoords`, `GetVehiclePedIsIn` out of inner loops; ox_lib `cache.ped`/`cache.vehicle`/`cache.coords` are updated for you.
- Use numeric `for i = 1, #t` over arrays in hot paths; localise frequently used natives (`local GetEntityCoords = GetEntityCoords`) only in genuinely hot code.
- `GetActivePlayers()` instead of `for i = 0, 255`; `GetGamePool('CVehicle'|'CPed'|'CObject')` instead of entity enumerators - and not every frame.
- Request assets once and release: `RequestModel` + wait for `HasModelLoaded` with a timeout, then `SetModelAsNoLongerNeeded`; `RemoveAnimDict` after use.
- Blips/markers: create blips once at start; `DrawMarker` only within range.
- Never `TriggerServerEvent` in a per-frame loop (players get dropped: `Reliable network event overflow.`).

## Server CPU and hitches

- `server thread hitch warning: timer interval of N milliseconds` = the main server thread was blocked > 150 ms. Causes: big synchronous loops over all players/entities each tick, `json.encode/decode` of huge tables, `LoadResourceFile`/`SaveResourceFile` of large files, `io` operations, many resources starting at once (expected at boot), CPU starvation on the host.
- `network thread hitch warning` / `sync thread hitch warning` = host CPU/network overload or too many synced entities; check host load and entity counts (`onesync_population false` if ambient peds/cars are not needed).
- Spread periodic jobs: one thread with `Wait(60000)` for paychecks; batch DB writes (`MySQL.prepare` with multiple parameter sets, `transaction`).
- Never wait on DB in tight loops; never `Wait(0)` on the server unless needed (server ticks at 20 Hz anyway).
- Cache static DB data at start (`MySQL.ready`), keep per-player data in memory, save on interval + `playerDropped`.

## NUI performance

- Hidden UI must not render: unmount/`display:none`, stop animations, no `backdrop-filter: blur` on large areas.
- Throttle `SendNUIMessage`; send diffs on change (e.g. HUD values only when they change, max ~10/s).
- Bundle and minify; avoid loading big fonts/images from remote CDNs on every join.

## Streaming / memory

- `Asset res/x.ytd uses N MiB of physical memory.` warnings start above 16 MiB; above 48 MiB the warning adds "Oversized assets can and WILL lead to streaming issues". Downscale textures (2048 -> 1024), split ytd, use proper LODs. Details in `fivem-server-setup` (streaming).
- Texture/pool overflows ("texture loss", props not loading) on heavy map packs: `increase_pool_size` in server.cfg for supported pools (e.g. `TxdStore`).

Optimisation recipes (vehicle HUD, markers, inventory refresh, database): [references/optimization-patterns.md](references/optimization-patterns.md). Sources: [references/sources.md](references/sources.md).

## Before/after checklist for a resource

- [ ] `resmon 1` idle value recorded before and after; no `Wait(0)` thread running when the player is far from the feature.
- [ ] No errors in server console or F8 on start, restart, player join, player drop.
- [ ] Restart-safe: `onResourceStop` cleans entities, blips, NUI focus, zones.
- [ ] No slow-query warnings; indexes on lookup columns.
- [ ] No `Warning: sending large event` messages; latent events for big payloads.
