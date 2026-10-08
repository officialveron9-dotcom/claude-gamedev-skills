# Settings and config storage for Brotato mods

Sources: Mod Loader `3.x` branch source (v6.3.0 head, diffed against tag v6.2.0), the old GitHub wiki pages "Mod Configs" and "Config JSON" (git history), dami-ModOptions 0.6.2, Oudstand ModOptions 1.0.1/1.1.0, Mojimoon DoubleSidedUpgrades, tato-Synergies `mod_settings.gd`, DPSLove Combat Tracker `core/config.gd`.

## Contents
- Decision table
- ModLoaderConfig: lifecycle, files, API traps
- config_schema keys
- Migration between mod versions
- Own store: ConfigFile
- Own store: JSON
- Options-menu frameworks (optional dependencies)
- Per-player vs per-host settings in co-op
- Hot-apply pattern

## Decision table

| Store | Where | Pros | Cons |
|---|---|---|---|
| `ModLoaderConfig` + `config_schema` | `user://configs/<ModId>/<name>.json` | validated, discoverable by config UIs (dami-ModOptions renders it), `--configs-path` override, profiles | `default` is read-only; first-start ordering trap; validation errors are silent nulls; floats for ints; no UI in Brotato itself |
| `ConfigFile` | `user://<ModId>/settings.cfg` | keeps Variant types (bool/int/float/Color), human-editable INI, comments possible when you write the file yourself | you own validation and migration |
| JSON via `File` + `JSON.print/parse` | `user://<ModId>/settings.json` | easy to share as text (Mojimoon exports Base64 "share codes") | every number is a float, no comments, dictionary keys are strings |

Recommendation for a new co-op/QoL mod: one `ConfigFile`-backed store object with typed defaults, a `schema_version`, a `settings_changed` signal and an atomic save; expose it through your own options tab, and optionally mirror it into Oudstand ModOptions when that mod is present. Use `config_schema` only if you want other tools to edit the file.

## ModLoaderConfig: lifecycle, files, API traps

Startup order (both 6.2.0 and 6.3.0, `mod_loader.gd`):

1. `ModLoader._init()`: zips mounted -> `mod_data` built -> user profiles applied -> for every mod `load_manifest()` then `load_configs()` if `extra.godot.config_schema` is non-empty -> dependencies/load order -> each `mod_main.gd` instanced (`_init()` runs here).
2. `ModLoader._ready()`: creates the `default` user profile if missing and `_update_mod_lists()`, which adds the `current_config` key to every active mod's entry in `user://mod_user_profiles.json`.

Consequences:

- `load_configs()` first calls `manifest.load_mod_config_defaults()`: it (re)generates `default.json` from the schema `default` values on every start (the md5-cache condition in 6.x regenerates whenever a cached md5 exists), validates it, and on failure logs `The default config values for <ns>-<name> are invalid. Configs will not be loaded.` -> `get_configs()` returns `{}` and every getter returns null. Every property needs a `default` that satisfies its own constraints.
- Then every other `*.json` in `user://configs/<ModId>/` is loaded as a `ModConfig` and validated; invalid ones still exist with `is_valid == false`.
- `current_config` comes from the profile entry; on the very first start that entry lacks `current_config` until `ModLoader._ready()`, so `get_current_config()` from `mod_main._init()` or `_ready()` logs `Mod "<id>" has no config file.` (6.2.0 also logs this once during `load_configs()`; 6.3.0 checks `ModLoaderUserProfile.is_initialized()` first). Read configs with `call_deferred` from `_ready()` and fall back to `get_default_config()`.
- `get_configs(mod_id)` with an unknown id is **fatal** (`Mod ID "<id>" not found`): only call it for your own id.

| Call | Behaviour (verified) | Trap |
|---|---|---|
| `get_current_config(mod_id) -> ModConfig` | profile's `current_config` name -> `get_config` | null + error when the profile entry is missing or the file was deleted (the profile then resets to `default` on next load) |
| `get_default_config(mod_id)` / `get_config(mod_id, name)` | from `ModLoaderStore.mod_data[mod_id].configs` | null + error `No config with name "<n>" found for mod_id "<id>"` |
| `create_config(mod_id, name, data) -> ModConfig` | validates `data` against the schema, saves `user://configs/<ModId>/<name>.json`, registers it | null if the name is empty, already exists, or data fails validation; does **not** set it current |
| `set_current_config(config)` | writes the name into the profile (`mod_user_profiles.json` saved immediately) and emits `ModLoader.current_config_changed(config)` | the only thing that emits that signal |
| `update_config(config) -> ModConfig` | re-validates `config.data`, saves the file | returns null and logs `The "default" config cannot be modified. Please create a new config instead.` for `default`, or `Update for config "<n>" failed validation with error message "<schema error>"`; emits no signal |
| `delete_config(config) -> bool` | sets current to default, removes file and entry | cannot delete `default` |
| `get_config_schema(mod_id)`, `get_schema_for_prop(config, "a.b")` | schema dictionaries | empty dict when the mod has no configs |
| `ModConfig` fields | `name`, `mod_id`, `schema`, `data`, `save_path`, `is_valid`; methods `validate() -> String` (empty = ok), `save_to_file()`, `remove_file()` | `data` is a plain Dictionary you may mutate before `update_config` |

