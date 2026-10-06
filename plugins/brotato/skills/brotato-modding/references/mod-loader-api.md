# Godot Mod Loader 6.x API (as used by Brotato)

Read from the `3.x` branch source (v6.2.0 tag and v6.3.0 = HEAD 2025-01-27). Everything here is GDScript 3 and static unless noted. Anything not listed (hooks, `extend_scene`, `is_mod_active`, `Callable` parameters) is Mod Loader 7 / Godot 4 and does not exist in Brotato.

## Contents
- Autoloads and scene tree
- ModLoaderMod
- ModLoaderLog
- ModLoaderConfig and config_schema
- ModLoaderUserProfile / ModLoaderModManager
- Manifest validation messages
- Options, CLI args, paths
- 6.2.0 vs 6.3.0 differences

## Autoloads and scene tree

- `ModLoaderStore` (autoload 1) and `ModLoader` (autoload 2). ML must be first so script extensions apply before the game's own autoloads (`RunData`, ...) are instanced. With an `override.cfg` setup this check is skipped.
- Each active mod's `mod_main.gd` is instanced (`.new()`) in load order and added as child `"/root/ModLoader/<Namespace-Name>"`.
- `ModLoaderStore.MODLOADER_VERSION` - `"6.2.0"` or `"6.3.0"`. `ModLoaderStore.UNPACKED_DIR == "res://mods-unpacked/"`.
- `ModLoaderStore.is_initializing` is `true` during `ModLoader._init()`. Extensions installed while it is true are collected, sorted and applied after all mod mains ran; later calls apply immediately and unsorted.
- Signals on `ModLoader`: `logged(entry)`, `current_config_changed(config)`.
- Do not touch `ModLoaderStore`/`_ModLoader*` internals (underscore classes are private and change without notice).

## ModLoaderMod

| Method | Notes |
|---|---|
| `install_script_extension(child_script_path: String) -> void` | Path must contain `res://mods-unpacked/<ModId>/` (the ModId is parsed from it). Child script must `extends "res://vanilla/path.gd"`. Uses `take_over_path`, so every later `load()`/scene instance of the vanilla path gets the child. |
| `add_translation(resource_path: String) -> void` | Needs a compiled `.translation` (editor import of a CSV creates `name.<locale>.translation`). Fatal if file missing. |
| `append_node_in_scene(modified_scene: Node, node_name := "", node_parent = null, instance_path := "", is_visible := true) -> void` | Use on an instanced vanilla scene, then `save_scene`. Note: with empty `instance_path` 6.x calls `Node.instance()` which is invalid - always pass `instance_path`. |
| `save_scene(modified_scene: Node, scene_path: String) -> void` | Packs the node, `take_over_path(scene_path)`, keeps a reference. Replaces the whole scene for everyone; two mods doing this on the same scene conflict. |
| `register_global_classes_from_array(classes: Array) -> void` | Entries `{"base", "class", "language": "GDScript", "path"}`. Writes `override.cfg` beside the game exe (restart needed; breaks other Godot tools in that folder until deleted). |
| `get_mod_data(mod_id) -> ModData` | Logs `"<id> is an invalid mod_id"` and returns null if unknown. `ModData`: `dir_name`, `dir_path`, `zip_path`, `is_loadable`, `is_active`, `importance`, `manifest` (`ModManifest`), `configs`, `current_config`. |
| `get_mod_data_all() -> Dictionary` | Includes inactive and broken mods (since 6.0.1). Filter on `is_active and is_loadable`. |
| `get_unpacked_dir() -> String` | `"res://mods-unpacked/"`. Replaces deprecated `ModLoader.UNPACKED_DIR`. |
| `is_mod_loaded(mod_id) -> bool` | True if known and `is_loadable` - also when the player disabled it. Warns when called during init. For "active", check `get_node_or_null("/root/ModLoader/" + id)`. |

Deprecated since 6.0.0 (fatal assert in the editor, warning in the shipped game): `ModLoader.install_script_extension`, `ModLoader.add_translation_from_resource`, `ModLoader.mod_data`, `ModLoader.UNPACKED_DIR`, `ModLoaderUtils.log_*`. `mod_main._init(modLoader = ModLoader)` deprecated since 6.1.0.

## ModLoaderLog

