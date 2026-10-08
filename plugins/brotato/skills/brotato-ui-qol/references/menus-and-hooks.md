# Brotato menus, HUD and UI mechanics (1.1.13.1-1.1.15.4)

Every path and member below was read from public mods that run on these versions (Oudstand ModOptions/DamageMeter/FocusFix, dami-ModOptions, tato-Synergies, DPSLove Combat Tracker, Mojimoon AutoAnthony, auto-brotato docs). Private members (`_x`) and container names move between patches: open the decompiled scene of the installed version before relying on a path, and wrap every lookup in `get_node_or_null`.

## Contents
- Scene tree per screen
- Vanilla widgets, themes, fonts, icons you may reuse
- CanvasLayer, draw order and mouse picking
- Focus: Godot focus vs Brotato's FocusEmulator
- Pause and popups
- Resolution, scaling, ultrawide
- Autoload vs per-scene UI
- Building settings widgets (code)

## Scene tree per screen

### Title screen and options menu

```
TitleScreen (res://ui/menus/title_screen/title_screen.tscn, script title_screen.gd)
└── Menus
    └── MenuOptions (MarginContainer, res://ui/menus/pages/menu_options.tscn, script menu_options.gd)
        └── Buttons                      # script = tab controller
            ├── HBoxContainer2           # tab buttons, all MyMenuButton with toggle_mode
            │   ├── (spacer)             # index 0
            │   ├── Audio_but  (%Audio_but)
            │   ├── Visual_but
            │   ├── Gameplay_but
            │   ├── Accessibility_but
            │   └── empty_space_right    # always last -> insert before it
            ├── HBoxContainer3
            │   └── TabContainer         # one child per tab, in button order
            │       ├── Audio_Container
            │       ├── ... 
            │       └── Accessibility_Container
            │           └── AccessibilityContainer   # VBoxContainer of CheckButtons (CharacterHighlightingButton, DarkenScreenButton, ...), colour pickers
            └── HBoxContainer
                └── BackButton (%BackButton)
```

- `Buttons` script members used by mods: `buttons_tab_np: Array` (NodePaths, exported in the scene), `buttons_tab: Array` (Button refs), `tab_container: TabContainer`, `_change_tab(index: int)`, `lb_texture` / `rb_texture` (bumper prompts with `player_index`). Bumper cycling iterates `buttons_tab`, so a tab button not pushed there is unreachable on a pad.
- `menu_options.gd` members: `init()` (called when the menu opens; FocusFix overrides it), `is_in_a_run: bool`, nodes in group `hide_in_run` are hidden in the pause-menu instance, `focus_before_created`, `init_values_from_progress_data()`, `adjust_buttons_font_size()`, `video_container`, `audio_container`, `all_check_buttons`, `_on_BackButton_pressed()`, signal `back_button_pressed`. Vanilla options read/write `ProgressData.settings` (`volume.master/sound/music`, `language`, `background`, `visual_effects`, `screenshake`, `fullscreen`, `damage_display`, `optimize_end_waves`, `limit_fps`, `mute_on_focus_lost`, `on_lost_focus`, `color_positive`, `tier_0_color`.., `main_screen_keyart`, `deactivated_dlc_tracks`, plus `manual_aim`, `pause_on_focus_lost`).
- The pause menu (`res://ui/menus/ingame/pause_menu.gd`) holds its own instance as `_menu_options`; `main.gd` holds the pause menu as `_pause_menu` (`enabled` flag). Anything you add to the title-screen instance must be added again in the pause-menu instance.
- Mod-made tabs seen in the wild: dami-ModOptions duplicates the last tab button and appends a `ScrollContainer` tab from both `title_screen.gd` and `pause_menu.gd` extensions (SKILL.md section 3). Oudstand ModOptions instead ships a modified copy of `menu_options.tscn` and `take_over_path`s it from `mod_main` (`call_deferred("_install_scene_overrides")`) - a full-scene replacement that conflicts with any other mod doing the same, so prefer the extension route for your own mod.

### Character / weapon selection

