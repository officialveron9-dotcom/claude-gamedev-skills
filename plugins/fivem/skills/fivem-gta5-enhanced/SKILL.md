---
name: fivem-gta5-enhanced
description: "Covers running, configuring and scripting servers for \"FiveM for GTAV Enhanced\" (the Cfx.re client + \"Cfx Server\"/cfx-server for the GTA V Enhanced PC edition, early access since 2026-07-21) and how it differs from FiveM Legacy (FXServer). Use when the user mentions GTA V Enhanced, GTA 5 Enhanced, FiveM Enhanced, Gen9 vs Gen8, Legacy vs Enhanced, cfx-server, gta5enhanced, stream_enhanced, Alchemist asset conversion, sv_syncTickRate, the new voice API, game build/sv_enforceGameBuild on Enhanced, DX12/ray tracing, porting resources or assets to Enhanced, or running a Legacy and an Enhanced server side by side. German triggers: \"Enhanced Server\", \"GTA 5 Enhanced\", \"FiveM Enhanced\", \"Enhanced-Version\", \"Legacy oder Enhanced\", \"Ressource portieren\", \"Assets konvertieren\"."
---

# FiveM for GTAV Enhanced

Reader: Claude. Facts carry a date and a confidence tag:
**[Official]** = Cfx docs/patch notes/repos, **[Reported]** = community/press, unverified,
**[Unknown]** = no source found. Never present [Reported] or [Unknown] items as fact.
Do not invent convars, natives, manifest fields or file names that are not in this skill or
its references; when unsure, tell the user to check `docs.fivem.net/docs/developers/legacy-vs-enhanced/`
and the patch notes at `github.com/citizenfx/rfc/discussions/categories/patch-notes`.

## Ground rules

- "FiveM Enhanced" = **FiveM for GTAV Enhanced** (Gen9), early access since 2026-07-21; "Legacy" = Gen8.
  Server binary `cfx-server.exe` (archives `cfx-server_win_x64` / `cfx-server-linux_x64`), not `FXServer.exe`.
  If the user might mean a graphics pack instead, ask. History: [references/timeline.md](references/timeline.md).
- **Keep cfx-server current.** Several patches (2026-08-13, 08-31, 09-22, 09-30) changed the protocol;
  an outdated server makes clients fail at the handshake. Check this first when "nobody can connect". [Official]
- **Scripts mostly carry over; 3D assets do not.** Gen8 `.ydr/.ytd/.yft/.ydd/.ypt` must be converted
  (Alchemist) and go in `stream_enhanced/`. [Official]
- **No client mods** (pure mode always on): never suggest ReShade/ASI/ScriptHook. **No Asset Escrow** yet. [Official]
- One server serves one platform; Legacy and Enhanced need separate servers and `server.cfg` files. [Official]

## Legacy vs Enhanced differences

| Area | FiveM Legacy (FXServer) | FiveM for GTAV Enhanced (Cfx Server) | Tag |
|---|---|---|---|
| Game | GTA V Legacy (DX10/11) | GTA V Enhanced (DX12, RT options) | [Official]/[Reported RT] |
| Server exe | `FXServer.exe` | `cfx-server.exe` | [Official] |
| Game builds | Many (`sv_enforceGameBuild 1604…3889`) | **Only latest** (The Kortz Center Heist, loaded by default) or `sv_enforceGameBuild 1` (base game); other numbers reportedly lock clients out | [Official]/[Reported] |
| Sync model | OneSync off/legacy/on, P2P possible | Client-server only; OneSync "big" mode only; `onesync` convar read-only | [Official] |
| Sync rate | 30 Hz (40 with `sv_useAccurateSends`) [Reported] | `sv_syncTickRate` 1-120, default 60; `sv_useAccurateSends` deprecated | [Official] |
| Player IDs | Increment to 65535, never reused quickly | Released on disconnect and reusable (docs); reports say reuse caps at ~4096 | [Official]/[Reported] |
| Asset folders | `stream/` | `stream_enhanced/` preferred; `stream/` used only if no `stream_enhanced/` (deprecated) | [Official] |
| Asset format | Gen8 | Gen9; convert with Alchemist | [Official] |
| Voice | Mumble natives + `voice_*` convars | New server-side voice API (`CreateVoiceChannel`, …); Mumble API only via `setr sv_mumble true` (deprecated, insecure) | [Official] |
| C# | Mono | .NET 10 (CoreCLR, sandboxed) | [Official] |
| JS runtime | FXServer's bundled Node/V8 | Node.js 26 (server), V8 14.6 (client) | [Reported, Dev Update #3] |
| Colshapes | none built in (PolyZone/ox_lib) | built-in Colshape natives | [Official] |
| Escrow | Supported | **Not implemented yet** | [Official] |
| Dev mode | `+set moo 31337` | `sv_devMode true` on server (caps at 8 clients) | [Official] |
| Two clients | `-cl2` | F8 > Debug > "Launch Additional Client" (needs `sv_devMode true`) | [Official] |
| KVP DB | FXServer format | Must be migrated (`citizenfx/kvdb-migrator`) | [Official] |
| fxmanifest game | `gta5` | `gta5enhanced` (official example: `games { 'gta5', 'gta5enhanced' }`); `gta5` also loads | [Official usage] |
| Detect platform | `IsGameEnhancedVersion()` returns false | client `IsGameEnhancedVersion()` true; server convar `gamename` = `gta5enhanced` | [Official]/[Reported] |
| NUI | CEF (older Chromium) | CEF, reportedly Chromium 140; WebView2 needed by the client | [Reported]/[Official] |
| Removed | — | `sv_netHttp2`, server ImGui, `onesync_automaticResend`, resource builders, multi-endpoint `endpoint_add_*` | [Official] |