Signature for all levels: `ModLoaderLog.<level>(message: String, mod_name: String, only_once := false)`; `debug_json_print(message, json_printable, mod_name, only_once := false)`.

| Level | Behaviour |
|---|---|
| `fatal` | `push_error`, writes entry + stack to the log, then `assert(false)` - stops execution only in debug/editor builds |
| `error` | `printerr` + `push_error`; always logged |
| `warning` | Logged at verbosity >= WARNING (`-v`) |
| `info`, `success` | Logged at verbosity >= INFO (`-vv`) |
| `debug` | Logged at verbosity DEBUG (`-vvv`) |

- `mod_name` is a free label: use `"Namespace-Name"` or `"Namespace-Name:Part"`; `--log-ignore=Namespace-Name:*` filters (wildcards since 6.3.0, exact names in 6.2.0).
- Read back: `get_all_as_string()`, `get_by_mod_as_string(mod_name)`, `get_by_type_as_string("error")`.
- Log file: `user://logs/modloader.log` (rotated each start, old copies `modloader_<datetime>.log`). Godot's own: `user://logs/godot.log`.
- `push_error` output lands in `godot.log` as `ERROR:` lines. Brotato reportedly disables all mods after a run whose log shows mod errors - use `warning`/`info` for expected situations.

## ModLoaderConfig and config_schema

```json
"config_schema": {
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"title": "Config",
	"type": "object",
	"properties": {
		"share_mode": {"type": "string", "enum": ["fixed", "half", "all"], "default": "half"},
		"amount": {"type": "integer", "minimum": 1, "maximum": 999, "default": 10},
		"show_hud": {"type": "boolean", "default": true},
		"tint": {"type": "string", "format": "color", "default": "#ffffffff"}
	}
}
```

| Method | Notes |
|---|---|
| `get_current_config(mod_id) -> ModConfig` | Null + error `Mod "<id>" has no config file.` if the mod has no schema or the profile has no entry yet. Read `.data` (Dictionary). |
| `get_default_config(mod_id)` / `get_config(mod_id, name)` / `get_configs(mod_id)` | `DEFAULT_CONFIG_NAME == "default"`. |
| `create_config(mod_id, name, data) -> ModConfig` | Validated against the schema; fails on empty or duplicate name. |
| `update_config(config)` | Refuses `"default"`: `The "default" config cannot be modified. Please create a new config instead.` |
| `set_current_config(config)` | Emits `ModLoader.current_config_changed(config)`. |
| `get_config_schema(mod_id)`, `get_schema_for_prop(config, prop)`, `get_mods_with_config()`, `get_current_config_name(mod_id)`, `delete_config(config)` | |

- Files: `user://configs/<ModId>/<name>.json` (override with `--configs-path`). Defaults are generated from `default` values; every property needs a `default`.
- Pattern: read config in `_ready()` or later, null-check, fall back to hard-coded defaults. Listen to `ModLoader.current_config_changed` or the options mod's signal for live changes.
- Brotato's Mods menu is documented by mod authors only as an enable/disable list; config UIs come from mods (e.g. `dami-ModOptions`; per the FruitDisabler mod source it exposes `/root/ModLoader/dami-ModOptions/ModsConfigInterface` with signal `setting_changed(setting_name, value, mod_name)` - verify against the current ModOptions version). Treat such a mod as an optional dependency.

## ModLoaderUserProfile / ModLoaderModManager

- Profiles: `user://mod_user_profiles.json` - `{"current_profile": "default", "profiles": {"default": {"mod_list": {"<ModId>": {"is_active": true, "zip_path": "...", "current_config": "default"}}}}}`. Brotato's in-game Mods menu edits this and asks for a restart.
- 6.2.0+6.3.0: `enable_mod(mod_id)`, `disable_mod(mod_id)`, `set_mod_current_config(mod_id, config)`, `create_profile(name)`, `set_profile(profile)`, `delete_profile(profile)`, `get_current()`, `get_profile(name)`, `get_all_as_array()`. 6.3.0 only: `rename_profile`, `is_initialized`.
- `ModLoaderModManager`: `uninstall_script_extension(path)`, `reload_mods()`, `disable_mods()`, `disable_mod(mod_data)`. On disable, ML calls `_disable()` on your mod main if present - undo anything ML cannot (nodes you added to `/root`, connected signals).

## Manifest validation messages (exact)

