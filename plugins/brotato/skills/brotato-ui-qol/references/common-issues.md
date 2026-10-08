# UI, settings, keybind, translation and save issues: symptom -> cause -> fix

Versions: Brotato 1.1.15.x (Godot 3.7-dev), Mod Loader 6.2.0/6.3.0. Exact engine/Mod Loader messages are quoted; "reported" rows come from mod authors' comments and changelogs, not from this skill's own tests. Mod-load failures, extension errors and crashes are in `brotato-modding` and `brotato-stability-performance`.

## Settings and config

| Symptom / message | Cause | Fix |
|---|---|---|
| Settings reset to defaults after updating the mod | option ids or registration id renamed; ModLoaderConfig user file missing new keys; store file moved | keep ids stable, merge defaults on load, `schema_version` migration, never rename the ModOptions registration id |
| `Mod "<id>" has no config file.` in `modloader.log` | `ModLoaderConfig.get_current_config` called before `ModLoader._ready()` wrote `current_config` into the profile (first start), or no `config_schema` | read deferred from `_ready()`, fall back to `get_default_config`; 6.2.0 logs it once during startup regardless (harmless) |
| `The default config values for <ns>-<name> are invalid. Configs will not be loaded.` | a schema `default` violates its own `minimum`/`maximum`/`enum`/type, or a property has no `default` | fix the schema; every property needs a valid `default` |
| `The "default" config cannot be modified. Please create a new config instead.` | `update_config` on the default config | `create_config(MOD_ID, "user", default.data.duplicate(true))` + `set_current_config` once, update that |
| `Update for config "user" failed validation with error message "..."` | value outside schema constraints, wrong type (string for number), `multipleOf` mismatch after float math | clamp/round before writing; use `stepify(v, step)` |
| `Invalid get index 'new_key' (on base: 'Dictionary')` | old user config lacks a key added in the new schema | merge defaults into `cfg.data` on load |
| `Failed to create config "user". A config with the name "user" already exists.` | `create_config` every start | `get_config(MOD_ID, "user")` first |
| Value is `2.0` instead of `2`, `if v == 2` false | JSON numbers parse as float | `int(v)`; compare with `is_equal_approx` for floats |
| Config edits in dami-ModOptions do not survive a restart | that mod only emits `setting_changed`; nothing persists | write the value yourself in the handler |
| Oudstand ModOptions values not applied at startup | `register_mod_options` loads saved values but emits no `config_changed` | read with `get_value` right after registering |
| "ModOptions manager not found" / your options never show | the framework loads after you, or is absent | `call_deferred` + retry with a 0.2 s timer up to 5 times; fall back to defaults |
| Slider drag spams disk writes / stutters | save on every `value_changed` | debounce (0.5 s timer) and `save_if_dirty` |
| Settings file empty after a crash | `File.WRITE` truncates before the content is written | temp file + rename; load `.tmp` as fallback |
| `ConfigFile.load` returns 7 (`ERR_FILE_NOT_FOUND`) | first start | normal: defaults apply |
| Window/overlay saved on a 4K monitor is off-screen on 1080p | absolute position persisted | clamp into `get_viewport().get_visible_rect()` on load and after resize |

## Options menu and widgets