Only in unreleased/other versions, do not use: `update_config_value`, `duplicate_config`, `save_mod_config_setting`.

Reading values safely:

```gdscript
static func cfg_int(data: Dictionary, key: String, fallback: int) -> int:
	var v = data.get(key, fallback)
	return int(v) if typeof(v) in [TYPE_INT, TYPE_REAL] else fallback   # JSON ints arrive as floats

static func cfg_color(data: Dictionary, key: String, fallback: Color) -> Color:
	var s = str(data.get(key, ""))
	return Color(s) if s.is_valid_html_color() else fallback            # schema "format": "color" stores "#aarrggbb"/"#rrggbb"
```

## config_schema keys

Supported (JSON Schema 2020-12 subset, validated by the bundled `JSONSchema` class): `type` (`object`, `number`, `integer`, `boolean`, `string`, `array`), `properties`, `default`, `title`, `description`, `minimum`, `maximum`, `multipleOf`, `minLength`, `maxLength`, `enum`, `required`, plus the Mod Loader extension `"format": "color"` (hex string, validated with `is_valid_html_color()`). Unsupported: `contains`, `minContains`, `maxContains`, `uniqueItems`, `patternProperties`, other `format` values.

What UIs read (dami-ModOptions): `title` -> label, `tooltip` (non-standard key) -> hover text through `Text.text()`, `enum` -> dropdown, `number` + `minimum`/`maximum`/`multipleOf` -> slider (`multipleOf` becomes the step; without it the slider is continuous), `boolean` -> `CheckButton`, `string` with `format: color` -> colour picker; nested `object` is flattened. Plain `string` and `array` properties have no widget there.

Example used by shipping mods:

```json
"config_schema": {
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"title": "QoLPack",
	"type": "object",
	"properties": {
		"schema_version": {"type": "integer", "default": 1},
		"overlay_scale": {"type": "number", "title": "Overlay scale", "minimum": 0.5, "maximum": 2.5, "multipleOf": 0.05, "default": 1.0},
		"share_mode": {"type": "string", "title": "Gold sharing", "enum": ["none", "half", "all"], "default": "half"},
		"show_ping": {"type": "boolean", "title": "Show ping", "default": true},
		"accent": {"type": "string", "title": "Accent colour", "format": "color", "default": "#ffffc34c"}
	}
}
```

## Migration between mod versions

- Keys you rename or retype lose the user's value; keep ids stable and add new keys instead.
- `ModLoaderConfig`: `default.json` always follows the schema, but a user's `*.json` keeps its old key set. On load merge: `for k in default.data: if not cfg.data.has(k): cfg.data[k] = default.data[k]`, then drop keys no longer in the schema if you use `required`/`additionalProperties`. A stricter `minimum`/`maximum` in the new schema makes old files `is_valid == false`: clamp and `update_config`, or the file stays unusable.
- Mojimoon's pattern: one config per mod version (`create_config(MOD_ID, version_number, default.data)`), copying missing keys from the defaults - simple, but leaves a file per version behind.
- Own store: write `schema_version`; on load run `while version < CURRENT: _migrate(version); version += 1` with explicit steps (rename, retype, clamp), then save.
- Window positions and layout values: clamp into the current viewport on load, not only on save.

## Own store: ConfigFile