Full list with convars and API details: [references/legacy-vs-enhanced.md](references/legacy-vs-enhanced.md).

## Setting up an Enhanced server (summary)

1. Download the Enhanced build from the Server Download page (switch the platform to
   "FiveM for GTAV Enhanced"). Install the VC++ 2017 x64 redistributable on Windows.
2. Use the txAdmin recipe **"FiveM Basic Server (Enhanced)"** (`default-fivem-enhanced`) or write
   `server.cfg` by hand. Compared with the Legacy recipe, it has no `sv_enforceGameBuild`, no
   `$onesync`, and no `chat`/`hardcap` resources. [Official, txAdmin-recipes]
3. Migrate KVP data if you are coming from Legacy (`kvdb-migrator`).
4. Players install the separate "FiveM for GTAV Enhanced" client from fivem.net. Client logs are in
   `%AppData%\FiveM for GTAV Enhanced\logs`.

Minimal Enhanced-specific `server.cfg` lines (all documented):

```cfg
endpoint_add_tcp "0.0.0.0:30120"   # one endpoint only on Enhanced
endpoint_add_udp "0.0.0.0:30120"
sv_maxclients 48
set sv_syncTickRate 60             # 1-120; higher = lower latency, more CPU
voice_internal                     # built-in voice server (new voice API)
# setr sv_mumble true              # ONLY for old Mumble-API voice scripts; insecure, deprecated
# sv_enforceGameBuild 1            # only to force base game; omit for latest DLC level
# sv_devMode true                  # local dev only; max 8 clients
```

More setup steps, Linux/Docker notes and the dev workflow: [references/server-setup.md](references/server-setup.md).

## Porting checklist (Legacy resource to Enhanced)

- [ ] **Escrow:** if any part is escrowed (Tebex/Asset Escrow), stop. It will not work on Enhanced yet.
- [ ] **Assets:** run Alchemist (`AlchemistCli.exe <in> <out> [--relaxed] [-jN] [-f]`) on
      `.ydr/.ytd/.yft/.ydd/.ypt`. Put the Gen9 output in `stream_enhanced/`, keep Gen8 in `stream/`
      if the same resource must also run on Legacy. Test every vehicle/MLO in game.
- [ ] **Non-converted formats** (`.ymap/.ytyp/.ybn/.ycd`, `.meta/.ymt`): Alchemist does not touch
      them. Reports say `.ybn/.ycd` need no conversion; this is unverified, so test.
- [ ] **Gen9 asset limits** [Reported]: max 128 materials/geometries per drawable; `script_rt_*`
      textures must be uncompressed A8R8G8B8 or the game crashes with `ERR_GFX_STATE`.
- [ ] **Game build:** remove `sv_enforceGameBuild <n>` unless it is `1`. Code that branches on old
      build numbers needs review.
- [ ] **OneSync assumptions:** remove `set onesync …` toggles. Handle player connect/disconnect events
      only arriving in range (big mode).
- [ ] **Player IDs:** never key persistent data by server ID; use identifiers (license). IDs can be
      reused quickly.
- [ ] **Voice:** port Mumble-channel logic to the server-side voice API, or set `setr sv_mumble true`
      temporarily. Remove `voice_use2dAudio/use3dAudio/useSendingRangeOnly/useNativeAudio`.
