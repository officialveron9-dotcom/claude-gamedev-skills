---
name: fivem-security
description: Hardens FiveM resources and servers against cheaters - validating server net events (source, distance, cooldowns, ACE permissions), server-authoritative money/items/prices, common exploit patterns (client-triggered give-money/give-item events, trusted prices or target IDs, NUI/ox_target trust, SQL injection, load() RCE, webhook leaks), sv_entityLockdown, sv_filterRequestControl, sv_stateBagStrictMode and client state bag writes, ACE/principals, protecting sv_licenseKey, webhooks and DB credentials, txAdmin and asset escrow basics. Use when writing or reviewing any RegisterNetEvent/callback handler, admin command, economy/inventory code or server.cfg security settings, or when the user writes German like "Sicherheitslücke", "Cheater spawnen Geld", "Exploit fixen", "Modder", "Trigger abgesichert".
---

# FiveM security for resource code

Model: every client is hostile. Cheat menus can call `TriggerServerEvent` with any name/args, call any NUI callback, any ox_lib/ESX/QB callback, write their own state bags (unless strict mode), spawn entities (unless lockdown) and request control of entities. Client-side checks (job checks, ox_target `groups`, disabled buttons, distance in Lua) are UX only.

## Server event template

```lua
local COOLDOWN_MS = 1000
local lastCall = {}

AddEventHandler('playerDropped', function() lastCall[source] = nil end)

RegisterNetEvent('fishing:server:sell', function(fishName, amount)
    local src = source                                   -- 1. capture before any yield
    local now = GetGameTimer()
    if (lastCall[src] or 0) + COOLDOWN_MS > now then return end
    lastCall[src] = now                                  -- 2. per-player rate limit

    if type(fishName) ~= 'string' or math.type(amount) ~= 'integer' then return end
    if amount < 1 or amount > 50 then return end         -- 3. types + bounds (reject floats/NaN/negatives)

    local price = Config.FishPrices[fishName]            -- 4. whitelist + server-side values
    if not price then return end

    local ped = GetPlayerPed(src)                        -- 5. server-side position check
    if #(GetEntityCoords(ped) - Config.SellPoint) > 5.0 then return end

    local player = Bridge.getPlayer(src)                 -- 6. loaded player + permission/job
    if not player then return end

    if not exports.ox_inventory:RemoveItem(src, fishName, amount) then return end   -- 7. take first,
    Bridge.addMoney(src, 'cash', price * amount, 'fishing-sell')                   --    then give
end)
```

Checklist per handler: captured `src` | rate limit | `type()`/`math.type()` + bounds | whitelist lookup, never client-supplied price/item/account/target | server-side distance (`GetEntityCoords(GetPlayerPed(src))`) | job/ACE from server data | state machine (was the action actually started? one-shot tokens) | atomic take-then-give with return-value checks | log suspicious calls (and optionally kick/ban).

## Top exploit patterns (wrong -> right)

```lua
-- 1. Client decides the reward
RegisterNetEvent('job:pay', function(amount) xPlayer.addMoney(amount) end)            -- WRONG
-- RIGHT: server tracks the job run and computes pay on completion
```
```lua
-- 2. Client chooses the target player
RegisterNetEvent('police:cuff', function(targetId) TriggerClientEvent('police:getCuffed', targetId) end) -- WRONG
-- RIGHT: check src is police on duty, targetId is a number, DoesPlayerExist(targetId), distance src<->target < 3.0
```
```lua
-- 3. Admin flag from client
RegisterNetEvent('admin:ban', function(target, isAdmin) if isAdmin then ... end end)  -- WRONG
-- RIGHT: if not IsPlayerAceAllowed(src, 'admin.ban') then return end
```
```lua
-- 4. Executing client strings
load(code)()                                  -- WRONG: remote code execution
ExecuteCommand('add_principal ' .. arg)       -- WRONG: console injection
MySQL.query('... WHERE name = "' .. name .. '"')  -- WRONG: SQL injection -> use ? placeholders
```
```lua
-- 5. Secrets on the client
local WEBHOOK = 'https://discord.com/api/webhooks/...'   -- in client/shared file = public
-- RIGHT: server-only file or `set my_webhook "..."` + GetConvar on the server; send logs from the server
```
More patterns (entities, state bags, NUI, callbacks, DoS): [references/exploit-patterns.md](references/exploit-patterns.md) - read when reviewing a resource.

## ACE permissions

```cfg
# server.cfg
add_ace group.admin command allow
add_ace group.admin admin.ban allow
add_principal identifier.license:abc123... group.admin
add_ace resource.myadmin command.add_principal allow    # only if the resource must run ExecuteCommand('add_principal ...')
```
```lua
RegisterCommand('heal', function(source, args) ... end, true)   -- restricted: needs ACE command.heal
if IsPlayerAceAllowed(src, 'admin.ban') then ... end            -- custom ACE objects work too
```
- `source == 0` in a command handler means console.
- Prefer `license:` (or `fivem:`) identifiers; `ip:` and `discord:` alone are weak. Use `GetPlayerIdentifierByType(src, 'license')`.
- Never grant `add_ace resource.X command allow` (all commands) to third-party resources.