```gdscript
# qol_settings.gd  (Reference, created once in mod_main._ready(), passed to UI/consumers)
extends Reference

signal settings_changed(key, value)

const PATH := "user://YourName-QoLPack/settings.cfg"
const SECTION := "qol"
const CURRENT_VERSION := 2
# key -> default. The default's type is the key's type (bool/int/float/String/Color/Array).
const DEFAULTS := {
	"schema_version": CURRENT_VERSION,
	"overlay_scale": 1.0,
	"show_ping": true,
	"share_mode": "half",
	"toggle_overlay_key": "F9",
	"overlay_pos": Vector2(12, 200),
}
const RANGES := {"overlay_scale": [0.5, 2.5]}
const CHOICES := {"share_mode": ["none", "half", "all"]}

var _cf := ConfigFile.new()
var _dirty := false
var _save_timer: SceneTreeTimer = null
var _tree: SceneTree = null

func _init(tree: SceneTree) -> void:
	_tree = tree
	var err := _cf.load(PATH)
	if err != OK and err != ERR_FILE_NOT_FOUND:
		var backup := File.new()
		if backup.file_exists(PATH + ".tmp"):            # crashed between write and rename
			_cf.load(PATH + ".tmp")
	for key in DEFAULTS:
		if not _cf.has_section_key(SECTION, key):
			_cf.set_value(SECTION, key, DEFAULTS[key])
	_migrate()
	save_now()

func get_value(key: String):
	var def = DEFAULTS.get(key)
	var v = _cf.get_value(SECTION, key, def)
	if def == null or typeof(v) != typeof(def):
		# ConfigFile keeps types, but a hand-edited file or an old schema can mismatch; coerce or reset
		match typeof(def):
			TYPE_BOOL: v = str(v).to_lower() in ["true", "1", "yes", "on"]
			TYPE_INT: v = int(v) if str(v).is_valid_float() else def
			TYPE_REAL: v = float(v) if str(v).is_valid_float() else def
			TYPE_STRING: v = str(v)
			_: v = def
	if RANGES.has(key):
		v = clamp(v, RANGES[key][0], RANGES[key][1])
	if CHOICES.has(key) and not v in CHOICES[key]:
		v = def
	return v

func set_value(key: String, value) -> void:
	if not DEFAULTS.has(key) or get_value(key) == value:
		return
	_cf.set_value(SECTION, key, value)
	emit_signal("settings_changed", key, value)
	_dirty = true
	if _save_timer == null:                               # debounce slider drags: one write per 0.5 s
		_save_timer = _tree.create_timer(0.5, true)
		_save_timer.connect("timeout", self, "_on_save_timer")

func _on_save_timer() -> void:
	_save_timer = null
	if _dirty:
		save_now()

func save_now() -> void:
	_dirty = false
	var dir := Directory.new()
	if not dir.dir_exists(PATH.get_base_dir()):
		dir.make_dir_recursive(PATH.get_base_dir())
	var tmp := PATH + ".tmp"
	if _cf.save(tmp) != OK:                                # ConfigFile.save truncates: write the temp first
		return
	if dir.rename(tmp, PATH) != OK:                        # Windows removes the old file, then renames
		push_warning("QoLPack: could not replace settings file")

func _migrate() -> void:
	var v := int(_cf.get_value(SECTION, "schema_version", 1))
	while v < CURRENT_VERSION:
		match v:
			1:                                             # v1 stored overlay_scale in percent
				_cf.set_value(SECTION, "overlay_scale", float(_cf.get_value(SECTION, "overlay_scale", 100)) / 100.0)
		v += 1
	_cf.set_value(SECTION, "schema_version", CURRENT_VERSION)
```

