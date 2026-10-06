# Legacy vs Enhanced: full reference

Primary source: docs.fivem.net "What's Changed in FiveM for GTAV Enhanced"
(`content/docs/developers/legacy-vs-enhanced.md` in `citizenfx/fivem-docs`, HEAD 2026-10-01),
server-commands, voice and console-commands pages, plus the official patch notes in
`citizenfx/rfc` Discussions. Tags: [Official], [Reported], [Unknown].

## Removed or deprecated on Enhanced [Official]

| Feature | Status on Enhanced |
|---|---|
| P2P sync | Removed. Client-server model only. |
| OneSync non-big mode | Removed. Big mode only: player connect/disconnect events arrive only for players in range. |
| `onesync_automaticResend` (ARQ) | Removed. |
| `onesync` convar | Read-only (Hotfix 1, 2026-07-21). OneSync is always on. |
| Asset Escrow | Not implemented yet. No staff timeline (rfc #58 had no staff reply as of 2026-10-06). |
| `sv_netHttp2` | Removed (no HTTP/2). |
| Server ImGui GUI | Removed. |
| `+set moo 31337` | Removed. Use `sv_devMode true` in server.cfg. |
| `sv_useAccurateSends` | Deprecated. Use `set sv_syncTickRate <1-120>`. |
| `-cl2` client param | Deprecated. Use F8 > Debug > "Launch Additional Client" (needs `sv_devMode true`). |
| Mumble | Deprecated. The new voice stack replaces it; Mumble natives still route through it. |
| Resource builders | Resources can no longer be builders. |
| Multiple endpoints | `endpoint_add_tcp`/`endpoint_add_udp` accept a single endpoint only. |
| Graphics mods | Pure mode always on; graphics mods not usable during early access. |
| Remote Console (DevCon) | Disabled by default. Enable in client F8 > Console > "Remote Console"; port `29200` (`29300` no longer used). |

No-op compatibility convars (accepted but ignored): `onesync_enableBeyond`, `sv_enhancedHostSupport`,
`sv_protectServerEntities` (use `sv_entityLockdown`).

## Breaking behaviour changes [Official unless marked]

- **Player/server IDs**: the docs say an ID is released on disconnect and may be reused by the next
  joiner (Legacy only increments up to 65535). Staff (rfc #136, 2026-07-25): "We will only reuse
  them up to 4k". The 2026-08-31 patch says "Entity and player ID handling improved to prevent
  reuse". [Reported] IDs now cycle at about 4096. Key all persistent data by identifier.
- **KVP database**: must be migrated with `citizenfx/kvdb-migrator` (Bun/TS tool; asks for the
  Legacy `db/<sv_kvsName>` folder and an output path). Since 2026-08-31, KVP DBs are no longer
  keyed by server URL, so data survives IP/proxy changes.
- **Remote commands**: output is no longer returned automatically. Call `PrintRemoteCommandLog(message)`.
- **Mono replaced by .NET**: needs the .NET 10 SDK. CoreCLR sandbox is on. For development only,
  `sv_devMode 1` plus `sv_enableCoreclrSandboxing 0` partially disables it (C# patch 2026-08-20).
  Whitelisted NuGet packages include Microsoft.Extensions.Logging.Abstractions,
  Microsoft.Extensions.DependencyInjection, Microsoft.EntityFrameworkCore and Npgsql. Legacy
  `CitizenFX.Core` assemblies load. Added: StateBag API, `API.EveryTick`, `[OnTick]`, ColShape API.
- **State bags**: callbacks fire only if the entity exists. Replicated values are only replicated
  if explicitly set. Since 2026-09-30: max 32 KB per value (was 256 KB), key names up to 1024
  chars, warnings above 256-char keys or 1 KB values.
- **Lockdown**: there is a new mode `full` that disables client dummy-object creation
  (Enhanced only). In `relaxed` mode, population entities spawn only if the player owns the world
  grid. The 2026-08-31 patch notes say `sv_entityLockdown` "accepts `no_dummy` mode again". Verify
  which name your build accepts.
- **Resource start events** (client): `onResourceStart` stopped firing for a resource's own start
  (2026-07-27). The 2026-08-31 patch aligned behaviour with Legacy: `onClientResourceStart` fires for
  all resources, and `onResourceStarting`/`onResourceStart` fire only on restart.
- **Threads**: threads created during resource load get their first tick after
  `onClientResourceStart` (2026-09-24).
- **Commands**: `RegisterCommand` returns an ID; `UnregisterCommand(id)` is new. There is no way to get
  the ID of default commands (rfc #504, open).
- **Unhandled net events**: `sv_disconnectOnUnhandledUnhandledNetEvent` (default off) disconnects
  clients that send unhandled reliable network events (2026-09-22; the name is spelled that way in the notes).

## Game builds [Official]

- Enhanced supports **only the latest game build, "The Kortz Center Heist"**. The docs table lists
  it as `3889` / `mp2026_01`. It loads by default when no build is set.
- `sv_enforceGameBuild 1` loads the base game without DLC.
- Do not set other build numbers on Enhanced. They are not supported. Community reports say a
  Legacy build number "locks Enhanced clients out". [Reported]
- Legacy keeps the full build list (1, 1604 … 3751, 3889) and `sv_replaceExeToSwitchBuilds`.

## New or Enhanced-only server convars and commands [Official]

| Convar / command | Default | Notes |
|---|---|---|
| `sv_syncTickRate` | 60 | Range 1-120. Replaces `sv_useAccurateSends`. |
| `sv_resourceFileDownloadTimeout` | 2 min | HTTP resource file download timeout (ms). |
| `sv_ioThreads` | 0 (= cores, 2-4) | Network IO threads, startup only. |
| `sv_clientConnectingTimeoutMilliseconds` | 60000 | |
| `sv_clientConnectedTimeoutMilliseconds` | 120000 | |
| `sv_pingIntervalMilliseconds` | 5000 | |
| `sv_voiceChat` | false | "controls whether voice chat is enabled" |
| `voice_internal` | — | Start the internal voice server (voice docs). |
| `voice_external_connect` / `voice_external_host` | — | External voice server; "very experimental"; license keys must match. |
| `sv_mumble` | false | Legacy Mumble-API compat (`setr sv_mumble true`); insecure, since any client can join any channel. |
| `sv_devMode` | false | Dev mode for clients; caps max clients at 8. Never in production. |
| `onesync_migrateDataTimeout` | 10000 | Force-migrate entity if the owner stops syncing. |
| `onesync_mapBoundsMinX/MinY/MaxX/MaxY` | -10000 / 65536 | Startup only. |
| `onesync_mapCellAreaSize` | 100 | World grid cell size; startup only. |
| `onesync_maxNearbyVehicles/Peds/Objects/Players/Other` | — | Streaming caps (patch 2026-08-04: defaults 256 vehicles, 256 peds, 512 objects). |
| `onesync_multithreadedPacketProcessing` | true | Parallel sync processing (2026-09-30); `set … false` to disable. |
| `rateLimiter_<name>_rate` / `_burst` | see docs | Limiters: challenge, handshake, handshakeUDP, http_*, netCommand*, netEvent (50/200), netEventFlood, rcon, res_http_handler, resourceList, stateBag (75/125), stateBagFlood, stateBagSize, plus netGameEvent/netGameEventFlood (2026-09-30). |
| `sync_start_recording` / `sync_stop_recording` / `replay_start` / `replay_stop` | — | Record and replay entity sync. |

Do not use `voice_use2dAudio`, `voice_use3dAudio`, `voice_useSendingRangeOnly` or
`voice_useNativeAudio`: they were removed. `voice_inBitrate` still works.

Client-only dev convars (Enhanced): `cl_drawResTimeGraphs`, `cl_drawResTimeWarnings`,
`con_archetypeMonitor`, `con_discordRichPresence`, `con_handlingEditor`, `con_inputViewer`,
`con_minconsole`, `con_poolInspector`, `con_streamingMonitor`, `con_timeCycleEditor`, `netobjlabeling`.

## New voice API (server-side only) [Official]

| Deprecated (client, Mumble) | Replacement (server) |
|---|---|
| `MumbleCreateChannel(id)` | `CreateVoiceChannel(mode, maxDistance)` returns channel ID (0-based, max 65535) |
| `MumbleSetVoiceChannel(id)` | `AddPlayerToVoiceChannel(channelID, clientID)` (resets muted/deaf) |
| leave channel | `RemovePlayerFromVoiceChannel(channelID, clientID)` |
| implicit cleanup | `DeleteVoiceChannel(channelID)` |
| client mute logic | `SetPlayerMutedInVoiceChannel(channelID, clientID, muted)` (hears, cannot speak) |
| client deaf/listen | `SetPlayerDeafInVoiceChannel(channelID, clientID, deaf)` (speaks, cannot hear) |

Modes: `0` non-spatial (radio; 2D output via client voice API), `1` spatial (3D, proximity within
`maxDistance`), `2` custom (no API yet), `3` temporary (spatial, auto-deleted when empty). Players are
removed from all channels automatically on disconnect. Mumble compat treats voice targets as a single
target. Since 2026-08-31, voice uses the OneSync relevancy grid. `pma-voice` radio was broken until
Hotfix 11 (2026-08-19).

## Other additions seen in patch notes [Official]

- Built-in colshapes (`CreateColshapePolygon` etc.; JS/Lua arrays and integer coords accepted).
- `SetPlayerName` (server) and the `onPlayerNameChanged` event; `onPedDeath` and `onPedHealthChanged` events (Hotfix 9).
- Prometheus metrics with per-resource performance and main-thread stage metrics (2026-09-22).
- `/voicechannels.json` endpoint; diagnostics endpoints require auth (2026-08-11).
- txAdmin is bundled and works (several txAdmin fixes in the patch notes).

## Manifest and platform detection

- `games { 'gta5', 'gta5enhanced' }` is used by Cfx's own `cfx-server-data` maps
  (fivem-map-hipster/skater, commit e265cb2 by radon@cfx.re, 2026-07-20). This is the safest
  cross-platform declaration. [Official usage; not in docs]
- `game 'gta5'`-only resources (spawnmanager, mapmanager, basic-gamemode with `game 'common'`) are
  part of the official Enhanced txAdmin recipe, so they load on Enhanced. [Official, inferred]
- `game 'gta5enhanced'` alone (Enhanced-only) appears in community repos. [Reported]
- Client: `IsGameEnhancedVersion()` (`IS_GAME_ENHANCED_VERSION`, CFX ns, apiset client, hash
  `0x4DD998F6`). It returns whether the script runs on GTAV Enhanced. It was added to
  citizenfx/fivem (Legacy) on 2026-05-26 and returns `false` there. Older Legacy builds lack it, so guard
  with `type(IsGameEnhancedVersion) == 'function'`. [Official]
- Server: the `gamename` convar is reportedly `gta5enhanced` on Cfx Server (`info.json` also reports
  it). ESX's `isEnhanced` import checks `GetConvar('gamename','gta5')` against
  `gta5enhanced`/`gta5_enhanced`. [Reported]
- The Enhanced-only CFX natives (voice channels, colshapes, `PrintRemoteCommandLog`,
  `UnregisterCommand`, …) are not in `citizenfx/fivem/ext/native-decls`. The Enhanced code base is not
  public in that repo. [Official, by absence] Use docs.fivem.net/natives for their signatures.

## Runtimes

- Lua: supported; patch notes fix Lua-specific items such as `warn()` and profiler scopes.
  Version: presumably 5.4 as on current Legacy, but no Enhanced-specific source states it. [Unknown]
- JS: Node.js 26 server, V8 14.6.202 client. [Reported via Dev Update #3 / EA post summaries]
- C#: .NET 10. [Official]
- NUI: still CEF-based (CEF remote debugging port "matches gen8"; DUI supported). Since Hotfix 6,
  clients without WebView2 get an error instead of a black screen, so WebView2 is a client
  dependency. [Official] Community code says the CEF is Chromium 140, where `nui://` is not a secure
  context; it references NUI assets as `https://cfx-nui-<resource>/…`. [Reported]
