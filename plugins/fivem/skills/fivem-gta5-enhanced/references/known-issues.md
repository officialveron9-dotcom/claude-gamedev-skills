# Known issues: FiveM for GTAV Enhanced (snapshot 2026-10-06)

Source: GitHub Discussions in `citizenfx/rfc` (the official Enhanced bug tracker). "#n" means
`https://github.com/citizenfx/rfc/discussions/n`. Status is as read on 2026-10-06. Server builds seen
in reports: about 123 (08-20), 139, 153, 156, 157, 161 (10-04). Things move fast, so re-check the
thread before you tell a user something is still broken.

## Open / unresolved

| Issue | Workaround | Source / status |
|---|---|---|
| Client freezes at 100% loading when the server serves `data_file` mounts (even a stock `explosion.ymt`) on server **b157** | Run server **b156** | #567 (2026-10-01), open |
| Custom ped models invisible (spawned ped or player model) | None known | #543 (09-24, b153), triaged |
| `increase_pool_size` ineffective for `CWeaponComponentInfo` (gen9 stock 470, 465 used), so 6+ custom weapon attachments crash the client | Keep custom attachments under the free slots | #524 (09-19, b139), triaged |
| Server performance regression vs b139 at moderate player counts (Linux RP server) | None. Staff asked for Prometheus metrics | #536 (09-23), needs-more-info |
| Resource downloads abort on slow connections ("Connection to the host has been aborted") | Raise `sv_resourceFileDownloadTimeout` (default 2 min). Untested as a fix | #561 (09-28), triaged |
| `SetNuiFocusKeepInput` has no effect (game input locked while NUI focused) | None. Staff asked for a minimal repro | #555 (09-27, b156/b157), triaged |
| NUI lag | None known | #514 (09-13), triaged |
| Loading screen: only `loadProgress` (with numeric `stage`); Legacy's granular events and `onLogLine` are missing | Plain 0-100% progress bar | #427 (08-18); staff: "we are looking into this" (08-26) |
| `InterpolateCamWithParams` "invalid native" | 09-22 patch notes say it is exposed, but the thread was still open on 09-23. Possible fallback: `SetCamActiveWithInterp` (untested on Enhanced) | #476, triaged |
| `ResetEntityDrawOutlineRenderTechnique` not working | None | #513 |
| `RegisterConsoleListener` freezes the console (the earlier server crash was fixed in Hotfix 1) | Avoid heavy console listeners | #488 |
| `RegisterRopeData` "rope pool full" | 08-11 patch says fixed; label "fix-to-be-confirmed" | #43 |
| Player IDs reused quickly (docs) / cycle at ~4096 (reports) | Key data by identifier; clean ACE principals on drop | #136, docs |
| No API to get the command ID of default commands (for `UnregisterCommand`) | — | #504 |
| Lua profiler scopes not working | Use Perfetto / resource time graphs | #510 |
| Voice sounds robotic/delayed | — | #551 |
| C# server crash: `NotImplementedException` from `CancelIoEx` when an HTTP/WebSocket op is cancelled | Do not cancel: `CancellationToken.None`, race with `Task.Delay`, `WebSocket.Abort()` | #572 (10-04, b161), open |
| C# client library has a hardcoded server-side element | — | #559 (area/dotnet) |
| C# `TriggerLocalEvent` throws during `playerDropped` | — | #557 (area/dotnet) |
| C# sandbox blocks some BCL/ADO.NET APIs (e.g. `DbConnectionStringBuilder`) | Partly fixed in the 08-20 C# patch (Npgsql, EF Core, DI whitelisted). Dev only: `sv_devMode 1` + `sv_enableCoreclrSandboxing 0`. Request APIs in #440 | #107 |
| No dual-stack (IPv4+IPv6) listening | — | #516 |
| `ERR_GEN_ZLIB_1` on Simplified Chinese systems; zlib init failure | — | #547, #573 |
| Launch problems with Rockstar Games Launcher / Epic Games | — | #574, #575 (10-04); earlier #6 (Epic) |
| NUI media permission dialog unresponsive | — | #571 |
| Resource Monitor crash after `ensure` | — | #570 |
| **Asset Escrow not implemented** | Keep escrowed resources on Legacy | docs; #58 (no staff reply) |
| **Graphics mods not allowed** (pure mode always on) | None during early access | docs |

