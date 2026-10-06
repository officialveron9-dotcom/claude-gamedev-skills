# Sources (accessed 2026-10-06)

| URL | Backs up |
|---|---|
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/GameServer.cpp | Hitch warnings (server thread > 150 ms, network/sync thread, frame time), 20 Hz server tick, `Server->client connection timed out. Pending commands` |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ServerResources.cpp | `Couldn't find/start resource`, category message, fx_version warning, large event warning, net-event rate limiter defaults |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-resources-core/src/ResourceDependencyLoader.cpp | `Could not find dependency` |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ServerResourceList.cpp | `outdated manifest (__resource.lua ...)` |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ResourceStreamComponent.cpp | Oversized asset thresholds 16/32/48/64 MiB and text |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-scripting-lua/src/LuaScriptRuntime.cpp | `SCRIPT ERROR`, `Error parsing script`, `Error loading script` |
| https://github.com/citizenfx/fivem/blob/master/data/shared/citizen/scripting/lua/scheduler.lua | `was not safe for net`, export errors, Await scheduler error, Entity/Player setter errors, NUI callback error |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-scripting-core/src/Profiler.cpp | `profiler` subcommands (status, record start/<frames>/stop, save, saveJSON, view) |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/InfoHttpHandler.cpp | Server `profiler view` DevTools URL + `/profileData.json` |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-devtools/src/ResourceTimeWarnings.cpp and ResourceMonitor.cpp | `resmon` convar, > 6 ms resource time warning text |
| https://github.com/citizenfx/fivem/tree/master/code/components/citizen-server-impl/src/packethandlers | Overflow drop reasons |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/InitConnectMethod.cpp and code/components/net/src/NetLibrary.cpp | Game build mismatch / invalid enforcement messages |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/state/ServerGameState.cpp | NetworkRequestControlOfEntity warning |
| https://github.com/citizenfx/txAdmin core/modules/Metrics/playerDrop/classifyDropReason.ts | Drop reason strings (timeouts, security overflows, crash prefixes incl. German) |
| https://docs.fivem.net/docs/server-manual/server-commands/ | `increase_pool_size`, `onesync_population`, `svgui`, Pool Monitor |
| https://docs.fivem.net/docs/server-manual/end-of-support-end-of-life/ | EOS/EOL warnings, 3-month joinability |
| https://docs.fivem.net/docs/developers/sandbox/ | Permission denied (13) sandbox errors |
| https://docs.fivem.net/docs/scripting-manual/runtimes/javascript/ | `No current resource manager` |
| https://docs.fivem.net/docs/cookbook/2019/06/29/get_active_players-the-replacement-for-player-loops/ | GetActivePlayers |
| https://github.com/citizenfx/fivem/tree/master/ext/native-decls (GetGamePool) | Pool names |
| https://github.com/overextended/oxmysql (src/database/pool.ts, src/logger/index.ts, src/config.ts) | DB connection error text, slow query text/threshold 200 ms, `/mysql` UI command |
| https://github.com/overextended/ox_lib (imports/callback) | Callback error/timeout texts, lib.points/zones/onCache |
| https://docs.fivem.net/docs/server-manual/asset-escrow/ + escrow troubleshooting pages (search snippets) | Entitlement and protected-resource errors |
| https://github.com/jgscripts/fivem-artifacts-db | Artifact 28626 packet loss/timeouts |
| https://xgamingserver.com/blog/fivem-server-performance-resmon-guide/ (search snippet) | resmon/profiler usage (secondary; thresholds in SKILL.md are guidance, not official) |