- [ ] **Resource events:** client start-event semantics changed during early access (07-27, 08-31).
      Since 2026-08-31 (aligned with Legacy), `onClientResourceStart` fires for all resources, and
      client `onResourceStarting`/`onResourceStart` fire only on restart. Re-test init code.
- [ ] **State bags:** values are limited to 32 KB per key (since 2026-09-30). Callbacks only fire if
      the entity exists, and replicated values are only sent if explicitly set.
- [ ] **Remote commands:** call `PrintRemoteCommandLog(msg)` to send output back to the client.
- [ ] **C#:** rebuild against .NET 10. Sandbox restrictions apply (whitelisted APIs/NuGet). Legacy
      `CitizenFX.Core` assemblies load since 2026-08-20.
- [ ] **Rate limits:** check `netEvent`/`stateBag` and the newer `netGameEvent` limiters. Tune with
      `set rateLimiter_<name>_rate|_burst`.
- [ ] **Loading screens:** Enhanced exposes only `loadProgress` (with `stage`). Legacy granular
      events and `onLogLine` are missing (open issue).
- [ ] **Natives:** check each used native against the open issues list; some were missing or broken
      in early access (see known issues).
- [ ] **NUI:** test focus/input (`SetNuiFocusKeepInput` is broken, #555). Reports say the CEF is
      Chromium 140 and `nui://` is not a secure context, so load assets via `https://cfx-nui-<resource>/…`. [Reported]
- [ ] **Manifest:** add `gta5enhanced` to `games { … }`. Keeping `lua54 'yes'` is harmless; one guide
      claims Enhanced requires it, others say it is deprecated. [Conflicting, unverified]

Asset pipeline details: [references/assets-and-streaming.md](references/assets-and-streaming.md).

## Sharing one codebase across both servers

- Manifest: Cfx's own `cfx-server-data` maps declare `games { 'gta5', 'gta5enhanced' }` (commit
  by a Cfx dev, 2026-07-20). Use that for cross-platform resources. Resources with only `game 'gta5'`
  (spawnmanager, mapmanager) still ship in the official Enhanced recipe, so `gta5` evidently loads
  too. The docs do not document `gta5enhanced`. [Official usage, semantics undocumented] Community
  code uses `game 'gta5enhanced'` for Enhanced-only resources. [Reported] No other new fxmanifest
  fields are known; `provide` works (Hotfix 2).
- Runtime detection, client: `IsGameEnhancedVersion()` (CFX native `IS_GAME_ENHANCED_VERSION`,
  hash `0x4DD998F6`). It was added to the Legacy codebase on 2026-05-26 and returns `false` there.
  [Official] Server: `GetConvar('gamename', 'gta5') == 'gta5enhanced'`, the check ESX uses
  (it also accepts `gta5_enhanced`). [Reported] Guard calls with `type(IsGameEnhancedVersion) == 'function'`
  for old Legacy builds.
- Scripts: keep one repo and deploy it to both servers; branch on the checks above.
- Assets: ship `stream/` (Gen8) and `stream_enhanced/` (Gen9) in the same resource. Legacy ignores
  `stream_enhanced` [Official, implied by the docs' cross-compat note]. Enhanced loads only `stream_enhanced` when present
  (wildcard matching fixed 2026-09-24).
- Config: keep separate `server.cfg` files. Enhanced-only convars (`sv_syncTickRate`,
  `voice_internal`, `sv_devMode`, `onesync_maxNearby*`, …) are unknown to Legacy FXServer.

## Known issues (top items, 2026-10-06)

- Data file mounts (e.g. `explosion.ymt`) freeze clients on server b157; workaround: b156. [#567]
- Custom ped models invisible (b153). [#543]
- `increase_pool_size` ineffective for `CWeaponComponentInfo`. [#524]
- Server performance regression reported after b153. [#536]
- Resource downloads time out on slow connections; `sv_resourceFileDownloadTimeout`. [#561]
- `InterpolateCamWithParams` reported missing (patch 09-22 says exposed; thread still open). [#476]

Full table with workarounds and sources: [references/known-issues.md](references/known-issues.md).

## What to tell the user

- Before suggesting Enhanced for production, ask about escrowed scripts, custom assets and
  client mods. These are the usual blockers.
- When debugging, ask for the server build (`version` command or `/info.json`), client logs, and
  whether cfx-server was updated after the latest patch notes.
- Report bugs in GitHub Discussions at `citizenfx/rfc` (Enhanced only), not citizenfx/fivem issues.

Sources (accessed 2026-10-06): [references/sources.md](references/sources.md).