- Scene name `CharacterSelection` (`res://ui/menus/run/character_selection.gd`), weapon selection reuses `character_panel_ui.tscn` as `.../DescriptionContainer/CharacterPanelUI`.
- Run options panel: `MarginContainer/VBoxContainer/DescriptionContainer/RunOptionsPanel/MarginContainer/VBoxContainer/VBoxContainer` with `CheckButton`s `EndlessButton`, `BanButton`, `CoopButton`, `ZoneSelectionButton`. Authoritative state is in `RunData` (`is_endless_run`, `is_ban_mode_active`, `is_coop_run`), not the buttons. The panel exists only while the selection screen is open; the grid is rebuilt when co-op is toggled (re-scan when child count changes).
- Co-op character panels `.../DescriptionContainer/HBoxContainer/Panel1..4`, description content under `vboxContainer/character_infos_container/right_panel/ScrollContainer/MarginContainer/VBoxContainer` (Synergies injects a card there and copies the passive-label font).

### Shop

- `base_shop.gd` (shared by `shop.gd` and `coop_shop.gd`): `_get_reroll_button(player_index)`, `_get_go_button(player_index)`, `%ShopItemsContainer`, `%GearContainer`, `%RerollButton`, `%GoButton`, `%ItemPopup`, signals `shop_item_bought`, `shop_item_insufficient_currency`.
- Adding a button next to reroll (Oudstand DamageMeter): `Button.new()` with `focus_mode = FOCUS_ALL`, insert with `move_child(btn, reroll.get_index() + 1)`, match height deferred, then rewire `reroll.focus_neighbour_right = reroll.get_path_to(btn)`, `btn.focus_neighbour_left`, inherit reroll's old right/top/bottom neighbours, fall back to the Go button for bottom. Without this the pad cursor can never reach your button.
- A popup opened from the shop: instance it as a child of the shop node (so it dies with the shop), restore focus with `Utils.focus_player_control(shop._get_go_button(i), i)` for every player before freeing it.

### Battle scene and HUD

- `/root/Main` (`res://main.tscn`): `UI/HUD` (member `_hud`), `UI/HUD/LifeContainerP1..4` (BoxContainer per player: HP bar, XP bar, gold, weapons; `custom_constants/separation` adjustable), `UI/UpgradesUI`, `WaveTimer`, `EntitySpawner`, `Camera`.
- HUD scripts you can extend to piggyback on HUD lifecycle: `res://ui/hud/ui_wave_timer.gd` (DamageMeter extends it to get `_process` and `onready` access to `UI/HUD`).
- P1/P2 bars are top-left/top-right, P3/P4 bottom; a player whose container centre is on the right half gets mirrored layouts (`Label.ALIGN_RIGHT`, `TextureProgress.FILL_RIGHT_TO_LEFT`). Co-op HUD elements use 0.75 alpha, solo 1.0.
- HP bar textures reusable for your own bars: `res://ui/hud/ui_lifebar_frame.png`, `ui_lifebar_bg.png`, `ui_lifebar_fill.png` (`TextureProgress` with `tint_progress`).
- Wave state: `main._cleaning_up == true` once the wave ends; `scene.has_signal("end_of_the_wave")` is another battle-scene test used by Combat Tracker. The shop scene's `filename` contains `shop`.
- `InputService.hide_mouse` / the game hides the cursor during waves and re-applies its rule every frame; if your window needs the cursor, set `Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)` while it is open (no restore needed).

### Level-up, end of run, difficulty

- `/root/Main/UI/UpgradesUI` (`upgrades_ui.gd`): `UpgradesUIPlayerContainer{1..4}` (`player_index`, `_upgrade_ui_1..4`, `_reroll_button`, `_take_button`, `_discard_button`, `_ban_button`), cards `UpgradeUI`, `UpgradeUI2..4` (`upgrade_data`), choose button `MarginContainer/VBoxContainer/ChooseButton` (`my_menu_button.gd`, text `MENU_CHOOSE`).
- `/root/EndRun` (`end_run.gd`, co-op `coop_end_run.gd`, strings in `base_end_run.gd`): `%Title`, `MarginContainer/VBoxContainer/HBoxContainer3/{RestartButton,NewRunButton,ExitButton}` (texts `MENU_RESTART`, `MENU_NEW_RUN`, `MENU_RETURN_MAIN`), `StatsContainer`; result in `RunData.run_won`.
- `/root/DifficultySelection`: `.../ScrollContainer/Inventories/Inventory1` of `InventoryElement`s (`item.my_id == "difficulty_0..6"`, `is_locked`), signals `element_pressed`/`element_focused`; pressing an element starts the run immediately (`change_scene`), there is no `run_started` signal.

