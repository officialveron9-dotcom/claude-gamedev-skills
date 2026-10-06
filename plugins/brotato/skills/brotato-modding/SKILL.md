---
name: brotato-modding
description: Builds and debugs Brotato mods correctly - Godot Mod Loader 6.x (manifest.json validation, mod_main.gd, ModLoaderMod.install_script_extension, ModLoaderLog, ModLoaderConfig), Godot 3 script extensions of res:// game scripts, Brotato internals (RunData, ProgressData, ItemService, Utils, Keys hashes, main.gd, player_index co-op), zip/.import packaging, Steam Workshop upload, logs and error fixes. Use for any Brotato mod code, mod-load failure or game-update breakage, also for German requests like "Brotato Mod", "Mod entwickeln", "Script erweitern", "Mod lädt nicht".
---

# Brotato modding (state 2026-10, Brotato 1.1.15.4)

## Verified baseline

| Thing | Value | Confidence |
|---|---|---|
| Game | Brotato 1.1.15.4 (Steam app `1942280`), base + DLC "Abyssal Terrors" (`abyssal_terrors`) | many mods target it |
| Engine | **Godot 3**, custom `3.7.dev.custom_build.74e86be54` since the Paws & Claws update (Feb 2026); scripts compiled as Godot 3 bytecode (rev 13) | log quoted by a mod author + patch-note snippets |
| Script language | **GDScript 3.x** - never Godot 4 syntax. Load the `godot3-gdscript-pitfalls` skill before writing code | certain |
| Mod Loader | GodotModding `godot-mod-loader` **6.x** (branch `3.x`). Shipped build is 6.2.0 or 6.3.0 - sources disagree | conflicting |
| Mod Loader 7.x | Godot 4 only. `install_script_hooks`, `add_hook`, `extend_scene`, `refresh_scene`, `is_mod_active` (and Godot 4's `super()`) **do not exist** here | certain |

Write code that runs on **both 6.2.0 and 6.3.0**: no `ModLoaderUserProfile.is_initialized()`, `rename_profile()`, `ModLoaderConfig.update_config_value()`/`duplicate_config()` (6.3+/unreleased). Check at runtime with `ModLoaderStore.MODLOADER_VERSION` if needed.

## Non-negotiables

1. Godot 3 GDScript only: `.method()` for the parent call, `yield`, `connect("sig", self, "_m")`, `export`, `onready`. A single Godot 4 token is a parse error that kills the whole mod.
2. Install every script extension from `mod_main.gd` `_init()`. Later calls do not affect already-instanced autoloads (RunData, ProgressData, ...).
3. Override signatures must match the vanilla method **exactly** (arg names may differ; count, types, defaults, return type must not). Copy them from the decompiled script of the exact game version.
4. Call `.method(args)` and return its result in every override unless you deliberately replace vanilla - otherwise you also cut off every other mod extending the same method.
5. Never call `._ready()`, `._process()`, `._input()`, `._init()` etc. from an extension: Godot 3 already calls the parent's version (multilevel call). Calling it runs vanilla twice.
6. Brotato 1.1.14+ uses **int hashes** for stats/effects/ids and **per-player** APIs: `Utils.get_stat(Keys.stat_armor_hash, player_index)`, not `Utils.get_stat("stat_armor")`.
7. Never ship game code or assets. Decompile locally for reference only; keep it out of the repo (`.gitignore` a `reference/` folder).

## Mod layout and minimal skeleton

```
mods-unpacked/YourName-QoLPack/        # folder name MUST equal "<namespace>-<name>"
├── manifest.json
├── mod_main.gd
└── extensions/main.gd                  # mirror the vanilla path; not required, but conventional
```

`manifest.json` (required: every root key shown plus `extra.godot.authors`, `compatible_mod_loader_version`, `compatible_game_version`; the other `extra.godot` keys are optional):

```json
{
	"name": "QoLPack",
	"namespace": "YourName",
	"version_number": "1.0.0",
	"description": "Quality-of-life tweaks.",
	"website_url": "",
	"dependencies": [],
	"extra": {
		"godot": {
			"authors": ["YourName"],
			"compatible_mod_loader_version": ["6.2.0", "6.3.0"],
			"compatible_game_version": ["1.1.15.4"],
			"optional_dependencies": [],
			"load_before": [],
			"incompatibilities": [],
			"tags": [],
			"config_schema": {}
		}
	}
}
```

`mod_main.gd`:

```gdscript
extends Node

const MOD_ID := "YourName-QoLPack"
const LOG_NAME := "YourName-QoLPack:Main"   # unique per mod

func _init() -> void:   # no parameter: the old _init(modLoader = ModLoader) is deprecated since 6.1.0
	var dir := ModLoaderMod.get_unpacked_dir().plus_file(MOD_ID)
	ModLoaderMod.install_script_extension(dir.plus_file("extensions/main.gd"))

func _ready() -> void:
	ModLoaderLog.info("loaded", LOG_NAME)
```

`extensions/main.gd` (signature verified in several 1.1.15.x mods):

```gdscript
extends "res://main.gd"

func _on_WaveTimer_timeout() -> void:
	._on_WaveTimer_timeout()   # keep vanilla + other mods
	for player_index in RunData.get_player_count():
		ModLoaderLog.info("wave %d end, P%d gold %d" % [RunData.current_wave, player_index + 1,
				RunData.get_player_gold(player_index)], "YourName-QoLPack:Main")
```

## manifest.json rules (Mod Loader 6.x source)

- `name`, `namespace`: `^[a-zA-Z0-9_]{3,}$` - no `-`, no spaces, at least 3 chars. Mod ID = `namespace-name`.
- `version_number` and every `compatible_mod_loader_version` entry: strict `X.Y.Z`, no leading zeros, < 16 chars. `compatible_game_version` is not validated (`"1.1.15.4"` is fine) and does **not** block loading.
- `compatible_mod_loader_version` must be an array; a string is deprecated, a missing key is fatal.
- IDs in `dependencies`/`optional_dependencies`/`load_before`/`incompatibilities` must be `Namespace-Name`, exactly one `-`, never your own ID, and the same ID may not appear in two of these lists.
- JSON must be strict: no trailing commas, no comments (`Error parsing JSON`).
- Load order: mods sorted by "importance" (= number of mods depending on them), dependencies first. Ties are unordered. To load after mod X, list X in `optional_dependencies`; to load before it, use `load_before`.

## Script extension rules

| Wrong | Right |
|---|---|
| `extends "res://ui/menus/shop/shop.gd"` for a co-op feature | Co-op runs `res://ui/menus/shop/coop_shop.gd`; both extend `base_shop.gd`. Extend the class that actually runs, or the shared base |
| `func take_damage(value, args):` | `func take_damage(value: int, args: TakeDamageArgs) -> Array:` then `return .take_damage(value, args)` |
| `super.on_gold_picked_up(gold, i)` / `super()` | `.on_gold_picked_up(gold, player_index)` |
| `func _ready(): ._ready(); _add_ui()` | `func _ready() -> void: _add_ui()` (vanilla `_ready` already ran) |
| Extending `res://entities/units/unit/unit.gd` for damage stats | Connect to `took_damage`/`health_updated` signals; extending a base class makes ML reload every subclass and costs per-entity time |
| `var _state = {}` per enemy in `enemy.gd` extension without reset | Enemies are pooled and respawn; reset per-entity state on respawn |
| Code after `.method()` assumes vanilla finished | If vanilla `yield`s, `.method()` returns a `GDScriptFunctionState`: `var s = .method(); if s is GDScriptFunctionState: yield(s, "completed")` |
| Editing a `.tscn` copy and shipping it | Add nodes from the extension's `_ready()`; `ModLoaderMod.append_node_in_scene` + `save_scene` exist but replace the whole packed scene (conflicts) |

Chain order when several mods extend the same script: each extension extends the previous one; the **last-loaded mod is outermost** and runs first. Tie-break for the same target: 6.3.0 uses mod load order, 6.2.0 sorts by extension path string. 6.2.0 also instantiates every extension once at install time (`child_script.new()`), so your extension's `_init()` runs once on a throwaway object - keep `_init()` side-effect free.

## Timing: where code may run

| Place | State | Do here |
|---|---|---|
| `mod_main._init()` | Runs while the ModLoader autoload is being constructed. Later autoloads (`RunData`, `ProgressData`, `ItemService`...) are still `null`; `get_tree()` errors (`Condition "!data.tree" is true`) | `install_script_extension`, `add_translation`, `take_over_path` overwrites |
| `mod_main._ready()` | ModLoader entered the tree; other autoloads exist but may not be in the tree or `_ready` yet | `call_deferred("_setup")`, add child nodes to yourself |
| Extension methods | Normal game time | Gameplay logic |
| `ProgressData.check_for_available_dlcs()` override | Game is checking which DLC is installed (startup) | DLC script extensions (see internals reference) |

Other mods' main nodes live at `/root/ModLoader/<ModId>`; that node exists only if the mod is active. `ModLoaderMod.is_mod_loaded(id)` checks `is_loadable`, **not** whether the player disabled it.

## Brotato data model (1.1.14+ hash refactor, co-op since 1.1.0)

```gdscript
# WRONG (1.0-era code, still common in old mods)
RunData.add_stat("stat_max_hp", 5)
var luck = Utils.get_stat("stat_luck") / 100.0
if item.my_id == "item_helmet": ...

# RIGHT (1.1.15.x) - never hard-code hash numbers; use Keys constants or resolve once
var _helmet_hash: int = Keys.generate_hash("item_helmet")   # cache, don't hash in hot loops
RunData.add_stat(Keys.stat_max_hp_hash, 5, player_index)
Utils.reset_stat_cache(player_index)        # stats are cached; without this the change "does nothing"
var luck = Utils.get_stat(Keys.stat_luck_hash, player_index) / 100.0
if item.my_id_hash == _helmet_hash: ...
```

- Loop players with `for player_index in RunData.get_player_count():`; single-player is index 0. Per-player data: `RunData.players_data[player_index]` (`.items`, `.weapons`, `.gold`, `.current_health`, `.current_xp`, `.current_level`).
- Effects: `RunData.get_player_effect(Keys.<x>_hash, player_index)`, `get_player_effect_bool(...)`, effect resources expose `key_hash`. Debug a hash with `Keys.hash_to_string(h)`.
- Item/weapon resources: `my_id` (String) and `my_id_hash` (int). Lookup: `ItemService.get_element(ItemService.items, id_hash)`.
- Resources loaded with `load("res://items/...tres")` are shared: mutating them changes every user. `duplicate()` before per-player changes (`RunData.add_item(item.duplicate(), player_index)`).
- Full map of verified singletons, scripts, members and signals: [references/brotato-internals.md](references/brotato-internals.md) - read before touching any game script.

## Config, translations, assets, inter-mod

- Config: put a JSON-Schema in `extra.godot.config_schema` (`"type": "object", "properties": {"x": {"type": "boolean", "default": false}}`). Read with `ModLoaderConfig.get_current_config(MOD_ID).data`. Files live in `user://configs/<ModId>/`. In-game UI comes from a separate options mod (e.g. `dami-ModOptions`), so default values must be sane.
- Translations: `ModLoaderMod.add_translation(path_to.en.translation)` needs an editor-imported `.translation`. Without the editor, build them at runtime: `var t = Translation.new(); t.locale = "en"; t.add_message("MY_KEY", "Text"); TranslationServer.add_translation(t)`.
- Images/sounds: `load("res://mods-unpacked/.../x.png")` works only if the zip contains `x.png.import` **and** `.import/x.png-<md5>.stex`. Otherwise `No loader found for resource`. Alternative: read bytes with `File`, `img.load_png_from_buffer(bytes)`, `var tex = ImageTexture.new(); tex.create_from_image(img)`; cache the texture.
- Replace a vanilla resource: `preload(mod_res).take_over_path("res://vanilla/path.png")` in `_init()` and keep a reference in a member var. Zip files never overwrite vanilla paths (ML mounts with `replace_files = false`).
- Expose an API to other mods as a child node of your mod main (`/root/ModLoader/YourName-QoLPack/Api`); custom `class_name`s are not registered globally in exported games. `ModLoaderMod.register_global_classes_from_array` works around that but writes `override.cfg` into the game folder: first launch may crash until restart, and it breaks GodotWorkshopUtility until deleted - avoid unless needed.

## Packaging, testing, Workshop (summary)

- Zip root must be `mods-unpacked/<ModId>/...` (plus `.import/` for assets). One mod per zip, forward-slash entry names.
- Steam build loads zips from `steamapps/workshop/content/1942280/<item_id>/*.zip` (ML Steam mode). Whether `<game>/mods/*.zip` also loads is disputed - check `modloader.log`.
- Fast loop: publish once as hidden, subscribe, then overwrite the zip in that Workshop folder and restart. Keep exactly one zip there.
- In-game **Mods** menu toggles mods (`user://mod_user_profiles.json`) and asks for a restart.
- Logs (Windows `%APPDATA%\Brotato\`, macOS `~/Library/Application Support/Brotato/`): `logs/godot.log`, `logs/modloader.log`. Add `--log-info` (`-vv`) or `--log-debug` (`-vvv`) to Steam launch options for info/debug lines; `--disable-mods` to start clean.
- Upload with `GodotWorkshopUtility.exe` from the game folder (via the Steam "modding" beta launch option, or with `steam_appid.txt` = `1942280`). Title = zip filename; paste the existing Workshop ID for updates.
- Full workflow, editor setup with a decompiled project, test harness and legal notes: [references/packaging-workshop.md](references/packaging-workshop.md).

## Most common failures

| Message / symptom | Cause | Fix |
|---|---|---|
| `Mod directory name "X" does not match the data in manifest.json. Expected "A-B"` (or `Expected "-"`) | Folder != `namespace-name`, or manifest validation failed earlier (`-` = empty fields) | Rename folder; fix the earlier fatal line |
| `The mod zip at path "..." does not have the correct file structure.` | Zip root is not `mods-unpacked/` | Re-zip from the parent of `mods-unpacked` |
| `Parse Error: Unexpected '@'` | Godot 4 `@export`/`@onready` | Godot 3 syntax |
| `The child script path '...' does not exist` | Wrong/case-mismatched path | Paths in zips are case-sensitive |
| `Attempt to call function 'set_meta' in base 'null instance'` in `script_extension.gd` | Your extension failed to compile | Fix the `Parse Error` printed just before |
| `Invalid call to function 'x' ... Expected N arguments.` / `Nonexistent function` after a game update | Vanilla signature changed or method removed | Re-decompile, diff, update signature and `compatible_game_version` |
| Game says "Unexpected error in mod X. Mods have been temporarily disabled." | Brotato saw script errors from a mod in the last run's log | Fix the error, re-enable in Mods menu; reported workaround: delete `%APPDATA%\Brotato\logs` |
| Change to stats has no effect | Stat cache / string keys | Hash keys + `Utils.reset_stat_cache(player_index)` |
| Vanilla logic runs twice (e.g. duplicated spawner players) | `._ready()` in an extension | Remove the parent call |

All rows with exact messages: [references/troubleshooting.md](references/troubleshooting.md) - read when a mod fails to load, crashes or misbehaves.

## Before shipping

- [ ] `namespace-name` == folder == `MOD_ID` const; `version_number` bumped (and any in-code version const).
- [ ] No Godot 4 syntax; every override signature copied from the current decompiled game; every override calls `.method()` unless intentional.
- [ ] Extensions installed in `_init()` only; no side effects in extension `_init()`.
- [ ] Hash keys + `player_index` everywhere; tested solo and with 2+ local players.
- [ ] Zip: `mods-unpacked/<ModId>/...` (+ `.import/` for assets), no game files, one zip.
- [ ] `godot.log` / `modloader.log` free of `ERROR`/`SCRIPT ERROR` lines mentioning your mod after a full run (shop, wave, end screen, quit).

## References

- [references/mod-loader-api.md](references/mod-loader-api.md) - Mod Loader 6.x API, manifest validation messages, options, CLI args, paths, 6.2.0 vs 6.3.0 differences. Read when calling any ModLoader* API.
- [references/brotato-internals.md](references/brotato-internals.md) - verified game scripts, singletons, members, signals, co-op, DLC.
- [references/packaging-workshop.md](references/packaging-workshop.md) - zip building, assets, dev loops, decompiling, Workshop upload, legal.
- [references/troubleshooting.md](references/troubleshooting.md) - error message -> cause -> fix.
- [references/sources.md](references/sources.md) - what each fact is based on.
