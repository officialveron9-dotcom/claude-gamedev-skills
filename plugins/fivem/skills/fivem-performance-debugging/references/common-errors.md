# Common FiveM console / F8 errors -> cause -> fix

Read for any server-console, txAdmin or F8 error. Messages marked (src) were verified verbatim in the citizenfx/fivem source; placeholders in `<>`. Framework/DB-specific errors are also in the fivem-frameworks skill (`references/migration-errors.md`).

## Resource loading (server console)

| Message | Cause | Fix |
|---|---|---|
| `Couldn't find resource <name>.` (src) | Folder name differs from the `ensure` name, no `fxmanifest.lua`/`__resource.lua` in the folder, folder nested inside another resource, or server not `refresh`ed after adding | Folder name = resource name; manifest at folder root; `refresh` then `ensure`. Server started from the wrong working directory (no `+exec`/wrong cwd) also finds 0 resources. |
| `Couldn't find resource category <[name]>.` (src) | `ensure [cat]` but no such bracket folder | Check spelling incl. brackets. |
| `Couldn't start resource <name>.` (src) | Summary only | Scroll up: dependency, manifest or script error printed before it. |
| `Could not find dependency <dep> for resource <name>.` (src) | `dependency`/`dependencies` entry not present/started, or constraint not met (e.g. `/server:12913` on older artifact, `/onesync` with OneSync off, `/gameBuild:` above enforced build) | Install/ensure the dependency first; update artifact; enable OneSync; raise `sv_enforceGameBuild`. |
| `Resource <name> does not specify an `fx_version` in fxmanifest.lua.` (src) | Missing `fx_version` | `fx_version 'cerulean'` + `game 'gta5'`. |
| `<name> has an outdated manifest (__resource.lua instead of fxmanifest.lua)` (src) | Legacy manifest | Convert to fxmanifest.lua. |
| `Error parsing script @res/file.lua in resource <res>: ...:<line>: <syntax error>` (src) | Lua syntax error (missing `end`, `=` vs `==`, stray char, non-CfxLua syntax in a different runtime) | Fix the line shown; note CfxLua accepts `+=`/`?.` but external linters may not. |
| `Error loading script @res/file.lua in resource <res>` (src) | Runtime error while executing the file top-level (nil global, failed `require`, error() in config) | Read the `SCRIPT ERROR` printed with it; guard top-level code. |
| `Permission denied` / error code 13 on `io.open`, `SaveResourceFile`, `os.execute`, `io.popen` | Server sandbox: writing outside own resource, `..` traversal, process spawning | Use `@thisres/path`; for legit cross-resource writes `add_filesystem_permission a write b`; processes need `add_unsafe_child_process_permission`. |
| `You lack the required entitlement ...` | Escrowed asset not owned by the Cfx.re account behind `sv_licenseKey` | Use the license key of the purchasing account, or transfer/grant the asset in the Cfx.re Portal. |
| `Failed to verify protected resource` | Escrow files damaged/missing (`.fxap`), FTP ASCII/partial transfer, renamed protected files, very old artifact | Re-download from Portal, upload the zip and extract on the server (SFTP/WinSCP binary), don't rename escrowed files, update artifacts. |
| `No license key was specified` (startup) | `sv_licenseKey` missing, or server started without `+exec server.cfg` / from wrong folder | Set `sv_licenseKey`; start from the server-data folder with `+exec server.cfg` (txAdmin handles this). |
| `Unable to establish a connection to the database (<CODE>)!` (oxmysql src) | DB down / creds / host / DB name; codes `ECONNREFUSED`, `ER_ACCESS_DENIED_ERROR`, `ER_BAD_DB_ERROR`, `ETIMEDOUT` | Start MariaDB, fix `set mysql_connection_string`, use `127.0.0.1`, create DB. |
| `<res> took N ms to execute a query!` (oxmysql) | Slow query (threshold `mysql_slow_query_warning`, default 200) | Index lookup columns; avoid `SELECT *` on big tables; cache static data. |

## Lua runtime (both sides)