## Vanilla widgets, themes, fonts, icons you may reuse

| Resource | Use |
|---|---|
| `res://resources/themes/base_theme.tres` | `theme` of your root Control (Mojimoon popups, Oudstand summary) |
| `res://resources/themes/tab_buttons_physic.tres` | theme of tab buttons; `res://resources/themes/button_styles/button_hover.tres` for `custom_styles/hover_pressed` |
| `res://ui/menus/global/slider_option.tscn` (`SliderOption`) | `_label`, `_slider` (HSlider), `_value` (Label), `set_value(v)`, signal `value_changed(value)`; it formats the value as percent via `_on_HSlider_value_changed` - disconnect that and connect your own formatter for plain numbers |
| `res://ui/menus/global/color_option.tscn` | `button_expand.text`, `_init_color(Color)`, signal `color_changed(Color)` |
| `res://ui/menus/global/my_menu_button.gd` (`MyMenuButton`) | hover/press sounds; assign as `script` to a `CheckButton`/`Button` you create |
| `InfoPopup` (vanilla class) | tooltip panel: `display(element, text)`, `_panel`, `DIST`; place it on a `CanvasLayer` above the tab |
| Fonts `res://resources/fonts/actual/base/font_22.tres`, `font_26.tres`, `font_26_outline.tres`, `font_32_outline.tres`, `font_40_outline.tres`, `font_very_smallest_text.tres` | `add_font_override("font", load(path))`; `FONT.duplicate()` then `.size = 24` for a custom size (DynamicFont) |
| Raw fonts `res://resources/fonts/raw/NotoSans{SC,TC,JP,KR}-Medium.otf` | build a `DynamicFont` with `font_data` + `add_fallback()` and `outline_size` for CJK-safe self-drawn text (Combat Tracker) |
| Icons `res://ui/menus/global/mods_icon.png`, `video_icon.png`, `res://ui/icons/misc/weapon_icon.png`, `ItemService.get_icon(hash)` | button icons; your own PNGs need `.import` + `.stex` in the zip or byte loading (`brotato-modding`) |
| `Text.text(key, [args])`, `Text.get_formatted_number(n)`, `ItemService.get_color_from_tier(tier)`, `CoopService.get_player_color(i)` | Brotato-style formatting and colours |

Default sizes: a `Label` or `CheckButton` created in code uses the theme default and looks about twice as large as vanilla rows (Synergies and Oudstand both copy the font from a neighbouring control or set 24-30 px).

## CanvasLayer, draw order and mouse picking

- `CanvasLayer.layer`: lower draws behind. Observed values: Synergies HUD 3 (sinks behind pause/shop menus like the life bar), char-select card 20, dami tooltip 10 (inside the tab), Mojimoon popups 100, Combat Tracker 110 (+1 for tooltips), test overlays 105. Pick 3-5 for "part of the HUD", 100+ for "always on top".
- `CanvasLayer.visible = false` hides everything under it without propagating to other layers; cheaper than toggling many controls.
- **Mouse picking ignores `layer`.** Godot 3 walks the tree to find the control under the cursor, so a full-screen container of the current scene receives the click first unless your layer is later in the tree. In co-op the game's `FocusEmulator._input` marks mouse events handled before GUI dispatch.
- Combat Tracker's robust solution: `CanvasLayer` added to `/root` and moved to the last index after every scene change (`root.move_child(ui, root.get_child_count() - 1)` from a per-frame scene-instance check), all windows `mouse_filter = IGNORE`, `_input()` routes `InputEventMouse` to its own hit rects, consumes only what it uses (`get_tree().set_input_as_handled()`), passes motion through so the game's aim cursor keeps working.
- Node order matters for `_input`: later siblings get `_input` first (reverse tree order), which is why "last child of root" wins.
- A `Node2D` overlay in world space (debug drawing that follows the camera) goes under `/root/Main` with a high `z_index` and is freed with `Main` (auto-brotato).

## Focus: Godot focus vs Brotato's FocusEmulator

