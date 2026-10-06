---
name: fivem-frameworks
description: Writes correct framework code for FiveM resources on ESX Legacy (es_extended, xPlayer, esx_lib), QBCore (qb-core, PlayerData, qb-inventory), Qbox (qbx_core, qb bridge), the ox stack (ox_lib, ox_inventory, ox_target) and oxmysql (MySQL.query/single/scalar/insert/update/prepare/transaction with .await), and replaces deprecated APIs (esx:getSharedObject event, QBCore:GetObject, Player.Functions.AddItem, mysql-async, ghmattimysql, named @placeholders). Covers detecting the framework of a codebase, framework-agnostic bridge code and migration traps (QBCore->Qbox, mysql-async->oxmysql, CommunityOx->overextended). Use when code touches ESX/QBCore/Qbox/ox_* APIs or SQL, or the user writes German like "ESX Script", "QBCore Fehler", "Datenbank Abfrage", "Framework umstellen".
---

# FiveM frameworks: correct APIs and migration traps

Versions verified 2026-10-06 (they change APIs, so check the target server first):
ESX Legacy `1.15.2` (ships `esx_lib`/`xLib` since 1.14.0) | qb-core `1.3.0` (Player class refactor 2026-05), qb-inventory `2.2.3` | qbx_core `1.24.0` | ox_lib `3.40.0`, ox_inventory `2.48.0`, ox_target `1.18.1`, oxmysql `2.14.3` - all from **github.com/overextended** again (maintenance moved back from CommunityOx in April 2026; CommunityOx forks stalled at ox_lib 3.32.3 / ox_inventory 2.45.0 / oxmysql 2.13.1; docs: overextended.dev, coxdocs.dev is the old fork).

## 1. Detect the framework before writing code

| Evidence in the codebase | Framework |
|---|---|
| `@es_extended/imports.lua`, `exports['es_extended']:getSharedObject()`, `ESX.GetPlayerFromId`, `xPlayer` | ESX |
| `exports['qb-core']:GetCoreObject()`, `QBCore.Functions.*`, `PlayerData.citizenid` | QBCore (or Qbox via bridge) |
| `exports.qbx_core:*`, `@qbx_core/modules/*.lua`, `QBX.PlayerData`, `qbx.` | Qbox |
| `exports.ox_core`, `Ox.GetPlayer` | ox_core |
| `server.cfg`: `ensure qbx_core` + `setr inventory:framework "qbx"` | Qbox (qb-core is *provided* by qbx_core) |

Runtime detection order (Qbox provides `qb-core`, so test it first):
```lua
local fw = GetResourceState('qbx_core') == 'started' and 'qbx'
    or GetResourceState('es_extended') == 'started' and 'esx'
    or GetResourceState('qb-core') == 'started' and 'qb'
    or GetResourceState('ox_core') == 'started' and 'ox'
    or 'standalone'
```
Full adapter: [references/bridge.md](references/bridge.md) - read when a resource must support several frameworks.

## 2. Getting the core object

```lua
-- WRONG (removed/deprecated): ESX event pattern, QB event pattern
ESX = nil
TriggerEvent('esx:getSharedObject', function(obj) ESX = obj end)
TriggerEvent('QBCore:GetObject', function(obj) QBCore = obj end)    -- no longer exists in qb-core

-- RIGHT
-- ESX: fxmanifest  shared_script '@es_extended/imports.lua'   (sets global ESX, keeps ESX.PlayerData updated on client)
--      or          ESX = exports['es_extended']:getSharedObject()
-- QBCore:          local QBCore = exports['qb-core']:GetCoreObject()
-- Qbox: no core object - use exports.qbx_core:* and modules (@qbx_core/modules/playerdata.lua, lib.lua)
```

## 3. Server-side player, money, jobs

| Task | ESX | QBCore | Qbox |
|---|---|---|---|
| Player obj | `local xPlayer = ESX.GetPlayerFromId(src)` | `local Player = QBCore.Functions.GetPlayer(src)` | `local player = exports.qbx_core:GetPlayer(src)` |
| Identifier | `xPlayer.identifier` / `getIdentifier()` | `Player.PlayerData.citizenid` | `player.PlayerData.citizenid` |
| Add money | `xPlayer.addAccountMoney('bank', n, reason)` (`addMoney` = cash) | `Player.Functions.AddMoney('bank', n, reason)` | `exports.qbx_core:AddMoney(src, 'bank', n, reason)` |
| Remove money (check result!) | `if xPlayer.getAccount('bank').money >= n then xPlayer.removeAccountMoney('bank', n, reason) end` | `if Player.Functions.RemoveMoney('cash', n, reason) then` | `if exports.qbx_core:RemoveMoney(src, 'cash', n, reason) then` |
| Job | `xPlayer.job.name`, `.job.grade` (number) | `Player.PlayerData.job.name`, `.job.grade.level` | `player.PlayerData.job.name`, `.job.grade.level` |
| Set job | `xPlayer.setJob(name, grade)` | `Player.Functions.SetJob(name, grade)` | `exports.qbx_core:SetJob(src, name, grade)` |
| All players | `ESX.GetExtendedPlayers()` | `QBCore.Functions.GetQBPlayers()` | `exports.qbx_core:GetQBPlayers()` |
| Usable item | `ESX.RegisterUsableItem(name, fn)` | `QBCore.Functions.CreateUseableItem(name, fn)` | `exports.qbx_core:CreateUseableItem(name, fn)` or ox_inventory item export |

Always `if not xPlayer then return end` - the object is nil while the player is still on character selection or already dropped.

## 4. Inventory traps

