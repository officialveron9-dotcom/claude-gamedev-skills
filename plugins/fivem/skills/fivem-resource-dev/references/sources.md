# Sources (accessed 2026-10-06)

docs.fivem.net was read from its source repository (github.com/citizenfx/fivem-docs, HEAD 2026-10-01); runtime behaviour was checked in github.com/citizenfx/fivem (HEAD 2026-09-30, tag v1.0.0.36897).

| URL | Backs up |
|---|---|
| https://docs.fivem.net/docs/scripting-reference/resource-manifest/ | Directives, `cerulean` = current fx_version, `lua54` deprecated (Lua 5.3 removed June 2025), `node_version` 16 default / 22 optional, OAL vector-unpacking caveat, dependency constraints, `provide`, `escrow_ignore` |
| https://docs.fivem.net/docs/scripting-manual/runtimes/lua/ | CfxLua 5.4, backtick hashes, vectors, exports, bundled json/promise/msgpack |
| https://github.com/citizenfx/lua (branch luaglm-548, README "Power Patches") | Compound operators, safe navigation, `in` unpacking, `joaat` |
| https://github.com/citizenfx/fivem/blob/master/data/shared/citizen/scripting/lua/scheduler.lua | `source` swapped per event and restored after yield, `was not safe for net`, `No such export`, `Wait/CreateThread` aliases, `RegisterServerEvent` alias, `GetPlayers()` returns strings, NUI callback wrapper message |
| https://docs.fivem.net/docs/developers/server-security/ | AddEventHandler vs RegisterNetEvent, source 65535 for server->client events |
| https://docs.fivem.net/docs/scripting-manual/networking/state-bags/ | Shallow get/set, replication defaults, `:set(key,val,replicated)`, write policy |
| https://docs.fivem.net/docs/server-manual/server-commands/ | `sv_stateBagStrictMode` (server 12739), `sv_entityLockdown`, `sv_filterRequestControl`, rate limiters |
| https://docs.fivem.net/docs/scripting-reference/onesync/ | Server-side entity creation, `SetEntityOrphanMode`, RPC natives, routing buckets, lockdown modes, 424-unit culling, scope events cost |
| https://docs.fivem.net/docs/scripting-manual/networking/ids/ | Server ID vs player index vs handle vs net ID |
| https://github.com/citizenfx/fivem/tree/master/ext/native-decls | Native names/signatures: AddStateBagChangeHandler, CreateVehicleServerSetter, SetEntityOrphanMode, KVP natives, RegisterKeyMapping, GetPlayerIdentifierByType |
| https://github.com/citizenfx/fivem/blob/master/ext/natives/rpc_spec_natives.lua | List of server RPC natives |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ServerResources.cpp | fx_version warning, large-event warning, net-event rate limiter defaults/drop reasons |
| https://docs.fivem.net/docs/scripting-manual/nui-development/full-screen-nui/ and .../nui-callbacks/ | `cfx-nui-` scheme, devtools port 13172, callback URL `https://<res>/<cb>`, must call cb |
| https://docs.fivem.net/docs/developers/sandbox/ | File-system and process sandbox, permission commands |
| https://docs.fivem.net/docs/scripting-manual/runtimes/javascript/ | Node 16/22, thread affinity + setImmediate, JS function names |
| https://docs.fivem.net/docs/scripting-manual/runtimes/csharp/ | C# templates |
| https://docs.fivem.net/docs/developers/legacy-vs-enhanced/ | Enhanced differences (.NET, no builders) |
| https://github.com/thorium-cfx/mono_v2_get_started | mono_rt2 preview (secondary) |
| https://github.com/overextended/ox_lib (v3.40.0, 2026-10-03) | lib.callback API, init.lua errors, strict-mode security warning |
| https://github.com/jgscripts/fivem-artifacts-db (db.json, 2026-09-10) | Broken artifact ranges (onEntityBucketChange 14583-14716, yarn 26261-27715) |
