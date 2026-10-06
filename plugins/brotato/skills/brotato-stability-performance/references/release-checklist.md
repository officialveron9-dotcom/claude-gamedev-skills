# Pre-release checklist (every mod version)

Copy into the release issue/PR and tick each line. "Clean" means a fresh Brotato install profile with only
the mods listed, launched from Steam.

## 1. Build hygiene

- [ ] `manifest.json`: `version_number` bumped; `compatible_game_version` and `compatible_mod_loader_version`
      list exactly the versions you tested (ModLoader does not enforce them; your version gate does).
- [ ] Version gate constants (`TESTED_GAME_VERSIONS`, `MIN_GAME_VERSION`) match the manifest.
- [ ] Feature flags have safe defaults; perf probe and verbose logging **off** by default.
- [ ] No dev-only code: no `DebugService` tweaks, no test hotkeys, no `print()` in per-frame paths.
- [ ] No `assert()` that can fail in normal play (if the build has debug features it aborts the function).
- [ ] Network protocol version bumped if any message format changed.

## 2. Performance test (offline, then local co-op)

Stress setup (dev-only test mod, 1.1.14.x field names, guard with `"field" in DebugService`):
`DebugService.starting_wave = 20`, `invulnerable = true`, `nb_enemies_mult = 2.0`-`3.0`, `disable_saving = true`.
Or play endless to wave 25+ with an AoE-heavy build (max projectiles, explosions, materials on the floor).

- [ ] Same seed/character/build with and without the mod: average frame time, worst frame, spikes > 33 ms.
      Mod adds ≤ 1 ms average, no new spikes (guidance).
- [ ] End-of-wave with 200+ enemies dying and a full floor of materials: no hitch from your code.
- [ ] First appearance of every mod effect: no shader-compile hitch (pre-warmed).
- [ ] 20+ waves: `OBJECT_COUNT`, `OBJECT_NODE_COUNT`, `MEMORY_STATIC`, orphan count flat across waves.
- [ ] 4-player local co-op at the worst wave (co-op raises enemy caps).
- [ ] Low-end check: one run with `--frame-delay` (if the build accepts it) or on the weakest PC available.

## 3. Online test (if the mod has online features)

- [ ] 2, 3 and 4 players on separate machines and Steam accounts.
- [ ] 100-150 ms latency, jitter, 2-5 % loss (clumsy/netem/Steam fake lag), then a 10 s outage.
- [ ] Host alt-tab, host pause menu, client pause menu, client quits mid-wave, host quits in shop,
      client reconnect, all players buying/rerolling at once, run end and "new run" in the same session.
- [ ] Max-enemy wave online: frame time on host and on a client.
- [ ] 30+ minute session: no queue/memory growth, no heartbeat drift.
- [ ] State hash matches at every wave start and shop exit (no desync warnings in the log).

## 4. Game-update compatibility (on every Brotato patch, before players report)

- [ ] Read the version line in `godot.log` (`Brotato v...`, engine line 1).
- [ ] Re-decompile and diff every vanilla script you extend; compare overridden signatures and every member
      you read (`brotato-modding` covers decompiling).
- [ ] Launch: no `Parse Error` for your files; `modloader.log` shows each extension installed. Also open the mod in
      the editor with the new decompiled project: signature mismatches are only reported in debug builds.
- [ ] Smoke path: new run → wave 1 → shop → wave 2 → die/win → end screen → new run → quit to menu →
      continue a saved run → exit game. With and without DLC.
- [ ] Update `TESTED_GAME_VERSIONS`; if not yet fixed, ship a version that enters safe mode on the new
      version instead of crashing.

## 5. Log review

- [ ] `%APPDATA%\Brotato\logs\godot.log`: zero `SCRIPT ERROR`/`ERROR` lines that mention your mod path
      (they also make Brotato's CrashReporter disable all mods on the next launch).
- [ ] No repeated warnings from your mod (one line per condition per session at most).
- [ ] `modloader.log` (run with `-vv` once): your mod loads, in the expected order relative to its dependencies.
- [ ] Your own log: no errors, circuit breakers did not trip, file size sane after a long run.

## 6. Packaging and Workshop

- [ ] Zip layout and mod ID as required by ModLoader (`brotato-modding`); test the **zip**, not the unpacked dev folder.
- [ ] Remove the dev `mods-unpacked` copy before testing the Workshop build, so you're not loading two versions.
- [ ] Clean profile with only your mod; then with 3-5 popular mods (content packs, UI mods).
- [ ] Changelog states the tested game version and any known incompatibilities.
- [ ] Keep the previous release zip to roll back quickly if a hotfix is needed.
- [ ] After upload: subscribe from a second account, launch, play one wave, check the log again.