Notes:
- `ConfigFile.load()` on a missing file returns `ERR_FILE_NOT_FOUND`; every `get_value` then returns its default - that is the normal first start (Synergies relies on it).
- `set_value(section, key, null)` deletes the key; never store `null`.
- `create_timer(0.5, true)` keeps running while the game is paused (options menu), so drags in the pause menu still flush.
- Flush on `_exit_tree()`/`NOTIFICATION_WM_QUIT_REQUEST` of your mod main as well (`save_now()` if dirty); a kill does not run it, which is why every change is also flushed within 0.5 s.
- Combat Tracker writes its own INI with bilingual `;` comments per key (Godot's `ConfigFile.save` drops comments), then reads it back with `ConfigFile.load`; `var2str` values round-trip.

## Own store: JSON

Same structure with `File` + `JSON.print(dict, "\t")` / `JSON.parse(text)`; check `result.error == OK and result.result is Dictionary`, copy only known keys (Oudstand ModOptions ignores unknown ones), cast numbers (`int(v)`), and write temp + rename as above. `JSON.print` cannot serialise `Vector2`/`Color`: store `[x, y]` / `color.to_html()`.

## Options-menu frameworks (optional dependencies)

Both are Workshop mods other players may or may not have. List them under `optional_dependencies` (never `dependencies` unless you accept the hard requirement), look the node up with `get_node_or_null`, retry a few times with a short timer if your `_ready()` runs before theirs, and keep working without them.

### Oudstand-ModOptions (Workshop 3598984651, GitHub Oudstand/Brotato-Mods, targets 1.1.15.0+)

- Node: `/root/ModLoader/Oudstand-ModOptions/ModOptions`. Register from `mod_main._ready()` via `call_deferred`:

```gdscript
mod_options.register_mod_options(MOD_ID, {
	"tab_title": "QOL_TAB",                                   # translation key or text
	"options": [
		{"type": "toggle", "id": "show_ping", "label": "QOL_SHOW_PING", "default": true},
		{"type": "slider", "id": "overlay_scale", "label": "QOL_SCALE", "min": 0.5, "max": 2.5, "step": 0.05, "default": 1.0, "display_as_integer": false},
		{"type": "dropdown", "id": "share_mode", "label": "QOL_SHARE", "choices": ["none", "half", "all"], "default": "half"},
		{"type": "text", "id": "player_name", "label": "QOL_NAME", "default": "", "multiline": false, "help_text": "QOL_NAME_HELP"},
	],
	"info_text": "QOL_INFO"
})
var v = mod_options.get_value(MOD_ID, "show_ping")             # null + error for unknown ids
mod_options.connect("config_changed", self, "_on_mod_options_changed")   # (mod_id, option_id, new_value)
```

- Also: `set_value(mod_id, id, value)` (saves + emits), `get_mod_values(mod_id)`, `get_registered_mods()`, signal `mod_registered(mod_id)`; `item_selector` type with `item_type` `weapon`/`item`/`character`; `visible_if` per option. Values persist in `user://mod_options_<registration id>.json`, written only on change. Registering twice errors; `register_mod_options` does not emit `config_changed`, read initial values with `get_value`. Dropdowns store the choice value, not the index. It relies on its own `menu_options.tscn` override and a `focus_emulator.gd` extension (controller support, bumper cycling, sidebar).
- Integration pattern: your store stays authoritative; on `config_changed` for your id copy into your store (`store.set_value`), and when your own UI changes a value call `mod_options.set_value` to keep both views in sync (guard against ping-pong with an `_applying` flag).

### dami-ModOptions (Workshop "Mod Options" by KANA/dami/Pasha, GitHub BrotatoMods/Brotato-Mod-Options 0.6.2, last targets 1.1.13.1)

- Reads every loaded mod's `config_schema` + current `ModLoaderConfig` data and renders a "Mods" tab (title screen + pause menu) using `slider_option.tscn`, `CheckButton`, `color_option.tscn`, `OptionButton` for `enum`.
- Node `/root/ModLoader/dami-ModOptions/ModsConfigInterface` (`class_name ModsConfigInterface`): signal `setting_changed(setting_name, value, mod_name)`, `get_settings(mod_name) -> Dictionary` (flattened: `key`, `key_max`, `key_min`, `key_step`, `key_title`, `key_tooltip`, `enum_key`, `enum_key_options`), `on_setting_changed(name, value, mod_name)` (emits).
- It does **not** write to `ModLoaderConfig`: persist yourself in the signal handler (Mojimoon writes `config.data[name] = value; config.save_to_file()` into a version-named config). Colour values arrive as `Color.to_html()` strings.
- Its tab is injected by `title_screen.gd` / `pause_menu.gd` extensions (SKILL.md section 3 is that recipe); compatibility with 1.1.15 is unverified.

## Per-player vs per-host settings in co-op

| Setting kind | Owner | Example |
|---|---|---|
| Visual, audio, HUD layout, UI scale, keybinds, language, damage-number display | local player, never synced | overlay scale, ping display |
| Rules that change the simulation | host; broadcast in the run config before the first scene loads; clients apply a temporary override and restore their own values when the session ends | gold sharing, enemy scaling tweaks, ready-check timeout |
| Social | host for enforcement, local for display | AFK auto-pick seconds (host), show other players' names (local) |

Implementation: keep `host_overrides: Dictionary` in your store; `get_value` returns the override when the session is live; `clear_host_overrides()` on disconnect. Validate incoming host values against `RANGES`/`CHOICES` exactly like local input (`brotato-online-multiplayer` rule 5: never trust decoded objects). Hash the gameplay-affecting subset into the lobby's mod/version check so mismatched defaults cannot desync a run.

## Hot-apply pattern

```gdscript
# consumer (overlay, extension, net code)
func _ready() -> void:
	var store = _get_store()                      # /root/ModLoader/YourName-QoLPack  ->  .settings
	if store != null:
		store.connect("settings_changed", self, "_on_setting")
		_apply_all(store)

func _on_setting(key: String, value) -> void:
	match key:
		"overlay_scale": rect_scale = Vector2(value, value)
		"show_ping": _ping_label.visible = value
		"toggle_overlay_key": _register_action(OS.find_scancode_from_string(value))
```

Things that cannot hot-apply (log retention, autoload-ish changes): mark the row "restart required" in the UI instead of pretending. For ModLoaderConfig users, `ModLoader.current_config_changed` only fires on `set_current_config`; keep your own signal for value changes.