| Message | Trigger |
|---|---|
| `Dictionary is missing required fields: [...]` | Missing root key (`name`, `namespace`, `version_number`, `website_url`, `description`, `dependencies`, `extra`) or `extra.godot` key (`authors`, `compatible_mod_loader_version`, `compatible_game_version`) |
| `Invalid name or namespace: "X". You may only use letters, numbers and underscores.` | `-`, space, dot in name/namespace |
| `Invalid name or namespace: "X". Must be longer than 3 characters.` | fewer than 3 chars (regex `{3,}`) |
| `Invalid semantic version: "X" in field "version_number" of mod "Y". ...` | not `X.Y.Z`, leading zero, letters |
| `"compatible_mod_loader_version" is a required field.` | empty/missing |
| `The single String value for "compatible_mod_loader_version" is deprecated.` | string instead of array |
| `The mod "X" lists itself as "dependency" in its own manifest.json file` | self-reference |
| `A dependency for the mod "X" is invalid: Expected a single hyphen in the mod ID ...` | malformed ID in a list |
| `The mod -> X lists the same mod(s) -> [...] - in "dependencies" and "incompatibilities".` | ID in two lists |
| `Mod directory name "D" does not match the data in manifest.json. Expected "N-M" (Format: {namespace}-{name})` | folder name mismatch; `Expected "-"` means the manifest was rejected above |
| `ERROR - D is missing a required file: res://mods-unpacked/D/mod_main.gd` | missing `mod_main.gd`/`manifest.json` |
| `Error parsing JSON` / `JSON is not a dictionary` | invalid JSON (trailing comma, comments, BOM issues) |
| `Missing dependency - mod: -> X dependency -> Y` | required dependency not installed/active; X is not loaded |
| `The default config values for N-M are invalid. Configs will not be loaded.` | `default` violates its own schema |

## Options, CLI args, paths

Options resource `res://addons/mod_loader/options/options.tres` (inside the game pack; feature-tag overrides, e.g. `editor`). Fields: `enable_mods`, `log_level`, `locked_mods`, `disabled_mods`, `allow_modloader_autoloads_anywhere`, `steam_workshop_enabled`, `override_path_to_mods`, `override_path_to_configs`, `override_path_to_workshop`, `ignore_deprecated_errors`, `ignored_mod_names_in_log`. (`load_from_local` exists only on the unreleased `3.x-dev` branch, Feb 2026.)

CLI (Steam launch options work; CLI wins over the options resource):

| Arg | Effect |
|---|---|
| `--disable-mods` | load nothing |
| `--mods-path="C:/path"` | override zip folder (only used when Steam Workshop mode is off) |
| `--configs-path="C:/path"` | override config folder |
| `-v` / `--log-warning`, `-vv` / `--log-info`, `-vvv` / `--log-debug` | verbosity |
| `--log-ignore=Name1,Name2:*` | mute log names |

Paths: zip loading in 6.x is **either** Workshop **or** local folder: if `steam_workshop_enabled`, ML scans `<steamapps>/workshop/content/<app_id>/*/` (app id from `steam_data.json` next to the exe), else `<exe dir>/mods/` (`res://mods` in the editor). Each `*.zip`/`*.pck` is mounted with `ProjectSettings.load_resource_pack(path, false)` (no overwriting of existing files). Then every folder in `res://mods-unpacked/` is set up.

Editor caveat (Godot bug): loading any zip in the editor wipes the virtual `res://`, so unpacked mods in `res://mods-unpacked/` vanish. In the editor use unpacked mods only.

## 6.2.0 vs 6.3.0 differences that affect mod code

| Area | 6.2.0 | 6.3.0 |
|---|---|---|
| Extension install | `child_script.new()` (throwaway instance: extension `_init()` runs, Node leaks) | `child_script.reload()` |
| Same-target ordering tie-break | extension path string (`res://mods-unpacked/A-...` < `B-...`) | mod load order |
| `add_translation` with unloadable resource | passes `null` to `TranslationServer` (breaks translations) | fatal log, skipped |
| `file_exists` | plain file check | also `ResourceLoader.exists` (remapped resources) |
| Log name filter | exact | supports `Name:*` |
| `ModLoaderUserProfile.is_initialized()`, `rename_profile()`, `_ModLoaderPath.get_mod_dir()` | missing | present |