- Solo keyboard/mouse: standard Godot focus works (`grab_focus()`, `focus_neighbour_*`, `ui_accept`).
- Any pad, and all of co-op: one `FocusEmulator` per player (`res://ui/menus/global/focus_emulator.gd`, `Utils.get_focus_emulator(player_index)`) tracks `focused_control`, `player_index`, `_device`, `_focused_parent`, `_focused_control_index`; it reads `ui_*_<device>` actions in `_handle_input(event) -> bool`, calls `_get_focus_neighbour_for_event(event, control)`, `_set_focused_control_with_style(control, false)`, `_press_button(control)`, and emits via `FocusEmulatorSignal.emit(control, "pressed"|"toggled"|"focus_entered"|"focus_exited"|"id_pressed", player_index, ...)`. Godot's own `ui_accept` never fires from a pad in these menus.
- A control is a candidate only if `focus_mode == FOCUS_ALL` and `is_visible_in_tree()`. Set `focus_neighbour_*` explicitly on injected controls; the emulator's best-guess search is unreliable across containers.
- `Utils.focus_player_control(control, player_index)` moves that player's cursor; `Utils.is_maybe_action_pressed(event, "ui_accept_%s" % device)` is the game's own tolerant check.
- Vanilla bug reported by Oudstand (1.1.15): when the focused control is freed (e.g. you rebuilt a tab), the emulator restores a dead reference and errors. Their fix: validate `focused_control`/`_focused_parent` with `is_instance_valid` + `is_queued_for_deletion()` and fall back to the first visible `Button`. Oudstand-FocusFix also guards `menu_options.init()` (`Utils.get_focus_emulator(0)` null) and `_on_BackButton_pressed()` (`focus_before_created` null). Treat these as "known to crash; guard before freeing focused controls".
- `OptionButton` dropdowns: the popup is a `PopupMenu` modal; in co-op the emulator does not scroll it, Oudstand overrides `_handle_input` to step `set_current_index` and scrolls the inner `ScrollContainer` manually. Prefer cycling buttons over dropdowns for pad users.
- A `LineEdit`/`TextEdit` with focus swallows `ui_*` keys; release focus on Enter/Esc or the player cannot navigate.

## Pause and popups

- Default `pause_mode` under `/root` is `INHERIT` which behaves as `STOP` when `get_tree().paused` is true. Overlays that must animate or accept input under the pause menu set `pause_mode = Node.PAUSE_MODE_PROCESS` (Combat Tracker, Synergies settings injector).
- Popup that pauses the game (Oudstand wave summary): on `_ready` remember `parent.pause_mode`, set it to `PAUSE_MODE_STOP`, `get_tree().paused = true`, own `pause_mode = PROCESS`, consume all key/pad events in `_input`. On close: hide, keep processing until no `ui_cancel`/`ui_pause` (any device suffix) is still held, then unpause, restore the parent's pause mode, restore shop focus, `queue_free()`. Skipping the "wait for release" step makes the Esc release open the pause menu.
- `get_tree().create_timer(t)` keeps running while paused unless you pass `false` as the second argument.
- In online play, never pause the tree from a client (`brotato-online-multiplayer`).

## Resolution, scaling, ultrawide

- Engine facts (Godot 3.x `SceneTree::_update_root_rect`): with stretch mode `2d` the root viewport size is the window in pixels and a size override holds the logical resolution; `aspect = expand` grows the logical width/height on non-16:9 screens. `get_viewport().get_visible_rect().size` and `get_viewport().get_size_override()` give the logical size; `OS.window_size` gives physical pixels.
- Brotato: FullMapCamera's verification matrix lists logical viewports 1920x1080, 1280x1024, 3440x1440, 1440x2560, 320x180, so the game uses expand-style stretching; mods read `Utils.project_width` / `Utils.project_height` (dami-ModOptions tooltip) for the design size. Combat Tracker scales its UI by 1.3 x user scale relative to a 1080p design and clamps windows into the visible rect.
- Consequences: anchor with presets (`set_anchors_and_margins_preset(Control.PRESET_TOP_RIGHT, ...)`), size panels by `rect_min_size` + containers, offer a UI-scale slider (0.5-2.5) applied as `rect_scale` on your root window and re-clamp into `get_visible_rect()`, and never store absolute positions without clamping them on load (window positions saved on a 4K monitor are off-screen on 1080p).
- Fonts: do not scale `DynamicFont.size` per frame; cache one font per size.

