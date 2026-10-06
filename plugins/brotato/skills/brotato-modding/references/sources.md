# Sources (accessed 2026-10-06)

Legend: **[src]** = cloned and read directly (commit date in brackets), **[snippet]** = seen only in web-search result snippets (page itself blocked from the sandbox), **[hist]** = read from git history of a deleted page.

## Mod Loader

| Source | Backs up |
|---|---|
| https://github.com/GodotModding/godot-mod-loader branch `3.x` = tag v6.3.0 **[src]** [2025-01-27]; tag v6.2.0 **[src]** [2023-07-14]; branch `3.x-dev` **[src]** [2026-02-10] | All ModLoaderMod/Log/Config/UserProfile/ModManager signatures; manifest required keys, regexes and exact messages (`mod_manifest.gd`, `mod_data.gd`, `mod_loader_utils.gd`); zip mounting with `load_resource_pack(path, false)`, Workshop-or-local zip source, `steam_data.json` app id lookup (`steam.gd` mentions Brotato paths); `user://logs/modloader.log`, `user://configs`, `user://mod_user_profiles.json`; CLI args; extension sorting and `take_over_path` (`script_extension.gd`); 6.2.0 vs 6.3.0 diff (`child_script.new()` vs `reload()`, tie-break, translation null check, `is_initialized`); `load_from_local` only on 3.x-dev; mod mains named by mod id under ModLoader; LICENSE CC0 |
| https://github.com/GodotModding/godot-mod-loader branch `4.x-dev` (v7.0.1) **[src]** | Hooks/`extend_scene`/`is_mod_active` are Mod Loader 7 (Godot 4) only |
| https://github.com/GodotModding/godot-mod-loader/wiki (pages deleted 2025-02-19, moved to https://wiki.godotmodding.com/) **[hist]** | Script-Extensions (virtual functions are called on parent automatically, don't call `._ready()`; Brotato `progress_data.gd` example; inheritance chaining), Mod-Structure (zip layout, `.import`), Mod-Files (manifest example, unique log name), Logging, Overwriting-Game-Resources (`take_over_path`), Global-Classes-&-Child-Nodes, Breaking-Changes, CLI-Args, Decompiling-Games (GDRE, "do not share game code"), `register_global_classes_from_array` override.cfg warning |
| https://wiki.godotmodding.com/ | Not reachable from sandbox; content taken from the wiki's previous GitHub version above |

## Brotato version, engine, Mod Loader version

