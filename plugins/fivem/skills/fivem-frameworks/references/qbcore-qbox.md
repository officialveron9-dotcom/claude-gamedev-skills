# QBCore (qb-core 1.3.0) and Qbox (qbx_core 1.24.0) - API facts and traps

Read when writing/fixing code for qb-core or qbx_core, or porting between them.

## QBCore

```lua
local QBCore = exports['qb-core']:GetCoreObject()
-- optional filter to avoid copying everything: exports['qb-core']:GetCoreObject({ 'Functions', 'Shared' })
```

Server:
```lua
local Player = QBCore.Functions.GetPlayer(src)          -- nil if not logged in
if not Player then return end
local pd = Player.PlayerData                            -- citizenid, license, name, money{cash,bank,crypto},
                                                        -- charinfo{firstname,lastname,...}, job{name,label,onduty,type,isboss,grade{name,level}},
                                                        -- gang{...}, metadata{hunger,thirst,isdead,...}, source
Player.Functions.AddMoney('bank', 500, 'job-payout')
if not Player.Functions.RemoveMoney('cash', price, 'shop') then return end
Player.Functions.SetJob('police', 2)
Player.Functions.SetMetaData('hunger', 100)
QBCore.Functions.Notify(src, 'Done', 'success', 5000)
QBCore.Functions.CreateUseableItem('bandage', function(source, item) ... end)
QBCore.Functions.HasPermission(src, 'admin')
QBCore.Functions.GetQBPlayers()                         -- table keyed by source
QBCore.Functions.GetPlayerByCitizenId(cid)
```
Since the 2026-05 refactor players are `Player` class instances; `Player.Functions.X(...)` still works (bound wrappers), and other resources get the same via `exports['qb-core']:GetPlayer(src)`. Add custom methods with `QBCore.Functions.AddPlayerMethod(ids, name, fn)` / `AddPlayerField` instead of mutating player tables.

Traps:
- `RemoveMoney` returns `false` when funds are insufficient, but `bank` may go negative down to `QBCore.Config.Money.MinusLimit` (-5000 default; only `cash`/`crypto` are in `DontAllowMinus`). Check `PlayerData.money.bank >= price` yourself if negative balances are unwanted.
- Job grade: `PlayerData.job.grade.level` (number). Shared jobs table keys grades as strings (`['0']`), Qbox as numbers.
- `Player.Functions.AddItem/RemoveItem/GetItemByName` do not exist any more. Use `exports['qb-inventory']:AddItem(src, item, amount, slot, info, reason)`, `RemoveItem(src, item, amount, slot, reason)`, `HasItem(src, items, amount)`; UI feedback `TriggerClientEvent('qb-inventory:client:ItemBox', src, QBCore.Shared.Items[item], 'add', amount)`.
- `QBCore:GetObject` event is gone; scripts still using it fail with `attempt to index a nil value (global 'QBCore')`.
- Money types are fixed by `QBCore.Config.Money.MoneyTypes`; `AddMoney('black_money', ...)` returns false unless configured.

Callbacks:
```lua
-- server (cb must be called once)
QBCore.Functions.CreateCallback('garage:getCars', function(source, cb, garage) cb(result) end)
-- client: callback style, or omit cb to await the result
QBCore.Functions.TriggerCallback('garage:getCars', function(cars) end, 'legion')
local cars = QBCore.Functions.TriggerCallback('garage:getCars', 'legion')
-- server -> client
QBCore.Functions.CreateClientCallback('x', function(cb, ...) end)      -- client
QBCore.Functions.TriggerClientCallback('x', src, ...)                  -- server
```
Concurrent `TriggerCallback` calls with the same name on one client overwrite each other's pending promise (stored by name) - don't fire the same QB callback twice in parallel; ox_lib callbacks don't have this issue.

Events:

| Side | Event | Args |
|---|---|---|
| client | `QBCore:Client:OnPlayerLoaded` | - (read `QBCore.Functions.GetPlayerData()`) |
| client | `QBCore:Client:OnPlayerUnload` | - |
| client | `QBCore:Player:SetPlayerData` | full PlayerData |
| client | `QBCore:Client:OnJobUpdate` / `OnGangUpdate` | job / gang |
| client | `QBCore:Client:SetDuty` | onduty |
| client | `QBCore:Client:OnMoneyChange` | type, amount, 'add'/'remove'/'set', reason |
| server | `QBCore:Server:PlayerLoaded` | Player |
| server | `QBCore:Server:OnPlayerUnload` | src |
| server | `QBCore:Server:OnJobUpdate` | src, job |
| server | `QBCore:Server:OnMoneyChange` | src, type, amount, action, reason |

## Qbox (qbx_core)

Requirements enforced at start (server quits otherwise): ox_lib >= 3.20.0, ox_inventory >= 2.42.1, `setr inventory:framework "qbx"`, OneSync on. Start order: `oxmysql`, `ox_lib`, `qbx_core`, `ox_inventory`, then the rest (follow the Qbox txAdmin recipe).

```lua
-- fxmanifest
shared_scripts { '@ox_lib/init.lua', '@qbx_core/modules/lib.lua' }   -- qbx.* helpers
client_scripts { '@qbx_core/modules/playerdata.lua', 'client/*.lua' } -- QBX.PlayerData kept in sync

-- server
local player = exports.qbx_core:GetPlayer(src)
if not player then return end
local cid = player.PlayerData.citizenid
exports.qbx_core:AddMoney(src, 'cash', 100, 'reason')               -- identifier may be source or citizenid
if not exports.qbx_core:RemoveMoney(src, 'bank', 50, 'fee') then return end
exports.qbx_core:SetJob(src, 'police', 1)
if exports.qbx_core:HasGroup(src, { police = 2 }) then end          -- job/gang, min grade
exports.qbx_core:Notify(src, 'Saved', 'success')
-- items: ox_inventory
exports.ox_inventory:AddItem(src, 'water', 1)

-- client
if QBX.PlayerData.job.name == 'police' then end
local data = exports.qbx_core:GetPlayerData()
```

Traps:
- Player-taking exports (`AddMoney`, `RemoveMoney`, `SetJob`, `SetMetadata`, ...) treat a **string** identifier as a citizenid (online or offline) and a number as a server ID. Sources from `GetPlayers()` or command args are strings -> `tonumber(src)` first, otherwise the call silently returns false.
- No core object: `QBX` is a module global, not `exports.qbx_core:GetCoreObject()`. Old QB scripts work via the bridge (qbx_core `provide 'qb-core'`; `qbx:enablebridge` convar, default true) - new code should use exports.
- `exports.qbx_core:HasGroup/HasPrimaryGroup/GetGroups(src, ...)` index `QBX.Players[src]` without a nil check - guard with `GetPlayer(src)` first or you get `attempt to index a nil value (field '?')`.
- Multi-job is built in (`qbx:max_jobs_per_player`): `SetJob` may replace or add depending on `qbx:setjob_replaces`; use `AddPlayerToJob(citizenid, job, grade)`/`SetPlayerPrimaryJob` explicitly.
- Shared data comes from exports: `GetJobs()`, `GetGangs()`, `GetVehiclesByName()`, `GetWeapons()`, `GetLocations()`, items from `exports.ox_inventory:Items()`.
- Drawtext/notify: `lib.showTextUI`/`lib.hideTextUI`/`lib.notify` instead of qb-core `DrawText` exports.
- `qbx:bucketlockdownmode` convar sets lockdown for bucket 0 (`inactive` default).
- `exports.qbx_core:ExploitBan(src, origin)` exists for kicking/banning detected exploiters.
