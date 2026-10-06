# Artifacts and game builds

Read when choosing/updating FXServer builds or changing `sv_enforceGameBuild`.

## Artifact facts (2026-10-06)

| Item | Value |
|---|---|
| Reported Recommended | 35245 (tag date 2026-08-20) |
| Newest tags | 35945 (09-07), 36727 (09-28), 36897 (09-30) |
| Reported client cutoff | Hosting providers report clients can no longer join servers below 35245 from 2026-10-15 (secondary source; not verified on forum.cfx.re) |
| Support window | Recommended supported until 6 weeks after the next recommended; latest/optional until 2 weeks after the next release; > 3 months old -> not joinable from the browser |
| `sv_replaceExeToSwitchBuilds` | default `false` above 12871: client always runs the newest game exe and only loads DLC content up to the enforced build |
| Node | 16 default, `node_version '22'` from 12913 |
| Lua | 5.4 only (5.3 removed June 2025) |
| `sv_stateBagStrictMode` | from 12739 |
| `sv_endpointPrivacy` | removed between 31725 (2026-06-24) and 32561 (2026-07-13); now warning only |

Download: docs.fivem.net/docs/server-download (links to runtime.fivem.net artifacts for `build_server_windows` / `build_proot_linux`). Prefer the build marked recommended over "latest".

## Known-bad builds (community database, jgscripts/fivem-artifacts-db, updated 2026-09-10)

| Builds | Problem |
|---|---|
| 35186-35214 | Lua `io.readdir` iteration errors (breaks ox_lib `getFilesInDirectory`, locales) |
| 34303, 34410, 31725, 25943, 17462 | Failed builds |
| 32698, 33230, 33746, 33864 | Failed Windows builds (Linux OK) |
| 31689 | Server `GetVehiclePedIsIn` returns 0 |
| 28626 | Packet loss / timeouts |
| 27783-27938 | SIGSEGV crashes |
| 27722 | Yarn doesn't exit cleanly on Windows |
| 26261-27715 | Yarn builds fail on some Linux servers |
| 25839-25988 | Node.js sandboxing issues |
| 21547 | Reports of server natives erroring/crashing |
| 16276 | JS loading issues |
| 14583-14862 | `onEntityBucketChange` crash (14583-14716), latency-unit timeouts |
| 13759-13890 | Mumble external connections blocked |
| 12913-14177 | High CPU on Linux (fixed 14193); 12913-13045 Node 22 restart crashes |

Before upgrading: check this list, keep the previous artifact folder for rollback, test on staging (start, join, restart resources, DB, NUI).

## Game builds

| Build | Alias | DLC |
|---|---|---|
| 1 | - | Base game, no DLC |
| 1604 | xm18 | Arena War |
| 2060 | sum | Los Santos Summer Special |
| 2189 | h4 | Cayo Perico Heist |
| 2372 | tuner / mptuner | Los Santos Tuners |
| 2545 | security | The Contract |
| 2612 | mpg9ec | - |
| 2699 | mpsum2 | Criminal Enterprises |
| 2802 | mpchristmas3 | Los Santos Drug Wars |
| 2944 | mp2023_01 | San Andreas Mercenaries |
| 3095 | mp2023_02 | The Chop Shop |
| 3258 | mp2024_01 | Bottom Dollar Bounties |
| 3407 | mp2024_02 | Agents of Sabotage |
| 3570 | mp2025_01 | Money Fronts |
| 3751 | mp2025_02 | A Safehouse in the Hills |
| 3889 | mp2026_01 | The Kortz Center Heist |

Every build includes all earlier content. Without `sv_enforceGameBuild` current Legacy artifacts mandate **3258** (Bottom Dollar Bounties) - newer DLC content is missing until you set it explicitly. (Source also knows a non-DLC patch build 3788.) Resources can require a minimum with `dependency '/gameBuild:3407'`; unmet -> `sv_enforceGameBuild needs to be at least 3407 (current is 3258)`. Enhanced servers support only the newest build (3889) or `1`.

Traps:
- Vehicle/clothing packs made for a newer DLC reference DLC textures/models -> missing textures on lower builds.
- MLOs placed where a newer DLC adds map geometry can clip after raising the build.
- Natives added in newer title updates are not callable on older enforced builds.
