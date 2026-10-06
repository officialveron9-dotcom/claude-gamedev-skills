---
name: fivem-server-setup
description: Configures and troubleshoots FiveM FXServer (Legacy) setups - server.cfg (endpoint_add_tcp/udp, sv_licenseKey, onesync, sv_enforceGameBuild with DLC build numbers up to 3889, ensure order, sv_maxclients, set/setr/sets), artifact choice (recommended 35245 vs latest, known broken builds), txAdmin pitfalls (recipes, onesync setting, TXHOST_ env vars), MariaDB + oxmysql connection, and streaming custom assets (stream folder, data_file entries, add-on vehicles with vehicles.meta/carvariations/carcols/handling, MLOs/ymap/ytyp, clothing, oversized assets). Use when editing server.cfg, adding cars/maps/clothes, updating artifacts or when a server or resource fails to start, or when the user writes German like "Server startet nicht", "Auto einfügen", "Addon Fahrzeug", "MLO einbauen", "server.cfg Fehler", "Artefakte updaten".
---

# FXServer setup and streaming - pitfalls

State 2026-10-06 (Legacy platform). Enhanced servers (`cfx-server.exe`, early access since 2026-07-21) differ: see the `fivem-gta5-enhanced` skill if present.

## Artifacts (server builds)

- Use the **Recommended** build in production. Reported current Recommended: **35245** (built 2026-08-20). Latest tags at time of writing: 36727 (2026-09-28), 36897 (2026-09-30). Hosting providers report that clients stop connecting to servers older than 35245 after **2026-10-15** (client always runs the latest GTA V exe and loads DLC content per `sv_enforceGameBuild`) - verify on the artifacts page/forum, but update before that date.
- Unsupported artifacts older than ~3 months are not joinable from the server browser (EOS grey / EOL red warning).
- Check a build against the community list of broken builds before upgrading (jgscripts fivem-artifacts-db). Recent entries: 31689 (server `GetVehiclePedIsIn` returns 0), 34303/34410 (failed builds), 35186-35214 (Lua `io.readdir` errors), 27783-27938 (SIGSEGV crashes), 28626 (packet loss/timeouts), 25839-25988 (Node sandbox problems). Details: [references/artifacts-gamebuilds.md](references/artifacts-gamebuilds.md).
- Dependencies that need newer builds: oxmysql `/server:12913` (Node 22), qbx_core `/server:10731`, ox_lib `/server:7290`.
- Linux build = `fx.tar.xz` + `run.sh`; Windows `server.7z` + `FXServer.exe`. Keep artifacts outside the server-data folder; update by replacing the artifact folder only.

## server.cfg essentials (order matters)

```cfg
endpoint_add_tcp "0.0.0.0:30120"
endpoint_add_udp "0.0.0.0:30120"      # both, same port; open TCP+UDP 30120 in firewall/router

sv_maxclients 48                       # > 48 needs a paid Cfx.re tier; > 32 needs onesync
set onesync on                         # NOT in server.cfg when using txAdmin (set it in txAdmin settings)
sv_enforceGameBuild 3889               # startup only; see build table
sets sv_projectName "My Project"       # <= 40 chars shown; required for listing
sets sv_projectDesc "Roleplay ..."     # <= 250 chars; required for listing
sv_hostname "My Server"                # <= 120 chars
sets locale "de-DE"                    # replace root-AQ
sets tags "roleplay, german"

exec secrets.cfg                       # set sv_licenseKey "...", set mysql_connection_string "..."

# start order: DB -> libs -> framework -> framework deps -> scripts -> maps/cars
ensure oxmysql
ensure ox_lib
ensure es_extended        # or qbx_core / qb-core
ensure ox_target
ensure ox_inventory
ensure [standalone]
ensure [jobs]
ensure [maps]
ensure [vehicles]
```

Traps:
- `set` vs `setr` vs `sets`: `set` server-only, `setr` replicated to clients, `sets` public server info. Secrets only with `set`. Convars read in `fxmanifest`/scripts at start must be set **before** the `ensure` that reads them (e.g. `mysql_connection_string` before `ensure oxmysql`, `inventory:framework` before ox_inventory/qbx_core).
- `start` fails silently if already started; `ensure` = start or restart. Use `ensure` everywhere.
- `sv_enforceGameBuild`, `onesync`, `increase_pool_size`, `sv_pureLevel`, `sv_kvsName` are startup-only - restart the server, not the resource.
- `#sv_master1 ""` must stay commented, else the server is listed as private.
- `endpoint_add_*` take exactly one argument; with txAdmin `TXHOST_FXS_PORT`/`TXHOST_INTERFACE` override them.
- Don't `ensure`/`stop` `monitor`/txAdmin resources; don't `ensure` a resource twice or both `qb-core` and `qbx_core`.
- `sv_endpointPrivacy` was removed in mid-2026 artifacts (only prints a warning) - delete it.

Annotated full template: [references/server-cfg.md](references/server-cfg.md).

