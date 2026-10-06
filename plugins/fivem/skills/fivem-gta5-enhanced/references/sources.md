# Sources (all accessed 2026-10-06)

Method note: forum.cfx.re, docs.fivem.net, support.cfx.re and most press sites were blocked for direct
fetching in the research environment. Official docs were read from their source repo
(`citizenfx/fivem-docs`, HEAD `c2b2125`, 2026-10-01). GitHub Discussions in `citizenfx/rfc` were
fetched directly. Forum and press items were seen only through search-engine summaries and are marked as such.

## Primary: read in full

| URL | Backs up |
|---|---|
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/developers/legacy-vs-enhanced.md (= https://docs.fivem.net/docs/developers/legacy-vs-enhanced/) | Removed features, breaking changes, player ID reuse, KVP migration, PrintRemoteCommandLog, .NET 10, pure mode, single endpoint, sv_devMode, sv_syncTickRate, sv_resourceFileDownloadTimeout, lockdown `full`, state bags, game builds (latest only / 1), file names, `stream_enhanced` |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/server-manual/server-commands.md | Enhanced-only convars (sv_ioThreads, timeouts, sv_voiceChat, sv_mumble, onesync_* map bounds, rate limiters, sync recording), game build table incl. 3889 / mp2026_01 Kortz Center Heist |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/alchemist/_index.md (= https://docs.fivem.net/docs/alchemist/) | Alchemist: Win 11, YDR/YTD/YFT/YPT/YDD, GUI/CLI, flags, escrow known issue |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/server-manual/onboarding-guide-fivem-for-gtav-enhanced.md | Onboarding: server download, VC++ 2017, Alchemist link |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/scripting-manual/voice/_index.md | New voice API, voice_internal, external voice server, sv_mumble compat, removed voice convars |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/client-manual/running-two-fivem-clients.md | Second client via F8 Debug menu, sv_devMode |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/client-manual/console-commands.md | Enhanced-only client dev convars |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/scripting-manual/migrating-from-other-platforms/_index.md | Built-in colshapes on Enhanced only |
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/server-manual/setting-up-a-server-vanilla.md and setting-up-a-server-txadmin.md | Archive/exe names (cfx-server_win_x64, cfx-server-linux_x64, cfx-server.exe), VC++ requirement |
| https://github.com/citizenfx/fivem-docs (git log) | Dates: Alchemist docs 2025-11-20; Enhanced docs 2026-07-20; stream_enhanced docs 2026-09-02; VC++ 2026-09-28 |
| https://github.com/citizenfx/rfc (readme + discussion template) | Official Enhanced bug tracker; log paths and prefixes; bug report fields |
| https://github.com/citizenfx/rfc/discussions/categories/patch-notes | List and dates of all EA patches/hotfixes |
| https://github.com/citizenfx/rfc/discussions/59 | Hotfix 1 (2026-07-21): OneSync convar read-only, load order, JS helpers |
| https://github.com/citizenfx/rfc/discussions/127 | Hotfix 2 (07-22) |
| https://github.com/citizenfx/rfc/discussions/176 | Hotfix 3 (07-23): asset version mismatch fix, txAdmin |
| https://github.com/citizenfx/rfc/discussions/220 | Hotfix 4 (07-24) |
| https://github.com/citizenfx/rfc/discussions/287 | Hotfix 5 (07-27): owner -1, endpoints |
| https://github.com/citizenfx/rfc/discussions/312 | Hotfix 6 (07-29): WebView2 message, older Windows, server update required |
| https://github.com/citizenfx/rfc/discussions/327 | Hotfix 7 (07-30) |
| https://github.com/citizenfx/rfc/discussions/360 | Patch 08-04: onesync_maxNearby* convars, streaming caps, cfx:// handler |
| https://github.com/citizenfx/rfc/discussions/375 | Hotfix 8 (08-06): add-on vehicle crash, 2048 textures |
| https://github.com/citizenfx/rfc/discussions/395 | Patch 08-11 |
| https://github.com/citizenfx/rfc/discussions/404 | Hotfix 9 (08-12): SetPlayerName, onPedDeath, fonts |
| https://github.com/citizenfx/rfc/discussions/406 | Hotfix 10 (08-13): protocol update |
| https://github.com/citizenfx/rfc/discussions/435 | Hotfix 11 (08-19): non-spatial voice / pma-voice |
| https://github.com/citizenfx/rfc/discussions/439 | C# runtime patch (08-20): sandbox, NuGet whitelist, legacy assemblies |
| https://github.com/citizenfx/rfc/discussions/474 | Patch 08-31: start events, stream_enhanced, KVP keying, protocol |
| https://github.com/citizenfx/rfc/discussions/530 | Patch 09-22: stream/stream_enhanced, cutscenes, protocol, txAdmin, rollback |
| https://github.com/citizenfx/rfc/discussions/545 | Hotfix 09-24: stream wildcard, thread timing |
| https://github.com/citizenfx/rfc/discussions/564 | Patch 09-30: protocol, state bag limits, multithreaded packet processing, netGameEvent limiters |
| https://github.com/citizenfx/rfc/discussions?discussions_q=label%3Atriaged | Open triaged bug list |
| https://github.com/citizenfx/rfc/discussions/567, /543, /524, /536, /561, /555, /476, /427, /136, /107, /572, /58 | Individual known issues and staff replies (see known-issues.md) |
| https://github.com/citizenfx/kvdb-migrator | Official KVP DB migration tool |
| https://github.com/citizenfx/txAdmin-recipes/tree/main/default-fivem-enhanced | Official "FiveM Basic Server (Enhanced)" recipe and server.cfg |

| https://github.com/citizenfx/cfx-server-data/commit/e265cb251c88260533c847d4a1a2838c7d828a66 | `games { 'gta5', 'gta5enhanced' }` in official map resources (2026-07-20) |
| https://github.com/citizenfx/fivem/blob/master/ext/native-decls/IsGameEnhancedVersion.md (commit 9ffada0e, 2026-05-26) | `IS_GAME_ENHANCED_VERSION` client native; Legacy handler returns false (code/components/citizen-scripting-core/src/ResourceScriptFunctions.cpp) |
| https://github.com/citizenfx/fivem/blob/master/ext/native-decls/EnableEnhancedHostSupport.md | Disambiguation: "enhanced host support" is the old P2P feature |

## Secondary: community, read in full

| URL | Backs up |
|---|---|
| https://github.com/Sollumz/wiki/blob/main/tutorials/asset-conversion-for-gtav-enhanced.md | CodeWalker converter; ERR_GFX_STATE / script_rt_ textures; 128 materials/geometries limit |
| https://github.com/Auhrus/fivem-docker-server (startup.sh) | Enhanced Linux download scraping URL, `cfx-server` binary, `--privileged` |
| https://github.com/esx-framework/esx_core/blob/HEAD/%5Bcore%5D/esx_lib/imports/isEnhanced/shared.lua (2026-09-07) | Server detection via `gamename` convar; client via `IsGameEnhancedVersion` |
| https://github.com/laforetbrut/v-core-framework-fivem (README/ARCHITECTURE, via code search) | Claims: `info.json` gamename `gta5enhanced`; FXServer rejects Enhanced clients (`bad_request`); Legacy build numbers lock Enhanced clients out; CEF 140 / `https://cfx-nui-` |
| https://github.com/sparkedhost/images/blob/HEAD/games/fivem/entrypoint.sh (via code search) | Host image switches Legacy/Enhanced by `GAME_NAME` `gta5`/`gta5enhanced` |

## Seen only via search-engine summaries (not opened)

| URL | Used for |
|---|---|
| https://forum.cfx.re/t/fivem-support-for-newly-announced-grand-theft-auto-v-upgrade-coming-soon/5307678 | 2025 statement: Legacy continues, no cross-play, not both on one server |
| https://forum.cfx.re/t/development-update-fivem-for-gtav-enhanced/5391635 | Dev Update #1 (OneSync overhaul, ~2048 players) |
| https://forum.cfx.re/t/development-update-2-fivem-for-gtav-enhanced/5412576 | Separate launcher; Legacy side by side; one server list as a long-term goal |
| https://forum.cfx.re/t/development-update-3-fivem-for-gtav-enhanced/5415045 | Raw UDP sync, 120 Hz, RAM -50%, .NET 10 / Node.js 26 / V8 14.6 |
| https://forum.cfx.re/t/fivem-for-gtav-enhanced-is-available-now-in-early-access/5412858 | EA availability 2026-07-21, "Download FiveM for GTAV Enhanced" button, Cfx Server |
| https://forum.cfx.re/t/introducing-alchemist-for-fivem/5366795 | Alchemist announcement 2025-11-20; ybn/ycd remark (unverified) |
| https://forum.cfx.re/t/public-stress-test-calendar-fivem-for-gtav-enhanced/5420662 | Stress tests 08-14, 09-04 |
| https://support.cfx.re/hc/en-us/articles/27623908811164-Downloading-and-installing-FiveM-for-GTAV-Enhanced | Client install article (content via summaries only) |
| https://www.sportskeeda.com/gta/fivem-announces-support-gta-5-enhanced-coming-soon ; https://gameranx.com/updates/id/561820/article/fivem-is-coming-to-gta-v-enhanced/ | Dev Update #1 date 2026-03-18 |
| https://www.gtaboom.com/fivem-for-gta-v-enhanced-is-live-c7cc ; https://rockstarintel.com/fivem-for-gta-v-enhanced-releases-next-week/ | EA launch coverage |
| https://chased.fr/en/blog/install-fivem-gta-5-enhanced/ ; https://hzscripts.com/blog/fivem-enhanced-guide (also the unverified "lua54 'yes' required" claim) ; https://respawnhost.com/en/wiki/games/fivem/fivem-enhanced/ ; https://yorkhost.fr/docs/en/fivem/fivem-enhanced | Player install steps, "Legacy assets don't load unconverted", separate server lists, keep production on Legacy |
| https://gta-zone.com/news/fivem-gta-v-enhanced-ray-tracing/ | Ray tracing on Enhanced servers (press) |
| https://zoov.dev/kb/bulletin/gta-v-enhanced-gen9-fivem-support | RSC versions per type (bounds same), ybn/ycd claim |
| https://fivemx.com/gta-news/codewalker-update-gtav-enhanced-assets-support | CodeWalker Gen9 converter |