| Symptom | Cause | Fix |
|---|---|---|
| New tab button invisible | inserted after `empty_space_right` (pushed out), or visible=false copied from a hidden template | insert at `get_child_count() - 2` with `add_child_below_node`; set `visible = true`, `disabled = false` |
| Tab button present but bumpers (LB/RB) skip it | not pushed into `Buttons.buttons_tab` / `buttons_tab_np` | push both; keep the order equal to the TabContainer child order |
| Pressing the tab button shows another tab | index passed to `_change_tab` differs from the TabContainer child index | compute the index from `tab_container.get_child_count()` after adding your tab |
| Tab appears on the title screen but not in the pause menu (or vice versa) | the two screens hold separate `MenuOptions` instances | add it from both `title_screen.gd` and `pause_menu.gd` extensions |
| Controls duplicated each time the menu opens | re-adding without a `has_node(NAME)` guard | fixed node names + guard |
| Two mods both replace `menu_options.tscn` | both `take_over_path` the scene; last loader wins | use script extensions and node injection instead; declare `incompatibilities` if you must override |
| Your `CheckButton`/`Label` is twice as big as vanilla rows | theme default font | copy the neighbour's font (`get_font("font")`) or load a 22-30 px `font_*.tres` |
| `toggled` fires during build and saves the default | `pressed` set after `connect` | set `pressed` first, connect after |
| Slider shows `50%` for an integer option | `SliderOption._on_HSlider_value_changed` formats percent | disconnect it and format yourself |
| Dropdown cannot be navigated with a pad in co-op (reported) | FocusEmulator does not scroll `PopupMenu` | cycling button instead of `OptionButton`, or Oudstand's `_handle_popup_menu_input_custom` approach |
| `Parent node is busy setting up children, add_node() failed...` | `add_child` inside `_ready` chain of the menu | `call_deferred("add_child", node)` |
| Settings tab blank for pad users, mouse works | controls have `focus_mode = FOCUS_NONE` or no `focus_neighbour_*` | `FOCUS_ALL`, wire neighbours, `ScrollContainer.follow_focus = true` |

## Focus, input, pause

| Symptom / message | Cause | Fix |
|---|---|---|
| Focus stuck: nothing selectable after closing a popup / rebuilding a tab | FocusEmulator keeps a reference to the freed control (`previously freed instance` errors in `focus_emulator.gd`, reported) | before `queue_free()`, `Utils.focus_player_control(target, i)` for each player; never free the focused control without moving focus |
| Crash opening Options in co-op: `Attempt to call function 'grab_focus' in base 'null instance'` (reported, 1.1.15) | vanilla `menu_options.init()` / `_on_BackButton_pressed` dereferences `focus_before_created` | Oudstand-FocusFix guards both; tell players to install it, or guard in your own extension |
| Closing your popup with Esc also opens the pause menu | the Esc **release** reached the game | keep consuming input until all `ui_cancel`/`ui_pause` (`_<d>` variants too) are released, then unpause and free |
| Popup does not react while the game is paused | `pause_mode` INHERIT -> STOP | `pause_mode = Node.PAUSE_MODE_PROCESS` on the popup root |
| Game keeps running under your "modal" popup | you never paused | `get_tree().paused = true`, parent `PAUSE_MODE_STOP` |
| Clicks go through your overlay to the game | input picking by tree order; CanvasLayer order irrelevant | overlay last under `/root` (re-move on scene change) or `_input` routing + `set_input_as_handled()` |
| Overlay gets no mouse at all in co-op | `FocusEmulator._input` marks mouse events handled | route in `_input()` yourself (runs before GUI) |
| Mouse cursor invisible over your window during a wave | the game hides the cursor in battle | `Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)` while the window is open |
| Keybind triggers twice | `._input()` called in an extension; `_input` + `_unhandled_input`; base + per-device actions both matched | single handler, mark handled |
| Keybind fires when the wave starts | the shop "go" key is still held | prime edge state at wave start |
| Rebind captured the key but the game also reacted | capture did not consume release | consume press and release while capturing |
| Pad does nothing in your menu | Godot focus with `ui_accept`; Brotato uses `ui_accept_<device>` through FocusEmulator | `FOCUS_ALL` + neighbours; for custom handling read `ui_*_<device>` actions |
| P2's pad controls P1's feature | slot taken from `connected_players[i][1]` or raw device id | slot = array index; raw pad 0 -> remapped 6; keyboard -> 7 |
| `InputMap already has action "qol_x".` | registered twice (re-init, two mods using the same name) | `has_action` guard; mod-prefixed names |

## HUD and overlays