| Message | Cause | Fix |
|---|---|---|
| `SCRIPT ERROR: @res/path.lua:<line>: <msg>` + stack | Uncaught runtime error in a thread/event/export | Fix at the top frame of your resource; see nil table below. |
| `attempt to index a nil value (global 'X')` | Global not defined on this side/yet: ESX/QBCore/lib/MySQL/Config | Correct manifest includes (`@es_extended/imports.lua`, `@ox_lib/init.lua`, `@oxmysql/lib/MySQL.lua`), `shared_script` for config, start order. |
| `attempt to index a nil value (local/field 'X')` | Lookup returned nil: player not loaded, entity gone, table key typo, string vs number key | Nil-guard; `tonumber`; check data exists before use. |
| `attempt to call a nil value (global 'X')` | Native not available on this side (client native on server or vice versa), typo, function defined later/local in another file | Use the right side; check native `apiset`; define before use. |
| `attempt to call a nil value (method/field 'X')` | API removed/renamed (`Player.Functions.AddItem`), wrong object | Use current API (see fivem-frameworks). |
| `attempt to compare number with string` | `GetPlayers()` returns strings, convars/NUI/JSON give strings | `tonumber(x)`. |
| `attempt to perform arithmetic on a nil value` | Missing field (e.g. `money.bank` on ESX where accounts are a list) | Use the framework's accessor; nil-check. |
| `bad argument #1 to 'pairs'/'ipairs' (table expected, got nil)` | Iterating a nil result (DB returned nil, callback timed out) | Default `or {}`; check DB/callback result. |
| `Current execution context is not in the scheduler, you should use CreateThread / SetTimeout or Event system (AddEventHandler) to be able to Await` (src) | `.await`/`Citizen.Await` at file top level | Wrap in `CreateThread(function() ... end)` or `MySQL.ready(function() ... end)`. |
| `attempt to yield from outside a coroutine` / `attempt to yield across a C-call boundary` | `Wait`/`.await` at top level or inside non-yieldable callbacks (`table.sort` comparator, `string.gsub` function, metamethods) | Move the wait into a thread; fetch data before sorting. |
| `Setting values on Entity is not supported at this time.` (src) | `Entity(x).foo = 1` | `Entity(x).state.foo = 1` / `:set()`. |
| `error during NUI callback <name>: <err>` (src) | Lua error inside `RegisterNUICallback` handler (the page's fetch then never resolves) | Fix error; always `cb()`. |
| `No current resource manager` (JS) | Native called from a Node/libuv callback thread | `setImmediate(() => ...)` before natives. |

## Events, exports, callbacks

| Message | Cause | Fix |
|---|---|---|
| `event <name> was not safe for net` (src) | Net-triggered event registered with `AddEventHandler` only, or event name typo (also: cheaters probing names) | `RegisterNetEvent(name, fn)` on the receiving side; check spelling on both sides. |
| `No such export <fn> in resource <res>` (src) | Provider not started (or started later), export defined on the other side, typo/case, provider errored during load, using `exports.res.fn` before the first tick of `export` manifest entries | `ensure` provider earlier + `dependency`; call on the correct side; check provider's own errors. |
| `An error occurred while calling export `<fn>` in resource `<res>`:` (src) | The export itself threw | Debug inside the provider; the nested trace follows. |
| `cannot set values on exports` / `cannot set values on an export resource` (src) | `exports.res = ...` or `exports.res.fn = ...` | Define with `exports('fn', fn)`. |
| `callback '<name>' does not exist` / `callback event '<key>' timed out` (ox_lib) | Not registered on the other side / handler never returned / provider crashed | Register on the right side; return a value on every path; check `SCRIPT ERROR`. |
| `Warning: sending large event <name> (<N> bytes). This may cause performance issues. Consider using latent events instead.` (src) | Huge event payload | `TriggerLatentClientEvent`/`TriggerLatentServerEvent`, paginate, send IDs instead of full tables. |

## Player drops / connection

| Message | Cause | Fix |
|---|---|---|
| `Reliable network event overflow.` / `Unreliable network event overflow.` / `latent event packet overflow.` (src, drop reason) | Client exceeded net-event rate limit (default 50/s, burst 200) - usually `TriggerServerEvent` in a loop | Remove per-frame server events; batch; tune `rateLimiter_netEvent_rate/_burst` only as last resort. |
| `Reliable state bag packet overflow.` (src) | Client spamming state bag writes | Write bags server-side or on change only; `rateLimiter_stateBag_*`. |
| `Reliable server command overflow.` (src) | Client spamming commands (keybind loops) | Fix the keybind/command loop. |
| `Server->client connection timed out. Pending commands: N.` (src) | Client can't keep up (huge event bursts, slow download, packet loss), or bad artifact (28626 had packet-loss issues) | Reduce burst traffic; latent events; update artifact; check host network. |
| `... timed out after 60 seconds` (drop reason) | Client stopped sending (game freeze/crash, network loss); en masse = server hitch or host network | Check server hitch warnings; host network; client crash dumps. |
| `Reliable network event size overflow: ...` (drop reason) | Single client->server event too large | Send less data; split; latent events. |
| `Game crashed: <hash>` / German `Spielabsturz: ...` (drop reason) | Client crash, often a broken streamed asset or bad native call | Group by crash hash in txAdmin; test recently added stream resources; check F8 before the crash. |
| `Invalid client configuration. Restart your game and reconnect` (drop reason) | Client failed the server-settings verification (txAdmin classes it as security; related to `sv_pure_verify_client_settings`: pure level, script hook) | Player restarts the game without mods; check `sv_pureLevel`/`sv_scriptHookAllowed`. |
| `This server requires a different game build (X) from the one you're using (Y). ...` (src) | Build switch failed / client not restarted | Let the client restart into the build; verify `sv_enforceGameBuild` is a supported number. |
| `Server specified an invalid game build enforcement (N).` (src) | Unsupported number in `sv_enforceGameBuild` | Use a listed build (1, 2060, 2189, ..., 3570, 3751, 3889). |
| `Client/Server game build revision mismatch: ...` (src) | Outdated artifact vs client after a title update | Update server artifacts. |
| End-of-support (grey) / end-of-life (red) warning when joining | Outdated artifacts (unsupported > 3 months are not joinable from the browser) | Update to the current recommended artifact. |
| `Connection to CNL timed out.` (kick) | Player's Cfx.re auth link lost (`sv_kick_players_cnl_*` convars) | Player-side network; don't tighten those convars without reason. |

## Streaming and assets

| Message | Cause | Fix |
|---|---|---|
| `Asset <res>/<file> uses N MiB of physical memory.` (yellow > 16, ... > 32, red > 64 MiB) ` Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering).` (> 48 MiB) (src) | Too-large `.ytd`/`.yft`/`.ydr` (uncompressed 4K textures, no mipmaps) | Resize textures (max 2048, usually 1024), DXT/BC compression with mipmaps, split ytd; physical vs virtual both count. |
| Vehicle spawns invisible / "model does not exist" | `stream/` files missing, model name mismatch with `vehicles.meta` `modelName`, meta files not in `files`+`data_file`, needs higher `sv_enforceGameBuild` | See fivem-server-setup streaming checklist. |
| Textures pop / map holes with big map packs | Pool/texture budget exhausted | `increase_pool_size` for supported pools; reduce assets. |
| `NetworkRequestControlOfEntity is deprecated, and should not be used because of potential abuse by cheaters. To disable this check, set "sv_filterRequestControl" "0".` (src) | Script relies on requesting control while filter is on | Do the action server-side / on owner; keep the filter. |
| `StateBags can't be modified from the client, because the StateBag strict mode is enabled. ...` (src) | Client writes replicated state with strict mode | Write via server. |

## Performance warnings

| Message | Cause | Fix |
|---|---|---|
| `server thread hitch warning: timer interval of N milliseconds` (src; > 150 ms) | Main thread blocked: heavy sync Lua/JS work, big JSON/file IO, resource (re)starts, host CPU starvation | Profile (`profiler record 500` on the server console), spread work over ticks, cache. One-off during boot/restart is normal. |
| `network thread hitch warning: ...` / `sync thread hitch warning: ...` (src) | Host overload, too many entities/players for the CPU | Check host CPU steal/load; reduce population/entities; better hardware. |
| `hitch warning: frame time of N milliseconds` (src) | Long server frame | Same as above. |
| `<res> is taking N ms (or -X FPS @ 60 Hz)` (client, avg > 6 ms) (src) | Expensive client loop | See SKILL.md client patterns; `resmon`, profiler. |
