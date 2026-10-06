# server.cfg hardening block and side effects

Read when editing server.cfg security settings or debugging "my script broke after enabling lockdown/strict mode".

```cfg
# --- secrets: keep in secrets.cfg (not in git), loaded with: exec secrets.cfg
set sv_licenseKey "cfxk_..."
set mysql_connection_string "mysql://fivem:...@127.0.0.1:3306/fivem?charset=utf8mb4"
set steam_webApiKey ""
set my_discord_webhook "https://discord.com/api/webhooks/..."   # read only by the logging resource:
add_convar_permission my_logger read my_discord_webhook

# --- client trust
sv_scriptHookAllowed 0
sv_pureLevel 1
set sv_entityLockdown relaxed          # 'strict' once all spawning is server-side
setr sv_stateBagStrictMode true        # server >= 12739
set sv_filterRequestControl 2          # or 3/4; 0 = off (default)
set sv_enableNetworkedSounds false
set sv_enableNetworkedScriptEntityStates false
# set sv_enableNetworkedPhoneExplosions false   # default already false
# block_net_game_event "EXPLOSION_EVENT"        # only if no resource needs it; test first

# --- misc
# rcon_password left unset (RCON disabled)
sv_disableClientReplays true           # disables Rockstar Editor
```

## Side effects to expect

| Setting | Symptom in existing scripts | Code fix |
|---|---|---|
| `sv_entityLockdown strict` | Client `CreateVehicle/CreateObject/CreatePed` with network=true return entities that never appear for others or get deleted; garages/jobs spawn nothing | Spawn server-side (`CreateVehicleServerSetter`, `CreateObjectNoOffset`, server `CreatePed`) and send net IDs. Local-only props (`isNetwork=false`) still work. |
| `sv_entityLockdown relaxed` | Script-created networked entities blocked, ambient population still works | Same as above. |
| `sv_stateBagStrictMode true` | F8: `StateBags can't be modified from the client, because the StateBag strict mode is enabled.` | Move writes to the server (event -> validate -> `Player(src).state:set`). Local-only bag writes (`replicated=false`) still work. |
| `sv_filterRequestControl >= 1` | `NetworkRequestControlOfEntity` never succeeds for player-occupied vehicles (warns in client console) | Do the action server-side or on the current owner (`NetworkGetEntityOwner` + targeted client event). |
| `sv_pureLevel 2` | Players with graphics/audio mods cannot join | Use 1 if visual mods are acceptable. |
| Rate limiters (`rateLimiter_netEvent_*`, `rateLimiter_stateBag_*`) | Players dropped: `Reliable network event overflow.`, `Reliable state bag packet overflow.` | Fix the spamming loop; raise limits only as last resort. |

## Per-bucket lockdown

```lua
SetRoutingBucketEntityLockdownMode(0, 'strict')    -- also what qbx_core's qbx:bucketlockdownmode sets for bucket 0
```

## HTTP endpoints

- `sv_requestParanoia 1..3` blocks proxied/browser floods of `/info.json`, `/dynamic.json`, `/players.json` (level >= 2 breaks browser access to these).
- `/players.json` only includes names/identifiers when `sv_playersToken` is set and supplied (artifacts from ~July 2026); `sv_endpointPrivacy` and `sv_exposePlayerIdentifiersInHttpEndpoint` were removed (warning only).
- Prometheus `/perf` can be protected with `sv_prometheusBasicAuthUser` / `sv_prometheusBasicAuthPassword`.
- Behind a proxy: `sv_forceIndirectListing`, `sv_proxyIPRanges`, `sv_httpFileServerProxyOnly true` (server >= 10543) so the file server only answers your proxy.