## Server convars that close whole exploit classes

| Convar | Recommended | Effect / breakage risk |
|---|---|---|
| `sv_entityLockdown` | `strict` (or `relaxed`) | Clients cannot create networked entities (`relaxed`: script entities blocked, population allowed). Breaks scripts spawning vehicles/props client-side -> move spawning to the server. Per bucket: `SetRoutingBucketEntityLockdownMode`. |
| `setr sv_stateBagStrictMode true` | `true` (server >= 12739) | Only the server writes replicated state bags. Breaks scripts that `LocalPlayer.state:set(..., true)`. |
| `sv_filterRequestControl` | `2`-`4` | Blocks `NetworkRequestControlOfEntity` abuse (mode 2: player-controlled entities; 4: no routing at all). Warns `NetworkRequestControlOfEntity is deprecated...` in client consoles. |
| `sv_enableNetworkedSounds` | `false` | Blocks sound-spam events. |
| `sv_enableNetworkedPhoneExplosions` | `false` (default) | |
| `sv_enableNetworkedScriptEntityStates` | `false` | Blocks `SCRIPT_ENTITY_STATE_CHANGE_EVENT` abuse. |
| `block_net_game_event NAME` | e.g. unused weapon/explosion events | See net game events list; test first. |
| `sv_scriptHookAllowed` | `0` | |
| `sv_pureLevel` | `1` or `2` | Blocks modified game files (2 = also audio/graphics). |
| `sv_authMaxVariance` / `sv_authMinTrust` | tighten carefully | Identity strength. |
| `sv_disableClientReplays` | `true` if Rockstar Editor not needed | |
| `rcon_password` | unset | RCON is plain UDP; leave disabled. |

Details and a hardened cfg block: [references/hardening.md](references/hardening.md).

## Secrets

- `sv_licenseKey`, `mysql_connection_string`, `steam_webApiKey`, `sv_tebexSecret`, webhook URLs: only `set` (never `setr`/`sets`), ideally in a separate `secrets.cfg` that is `exec`'d and not committed. `sets` values are public in `/info.json`; `setr` values are readable by every client.
- Restrict reads: `add_convar_permission <resource> read <convar>` (once any permission exists, only listed resources can read it).
- Never print connection strings/keys; oxmysql masks the password, your code may not.
- A leaked license key lets others run escrowed assets bound to your account - regenerate it on portal.cfx.re.
- Removed in artifacts from mid-2026 (~32561+): `sv_endpointPrivacy` and `sv_exposePlayerIdentifiersInHttpEndpoint` (they now only warn); endpoints are never exposed and `/players.json` names/identifiers require `sv_playersToken` (`X-Players-Token` header or `?token=`).

## txAdmin

- Panel port 40120: firewall it to admin IPs or put it behind a reverse proxy; do not run it on a shared/public interface without need. Use Cfx.re login for admins, unique accounts, least permissions.
- txAdmin v8+: configure host settings via `TXHOST_*` env vars (old `txAdminPort`/`txDataPath` convars deprecated); keep env files readable only by the txAdmin process.
- Never `ensure`/`stop` the `monitor`/txAdmin resource from server.cfg; set OneSync in txAdmin settings, not in server.cfg.

## Asset escrow (paid scripts)

- Escrowed files (`.lua`, `.yft`, `.ydd`, `.ydr`) are encrypted and bound to the Cfx.re account that owns the server key. `You lack the required entitlement` = key from another account; `Failed to verify protected resource` = corrupted/missing `.fxap` (FTP transfer, partial upload) - re-download, upload the zip, extract on the server.
- Config files listed in `escrow_ignore` stay editable. NUI is never escrowed.
- Escrow does not make the resource secure: its net events are still callable. Review event names exposed by escrowed scripts (`event X was not safe for net` spam shows probing).

## Review checklist before shipping

- [ ] grep `RegisterNetEvent`, `lib.callback.register`, `RegisterServerCallback`, `CreateCallback`, `RegisterNUICallback`: each handler passes the template checks.
- [ ] No price/amount/reward/target/account/job/isAdmin comes from the client unvalidated.
- [ ] No secrets in client/shared files, NUI, or `setr`/`sets`.
- [ ] No `load`, `ExecuteCommand`, `os.*`, string-built SQL with client data.
- [ ] Entities that matter are spawned server-side; works with `sv_entityLockdown strict`.
- [ ] State written server-side; works with `sv_stateBagStrictMode true`.
- [ ] Client events that only the server should trigger check `source == 65535` (defence in depth).

Sources: [references/sources.md](references/sources.md).
