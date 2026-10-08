---
name: brotato-ui-qol
description: Builds Brotato mod UI and QoL plumbing without the usual bugs - options-menu tabs and settings panels (menu_options, ModOptions/dami-ModOptions frameworks), Mod Loader 6.x ModLoaderConfig and manifest config_schema vs an own ConfigFile at user://, keybinds via InputMap with Brotato's per-device actions and CoopService, HUD overlays on CanvasLayer, translations (ModLoaderMod.add_translation, .translation vs runtime CSV, tr()), crash-safe persistent data and co-op settings sync. Use for Brotato mod options, settings menu, keybind, HUD overlay, translation or save-data questions, also German "Einstellungen", "Menü", "Optionen", "Tastenbelegung", "Übersetzung", "HUD", "QoL".
---

# Brotato UI and QoL plumbing (Brotato 1.1.15.x, Godot 3.7-dev, Mod Loader 6.2/6.3)

Baseline, Mod Loader API, script-extension rules and game internals: `brotato-modding`. Godot 3 syntax: `godot3-gdscript-pitfalls`. Netcode: `brotato-online-multiplayer`. Per-frame cost and crash rules: `brotato-stability-performance`. This skill only covers menus, settings, keybinds, HUD, translations and saved data. Node paths below were read from mods that run on 1.1.13-1.1.15.4; re-check them in the decompiled game after every patch.

## 1. Where to hook UI

| Screen | Scene / script | Hook | Trap |
|---|---|---|---|
| Title screen | `res://ui/menus/title_screen/title_screen.gd` (scene name `TitleScreen`), `$Menus/MenuOptions` | extend `title_screen.gd`, add nodes in `_ready()` | the options menu instance here is separate from the in-run one |
| Main menu page | `res://ui/menus/pages/main_menu.gd` (`init()`, `version_label`) | override `init()`, call `.init()` | |
| Options menu (title + pause) | `res://ui/menus/pages/menu_options.tscn/.gd`: `Buttons` (tab controller: `buttons_tab_np`, `buttons_tab`, `tab_container`, `_change_tab(i)`), `Buttons/HBoxContainer2/*_but` (last child is `empty_space_right`), `Buttons/HBoxContainer3/TabContainer/<X>_Container`, `%BackButton`, `%Audio_but`, `init()`, `is_in_a_run`, group `hide_in_run` | add a tab from `title_screen.gd` + `pause_menu.gd` extensions (section 3) | overriding `menu_options.tscn` with `take_over_path` works but two mods doing it conflict |
| Pause menu | `res://ui/menus/ingame/pause_menu.gd`, member `_menu_options` | extension `_ready()` | tree is paused: your nodes need `pause_mode = PAUSE_MODE_PROCESS` |
| Character select | scene name `CharacterSelection`; run options `.../DescriptionContainer/RunOptionsPanel/MarginContainer/VBoxContainer/VBoxContainer/{EndlessButton,BanButton,CoopButton}`; panels `Panel1..4` | add `CheckButton` after `CoopButton`, copy its font (`coop_btn.get_font("font")`) | the panel is rebuilt when co-op toggles: re-check `has_node` every time |
| Shop | `base_shop.gd` (`_get_reroll_button(i)`, `_get_go_button(i)`, `%GoButton`, `%RerollButton`) | add buttons next to reroll, wire `focus_neighbour_*` | solo = `shop.gd`, co-op = `coop_shop.gd`: extend `base_shop.gd` |
| HUD in a wave | `/root/Main/UI/HUD/LifeContainerP1..4` (BoxContainer), `/root/Main/WaveTimer`, `res://ui/hud/ui_wave_timer.gd` | add children in a `main.gd` extension `_enter_tree()`; or own `CanvasLayer` under `/root` | HUD nodes die with `Main`; a root CanvasLayer does not |
| Level-up, end of run, difficulty | `/root/Main/UI/UpgradesUI`, `/root/EndRun` (`%Title`, `.../HBoxContainer3/{RestartButton,NewRunButton,ExitButton}`), `/root/DifficultySelection` | `get_tree().current_scene` + `get_node_or_null` | names are private; guard everything |

Full tree, members, vanilla reusable scenes, theme/font paths, layering and focus: [references/menus-and-hooks.md](references/menus-and-hooks.md).

