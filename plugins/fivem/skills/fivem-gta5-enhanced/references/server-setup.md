# Enhanced server setup, client and dev workflow

Tags: [Official], [Reported], [Unknown]. Dates are for 2026.

## Server binaries

- Get them from docs.fivem.net "Server Download" and switch the platform selector to "FiveM for GTAV
  Enhanced". [Official docs + Reported UI detail]
- Archive names in the docs: Windows `cfx-server_win_x64`, Linux `cfx-server-linux_x64`.
  Executable: `cfx-server.exe` (Windows) / `cfx-server` (Linux). [Official]
  - A community Docker script (Auhrus/fivem-docker-server, 2026-08-08) scrapes
    `https://docs.fivem.net/docs/server-download/?platform=enhanced&os=linux` for a
    `https://downloads.cfx-services.net/prod/...cfx-server_linux_x64.tar.xz` link. The underscore
    differs from the docs' `cfx-server-linux_x64`. Treat exact URLs and names as [Reported].
- Windows: install the **Microsoft Visual C++ 2017 Redistributable (x64)**
  (`https://aka.ms/vs/17/release/vc_redist.x64.exe`) first. [Official]
- Older Windows: Cfx Server starts on Windows versions without `SetThreadDescription` (Hotfix 6), and
  Windows Server 2012/2016 compatibility was restored (2026-08-04). [Official]
- Linux and Docker are supported platforms (the bug form offers Windows/Linux/Docker). The community
  Docker image needs `--privileged` for Enhanced and exposes 40120/tcp (txAdmin) and 30120/tcp+udp.
  [Official platform list / Reported Docker details]
- Server build numbers in bug reports look like `139`, `153`, `156`, `157` (Sep-Oct 2026). Get the build
  with the `version` console command or the `/info.json` endpoint. [Official form / Reported numbers]
- Servers check for updates on startup and announce new builds (Hotfix 3). [Official]

## Keep up with protocol bumps [Official]

These patches required updating cfx-server, or clients failed with handshake/connection errors:
Hotfix 6 (07-29), Hotfix 10 (08-13), 08-31, 09-22, 09-30. When "players can't connect" right after a
Cfx patch, update cfx-server first.

## server.cfg

Base it on the official txAdmin recipe `default-fivem-enhanced` (citizenfx/txAdmin-recipes,
"FiveM Basic Server (Enhanced)"). Its server.cfg, with txAdmin placeholders
(`{{serverEndpoints}}`, `{{maxClients}}`, …) filled in by example values:

```cfg
sv_hostname "..."
sets sv_projectName "..."
sets sv_projectDesc "..."
sets tags "enhanced, default, deployer"
sets locale "root-AQ"
sv_licenseKey "..."
sv_maxclients 48
endpoint_add_tcp "0.0.0.0:30120"
endpoint_add_udp "0.0.0.0:30120"
ensure mapmanager
ensure spawnmanager
ensure basic-gamemode
add_ace group.admin command allow
add_ace group.admin command.quit deny
```

Compared with the Legacy recipe, it drops `sv_enforceGameBuild 3751`, `$onesync: on`,
`steam_webApiKey`, `resources_useSystemChat`, `ensure chat` and `ensure hardcap`. Why chat/hardcap were
dropped is not documented [Unknown]. Do not claim they are broken; just do not assume they are needed.

Enhanced-specific additions you may need (all documented): `set sv_syncTickRate <1-120>`,
`voice_internal`, `setr sv_mumble true` (legacy voice scripts), `sv_devMode true` (dev only),
`onesync_maxNearby*`, `rateLimiter_*`, `sv_resourceFileDownloadTimeout`. See
[legacy-vs-enhanced.md](legacy-vs-enhanced.md).

Things that are gone: a second `endpoint_add_*` line (single endpoint only), `sv_netHttp2`,
`onesync_automaticResend`, `+set moo 31337`. `set onesync on` is pointless because the convar is read-only.

## Migrating from a Legacy server

1. Clone the server-data folder and keep the Legacy server running. Cfx and hosts recommend
   testing Enhanced on a second server. [Official intent / Reported advice]
2. Remove escrowed resources. Asset Escrow is not implemented.
3. Convert assets with Alchemist and place them in `stream_enhanced/`
   ([assets-and-streaming.md](assets-and-streaming.md)).
4. Migrate the KVP DB with `citizenfx/kvdb-migrator` (releases or `bun run start`). Input: Legacy
   `db/<sv_kvsName>` (default `db/default`). Output: a new folder for cfx-server.
5. Adjust server.cfg as above; remove `sv_enforceGameBuild <n>` (keep only `1` if needed).
6. Go through the porting checklist in SKILL.md, then test with two clients (dev mode).
7. External databases (MySQL via oxmysql etc.) are not affected by the KVP migration. [Unknown whether
   any DB driver issues exist; none found in the patch notes]

## Players / client

- Install "FiveM for GTAV Enhanced" from fivem.net. It is a separate installer and launcher,
  installed alongside Legacy FiveM. [Official]
- It requires GTA V Enhanced (Steam, Epic or Rockstar Games Launcher). Launch the game once
  and keep it updated. [Reported]. Fixes in the patch notes mention Steam/Epic dual-client launch and
  Rockstar Games Launcher/Epic errors (rfc #574/#575, open). [Official]
- Client logs: `%AppData%\FiveM for GTAV Enhanced\logs` (`fivem-for-gtav-enhanced-*`,
  `fivem-launcher-*`, `installer-*`). [Official]
- Join: server list (Enhanced servers only), F8 `connect ip:port` / `connect cfx.re/join/<id>`. A
  `cfx://` protocol handler exists (fixed 2026-08-04). [Official mention] Exact URL syntax: [Unknown]
- The launcher can switch branches via a command-line argument (08-31). The argument name is [Unknown].
- Client mods: pure mode always on, no graphics mods in early access. [Official] ASI/ScriptHook/ReShade:
  treat them as unsupported.

## Dev workflow

- `sv_devMode true` in server.cfg enables client dev mode and caps the server at 8 clients.
- Second client: F8 > Debug > "Launch Additional Client" (replaces `-cl2`).
- Remote Console: client F8 > Console > "Remote Console", port 29200.
- Client dev tools (F8 / convars): resource time graphs, pool inspector, streaming monitor, handling
  editor, timecycle editor, input viewer, net object labeling.
- Profiling: Perfetto profiles and Prometheus metrics (per resource) are what Cfx asks for in bug
  reports. Lua profiler scopes are reported broken (rfc #510).
- Bug reports: GitHub Discussions at `citizenfx/rfc`. Include server build, client OS/GPU, `/perf`
  output, txAdmin yes/no, hosting, and a minimal repro resource. Security issues go to HackerOne
  (rfc #3).
