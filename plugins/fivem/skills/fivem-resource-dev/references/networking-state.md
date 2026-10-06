# Networking, state bags, entities, buckets - traps and patterns

Read when code crosses client/server, spawns networked entities, or uses state bags/buckets.

## IDs - which one you have

| Thing | Client | Server | Trap |
|---|---|---|---|
| Player server ID | `GetPlayerServerId(PlayerId())`, `cache.serverId` | `source` | Server IDs are not client player indices. Convert on client with `GetPlayerFromServerId(id)` (may be `-1` if not in scope). |
| Player index | `PlayerId()` | does not exist | Never send `PlayerId()` to the server. |
| Entity handle | local per client | local per server | Never send handles over the network. |
| Net ID | `NetworkGetNetworkIdFromEntity` / `VehToNet` | same | Send this. Validate on receive. |

```lua
-- client receives a net id
RegisterNetEvent('veh:client:lock', function(netId, locked)
    if not NetworkDoesEntityExistWithNetworkId(netId) then return end  -- culled / not in scope
    local veh = NetworkGetEntityFromNetworkId(netId)
    SetVehicleDoorsLocked(veh, locked and 2 or 1)
end)

-- server receives a net id from a client: validate existence + proximity + ownership
RegisterNetEvent('veh:server:lock', function(netId)
    local src = source
    local veh = NetworkGetEntityFromNetworkId(netId)
    if veh == 0 or not DoesEntityExist(veh) then return end
    if #(GetEntityCoords(GetPlayerPed(src)) - GetEntityCoords(veh)) > 10.0 then return end
    -- check ownership in your DB / state, then act
end)
```

## Server-side entity creation

```lua
-- WRONG: client spawns persistent vehicle (fails under sv_entityLockdown strict, despawns on owner leave, trivially abusable)
local veh = CreateVehicle(`adder`, coords.x, coords.y, coords.z, h, true, false)

-- RIGHT (server)
local veh = CreateVehicleServerSetter(`adder`, 'automobile', coords.x, coords.y, coords.z, heading)
while not DoesEntityExist(veh) do Wait(0) end   -- usually immediate; guard anyway
SetEntityOrphanMode(veh, 2)                     -- 0 delete when not relevant (default), 1 delete on owner disconnect, 2 keep
SetVehicleNumberPlateText(veh, plate)
Entity(veh).state:set('owner', citizenId, true)
local netId = NetworkGetNetworkIdFromEntity(veh)
TriggerClientEvent('garage:client:spawned', src, netId)
```

- Server `CreateVehicle` is an RPC to a client (unreliable); `CreateVehicleServerSetter` is the reliable variant. Server `CreatePed` creates on the server.
- Server-side game natives are RPC natives (forwarded to the owning client, fallible): e.g. `SetEntityCoords`, `SetEntityHeading`, `FreezeEntityPosition`, `SetPedIntoVehicle`, `GiveWeaponToPed`, `RemoveAllPedWeapons`, `SetPedArmour`, `SetPlayerModel`, `TaskWarpPedIntoVehicle`, `ClearPedTasksImmediately`, `SetVehicleNumberPlateText`, `SetVehicleDoorsLocked`, `SetVehicleColours`, `AddBlipForCoord`. Other client natives simply do not exist on the server. RPC calls can silently not apply if nobody owns the entity yet; for values that must stick, set a state bag and apply it in a client change handler.
- Model must exist (`IsModelInCdimage` on client); add-on models need the matching `sv_enforceGameBuild`/stream resource.
- Clean up: `DeleteEntity(veh)` on the server for server-created entities; track handles in a table and delete on `onResourceStop`.

## State bags

```lua
-- server: authoritative writes
Player(src).state:set('duty', true, true)
Entity(veh).state:set('fuel', 63.5, true)
GlobalState.blackout = false

-- client: react
AddStateBagChangeHandler('duty', nil, function(bagName, _, value)
    local ply = GetPlayerFromStateBagName(bagName)
    if ply == 0 then return end
end)
```

Traps:
- `Entity(x).state.tbl.y = 1` does not replicate (the getter deserialises a copy). Write `state:set('tbl', newTbl, true)` or flat keys `state['tbl:y']`.
- Reading `state.x.y` twice deserialises twice - read into a local once.
- Client writes: by default the owner may write its entity bags and its player bag; with `setr sv_stateBagStrictMode true` only the server may write replicated values and clients get `StateBags can't be modified from the client, because the StateBag strict mode is enabled...`. ox_lib (>= 3.37) prints a SECURITY WARNING when strict mode is off (silence with `set ox:ignoreSecurityAdvisory ["stateBagStrictMode"]`, auto-silenced when `qb-core` is present).
- Change handlers fire before the value is stored (old value still readable) and cannot reject changes. Server-side validation of client-written bags is impossible -> keep authoritative data server-written.
- Handler for entity bags runs only where the entity exists; `GetEntityFromStateBagName` returns 0 otherwise.
- Rate limits: clients spamming bag writes get dropped with `Reliable state bag packet overflow.` (`rateLimiter_stateBag_rate/_burst`, `rateLimiter_stateBagSize_rate`).
- Prefer state bags over `playerEnteredScope`/`playerLeftScope` (cost scales with players in scope).

## Routing buckets

```lua
SetRoutingBucketEntityLockdownMode(42, 'strict')
SetRoutingBucketPopulationEnabled(42, false)
SetPlayerRoutingBucket(src, 42)
SetEntityRoutingBucket(veh, 42)      -- entities must be moved too, or the player won't see them
-- back:
SetPlayerRoutingBucket(src, 0)
```

- Bucket 0 = default world. Players see only players/entities in the same bucket. Voice (pma-voice etc.) usually needs its own channel handling.
- Not for interiors (use conceal/visibility natives). Events `onPlayerBucketChange`, `onEntityBucketChange` exist; artifacts 14583-14716 crashed with `onEntityBucketChange` (avoid those builds).

## Scope / culling

- OneSync culls entities ~424 units from a player. A client cannot touch entities it does not have; `GetPlayerPed(GetPlayerFromServerId(id))` fails for far players. Do cross-map logic on the server (`GetPlayerPed(src)`, `GetEntityCoords` work server-side).
- `SetEntityDistanceCullingRadius` / `SetPlayerCullingRadius` are documented as deprecated with unfixable issues.

## Large data

- Events above the reliable size warn `Warning: sending large event X (N bytes). This may cause performance issues. Consider using latent events instead.` Use `TriggerLatentClientEvent(name, target, bps, ...)` or a callback that pages data.
- Event payload is msgpack: functions, userdata and mixed sparse tables do not survive; sparse arrays become maps, `nil` holes truncate arrays.

## Event rate limits (server built-in)

`netEvent` (50/s, burst 200) and `netEventFlood` (75/s, burst 300): overflow -> client dropped with `Reliable network event overflow.`/`Unreliable network event overflow.`. A client loop firing `TriggerServerEvent` every frame will get players kicked. Tune with `set rateLimiter_netEvent_rate N` only after fixing the loop.
