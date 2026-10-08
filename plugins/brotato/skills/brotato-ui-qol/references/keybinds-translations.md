# Keybinds, translations and persistent data in Brotato mods

Godot 3.x API signatures below were checked against the engine's `doc/classes/*.xml` on the `3.x` branch; Brotato specifics come from DPSLove Combat Tracker (hotkeys), tato-Synergies (per-player skill button), Oudstand ModOptions/DamageMeter (per-device actions, translations), Mojimoon AutoAnthony (runtime CSV), Mod Loader 6.x source (`add_translation`).

## Contents
- Keybinds: InputMap facts
- Keybinds: Brotato's device model
- Keybinds: rebind UI and saving
- Keybinds: conflicts and double triggers
- Translations: file formats
- Translations: runtime CSV loader
- Translations: locale and fallback rules
- Translations: naming and text building
- Persistent data

## Keybinds: InputMap facts

| API (Godot 3.x) | Note |
|---|---|
| `InputMap.has_action(name)`, `add_action(name, deadzone = 0.5)`, `erase_action(name)` | adding an existing name errors: always `has_action` first |
| `action_add_event(name, ev)`, `action_erase_event(name, ev)`, `action_erase_events(name)`, `action_has_event(name, ev)`, `get_action_list(name) -> Array` | events are `InputEventKey` (`scancode`, `physical_scancode`, modifiers), `InputEventJoypadButton` (`device`, `button_index`), `InputEventJoypadMotion` (`axis`, `axis_value` sign), `InputEventMouseButton` |
| `event.is_action_pressed(name, allow_echo = false, exact_match = false)`, `is_action_released(name)`, `Input.is_action_pressed(name)`, `Input.is_action_just_pressed(name)` | `is_action_pressed` on an event already drops echoes; `exact_match` ignores extra modifiers when false |
| `InputMap.load_from_globals()` | wipes runtime-added actions (reload from ProjectSettings): never call it |
| `OS.get_scancode_string(code)`, `OS.find_scancode_from_string(str)` | "F9", "Shift+F9", "Escape"; `find_scancode_from_string` returns 0 for unknown text |
| `InputEventKey.get_scancode_with_modifiers()` | store this if you want Shift/Ctrl combos |

`InputEventJoypadButton.device` defaults to 0: an action event with device 0 only matches pad 0. `ev.device = -1` (`InputMap.ALL_DEVICES`, engine source `core/input_map.cpp`) matches every pad - fine for a global hotkey, useless when you need to know *which* player pressed it: then register per device (section below) or poll `Input.is_joy_button_pressed(device, button)`. `InputMap.add_action` on an existing name logs `InputMap already has action "<name>".` and does nothing.

## Keybinds: Brotato's device model

- Vanilla registers its UI actions per device: `ui_accept_<d>`, `ui_cancel_<d>`, `ui_up_<d>`, `ui_down_<d>`, `ui_left_<d>`, `ui_right_<d>`, `ui_pause_<d>` for `d` in 0..7 (Oudstand loops `range(8)`); the plain `ui_accept` etc. are the keyboard/solo path. Check with `InputMap.has_action("ui_accept_%d" % d)` before using one.
- `CoopService` (`res://singletons/coop_service.gd`): `connected_players[i] == [remapped_device, player_type]`, `get_remapped_player_device(player_index)`, `get_player_input_type(player_index)`, `is_player_using_gamepad(player_index)`, `enum PlayerType { KEYBOARD_AND_MOUSE, GAMEPAD_XBOX, GAMEPAD_PLAYSTATION, GAMEPAD_SWITCH }`. Devices are remapped on join: keyboard -> `KEYBOARD_REMAPPED_DEVICE_ID` (7), a pad on raw device 0 -> `GAMEPAD_REMAPPED_DEVICE_ID` (6), other pads keep their raw id (constants read from the decompiled 1.1.15 by the Synergies author; confirm in your build).
- The player slot is the **array index** (same index as `RunData.players_data`); `connected_players[i][1]` is the pad brand - a shipped mod cross-mapped inputs by reading it as the slot.
- In the battle scene, movement is read per player through `PlayerMovementBehavior`/`Utils.is_player_action_pressed(event, player_index, action)` (seen in online mods; signature to verify), so a mod key must either be global (one setting, all players) or resolved to a slot via the device.