| Symptom | Cause | Fix |
|---|---|---|
| HUD stays after the run ends / shows in the shop or menu | overlay under `/root` without scene gating | gate on `current_scene.filename == "res://main.tscn"`, `_cleaning_up`, `get_tree().paused`; hide in shop unless intended |
| Overlay drawn over the pause menu / level-up cards and eats their clicks | `layer` 100+ with `mouse_filter` STOP | layer 3-5 to sit with the HUD, or hide while paused/level-up (`UpgradesUI` visible) |
| Overlay hidden behind the game | `layer` lower than the game's HUD/menus, or node under `Main` without CanvasLayer | own `CanvasLayer`, pick layer (menus-and-hooks.md) |
| Text misplaced at 4K / ultrawide / vertical monitors | absolute pixels from `OS.window_size` or hard-coded 1920x1080 | anchors + `get_visible_rect().size`; `Utils.project_width/height` |
| Overlay blurry or tiny on 4K | not scaled | `rect_scale` from a UI-scale setting; cache one `DynamicFont` per size |
| FPS drop with the overlay on | `Label.text` set every frame, `RichTextLabel` BBCode re-parse, `get_nodes_in_group` per frame | update only on change at 4-10 Hz; one `_draw()` node for many rows |
| `Attempt to call function 'get_global_rect' in base 'previously freed instance'` | cached `LifeContainerP<n>` from the previous `Main` | re-resolve per scene; `is_instance_valid` |
| Damage/ping values freeze after a scene change | signals connected to the old `Main`/`WaveTimer` | reconnect on each attach; `is_connected` guard |
| Overlay node added twice per run | `_enter_tree()`/`_ready()` of an extension runs again when the scene is re-instanced | `has_node(NAME)` or a per-instance flag |
| Co-op HUD element for P3/P4 in the wrong place | all players laid out like P1 | mirror by the container's global rect (right half -> right-aligned, bottom players reversed order) |

## Translations

| Symptom / message | Cause | Fix |
|---|---|---|
| Label shows `QOL_SHOW_PING` | key missing in that locale, translation registered after the label existed, typo in key | add translations in `_init()`; fill empty cells with English; grep the CSV |
| Everything English although the game is German | `Translation.locale` is `de_DE`/`DE` instead of `de`, or CSV header wrong | locale codes `en`, `de`; header `keys,en,de` |
| `Tried to load a translation resource from a file that doesn't exist. The invalid path was: ...` (fatal) | wrong path/case in `add_translation` | path from `ModLoaderMod.get_unpacked_dir().plus_file(MOD_ID)`; case-sensitive in zips |
| No error but keys unresolved (6.2.0) | `load()` of the `.translation` returned null (not imported, wrong file) and `add_translation(null)` was called | ship real `.translation` files or use the runtime CSV loader; check `Added Translation from Resource` with `--log-info` |
| `No loader found for resource: ....csv` | `load()` on a CSV | read it with `File`; CSVs are not resources in an exported game |
| Umlauts garbled | CSV saved as ANSI/with BOM | UTF-8 without BOM; `get_as_text()` assumes UTF-8 |
| Text does not change when switching language in Options | you built strings with `tr()` once | rebuild on `NOTIFICATION_TRANSLATION_CHANGED`; set keys as `text` so Controls re-translate themselves |
| Another mod's text changed | both registered the same key (`RESET`, `SETTINGS`) | mod-prefixed keys |
| Chinese/Japanese shows boxes in your custom `DynamicFont` | no CJK fallback data | add Brotato's `NotoSans*-Medium.otf` as fallbacks |

## Persistent data

| Symptom / message | Cause | Fix |
|---|---|---|
| `Error parsing JSON` / config dictionary empty | corrupt file (crash mid-write, hand edit) | temp+rename; fall back to `.tmp`, then defaults; never overwrite a corrupt file with defaults silently - back it up as `.bad` |
| File saved but values missing | `JSON.print` of `Vector2`/`Color`/objects | serialise to arrays/strings |
| Save works in the editor, not in the game | wrote to `res://` | `user://` only (mounted zips are read-only) |
| Stutter at wave end | synchronous multi-MB write | aggregate, write small summaries, chunk logs |
| Player progress corrupted / "Mods have been temporarily disabled" after your mod wrote into `ProgressData` | invalid value in the game's save, error logged with your mod path | do not write `ProgressData`; if unavoidable, primitives only under one namespaced key, mirrored in your own file |
| Settings shared between Steam accounts on the same PC | `user://` is per OS user, not per Steam account | key your file by `Steam.getSteamID()` if that matters (online mod) |