## Fixed during early access (if a user is on an old build, update)

| Fixed | What |
|---|---|
| Hotfix 1 (07-21) | File load order and `_`-prefixed files first; loading screen handover object + `serverAddress`; `RegisterConsoleListener` crash; `SetDiscord*` crash; JS `getPlayers()`/`getPlayerIdentifiers()` restored; `RegisterKeyMapping` defaults; external loading screens |
| Hotfix 2 (07-22) | `provide` satisfies dependencies; server player state bags replicate to the owner; ACE checks in `playerConnecting`; `deferrals.done()` msgpack error; `PerformHttpRequest` >10 MB; KVP find natives; async JS exports; `GetCamMatrix` |
| Hotfix 3 (07-23) | NUI callbacks from external `ui_page` (403); runtime textures; non-Latin text in NUI; `GetInvokingResource`; Qbox "asset version mismatch"; `IsPlayerAceAllowed` string source |
| Hotfix 4 (07-24) | DUI flipped; `SetVehicleHandling*` fields; `NetworkIsPlayerTalking`; `GetConvar` without default crash; `LoadResourceFile` empty file returns `""`; C# `[FromSource]` |
| Hotfix 5 (07-27) | `NetworkGetEntityOwner` returns `-1` for server-owned (was 65535); `Decor*` natives; `SetNuiFocus` release delay; `sv_endpoints`/proxy listing; cfg comments; TLS 1.3 |
| Hotfix 6-8 (07-29 to 08-06) | ENet handshake retry; ox_lib import spam; `GetPlayerEndpoint` IP only; invisible player after exiting a vehicle; ox_target refocus; 3+ add-on vehicles crash; 2048 px vehicle textures |
| 08-04 patch | `GetGamePool('CObject')` near MLOs; head blend/overlay getters; `RegisterNUICallback` types; `onesync_maxNearby*` convars; advanced population on by default |
| 08-11 patch | `SetHttpHandler` POST data; rope natives; routing-bucket vehicle leak; Raw Input default mouse mode; diagnostics endpoints need auth |
| Hotfix 9-11 (08-12 to 08-19) | `.ttf/.otf` NUI fonts; server-spawned vehicles at boot visible; `SetPlayerName`, `onPedDeath`, `onPedHealthChanged`; deferral kicks; non-spatial voice / pma-voice radio |
| 08-31 patch | Resource start events aligned with Legacy; `SaveResourceFile` numbers/bools; server RPC natives in capitalised resources; `stream_enhanced` + `stream` deprecation warning; KVP no longer tied to server URL |
| 09-22 / 09-24 | Cutscenes load; synced scenes for all; `DeleteEntity` ghost entities; `add_ace` takes effect at runtime; 25 MB/s cap removed; `ensure` exact-name match; `AddEventHandler` cross-resource refs; decorator pool 1500 crash |
| 09-30 | `gameEventTriggered` `CEventNetworkPlayerEnteredVehicle` restored; state bag 32 KB limit; parallel sync processing; `netGameEvent` rate limiters |

## Triage heuristics for Claude

1. Connection or handshake errors right after a Cfx patch: update cfx-server.
2. Crash or invisible content with custom assets: check that the assets are Gen9 (Alchemist), the
   128-material limit, and `script_rt_` texture formats. Then check #543 and #567.
3. Script works on Legacy but not on Enhanced: check this table, then search `citizenfx/rfc`
   discussions for the native or event name.
4. Never promise a fix date. Cfx gives none.
