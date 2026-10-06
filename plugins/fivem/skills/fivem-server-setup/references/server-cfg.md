# Annotated server.cfg template (Legacy FXServer, 2026-10)

Read when writing or reviewing a complete server.cfg.

```cfg
## ---------- network ----------
endpoint_add_tcp "0.0.0.0:30120"
endpoint_add_udp "0.0.0.0:30120"
# sv_endpoints "1.2.3.4:30120"            # only if clients must use a specific public IP
# sv_listingIpOverride "1.2.3.4"           # behind NAT/proxy
# net_tcpConnLimit 16                      # per-IP TCP connection limit (default 16)

## ---------- identity / listing ----------
sv_hostname "My Server"                    # <= 120 chars
sets sv_projectName "My Project"           # <= 40 chars, a name, no tag lists
sets sv_projectDesc "German roleplay ..."  # <= 250 chars, a sentence
sets locale "de-DE"
sets tags "roleplay, german, economy"
load_server_icon "icon.png"                # 96x96 PNG
# sets banner_detail "https://..."  / sets banner_connecting "https://..."
# sets sv_appearAllowlisted true ; sets sv_allowlistInstructions "Join discord.gg/..."   # txAdmin overrides these
#sv_master1 ""                             # keep commented, else server shows as private

## ---------- game ----------
sv_maxclients 48                           # >48 requires a Cfx.re subscription tier
set onesync on                             # omit when using txAdmin (set in txAdmin settings)
sv_enforceGameBuild 3889                   # startup-only
# increase_pool_size "TxdStore" 6000       # startup-only, only listed pools/limits
# set onesync_population false             # no ambient peds/cars (saves CPU)

## ---------- security ----------
sv_scriptHookAllowed 0
sv_pureLevel 1
set sv_entityLockdown relaxed
setr sv_stateBagStrictMode true
set sv_filterRequestControl 2
set sv_enableNetworkedSounds false
# rcon_password  -> leave unset

## ---------- secrets (separate file, not in git) ----------
exec secrets.cfg
#   set sv_licenseKey "cfxk_..."
#   set mysql_connection_string "mysql://fivem:...@127.0.0.1:3306/fivem?charset=utf8mb4"
#   set steam_webApiKey "..."              # needed only for steam: identifiers
#   sv_tebexSecret "..."

## ---------- resource convars (before the ensure that reads them) ----------
set mysql_slow_query_warning 150
setr ox:locale "de"
setr inventory:framework "esx"             # "qbx" for Qbox
setr esx:locale "de"

## ---------- permissions ----------
add_ace group.admin command allow
add_ace group.admin command.quit deny
add_principal identifier.fivem:123456 group.admin
add_ace resource.ox_lib command.add_ace allow
add_ace resource.ox_lib command.remove_ace allow
add_ace resource.ox_lib command.add_principal allow
add_ace resource.ox_lib command.remove_principal allow
# exec permissions.cfg

## ---------- resources ----------
ensure mapmanager
ensure chat
ensure spawnmanager
ensure sessionmanager
ensure hardcap
ensure oxmysql
ensure ox_lib
ensure es_extended
ensure ox_target
ensure ox_inventory
ensure [core]
ensure [scripts]
ensure [maps]
ensure [vehicles]
```

Notes:
- Framework recipes ship their own server.cfg (and often `ox.cfg`, `permissions.cfg`, `voice.cfg` for Qbox). When merging, keep one `ensure` per resource and the recipe's order.
- Default cfx-server-data resources (`mapmanager`, `chat`, `spawnmanager`, `sessionmanager`, `hardcap`, `basic-gamemode`, `rconlog`) are often replaced by framework equivalents (e.g. ESX/Qbox spawn handling) - don't run two spawn managers.
- `exec @resourceName/file.cfg` executes a cfg shipped inside a resource.
- Use `#` for comments at line start; inline `#` after commands works for most commands but not inside quoted values.
- With txAdmin: `TXHOST_MAX_SLOTS` caps `sv_maxclients`; the cfg editor validates and comments out `onesync` lines.