| Source | Backs up |
|---|---|
| https://github.com/L1SC/brotato-full-map-camera `docs/verification.md` **[src]** [2026-09-17] | Brotato 1.1.15.4, Steam build 23429717, engine `3.7.dev.custom_build.74e86be54`, "built-in ModLoader 6.2.0"; manual `mods/` install claim; `--main-pack` test packs |
| https://github.com/DPS-Love/brotato-combat-tracker `docs/DEVELOPMENT.md`, `tools/testpack/*` **[src]** [2026-10-01] | Game 1.1.15.4 / ML 6.3.0 / Godot 3 bytecode 13; Steam build loads only subscribed Workshop items; signal-based hooks (`took_damage` args, `health_updated` order, spawner signals, pooled `enemy_respawned`); extending `unit.gd` reloads subclasses; signature must match; Godot 3 input picking by tree order; FocusEmulator eats mouse in multiplayer; GodotWorkshopUtility needs `steam_appid.txt`, title = zip name; workshop changenote behaviour; harmless `pd_player.gd` error; update checklist |
| https://github.com/64922/auto-brotato `docs/architecture.md`, `docs/protocol.md` §8 **[src]** [2026-10-06] | Brotato 1.1.15.4 on custom Godot 3.7; save/profile paths under `%APPDATA%\Brotato`; `mod_user_profiles.json` structure; node paths `/root/Main/UI/UpgradesUI`, `/root/DifficultySelection`, `/root/EndRun`; many private members of main/shop/menus |
| https://github.com/mojimoon/BrotatoMods `tests/*/run_tests.sh`, `tools/pack_mod.py` **[src]** [2026-10-05] | Godot_v3.7-dev1 editor for the decompiled project; headless `-s` test runner; game disables mods after mod errors in the log; `bad comparison function` crashes release build; runtime CSV translations |
| https://github.com/hhoangg/brotato-synergies `CONTRIBUTING.md`, `README.md`, `publish-steamcmd.sh`, `workshop_item.vdf` **[src]** [2026-09-05] | Workshop-only loading in shipped build; tabs only; built-in names as identifiers fail; mod PNGs need byte loading; stat cache invalidation; SteamCMD upload; `CoopService.connected_players[i][1]` is controller type |
| https://github.com/MattieTK/brotato-extended-coop-8 `workshop/UPLOAD_INSTRUCTIONS.md` **[src]** [2026-08-31] | `modding` beta branch -> uploader; blank Workshop ID creates item; title from zip name; USD 5 requirement; `_input` multilevel note |
| https://github.com/xx666zz/BrotatoOnline `extensions/main_safe_pool_exit.gd` **[src]** [2026-09-26] | Calling `._ready()` from a `main.gd` extension runs vanilla twice and duplicates `EntitySpawner` players; current `clean_up_room() -> void` |
| https://github.com/DarkTwinge/Brotato-BalanceMod (full history) **[src]** [2026-08-24] | Hash-key refactor in Jan 2026 ("console performance code changes"), Paws & Claws compatibility commit, All Pain No Gain (1.1.15.0) Apr 2026; DLC extension guard in `check_for_available_dlcs` |
| https://github.com/CYoJkoY/Yoko-NewContentLoader `docs/USAGE.en.md` **[src]** [2026-10-02] | Baseline Brotato 1.1.15.4 / ML 6.3.0; DLC extension pattern; `.method()` parent calls; yield in hooks; license is restricted-source |
| https://github.com/BrotatoMods/Brotato-ContentLoader **[src]** [2025-11-30] | ContentLoader 6.2.3 targets game 1.1.13.1 / ML 6.2.0, depends on Darkly77-Brotils; child-node API pattern |
| https://github.com/Oudstand/Brotato-Mods, https://github.com/Xterionix/BrotatoMod-FruitDisabler, https://github.com/CommanderAstern/brotato-share-money, https://github.com/SellenChen/brotangto-mod, https://github.com/liamstewart23/brotato-easy-ready, https://github.com/rauldzmartin/Brotato-AspectRatio1610, https://github.com/SanQing-justsoso/brotato-supermarket-buyfix, https://github.com/boardengineer/Brotatogether **[src]** | Extension targets and override signatures counted across mods (internals map); in-game Mods menu + restart prompt; ModOptions integration; `.import` assets in zips; `compatible_*` values in use |
| Patch-note articles (ingamenews.com 2026-02, gamingonlinux.com 2026-02 "Paws & Claws") **[snippet]** | Paws & Claws migrated to "Godot Engine 3.7 dev-1"; pets, Beast Master |
| gematsu.com / gamingonlinux.com 2025-10 "New Dawn" **[snippet]** | 1.1.13.0 New Dawn by Evil Empire, native Linux/macOS |
| Brotato wiki / Steam patch notes 1.1.15 "All Pain No Gain" **[snippet]** | Nightmare difficulty, Wounded, Rail gun |
| steamcommunity.com Brotato discussions **[snippet]** | "Unexpected error in mod X. Mods have been temporarily disabled."; delete `%APPDATA%\Brotato\logs` workaround; 1.0.1.3 and 1.1.7.1 breakages; pre-Oct-2024 mods broken |
| https://github.com/Blobfish-Games/godot-workshop-utility README **[src: raw README]** | `steam_data.json`, launch option with beta branch, tags |

## Godot engine behaviour

| Source | Backs up |
|---|---|
| https://github.com/godotengine/godot branch `3.x` (version.py = 3.7 dev) files `main/main.cpp`, `scene/main/node.cpp`, `node.h`, `scene_tree.cpp`, `viewport.cpp`, `modules/gdscript/gdscript.cpp`, `gdscript_parser.cpp`, `gdscript_function.cpp`, `core/object.cpp`, `core/sort_array.h` **[src: raw files]** | Autoloads instanced first then added to root (globals null during earlier `_init`); multilevel `_ready`/`_process`/`_input`/`_draw`; `create_timer(time, pause_mode_process = true)`; exact error strings quoted in troubleshooting; signature check only under `DEBUG_ENABLED`; sort validation only in debug builds |

## Not verified

- Which Mod Loader version Brotato 1.1.15.4 actually ships (6.2.0 vs 6.3.0): two sources disagree; no access to the game files.
- Whether `<game>/mods/*.zip` is loaded by the Steam build (2 sources no, 1 yes).
- Exact Brotato version numbers of Paws & Claws (1.1.14.x assumed from mod manifests) and the exact patch that introduced hash keys.
- Steam guides "Modding Guide for Brotato" (steamcommunity id 2931079751) and the Brotato modding Discord/wiki pages: blocked, not read.
