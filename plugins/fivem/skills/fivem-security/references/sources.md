# Sources (accessed 2026-10-06)

| URL | Backs up |
|---|---|
| https://docs.fivem.net/docs/developers/server-security/ (source: citizenfx/fivem-docs) | AddEventHandler vs RegisterNetEvent, 65535 server source on client, server-side checks list, CnL/adhesive convars, `sv_disableClientReplays` |
| https://docs.fivem.net/docs/server-manual/server-commands/ | `sv_entityLockdown` modes, `sv_filterRequestControl` modes + settle timer, `sv_stateBagStrictMode` (12739) + client error text, networked sound/phone-explosion/script-entity-state convars, `block_net_game_event`, `sv_pureLevel`, `sv_authMaxVariance/MinTrust`, `sv_requestParanoia`, `sv_httpFileServerProxyOnly` (10543), ACE commands, `rcon_password` (UDP), Prometheus auth |
| https://docs.fivem.net/docs/scripting-reference/onesync/ | Entity lockdown per routing bucket, server-side entity creation |
| https://docs.fivem.net/docs/developers/sandbox/ | `add_convar_permission`, filesystem/process permissions |
| https://docs.fivem.net/docs/cookbook/2021/07/17/quick-note-on-using-built-in-acl-security/ and .../migrating-from-deprecated/creating-commands/ | ACE principals at runtime, `RegisterCommand` restricted flag -> `command.<name>` |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/InfoHttpHandler.cpp | `sv_endpointPrivacy` / `sv_exposePlayerIdentifiersInHttpEndpoint` removed, `sv_playersToken`; present in tags >= 32561 (2026-07-13), absent in 31725 (2026-06-24) |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/state/ServerGameState.cpp | `NetworkRequestControlOfEntity is deprecated...` warning |
| https://github.com/citizenfx/fivem/tree/master/code/components/citizen-server-impl/src/packethandlers | Rate-limit drop reasons (`Reliable network event overflow.`, `Reliable state bag packet overflow.`) |
| https://docs.fivem.net/docs/server-manual/asset-escrow/ | Escrow file types, `escrow_ignore`, NUI not supported, `You lack the required entitlement` |
| https://docs.jgscripts.com/getting-started/fivem-escrow-errors , https://docs.otherplanet.dev/troubleshooting/failed-to-verify-protected-resource (search snippets) | `Failed to verify protected resource` causes (.fxap missing, FTP corruption) - secondary |
| https://github.com/citizenfx/txAdmin/blob/master/docs/env-config.md (v8.1.1) | `TXHOST_*` env vars, deprecated convars, env file permissions |
| https://github.com/citizenfx/txAdmin core/lib/fxserver/fxsConfigHelper.ts | onesync only in txAdmin settings, don't start/stop txAdmin resources |
| https://github.com/overextended/ox_lib resource/server.lua | Strict-mode security advisory |
| https://github.com/Qbox-project/qbx_core server/functions.lua | `ExploitBan` export |
| https://github.com/TheIndra55/secure-resource-examples (linked from docs) | Example secure event flow |