- `Player.Functions.AddItem/RemoveItem` are **gone** from current qb-core; use `exports['qb-inventory']:AddItem(src, item, amount, slot, info, reason)` / `RemoveItem(src, item, amount, slot, reason)` / `HasItem(src, items, amount)` - or ox_inventory.
- ox_inventory: `exports.ox_inventory:AddItem(src, item, count, metadata)` returns `success, response`; check `CanCarryItem(src, item, count)` first. Items are defined in `ox_inventory/data/items.lua`, not in the framework's items table/DB.
- ox_inventory and ox_target only ship bridges for **esx, qbx, ox, nd** - there is no plain qb-core bridge. On QBCore use qb-inventory/qb-target or migrate to Qbox.
- ESX with ox_inventory: `xPlayer.addInventoryItem` etc. are overridden to call ox_inventory (`Config.CustomInventory = 'ox'` auto-set when ox_inventory is present). Weight/limit logic of old esx_* scripts no longer applies.
- `setr inventory:framework "esx"|"qbx"|"ox"|"nd"` must match the core; default is `esx`. qbx_core refuses to start unless it is `qbx`.

Details per framework: [references/esx.md](references/esx.md), [references/qbcore-qbox.md](references/qbcore-qbox.md), [references/ox-stack.md](references/ox-stack.md).

## 5. oxmysql - correct usage

```lua
-- fxmanifest: server_script '@oxmysql/lib/MySQL.lua'

-- WRONG: string concatenation -> SQL injection; ignoring await -> nil result
local row = MySQL.query('SELECT * FROM users WHERE identifier = "' .. id .. '"')

-- RIGHT
local row    = MySQL.single.await('SELECT firstname, lastname FROM users WHERE identifier = ? LIMIT 1', { id })
local money  = MySQL.scalar.await('SELECT money FROM users WHERE identifier = ?', { id })
local rows   = MySQL.query.await('SELECT plate FROM owned_vehicles WHERE owner = ?', { id })     -- array
local newId  = MySQL.insert.await('INSERT INTO logs (who, what) VALUES (?, ?)', { id, what })    -- insertId
local n      = MySQL.update.await('UPDATE users SET money = money - ? WHERE identifier = ? AND money >= ?', { amt, id, amt }) -- affectedRows
local ok     = MySQL.transaction.await({
    { query = 'UPDATE users SET bank = bank - ? WHERE identifier = ?', values = { amt, from } },
    { query = 'UPDATE users SET bank = bank + ? WHERE identifier = ?', values = { amt, to } },
})
```

| mysql-async / ghmattimysql (deprecated) | oxmysql |
|---|---|
| `MySQL.Async.fetchAll(q, p, cb)` / `MySQL.Sync.fetchAll` | `MySQL.query(q, p, cb)` / `MySQL.query.await` |
| `fetchScalar` | `MySQL.scalar` |
| `fetchSingle` | `MySQL.single` |
| `MySQL.Async.execute` | `MySQL.update` (returns affected rows) |
| `MySQL.Async.insert` | `MySQL.insert` (returns insert id) |
| `exports.ghmattimysql:execute` | `exports.oxmysql:query` |
| `@name` placeholders | `?` placeholders (named are deprecated; `prepare` rejects them) |

- Delete `mysql-async`/`ghmattimysql`; oxmysql `provide`s both. `.await` only inside a thread/handler (yields). `MySQL.prepare` only accepts `?`, returns raw types (no booleans for TINYINT(1), no date strings).
- Upsert with `INSERT ... ON DUPLICATE KEY UPDATE`, not select-then-insert.
- Use `MySQL.ready(function() ... end)` for startup queries.
- Debug: `set mysql_debug true` (or `["resA"]`), slow query threshold `set mysql_slow_query_warning 150`, `set mysql_ui true` for the in-game UI.

## 6. ox_lib essentials

`shared_script '@ox_lib/init.lua'` (once, first). Globals: `lib`, `cache` (`cache.ped`, `cache.vehicle`, `cache.seat`, `cache.coords`, `cache.serverId`, `cache.playerId`, `cache.weapon`, `cache.resource`), `require`, `lib.onCache('vehicle', fn)`. Callbacks `lib.callback.register/await`, commands `lib.addCommand(name, { params, restricted = 'group.admin' }, fn)`, `lib.points.new`, `lib.zones.box/sphere/poly`, `lib.notify`, `lib.progressBar`, `lib.registerContext`, `lib.inputDialog`. Its ACL commands need `add_ace resource.ox_lib command.add_ace allow` (+ `remove_ace`, `add_principal`, `remove_principal`).

## 7. Migration checklist

- [ ] Replace getSharedObject/GetObject events (section 2); grep for `ESX = nil`.
- [ ] mysql-async/ghmattimysql -> oxmysql; convert `@named` to `?`; check callers that expected `execute` to return rows.
- [ ] QBCore -> Qbox: job/gang grades become numbers (not `'0'` strings); `citizenid` columns need `utf8mb4_unicode_ci` collation; run qbx_core.sql; `setr inventory:framework "qbx"`; inventory to ox_inventory (convert DB); remove qb-target/qb-inventory dependants or adapt; `exports['qb-core']` calls keep working through the bridge (`qbx:enablebridge`).
- [ ] CommunityOx -> overextended: same resource names; download releases from github.com/overextended (prebuilt zip - the repo source needs a web build).
- [ ] ox_lib `lib.callback` signature: client `lib.callback.await(name, delay, ...)` - the second arg is a rate-limit delay (`false` for none), not the first payload value.
- [ ] After migrating, grep for `Player.Functions.AddItem`, `QBCore.Shared.Items` (Qbox: `exports.ox_inventory:Items()`), `xPlayer.getInventoryItem(...).count` on ox setups.

Common migration errors and fixes: [references/migration-errors.md](references/migration-errors.md). Sources: [references/sources.md](references/sources.md).
