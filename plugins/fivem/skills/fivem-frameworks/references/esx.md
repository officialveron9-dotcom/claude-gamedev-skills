# ESX Legacy (1.15.x) - API facts and traps

Read when writing or fixing ESX code. Verified against esx-framework/esx_core 1.15.2 (2026-09-06).

## Start order (server.cfg)

```
ensure oxmysql
ensure esx_lib          # new in 1.14+; es_extended loads '@esx_lib/imports.lua'
ensure es_extended
ensure [core]           # esx_* core resources
ensure [esx_addons]     # your scripts after the core
```
Missing `esx_lib` on 1.14+ -> es_extended fails to load (`xLib` nil). With ox_inventory: `ensure ox_lib` before es_extended and `ensure ox_inventory` immediately after es_extended (ox docs). ESX switches to ox mode whenever the `ox_inventory` resource exists (`Config.CustomInventory = 'ox'`), even if it is not started - a leftover folder breaks the default inventory.

## Getting ESX

```lua
-- fxmanifest (preferred): sets global ESX on both sides, client ESX.PlayerData auto-updated
shared_script '@es_extended/imports.lua'
-- or in code
ESX = exports['es_extended']:getSharedObject()
```
The `esx:getSharedObject` event still exists only as a local (non-net) compatibility handler; old scripts using `ESX = nil` + `TriggerEvent('esx:getSharedObject', ...)` inside a `while ESX == nil do` loop are the #1 cause of `attempt to index a nil value (global 'ESX')`. Replace with the import.

## xPlayer (server) - methods that exist in 1.15

`getIdentifier()`, `getSSN()`, `getName()/setName()`, `getGroup()/setGroup()`, `isAdmin()`, `getMoney()/setMoney()/addMoney(n, reason)/removeMoney(n, reason)` (cash), `getAccounts()/getAccount(name)`, `setAccountMoney/addAccountMoney/removeAccountMoney(name, n, reason)`, `getInventory()/getInventoryItem(name)/addInventoryItem/removeInventoryItem/setInventoryItem/hasItem(name)`, `canCarryItem(name, n)`, `canSwapItem(...)`, `getWeight()/getMaxWeight()/setMaxWeight()`, `getJob()/setJob(name, grade, onDuty?)/refreshJob()`, `getLoadout()/addWeapon/removeWeapon/hasWeapon/addWeaponAmmo/...`, `getCoords(asVector)/setCoords(v)`, `getMeta(k)/setMeta(k,v)/clearMeta(k)`, `showNotification(msg)`, `triggerEvent(name, ...)`, `kick(reason)`, `getPlayTime()`, `togglePaycheck()`, `executeCommand(cmd)`. Fields: `xPlayer.source`, `xPlayer.identifier`, `xPlayer.job` (`name`, `label`, `grade` number, `grade_name`, `grade_salary`).

```lua
-- WRONG: trusts client price, no nil check, removes without checking balance
RegisterNetEvent('shop:buy', function(item, price)
    local xPlayer = ESX.GetPlayerFromId(source)
    xPlayer.removeMoney(price)
    xPlayer.addInventoryItem(item, 1)
end)

-- RIGHT
local Items = { bread = 5, water = 3 }   -- server-side prices
RegisterNetEvent('shop:buy', function(item)
    local src = source
    local xPlayer = ESX.GetPlayerFromId(src)
    local price = Items[item]
    if not xPlayer or not price then return end
    if xPlayer.getMoney() < price or not xPlayer.canCarryItem(item, 1) then
        return xPlayer.showNotification('Not enough money or space')
    end
    xPlayer.removeMoney(price, 'shop purchase')
    xPlayer.addInventoryItem(item, 1)
end)
```

Other server functions: `ESX.GetPlayerFromId(src)`, `ESX.GetPlayerFromIdentifier(id)`, `ESX.GetExtendedPlayers(key?, val?)` (e.g. `('job', 'police')`), `ESX.RegisterUsableItem(name, function(source, item, ...) end)`, `ESX.RegisterCommand(name, group, function(xPlayer, args, showError) end, allowConsole, suggestion)` (`xPlayer` is `false` when run from console), `ESX.OneSync.GetPlayersInArea(...)`.

## Callbacks

```lua
-- server: MUST call cb exactly once on every path, else the client waits until timeout
ESX.RegisterServerCallback('garage:getCars', function(source, cb, garage)
    local xPlayer = ESX.GetPlayerFromId(source)
    if not xPlayer then return cb({}) end
    cb(MySQL.query.await('SELECT plate FROM owned_vehicles WHERE owner = ?', { xPlayer.identifier }))
end)
-- client
ESX.TriggerServerCallback('garage:getCars', function(cars) ... end, 'legion')
local cars = ESX.AwaitServerCallback('garage:getCars', 'legion')   -- 1.14+
```
Server -> client: `ESX.RegisterClientCallback` (client) + `ESX.TriggerClientCallback(src, name, cb, ...)` / `ESX.AwaitClientCallback(src, name, ...)` (server). In 1.15 these run on esx_lib (`xLib.callback`); handlers are cleaned up when the owning resource stops.

## Events

| Side | Event | Args |
|---|---|---|
| server | `esx:playerLoaded` | `playerId, xPlayer, isNew` |
| server | `esx:playerDropped` | `playerId, reason` |
| server | `esx:setJob` | `playerId, job, lastJob` |
| server | `esx:setAccountMoney` / `esx:addAccountMoney` / `esx:removeAccountMoney` | money changes |
| client | `esx:playerLoaded` (net) | `xPlayer, isNew, skin` |
| client | `esx:onPlayerLogout` | - |
| client | `esx:setJob` (net) | `job, lastJob` |
| client | `esx:onPlayerDeath` / `esx:onPlayerSpawn` | death data / - |

Client data: with the import, read `ESX.PlayerData.job.name`; `ESX.PlayerLoaded` is true after load. Define global `OnPlayerData(key, val, last)` to react to changes. ESX also mirrors `job`, `group`, `name` into player state bags (`Player(src).state.job`) - read-only use on clients.

## Traps

- Job grade on ESX is a number in `xPlayer.job.grade`; QBCore uses `job.grade.level`. Do not mix.
- `xPlayer.getInventoryItem(name).count` with ox_inventory: overridden, returns ox data; prefer `exports.ox_inventory:GetItemCount(src, name)`.
- Identifier type is configurable: `set esx:identifier "license"` (default). Do not hardcode `steam:`.
- Locale convar `setr esx:locale "de"`.
- Old `esx_*` addons using `MySQL.Async` need oxmysql's compatibility (it provides mysql-async) or conversion.
- ESX admin commands rely on ACE: `add_ace resource.es_extended command.add_ace allow` etc. (see the ESX recipe server.cfg).