## Game builds (sv_enforceGameBuild)

`1` base game, 2060 Summer Special, 2189 Cayo Perico, 2372 Tuners, 2545 The Contract, 2612, 2699 Criminal Enterprises, 2802 Drug Wars, 2944 Mercenaries, 3095 Chop Shop, 3258 Bottom Dollar Bounties, 3407 Agents of Sabotage, 3570 Money Fronts, 3751 A Safehouse in the Hills, **3889 The Kortz Center Heist** (newest). Aliases: `mp2025_02` = 3751, `mp2026_01` = 3889, `h4` = 2189, `mptuner` = 2372.

- Unset = 3258 on current artifacts. Content needs the build: DLC vehicles/clothes/maps of a newer DLC, and resources declaring `dependency '/gameBuild:3095'`, fail on lower builds (invisible models; resource refuses to start: `sv_enforceGameBuild needs to be at least N (current is M)`).
- Changing the build makes every client restart into it on next join (like pool-size changes) and adds DLC map/vehicle content that can collide with custom maps; test on a staging server. An unsupported number -> clients get `Server specified an invalid game build enforcement`.

## txAdmin pitfalls

- Start `FXServer.exe`/`run.sh` **without** `+exec` so txAdmin (port 40120) manages the server; txAdmin passes `+exec <your cfg>`, `+set onesync <setting>`.
- txAdmin v8.x (8.1.1, June 2026): host config via env vars `TXHOST_DATA_PATH`, `TXHOST_TXA_PORT`, `TXHOST_FXS_PORT`, `TXHOST_INTERFACE`, `TXHOST_MAX_SLOTS`; convars `txAdminPort`, `txDataPath`, `txAdminInterface` are deprecated.
- Recipes deploy a framework base (YAML tasks: download_github, unzip, query_database, replace_string, ...). Re-running a recipe on an existing server overwrites files - deploy to a new folder.
- Save player data on `txAdmin:events:serverShuttingDown` (`delay` ms until kill) and on `txAdmin:events:scheduledRestart` (fires 30/15/10/5/4/3/2/1 min before, `eventData.secondsRemaining`).

## Database

- Install **MariaDB** (not XAMPP). Create a dedicated DB user with rights on one schema; `utf8mb4` charset, `utf8mb4_unicode_ci` collation (Qbox requires it on `citizenid`).
- `set mysql_connection_string "mysql://fivem:PASS@127.0.0.1:3306/fivem?charset=utf8mb4"`; avoid `; , / ? : @ & = + $ #` in the password or use the `user=...;password=...` format.
- Import the framework SQL before first start; import each script's `.sql` on install (`ER_NO_SUCH_TABLE` otherwise).
- Remove `mysql-async`/`ghmattimysql` folders - oxmysql provides them.

## Streaming custom assets

Everything in a resource's `stream/` folder (any depth) is streamed automatically; meta files need `files` + `data_file`. Checklists for add-on vehicles, replacements, MLOs, clothing and size limits: [references/streaming-assets.md](references/streaming-assets.md) - read before adding cars/maps/clothes.

Minimal add-on vehicle pack:
```lua
fx_version 'cerulean'
game 'gta5'
files {
    'data/**/vehicles.meta', 'data/**/carvariations.meta', 'data/**/carcols.meta',
    'data/**/handling.meta', 'data/**/vehiclelayouts.meta',
}
data_file 'HANDLING_FILE'          'data/**/handling.meta'
data_file 'VEHICLE_METADATA_FILE'  'data/**/vehicles.meta'
data_file 'CARCOLS_FILE'           'data/**/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/**/carvariations.meta'
data_file 'VEHICLE_LAYOUTS_FILE'   'data/**/vehiclelayouts.meta'
-- models: stream/<model>.yft, stream/<model>_hi.yft, stream/<model>.ytd
```

## Common setup failures

| Symptom | Fix |
|---|---|
| `Couldn't find resource X` for everything / 0 resources found | Wrong working dir or missing `+exec server.cfg`; resources not in `resources/`. |
| `No license key was specified` | `sv_licenseKey` missing or cfg not executed; key from portal.cfx.re. |
| Server not in list / "private" | `sv_master1` uncommented, ports closed (check `http://IP:30120/info.json` externally), `sv_projectName/Desc` missing, wait up to ~8 min. |
| Only 48 slots usable | Higher `sv_maxclients` needs a Cfx.re subscription tier and OneSync. |
| Slow startup on Windows | Defender scanning: `Add-MpPreference -ExclusionPath 'C:\FXServer\'`. |
| Players can't see each other's cars / weird sync | OneSync off or `legacy` - use `on`. |
| Add-on cars invisible / "model does not exist" | See streaming checklist (meta not loaded, name mismatch, build too low). |
| Escrow errors | Same Cfx.re account for key and purchase; re-upload escrowed files intact (see fivem-security). |

Sources: [references/sources.md](references/sources.md).
