# Framework-agnostic bridge (server side)

Read when a resource must run on ESX, QBCore and Qbox. Keep all framework calls in one file; the rest of the resource calls `Bridge.*` only.

```lua
-- server/bridge.lua  (fxmanifest: server_scripts { '@oxmysql/lib/MySQL.lua', 'server/bridge.lua', 'server/main.lua' })
Bridge = {}
local ESX, QBCore

local function started(res) return GetResourceState(res) == 'started' end

-- Qbox first: qbx_core `provide`s qb-core
if started('qbx_core') then
    Bridge.name = 'qbx'
    function Bridge.getPlayer(src) return exports.qbx_core:GetPlayer(src) end
    function Bridge.getIdentifier(src)
        local p = Bridge.getPlayer(src); return p and p.PlayerData.citizenid
    end
    function Bridge.getJob(src)
        local p = Bridge.getPlayer(src); if not p then return end
        return p.PlayerData.job.name, p.PlayerData.job.grade.level
    end
    function Bridge.addMoney(src, account, amount, reason)
        return exports.qbx_core:AddMoney(src, account == 'money' and 'cash' or account, amount, reason)
    end
    function Bridge.removeMoney(src, account, amount, reason)
        return exports.qbx_core:RemoveMoney(src, account == 'money' and 'cash' or account, amount, reason)
    end
    function Bridge.notify(src, msg, kind) exports.qbx_core:Notify(src, msg, kind or 'inform') end

elseif started('es_extended') then
    Bridge.name = 'esx'
    ESX = exports['es_extended']:getSharedObject()
    function Bridge.getPlayer(src) return ESX.GetPlayerFromId(src) end
    function Bridge.getIdentifier(src)
        local x = ESX.GetPlayerFromId(src); return x and x.identifier
    end
    function Bridge.getJob(src)
        local x = ESX.GetPlayerFromId(src); if not x then return end
        return x.job.name, x.job.grade
    end
    local accountMap = { cash = 'money', money = 'money', bank = 'bank' }
    function Bridge.addMoney(src, account, amount, reason)
        local x = ESX.GetPlayerFromId(src); if not x then return false end
        x.addAccountMoney(accountMap[account] or account, amount, reason); return true
    end
    function Bridge.removeMoney(src, account, amount, reason)
        local x = ESX.GetPlayerFromId(src); if not x then return false end
        local acc = x.getAccount(accountMap[account] or account)
        if not acc or acc.money < amount then return false end
        x.removeAccountMoney(acc.name, amount, reason); return true
    end
    function Bridge.notify(src, msg) TriggerClientEvent('esx:showNotification', src, msg) end

elseif started('qb-core') then
    Bridge.name = 'qb'
    QBCore = exports['qb-core']:GetCoreObject()
    function Bridge.getPlayer(src) return QBCore.Functions.GetPlayer(src) end
    function Bridge.getIdentifier(src)
        local p = QBCore.Functions.GetPlayer(src); return p and p.PlayerData.citizenid
    end
    function Bridge.getJob(src)
        local p = QBCore.Functions.GetPlayer(src); if not p then return end
        return p.PlayerData.job.name, p.PlayerData.job.grade.level
    end
    function Bridge.addMoney(src, account, amount, reason)
        local p = QBCore.Functions.GetPlayer(src); if not p then return false end
        return p.Functions.AddMoney(account == 'money' and 'cash' or account, amount, reason)
    end
    function Bridge.removeMoney(src, account, amount, reason)
        local p = QBCore.Functions.GetPlayer(src); if not p then return false end
        account = account == 'money' and 'cash' or account
        if (p.PlayerData.money[account] or 0) < amount then return false end   -- bank may go negative otherwise
        return p.Functions.RemoveMoney(account, amount, reason)
    end
    function Bridge.notify(src, msg, kind) QBCore.Functions.Notify(src, msg, kind or 'primary') end

else
    error('No supported framework started (qbx_core, es_extended, qb-core). Check ensure order.')
end

-- Items: prefer ox_inventory when present, it is identical on all three
function Bridge.addItem(src, item, count, meta)
    if started('ox_inventory') then
        if not exports.ox_inventory:CanCarryItem(src, item, count, meta) then return false end
        return (exports.ox_inventory:AddItem(src, item, count, meta))
    elseif Bridge.name == 'esx' then
        local x = ESX.GetPlayerFromId(src)
        if not x or not x.canCarryItem(item, count) then return false end
        x.addInventoryItem(item, count); return true
    elseif Bridge.name == 'qb' then
        return exports['qb-inventory']:AddItem(src, item, count, nil, meta, 'bridge')
    end
    return false
end
```

Rules for bridge code:
- Detect once at load; never call `GetResourceState` per request.
- Normalise account names (`money`/`cash`), job grade (number), identifier (ESX identifier vs QB citizenid) at the boundary.
- `ensure` the bridge resource after the framework, or declare framework-specific `dependency` per variant. Do not hard-depend on all frameworks.
- Write the resource's DB tables keyed by the bridge identifier; do not join on framework tables you don't control.
- Client-side bridges: player-loaded events differ (`esx:playerLoaded`, `QBCore:Client:OnPlayerLoaded` - also fired by Qbox). Listen to both and guard against double init.