Resolving which player pressed your action (event path):

```gdscript
func _player_for(event: InputEvent, base_action: String) -> int:
	for i in RunData.get_player_count():
		var device: int = CoopService.get_remapped_player_device(i)
		var action := "%s_%d" % [base_action, device]
		if InputMap.has_action(action) and event.is_action_pressed(action):
			return i
	return 0 if event.is_action_pressed(base_action) else -1
```

Polling path for pads (Synergies, no InputMap needed): each frame `for dev in Input.get_connected_joypads(): down = Input.is_joy_button_pressed(dev, JOY_BUTTON_X)`, keep a `{dev: bool}` edge table, map `dev` (raw 0 -> 6) to the slot whose `connected_players[i][0]` matches; keyboard key -> the slot whose `[1] == KEYBOARD_AND_MOUSE` or `[0] == 7`. Prime the edge table at wave start from the current state, or the "go" press that started the wave fires the action.

Registering a mod action per device (so the game's own `is_action_pressed` plumbing works):

```gdscript
func _register_pad_action(base: String, button_index: int) -> void:
	for device in 8:
		var name := "%s_%d" % [base, device]
		if not InputMap.has_action(name):
			InputMap.add_action(name)
		InputMap.action_erase_events(name)
		var ev := InputEventJoypadButton.new()
		ev.device = device
		ev.button_index = button_index
		InputMap.action_add_event(name, ev)
```

## Keybinds: rebind UI and saving

- Store the key as a string (`OS.get_scancode_string(scancode)`), `""` = unbound; load with `OS.find_scancode_from_string()`, and on `0` fall back to the default (Combat Tracker: F9 overlay, F8 log, F10 reset, F11 export). Pad buttons: store `button_index` as int, `-1` = unbound.
- Capture flow (Combat Tracker): the settings row shows the current label and a "press a key" state; while `capturing != ""`, `_input` takes the next non-echo `InputEventKey.pressed`: `KEY_ESCAPE` cancels, `KEY_DELETE`/`KEY_BACKSPACE` clears, anything else becomes the bind; save, re-register the action, `set_input_as_handled()`. Show the label with `tr()`-free text (key names are not translated).
- The rebind row must consume the press **and** the release, or the key also reaches the game (Esc opens the pause menu on release).
- Re-register actions after loading settings and after every change; `InputMap` is not persisted by Godot.
- Keep keybinds local (never synced) and per keyboard layout: `scancode` follows the layout, `physical_scancode` the position; use `scancode` + `get_scancode_string` so the label matches what the player sees on the key.

## Keybinds: conflicts and double triggers

| Problem | Cause | Fix |
|---|---|---|
| Action fires twice per press | `_input()` runs on every script level of an extension chain (and you called `._input()`), or both `_input` and `_unhandled_input` handle it, or you registered the base action and the `_<device>` variants and check both | handle once, `get_tree().set_input_as_handled()`, never call `._input()` |
| Fires on wave start | the key that confirmed "go" in the shop is still held on the first in-wave frame | poll-based edge detection primed at wave start; or require release (`is_action_just_pressed`) |
| Opens the pause menu too | your popup consumed the press but not the release of Esc | keep consuming until `Input.is_action_pressed("ui_cancel")` and `ui_cancel_<d>` are all false |
| Works for P1 only | base action without device suffix | per-device actions or polling (above) |
| Key swallowed in menus | a `LineEdit` has focus, or the FocusEmulator handled the event | release focus on Enter/Esc; use `_input` (runs before GUI) for global hotkeys |
| F-key does nothing in fullscreen on some layouts | `scancode` differs by layout | offer rebind; fall back to `physical_scancode` matching |
| Collides with vanilla | names like `ui_*`, `move_*`, `dash`, `pause`... | prefix with your mod id; log `InputMap.get_actions()` once to see the real list in your build |

## Translations: file formats

| Form | How | When |
|---|---|---|
| Compiled `.translation` resources | `ModLoaderMod.add_translation("res://mods-unpacked/<ModId>/translations/QoL.de.translation")` in `mod_main._init()`; one call per locale file | you run a Godot 3.x editor with the mod folder inside a project: importing `QoL.csv` (header `keys,en,de`, `importer="csv_translation"`, `compress=true`) produces `QoL.en.translation`, `QoL.de.translation` next to it (Oudstand ships CSV + `.csv.import` + both `.translation` files; only the `.translation` files matter at runtime) |
| Generated without the editor | `var t := Translation.new(); t.locale = "de"; t.add_message(k, v); ResourceSaver.save("res://.../QoL.de.translation", t)` from a tool/headless script (`Translation` has resource extension `translation`) | build pipelines |
| Runtime CSV | parse at startup, build `Translation` objects, `TranslationServer.add_translation(t)` (loader below) | no editor in the loop; hot-editable text; Mojimoon and this skill's default |
| Hard-coded dictionaries | `const T := {"en": {...}, "de": {...}}` + `TranslationServer.get_locale().substr(0, 2)` | tiny mods; Synergies and Combat Tracker do this; loses `tr()` auto-translation on Controls |

Mod Loader behaviour: `add_translation` checks `file_exists`, then `load(path)`; 6.2.0 passes a null to `TranslationServer.add_translation` when `load` fails (silent breakage), 6.3.0 logs `Failed to load translation at path:` as fatal. Success logs `Added Translation from Resource -> <path>` at info level (`--log-info`). Remove on disable with `TranslationServer.remove_translation(t)` if you keep the references (NewContentLoader does this in teardown).

## Translations: runtime CSV loader

```gdscript
# translations/QoL.csv (UTF-8, no BOM):
# keys,en,de
# QOL_TAB,QoL,QoL
# QOL_SHOW_PING,Show ping,Ping anzeigen
# QOL_NAME_HELP,"Shown to other players, max 16 chars","Wird anderen Spielern angezeigt, max. 16 Zeichen"

const CSV_PATH := "res://mods-unpacked/YourName-QoLPack/translations/QoL.csv"
var _translations := []        # keep references for remove_translation on disable

func _load_translations() -> void:          # call from mod_main._init()
	var f := File.new()
	if f.open(CSV_PATH, File.READ) != OK:
		ModLoaderLog.error("missing %s" % CSV_PATH, LOG_NAME)
		return
	var lines: PoolStringArray = f.get_as_text().split("\n", false)
	f.close()
	if lines.size() < 2:
		return
	var header := _split_csv(lines[0].strip_edges())
	var per_locale := {}                    # "en" -> Translation
	for i in range(1, header.size()):
		var t := Translation.new()
		t.locale = header[i].strip_edges()
		per_locale[header[i].strip_edges()] = t
	for li in range(1, lines.size()):
		var row := _split_csv(lines[li].strip_edges())
		if row.size() < 2 or row[0].strip_edges() == "" or row[0].begins_with("#"):
			continue
		var key := row[0].strip_edges()
		for i in range(1, min(row.size(), header.size())):
			var value := row[i].c_unescape()
			if value == "":
				value = row[1].c_unescape()  # empty cell -> English
			per_locale[header[i].strip_edges()].add_message(key, value)
	for locale in per_locale:
		TranslationServer.add_translation(per_locale[locale])
		_translations.append(per_locale[locale])

static func _split_csv(line: String) -> PoolStringArray:   # handles "quoted, cells" and "" escapes
	var out := PoolStringArray()
	var cur := ""
	var quoted := false
	var i := 0
	while i < line.length():
		var ch := line[i]
		if quoted:
			if ch == "\"":
				if i + 1 < line.length() and line[i + 1] == "\"":
					cur += "\""
					i += 1
				else:
					quoted = false
			else:
				cur += ch
		elif ch == "\"":
			quoted = true
		elif ch == ",":
			out.append(cur)
			cur = ""
		else:
			cur += ch
		i += 1
	out.append(cur)
	return out
```

`split("\n", false)` drops empty lines; Windows line endings leave a trailing `\r` that `strip_edges()` removes. Multi-line cells are not supported by this loader; write `\n` in the cell and rely on `c_unescape()`.

## Translations: locale and fallback rules

- `TranslationServer.translate(key)` (what `tr()` calls) scores every loaded `Translation` against the current locale (`compare_locales`: exact `de_DE` = 10, language-only `de` still > 0), takes the best one that **has the key**, then retries with the project's fallback locale, then returns the key unchanged. So ship `de` not `de_DE`, and a missing German row shows English only if Brotato's fallback is `en` (not verified; fill empty cells yourself as in the loader).
- Controls translate on `set_text` (`Label`, `Button`, `CheckButton`, `OptionButton` items...) and again on `NOTIFICATION_TRANSLATION_CHANGED`, which fires on `TranslationServer.set_locale()` (Brotato's language option). A translation registered after a label was built does nothing until the language changes. Register in `_init()`.
- Keys that look like text ("Reset") are translated too if some mod registered that key: always use `MODNAME_` prefixes, both to avoid clashes and to make raw keys obvious.
- `TranslationServer.get_locale()` returns the engine locale ("de", "zh_CN", "pt_BR"...); Brotato stores the chosen language in `ProgressData.settings.language` and applies it at startup/option change. Test both German and English by switching in the Options menu without restarting: your dynamic strings must re-read `tr()` on `NOTIFICATION_TRANSLATION_CHANGED` (override `_notification` and rebuild text).
- CJK: Brotato's `DynamicFont`s already chain the Noto fallbacks; if you build your own `DynamicFont`, add `res://resources/fonts/raw/NotoSans{SC,TC,JP,KR}-Medium.otf` as `add_fallback` data, ordered by the current locale (Combat Tracker).

## Translations: naming and text building

- Keys: `QOL_<AREA>_<THING>` in SCREAMING_SNAKE; one key per UI string, `_HELP` suffix for help text, `_TITLE` for headers.
- Placeholders: use `"%s"`/`"%d"` with `tr(key) % [a, b]` for your own strings; Brotato's `Text.text(key, [args])` substitutes its `{0}`-style placeholders and handles `keys_needing_percent`/`keys_needing_operator` - use it when reusing vanilla keys (`Text.text("WAVE", [str(RunData.current_wave)])`).
- Reuse vanilla keys where the text exists: `MENU_BACK`, `MENU_CHOOSE`, `MENU_RESTART`, `MENU_NEW_RUN`, `MENU_RETURN_MAIN`, `MENU_MODS`, item/weapon/character names via `tr(item.name)`.
- `RichTextLabel` with BBCode: escape `[` in player-provided strings (`"[lb]"`).
- Never send translated strings over the network; send keys/ids (`brotato-online-multiplayer`).

## Persistent data

- Paths: `user://` resolves to `%APPDATA%\Brotato\` (Windows), `~/Library/Application Support/Brotato/` (macOS), `~/.local/share/Brotato/` (Linux) - the same folder as `logs/`, `mod_user_profiles.json`, `configs/`, `mod_loader_cache.json` and the game's saves. Use a sub-folder named after your mod id; `Directory.make_dir_recursive()` before the first write.
- Crash-safe write: open `path.tmp` with `File.WRITE`, `store_string`, `close()`, then `Directory.new().rename(tmp, path)`. Godot's Windows implementation deletes an existing target and then renames (not a single atomic step, but the full new content is on disk before the old file goes). On load, if `path` is missing or corrupt and `path.tmp` exists, read the `.tmp`.
- `File.open(path, File.WRITE)` truncates immediately: a crash mid-write leaves an empty file - the reason for the temp file.
- Never write every frame or per hit; aggregate (Combat Tracker writes its event log in batches and compresses finished files, DamageMeter never persists per-wave data). Writes are synchronous on the main thread: a few KB is fine, megabytes stall a frame - chunk big logs across frames or write them at wave end.
- Validate on load: type-check every value, clamp ranges, treat unknown keys as data to keep (if you want forward compatibility) or drop (if the schema is strict), never trust `float` vs `int`.
- `ProgressData` is Brotato's own save (`ProgressData.save()`, `load_game_file()`, `settings` dictionary, `saved_run_state`). Extra keys you put into `ProgressData.settings` are written by the game's own save, but whether its loader keeps unknown keys, and how save profiles (1.1.13+) partition the file, is unverified; a wrong write there corrupts the player's progress and the CrashReporter disables all mods on the next start. If you must (e.g. a per-save-profile setting), only store primitives under one namespaced key (`settings["YourName_QoLPack"] = {...}`), read it with `get()` + type checks, and keep a mirror in your own file to recover from a reset.
- Run-scoped data (per-wave stats) belongs in memory on your mod main and is cleared on `RunData.reset()`/scene change; only summaries go to disk.