## Autoload vs per-scene UI

| Lifetime | Where | How |
|---|---|---|
| Whole session (overlay, settings, net UI) | child of `/root` or of your mod main (`/root/ModLoader/<ModId>`) | `get_tree().root.call_deferred("add_child", layer)` from `mod_main._ready()`; poll `get_tree().current_scene` (instance id change) to attach/detach per scene |
| One battle | child of `/root/Main` or `UI/HUD/...` | `main.gd` extension `_enter_tree()`/`_ready()`; freed automatically with `Main` |
| One menu instance | child of that menu | extension `_ready()` with `call_deferred`; `has_node(NAME)` guard; re-added when the menu is re-instanced |

Never keep references to per-scene nodes in a session-long node without `is_instance_valid` (`brotato-stability-performance`).

## Building settings widgets

```gdscript
# Inside your tab scene/script. `store` = your settings object (see config-and-settings.md).
const FONT_26 := "res://resources/fonts/actual/base/font_26.tres"
const SLIDER := "res://ui/menus/global/slider_option.tscn"
const MENU_BUTTON := "res://ui/menus/global/my_menu_button.gd"

func _toggle(id: String, label_key: String) -> CheckButton:
	var cb := CheckButton.new()
	cb.name = id
	cb.set_script(load(MENU_BUTTON))                 # click/hover sounds like vanilla
	cb.text = label_key                              # translated by set_text
	cb.add_font_override("font", load(FONT_26))
	cb.focus_mode = Control.FOCUS_ALL
	cb.pressed = bool(store.get_value(id))           # set BEFORE connecting, or toggled fires now
	cb.connect("toggled", self, "_on_toggled", [id])
	return cb

func _on_toggled(pressed: bool, id: String) -> void:
	store.set_value(id, pressed)

func _slider(id: String, label_key: String, min_v: float, max_v: float, step: float, as_int: bool) -> Control:
	var row = load(SLIDER).instance()
	row.name = id
	row._label.text = label_key
	row._slider.min_value = min_v
	row._slider.max_value = max_v
	row._slider.step = step
	row.set_value(float(store.get_value(id)))
	if as_int:                                       # vanilla formats "%"; replace it
		row._slider.disconnect("value_changed", row, "_on_HSlider_value_changed")
		row._slider.connect("value_changed", self, "_on_int_slider", [row, id])
		row._value.text = str(int(row._slider.value))
	else:
		row.connect("value_changed", self, "_on_float_slider", [id])
	return row

func _on_int_slider(value: float, row, id: String) -> void:
	row._value.text = str(int(value))
	store.set_value(id, int(value))                  # store debounces the disk write

func _on_float_slider(value: float, id: String) -> void:
	store.set_value(id, value)

func _choice(id: String, label_key: String, choices: Array) -> Control:   # cycling button: pad-friendly, no PopupMenu
	var btn := Button.new()
	btn.name = id
	btn.focus_mode = Control.FOCUS_ALL
	btn.add_font_override("font", load(FONT_26))
	btn.set_meta("choices", choices)
	_refresh_choice(btn, id, label_key)
	btn.connect("pressed", self, "_on_choice", [btn, id, label_key])
	return btn

func _on_choice(btn: Button, id: String, label_key: String) -> void:
	var choices: Array = btn.get_meta("choices")
	var i: int = (choices.find(store.get_value(id)) + 1) % choices.size()
	store.set_value(id, choices[i])
	_refresh_choice(btn, id, label_key)

func _refresh_choice(btn: Button, id: String, label_key: String) -> void:
	btn.text = "%s: %s" % [tr(label_key), tr(str(store.get_value(id)))]
```

Wire vertical navigation once after building: for each consecutive pair set `a.focus_neighbour_bottom = a.get_path_to(b)` and `b.focus_neighbour_top = b.get_path_to(a)` (use the `HSlider` inside a `SliderOption` as the focus node). Put the rows in a `ScrollContainer` with `follow_focus = true` so pad navigation scrolls.