## 2. Rules

1. **Build UI in code, add it deferred.** `parent.call_deferred("add_child", node)` from an extension `_ready()`; never ship edited vanilla `.tscn` files. Mark your nodes with a fixed `name` and `if parent.has_node(NAME): return` so re-entering a menu does not duplicate them.
2. **Reuse Brotato's look**: `theme = load("res://resources/themes/base_theme.tres")` on your root Control, fonts `res://resources/fonts/actual/base/font_26.tres` / `font_26_outline.tres` / `font_40_outline.tres`, vanilla widgets `res://ui/menus/global/slider_option.tscn`, `color_option.tscn`, script `my_menu_button.gd` (click sounds), tab theme `res://resources/themes/tab_buttons_physic.tres`. A default `Label`/`CheckButton` is roughly 2x too big here: copy the font from a neighbouring vanilla control.
3. **Layering and input picking**: `CanvasLayer.layer` 3-ish sits with the HUD (pause/shop menus cover it), 100+ covers everything. Godot 3 picks the control under the mouse by tree order, not by layer, and in co-op the game's `FocusEmulator` marks mouse events handled in `_input`. An overlay that must take clicks lives as the **last child of `/root`** (re-move it after every scene change) or routes mouse events itself in `_input()`.
4. **Focus**: overlay controls get `focus_mode = Control.FOCUS_NONE` and `mouse_filter = MOUSE_FILTER_IGNORE` unless you want them in the menu's gamepad navigation; menu controls need `FOCUS_ALL` and explicit `focus_neighbour_*` paths, or the per-player `FocusEmulator` skips them. Use `Utils.focus_player_control(control, player_index)` to move a player's cursor, never a bare `grab_focus()` in co-op.
5. **Per-device input**: Brotato's actions are `ui_accept_<device>`, `ui_cancel_<device>`, `ui_up/down/left/right_<device>`, `ui_pause_<device>` for devices 0-7; the keyboard is remapped to device 7, a pad on raw device 0 to 6; `CoopService.get_remapped_player_device(player_index)` gives the slot's device and the slot is the **index** into `CoopService.connected_players` (element `[1]` is the pad brand). Pads drive the per-player `FocusEmulator` through these suffixed actions, so Godot's built-in focus navigation and plain `ui_accept` do not respond to pads in co-op menus.
6. **Pause**: a menu opened while the tree is paused needs `pause_mode = PAUSE_MODE_PROCESS` on its root; a popup that pauses the game sets the parent to `PAUSE_MODE_STOP`, pauses, and on close waits until every cancel key is **released** before unpausing, or the Esc release opens the pause menu.
7. **Size for 4K and ultrawide**: Brotato uses 2D stretch with an expanding logical viewport (1920x1080 on 16:9, 3440x1440 on 21:9 - FullMapCamera's test matrix). Read `get_viewport().get_visible_rect().size` or `Utils.project_width/height`, anchor to edges, never `OS.window_size` or hard-coded 1920.
8. **Localize with keys**: set `label.text = "MYMOD_KEY"` (Controls `tr()` on `set_text`); register translations in `mod_main._init()`, before any UI exists, because existing labels only re-translate on a locale change.
9. **Hot-apply settings** through one signal (`settings_changed(key, value)`); readers refresh from it, never poll files. Save on change with a debounce (slider drags), never per frame.
10. **Co-op**: gameplay-affecting settings are host values (send them in the run config); visuals, volume, keybinds, language stay local. See `brotato-online-multiplayer` qol-features.

## 3. Add a tab to the options menu (title screen + pause menu)

```gdscript
# extensions/ui/menus/title_screen/title_screen.gd   (same body in pause_menu.gd with `_menu_options`)
extends "res://ui/menus/title_screen/title_screen.gd"

const TAB_SCENE := "res://mods-unpacked/YourName-QoLPack/ui/qol_tab.tscn"   # or build a ScrollContainer in code

func _ready() -> void:
	call_deferred("_qol_add_tab", $Menus/MenuOptions)

func _qol_add_tab(menu: Node) -> void:
	var buttons = menu.get_node_or_null("Buttons/HBoxContainer2")
	var controller = menu.get_node_or_null("Buttons")
	if buttons == null or controller == null or buttons.has_node("QoLTabButton"):
		return
	var template: Button = buttons.get_child(buttons.get_child_count() - 2)   # last real tab button, before `empty_space_right`
	var btn: Button = template.duplicate()                        # keeps theme, MyMenuButton script, toggle_mode
	btn.name = "QoLTabButton"
	btn.text = "QOL_TAB"                                          # translation key
	buttons.add_child_below_node(template, btn)
	var tab_index: int = controller.tab_container.get_child_count()   # tabs are 0-based; buttons have a leading spacer
	var tab = load(TAB_SCENE).instance()
	tab.name = "QoL_Container"
	controller.tab_container.add_child(tab)
	btn.connect("pressed", controller, "_change_tab", [tab_index])
	controller.buttons_tab_np.push_back(btn.get_path())           # bumper (LB/RB) cycling
	controller.buttons_tab.push_back(btn)
```

`_change_tab`, `buttons_tab_np`, `buttons_tab`, `tab_container` are private names verified in 1.1.13.1 (dami-ModOptions) and 1.1.15 (Oudstand ModOptions); guard with `has_method`/`in` and diff after updates. Settings widgets inside the tab: [references/menus-and-hooks.md](references/menus-and-hooks.md#building-settings-widgets).

## 4. Settings and config: pick one store

| Need | Use | Notes |
|---|---|---|
| Simple per-player preferences, your own UI | own `ConfigFile` at `user://<ModId>/settings.cfg` | typed defaults, schema version, atomic save (section 8) |
| Config editable by other tools / the Mods ecosystem | Mod Loader `config_schema` + `ModLoaderConfig` | files `user://configs/<ModId>/<name>.json`; `default.json` is regenerated from the schema every start and **cannot be modified** (`update_config` refuses it) |
| In-game UI without writing one | optional dependency on `Oudstand-ModOptions` (own store `user://mod_options_<id>.json`, signal `config_changed`) or `dami-ModOptions` (renders `config_schema`, signal `setting_changed`, does **not** persist) | both are optional: fall back to defaults when the node is missing |

ModLoaderConfig essentials (6.2.0 and 6.3.0, verified in source):

```gdscript
# mod_main.gd - never in _init(): the user profile entry gets its "current_config" key in ModLoader._ready()
func _ready() -> void:
	call_deferred("_load_config")

func _load_config() -> void:
	var cfg: ModConfig = ModLoaderConfig.get_current_config(MOD_ID)   # null + error "has no config file." on first start
	if cfg == null:
		cfg = ModLoaderConfig.get_default_config(MOD_ID)
	if cfg == null:
		return                                                       # schema invalid -> keep hard-coded defaults
	if cfg.name == ModLoaderConfig.DEFAULT_CONFIG_NAME:              # make a writable copy once
		var user_cfg: ModConfig = ModLoaderConfig.get_configs(MOD_ID).get("user")   # no error log, unlike get_config()
		if user_cfg == null:
			user_cfg = ModLoaderConfig.create_config(MOD_ID, "user", cfg.data.duplicate(true))
		if user_cfg != null:
			ModLoaderConfig.set_current_config(user_cfg)             # persists to mod_user_profiles.json, emits ModLoader.current_config_changed
			cfg = user_cfg
	var defaults: Dictionary = ModLoaderConfig.get_default_config(MOD_ID).data
	for key in defaults:                                             # old user file + new schema key -> "Invalid get index"
		if not cfg.data.has(key):
			cfg.data[key] = defaults[key]
	_apply(cfg.data)

func set_option(key: String, value) -> void:
	var cfg := ModLoaderConfig.get_current_config(MOD_ID)
	cfg.data[key] = value
	if ModLoaderConfig.update_config(cfg) == null:                   # schema validation failed (min/max/enum) or default config
		ModLoaderLog.warning("rejected %s=%s" % [key, str(value)], LOG_NAME)
		return
	emit_signal("settings_changed", key, value)                      # update_config emits nothing itself
```

JSON numbers come back as `float`: cast with `int()`. Every property needs a `default`, else `The default config values for X are invalid. Configs will not be loaded.` Details, schema keys, migration, frameworks' APIs: [references/config-and-settings.md](references/config-and-settings.md).

## 5. Keybinds

```gdscript
const ACTION := "qol_toggle_overlay"      # prefix with your mod; "ui_*"/"move_*" collide with vanilla

func _register_action(scancode: int) -> void:
	if not InputMap.has_action(ACTION):
		InputMap.add_action(ACTION)
	InputMap.action_erase_events(ACTION)
	if scancode > 0:
		var ev := InputEventKey.new()
		ev.scancode = scancode
		InputMap.action_add_event(ACTION, ev)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed(ACTION) and not event.is_echo():     # is_action_pressed already drops echoes
		_toggle_overlay()
		get_tree().set_input_as_handled()
```

- Store binds as `OS.get_scancode_string(code)` ("F9", "Shift+F9"), load with `OS.find_scancode_from_string()`; `0` = unbound. Capture a rebind in `_input`: Esc cancels, Delete/Backspace clears, any other key binds, then `set_input_as_handled()`.
- Default to keys Brotato does not use (F-keys; Combat Tracker ships F8-F11). Space/`ui_accept` and the bottom face button are the shop "buy/go" inputs: a held confirm at wave start fires your action on the first in-wave frame unless you prime the edge state at wave start.
- Gamepad per player: poll `Input.is_joy_button_pressed(raw_device, JOY_*)` with your own rising-edge table and map raw device -> slot via `CoopService.connected_players` (raw 0 -> remapped 6), or register `ACTION + "_" + str(device)` for devices 0-7 like the game. Vanilla's `Utils.is_player_action_pressed(event, player_index, action)` exists; verify its signature in your build before using it.
- Fires twice: `_input()` runs on every level of an extension chain (never call `._input()`), and `_input` + `_unhandled_input` both see unhandled events. Handle in one place and mark handled.

Rebind UI, device table, conflicts, saving: [references/keybinds-translations.md](references/keybinds-translations.md#keybinds).

## 6. HUD overlays

```gdscript
# qol_overlay.gd - one node under /root, survives scene changes
extends CanvasLayer

var _label: Label
var _last_text := ""
var _acc := 0.0

func _ready() -> void:
	layer = 110
	pause_mode = Node.PAUSE_MODE_PROCESS
	_label = Label.new()
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.focus_mode = Control.FOCUS_NONE
	_label.add_font_override("font", load("res://resources/fonts/actual/base/font_26_outline.tres"))
	_label.align = Label.ALIGN_RIGHT
	_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN                     # grow leftwards from the right edge
	_label.set_anchors_and_margins_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_MINSIZE, 16)
	add_child(_label)

func _process(delta: float) -> void:
	_acc += delta
	if _acc < 0.2:                                   # 5 Hz is plenty for text
		return
	_acc = 0.0
	var scene = get_tree().current_scene
	var in_wave: bool = scene != null and scene.filename == "res://main.tscn" and scene.get("_cleaning_up") != true
	visible = in_wave and not get_tree().paused      # hide under pause/level-up/shop menus
	if not visible:
		return
	var text := _build_text()                        # cheap: pre-formatted ints, no per-frame allocation
	if text != _last_text:                           # Label.set_text re-layouts; only on change
		_last_text = text
		_label.text = text
```

`Label` is cheaper than `RichTextLabel` (no BBCode parse); one `_draw()` node beats many labels (`brotato-stability-performance`). Use `Text.get_formatted_number(n)` for Brotato-style numbers. Anchor relative to `UI/HUD/LifeContainerP<n>.get_global_rect()` to sit next to a player's bars; mirror for players whose bars are on the right half.

## 7. Translations

- Shipping `.translation` files: `ModLoaderMod.add_translation("res://mods-unpacked/<ModId>/translations/X.de.translation")` in `_init()`; they must be produced by a Godot 3 editor import of a CSV (`keys,en,de` header) or by `ResourceSaver.save(path, translation)` in a tool script. 6.2.0 passes a null to `TranslationServer` if the file fails to load, 6.3.0 logs fatal: check the path.
- No editor step: parse the CSV at runtime and add `Translation` objects (full loader in the reference). Fill empty cells with the English value yourself.
- Locale matching: a `de` translation serves `de_DE`; a key missing in the matched translation falls through to the project fallback locale, then returns the key itself. Read the player's language with `TranslationServer.get_locale()` (`ProgressData.settings.language` is the saved value); compare with `begins_with("de")`.
- Keys: `MODNAME_SCREAMING_SNAKE`; keep them unique across mods. Use `tr(key)` for strings you build, `Text.text(key, [args])` for Brotato-style placeholders. CJK players: Brotato's fonts (`res://resources/fonts/raw/NotoSans{SC,TC,JP,KR}-Medium.otf`) are what Combat Tracker loads into a `DynamicFont` with fallbacks.

## 8. Persistent data

`user://` = `%APPDATA%\Brotato\` (Windows). Write `path + ".tmp"`, close, then `Directory.new().rename(tmp, path)` (Windows removes the target first; a crash between the two leaves the `.tmp`, so on load fall back to it). Keep a `schema_version` key and migrate on load; validate types (JSON gives floats, ConfigFile keeps types). Never write into `ProgressData` (`ProgressData.save()` is the game's save; its loader is not guaranteed to keep unknown keys and the CrashReporter disables all mods after a save-related error). Patterns and a copy-ready store: [references/config-and-settings.md](references/config-and-settings.md#own-store-configfile).

## 9. Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Settings reset after a mod update | config key renamed, or ModLoaderConfig user file lacks new keys | keep keys stable; merge defaults on load; `schema_version` migration |
| New options tab button invisible or not reachable with bumpers | not registered in `buttons_tab_np`/`buttons_tab`, or inserted after `empty_space_right` | section 3 recipe |
| Focus stuck / nothing selectable after closing your popup | focused control freed; `FocusEmulator` restores a dead reference | restore focus with `Utils.focus_player_control(go_button, i)` before `queue_free()` |
| Keybind triggers twice | `._input()` called, or `_input` and `_unhandled_input` both handle | one handler + `set_input_as_handled()` |
| Label shows `MYMOD_KEY` | translation added after the label was created, wrong locale code, bad path (6.2.0 silently adds null) | add in `_init()`; check `modloader.log` for `Added Translation` |
| UI huge or off-screen on 4K/ultrawide | `OS.window_size` or hard-coded 1920x1080 | logical viewport + anchors (rule 7) |
| HUD stays after the run ends | overlay under `/root` never checks the scene | gate on `current_scene.filename == "res://main.tscn"` and `_cleaning_up` |
| Clicks on your overlay reach the game, or never arrive in co-op | input picking by tree order; `FocusEmulator` eats mouse events | last child of `/root` + own `_input` routing |

## 10. Checklist: one QoL option end to end

- [ ] Setting: key, type, default, min/max, `schema_version` bump if the shape changed; is it local or host-authoritative?
- [ ] Store: one owner (ConfigFile or ModLoaderConfig), merged defaults on load, atomic save, debounce.
- [ ] Apply: one `settings_changed` signal; every consumer refreshes from it; works without restart.
- [ ] UI: widget in your tab, Brotato theme/font, `FOCUS_ALL` + `focus_neighbour_*`, label is a translation key, tested with mouse, keyboard and a pad in a 2-player local run.
- [ ] Keybind (if any): mod-prefixed action, unbound-by-default or an F-key, rebind UI, saved as scancode string, respects player device.
- [ ] Translation: `en` + `de` rows added in `_init()`; no raw key visible in either language.
- [ ] Co-op (online mod): host sends the value in the run config; clients restore their own value when the session ends.
- [ ] Cleanup: nodes removed or hidden on scene change; nothing survives into the shop/next run; no `ERROR` lines in `godot.log`.

## References

- [references/menus-and-hooks.md](references/menus-and-hooks.md) - verified scene tree of every menu, vanilla widgets and themes, CanvasLayer/input/focus mechanics, widget-building code. Read before touching any menu or HUD.
- [references/config-and-settings.md](references/config-and-settings.md) - ModLoaderConfig lifecycle and API traps, config_schema keys, own ConfigFile store, migration, Oudstand-ModOptions and dami-ModOptions APIs, co-op sync. Read when adding or changing a setting.
- [references/keybinds-translations.md](references/keybinds-translations.md) - InputMap recipes, Brotato device model, rebind UI, translation file formats and runtime CSV loader, persistent-data rules. Read for keybinds, text or save files.
- [references/common-issues.md](references/common-issues.md) - symptom -> cause -> fix.
- [references/sources.md](references/sources.md) - what each fact is based on (accessed 2026-10-08).
