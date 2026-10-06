# fxmanifest.lua reference and traps

Read when writing/reviewing a manifest or when a resource fails to start / files are missing on the client.

## Directives

| Directive | Notes / traps |
|---|---|
| `fx_version 'cerulean'` | Required. Missing -> warning ``Resource X does not specify an `fx_version` in fxmanifest.lua.`` `cerulean` makes NUI a secure context: callbacks must be `https://<res>/<cb>`, not `http://`. |
| `game 'gta5'` / `games {'gta5','rdr3'}` | Required since `adamant`. `common` = only CFX natives, no game natives. |
| `lua54 'yes'` | Deprecated/no-op since June 2025 (Lua 5.3 removed, everything is 5.4). Harmless. |
| `client_script(s)`, `server_script(s)`, `shared_script(s)` | Glob support. Extension picks runtime: `.lua`, `.js`, `.net.dll`. Load order = listed order. `@other/file.lua` loads a file from another resource (that resource must be started first or listed as dependency). |
| `files {}` / `file ''` | Every client-side non-script file (NUI html/js/css/images, meta files for `data_file`, JSON loaded with `LoadResourceFile` on the **client**). Forgotten files -> 404 in NUI / `LoadResourceFile` returns nil on client. Server-side `LoadResourceFile` does not need `files`. |
| `ui_page 'web/index.html'` | One page per resource. File + its assets must be in `files`. Remote URL allowed. |
| `loadscreen 'x.html'` + `loadscreen_manual_shutdown 'yes'` | Then close with `ShutdownLoadingScreenNui()`; otherwise the loadscreen stays forever. |
| `dependency 'x'` / `dependencies {}` | Resource must exist and start first, else `Could not find dependency X for resource Y.` Constraints: `'/server:12913'`, `'/onesync'`, `'/gameBuild:3095'` (or alias like `h4`), `'/native:0xHASH'`, `'/policy:subdir_file_mapping'`. |
| `provide 'mysql-async'` | Resource stands in for another (oxmysql provides `mysql-async`, `ghmattimysql`; qbx_core provides `qb-core`; ox_target provides `qtarget`). Never ship the real and the provider together. |
| `export 'fn'` / `server_export 'fn'` | Legacy declarative exports of **global** functions. Prefer `exports('fn', fn)` in code. |
| `data_file 'TYPE' 'path'` | Game data (vehicles.meta, handling, carcols, ...). Path must also be in `files`. Globs allowed in the path. |
| `this_is_a_map 'yes'` | For map/MLO resources (ymap/ytyp in `stream/`). |
| `server_only 'yes'` | Clients download nothing (use for pure server libs). |
| `node_version '22'` | Server JS uses Node 22 instead of default 16. Artifact >= 12913. |
| `use_experimental_fxv2_oal 'yes'` | Faster native calls; **breaks vector unpacking**: `SetEntityCoords(ped, coords)` must become `SetEntityCoords(ped, coords.x, coords.y, coords.z)`; wrongly-typed natives misbehave. Used by ox_lib/ox_inventory/qbx_core - do not copy blindly. |
| `escrow_ignore {}` | Files that stay readable when uploaded to Asset Escrow (configs!). |
| `ox_libs {'locale','table'}` / `ox_lib 'locale'` | Custom metadata read by ox_lib; preloads modules. |
| `convar_category` | FxDK UI only. |
| arbitrary keys (`my_data 'x'`) | Readable with `GetNumResourceMetadata`/`GetResourceMetadata`. |

## Wrong vs right

```lua
-- WRONG (2018-era)
resource_manifest_version '44febabe-d386-4d18-afbe-5e627f4af937'
client_script 'client.lua'

-- RIGHT
fx_version 'cerulean'
game 'gta5'
client_script 'client.lua'
```

```lua
-- WRONG: NUI build output not shipped
ui_page 'web/dist/index.html'
files { 'web/dist/index.html' }          -- assets/*.js missing -> blank UI

-- RIGHT
files { 'web/dist/index.html', 'web/dist/**/*' }
```

```lua
-- WRONG: ox_lib loaded twice -> "Cannot load ox_lib more than once."
shared_scripts { '@ox_lib/init.lua', '@ox_lib/init.lua', 'config.lua' }
-- WRONG: ox_lib not started before this resource -> "ox_lib must be started before this resource."
-- RIGHT: '@ox_lib/init.lua' once, first in shared_scripts, and `ensure ox_lib` earlier in server.cfg
```

```lua
-- WRONG: config only on server but read on client
server_script 'config.lua'
client_script 'client.lua'          -- Config is nil -> attempt to index a nil value (global 'Config')
-- RIGHT
shared_script 'config.lua'
```

Secrets (webhook URLs, API keys) never go into `shared_script`/`client_script` files - those are downloaded to every client. Keep them in a server-only file or a `set` convar.

## Folder layout that avoids trouble

```
my_resource/
  fxmanifest.lua
  shared/config.lua        -- non-secret config
  server/main.lua
  server/secrets.lua       -- server_script only (or use convars)
  client/main.lua
  web/dist/...             -- built NUI (commit the build or build in CI)
  stream/                  -- streamed assets (auto-mounted, no manifest entry needed)
```

Resource folder name = resource name. `[category]` folders (brackets) are only grouping; `ensure [category]` starts all inside.
