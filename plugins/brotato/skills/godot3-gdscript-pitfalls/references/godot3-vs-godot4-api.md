# Godot 3 <-> Godot 4 rename table

Left column is what to write in a Godot 3 project (Brotato). Right column is the Godot 4 name that must **not** appear. Extends the table in SKILL.md.

## Contents
- Keywords and syntax
- Global functions
- Classes
- Node / Control / CanvasItem members
- OS, Engine, servers
- Input
- Physics queries
- Strings, arrays, dictionaries
- Files, JSON, resources
- Project and scene file formats

## Keywords and syntax

| Godot 3 | Godot 4 |
|---|---|
| `export var x = 1`, `export(Texture) var t`, `export(int, FLAGS, "A", "B") var f` | `@export`, `@export_flags(...)` |
| `onready var n = $N` | `@onready` |
| `tool` | `@tool` |
| `remote func f()`, `remotesync`, `master`, `puppet`, `rpc("f")`, `rpc_id(id, "f")`, `rpc_unreliable("f")`, `rset("v", x)` | `@rpc(...)`, `f.rpc()`, `f.rpc_id(id)` |
| `var v setget set_v, get_v` (setter not triggered by `v = x` inside the same script unless `self.v = x`) | `var v: set = ..., get = ...` |
| `.method(args)`; `func _init(a).(a):` | `super.method(args)`; `super(a)` |
| `yield(obj, "signal")`, `yield(fn(), "completed")` | `await obj.signal`, `await fn()` |
| `funcref(obj, "m")`, `obj.call("m", a)`, `obj.callv("m", [a])` | `Callable(obj, "m")`, `obj.m.call(a)` |
| `class_name Foo, "res://icon.svg"` | `class_name Foo` + `@icon(...)` |
| `enum E {A, B}` (same) | same |
| `match x:` with `_:` default (same) | same |
| no lambdas, no typed arrays, no `static var`, no `@abstract` | exist in 4.x |

## Global functions

| Godot 3 | Godot 4 |
|---|---|
| `rand_range(a, b)` | `randf_range(a, b)` |
| `stepify(v, s)` | `snapped(v, s)` |
| `deg2rad`, `rad2deg` | `deg_to_rad`, `rad_to_deg` |
| `linear2db`, `db2linear` | `linear_to_db`, `db_to_linear` |
| `range_lerp(v, a, b, c, d)` | `remap(...)` |
| `str2var`, `var2str`, `bytes2var`, `var2bytes`, `inst2dict`, `dict2inst` | `str_to_var`, `var_to_str`, `bytes_to_var`, `var_to_bytes`, `inst_to_dict`, `dict_to_inst` |
| `to_json(v)`, `parse_json(s)`, `validate_json(s)` | `JSON.stringify`, `JSON.parse_string` |
| `ColorN("red")`, `Color8(r, g, b)` | `Color("red")`, `Color8(...)` |
| `deep_equal(a, b)` (3.5+) - `==` on two `Dictionary` values compares references in 3.x | `==` compares dictionaries by content |
| `is_nan`, `is_inf` (no `is_finite`) | `is_finite` added |
| `printraw`, `prints`, `printt`, `print_debug` | same names |

## Classes

| Godot 3 | Godot 4 |
|---|---|
| `KinematicBody2D` / `KinematicBody` | `CharacterBody2D` / `CharacterBody3D` |
| `Spatial`, `MeshInstance`, `Area`, `RigidBody`, `Camera`, `CollisionShape` | `Node3D`, `MeshInstance3D`, `Area3D`, `RigidBody3D`, `Camera3D`, `CollisionShape3D` |
| `Sprite`, `AnimatedSprite` | `Sprite2D`, `AnimatedSprite2D` |
| `Position2D`, `Position3D` | `Marker2D`, `Marker3D` |
| `Light2D` | `PointLight2D` |
| `YSort` | `Node2D.y_sort_enabled` |
| `Particles2D` / `CPUParticles2D` | `GPUParticles2D` / `CPUParticles2D` |
| `VisibilityNotifier2D`, `VisibilityEnabler2D` | `VisibleOnScreenNotifier2D`, `VisibleOnScreenEnabler2D` |
| `TextureProgress` | `TextureProgressBar` |
| `ToolButton` | `Button` with `flat = true` |
| `Reference` | `RefCounted` |
| `PoolByteArray`, `PoolIntArray`, `PoolRealArray`, `PoolStringArray`, `PoolVector2Array`, `PoolColorArray` | `Packed*Array` |
| `Quat`, `Transform` | `Quaternion`, `Transform3D` |
| `StreamTexture` (`.stex`), `Texture` | `CompressedTexture2D` (`.ctex`), `Texture2D` |
| `DynamicFont`, `DynamicFontData`, `BitmapFont` | `FontFile`, `FontVariation` |
| `File`, `Directory` | `FileAccess`, `DirAccess` |
| `JSONParseResult` (from `JSON.parse`) | `JSON` instance |
| `GDScriptFunctionState` | (coroutines via `await`) |
| `FuncRef` | `Callable` |
| `NetworkedMultiplayerENet`, `WebSocketClient`/`Server` | `ENetMultiplayerPeer`, `WebSocketPeer` |
| `Tween` node (`interpolate_property` + `start()`) and `SceneTreeTween` (`create_tween()`, 3.5+) | `Tween` (only `create_tween()`) |
| `VisualServer`, `Physics2DServer`, `PhysicsServer` | `RenderingServer`, `PhysicsServer2D`, `PhysicsServer3D` |
| `ARVR*` | `XR*` |

## Node / Control / CanvasItem members

| Godot 3 | Godot 4 |
|---|---|
| `scene.instance()` | `instantiate()` |
| `get_tree().change_scene(path)`, `change_scene_to(packed)` | `change_scene_to_file`, `change_scene_to_packed` |
| `node.filename` (scene path of an instanced scene root) | `scene_file_path` |
| `pause_mode = PAUSE_MODE_PROCESS / STOP / INHERIT` | `process_mode = PROCESS_MODE_ALWAYS / PAUSABLE / INHERIT` |
| `raise()` | `move_to_front()` |
| `get_network_master()`, `is_network_master()`, `set_network_master(id)` | `get_multiplayer_authority()`, `is_multiplayer_authority()`, `set_multiplayer_authority(id)` |
| `update()` (CanvasItem redraw) | `queue_redraw()` |
| `rect_position`, `rect_size`, `rect_min_size`, `rect_scale`, `rect_global_position`, `rect_pivot_offset`, `rect_rotation` | `position`, `size`, `custom_minimum_size`, `scale`, `global_position`, `pivot_offset`, `rotation` |
| `margin_left/top/right/bottom` | `offset_left/...` |
| `Label.align`, `valign`, `percent_visible` | `horizontal_alignment`, `vertical_alignment`, `visible_ratio` |
| `add_font_override("font", f)`, `add_color_override`, `add_stylebox_override`, `add_constant_override` | `add_theme_font_override`, `add_theme_color_override`, ... |
| `get_font("font")`, `get_color(...)`, `get_stylebox(...)` | `get_theme_font`, `get_theme_color`, ... |
| `Camera2D.current = true`, `smoothing_enabled` | `make_current()`/`enabled`, `position_smoothing_enabled` |
| `AnimationPlayer.playback_speed` | `speed_scale` |
| `Sprite.region_rect` (same), `Sprite.texture` (same) | same |
| `move_and_slide(velocity, Vector2.UP)` returns new velocity | `velocity` property, `move_and_slide()` returns bool |
| `move_and_collide(v)` returns `KinematicCollision2D` | same |
| `TileMap.set_cell(x, y, id)`, `get_cellv(v)`, `world_to_map`, `map_to_world` | `set_cell(layer, coords, source_id, atlas)`, `local_to_map`, `map_to_local` |

## OS, Engine, servers

| Godot 3 | Godot 4 |
|---|---|
| `OS.get_ticks_msec()`, `OS.get_ticks_usec()` (`Time` singleton also exists in 3.5+) | `Time.get_ticks_msec()` |
| `OS.get_unix_time()`, `OS.get_datetime()`, `OS.get_system_time_msecs()` | `Time.get_unix_time_from_system()`, `Time.get_datetime_dict_from_system()` |
| `OS.window_size`, `OS.window_fullscreen`, `OS.set_window_title()`, `OS.get_screen_size()`, `OS.clipboard`, `OS.vsync_enabled` | `DisplayServer.window_get_size()`, `window_set_mode()`, `window_set_title()`, `screen_get_size()`, `clipboard_get()`, `window_set_vsync_mode()` |
| `OS.get_executable_path()`, `OS.get_cmdline_args()`, `OS.has_feature()`, `OS.is_debug_build()` | same |
| `Engine.editor_hint` | `Engine.is_editor_hint()` |
| `Engine.get_idle_frames()`, `get_tree().idle_frame` | `get_process_frames()`, `process_frame` |
| `Engine.get_version_info()` (same) | same |

## Input

| Godot 3 | Godot 4 |
|---|---|
| `InputEventKey.scancode`, `physical_scancode` | `keycode`, `physical_keycode` |
| `BUTTON_LEFT`, `BUTTON_WHEEL_UP` | `MOUSE_BUTTON_LEFT`, `MOUSE_BUTTON_WHEEL_UP` |
| `JOY_BUTTON_0`/`JOY_XBOX_A`, `JOY_AXIS_0` | `JOY_BUTTON_A`, `JOY_AXIS_LEFT_X` |
| `Input.get_vector()` (3.4+), `get_action_strength()` | same |
| `InputMap.add_action("x")`, `action_add_event` | same |
| `_unhandled_key_input(event)` | `_unhandled_key_input(event)` (different dispatch in 4) |

## Physics queries

| Godot 3 | Godot 4 |
|---|---|
| `get_world_2d().direct_space_state.intersect_ray(from, to, [self], mask)` returns Dictionary | `intersect_ray(PhysicsRayQueryParameters2D.create(from, to, mask, [rid]))` |
| `intersect_point(pos, 32, [], mask)` | `intersect_point(PhysicsPointQueryParameters2D)` |
| `area.get_overlapping_bodies()` (same) | same |

## Strings, arrays, dictionaries

| Godot 3 | Godot 4 |
|---|---|
| `s.empty()`, `arr.empty()`, `dict.empty()` | `is_empty()` |
| `path.plus_file("x")` | `path_join("x")` |
| `pool_string_array.join(", ")` (also `", ".join(arr)` in late 3.x) | `", ".join(arr)` |
| `s.find_last("x")` | `rfind("x")` |
| `s.http_escape()`, `percent_encode()` | `uri_encode()` |
| `arr.remove(i)` | `remove_at(i)` |
| `arr.invert()` | `reverse()` |
| `arr.slice(a, b)` (inclusive end, `b` required) | `slice(a, b)` (exclusive end, `b` optional) |
| `arr.sort_custom(obj, "method")` | `sort_custom(callable)` |
| `arr.pop_at(i)`, `arr.has(x)`, `arr.find(x)` | same |
| `dict.duplicate(true)`, `dict.has(k)`, `k in dict`, `dict.get(k, default)` | same |
| `str(x)`, `"%s" % [x]`, `"{a}".format({"a": 1})` | same |

## Files, JSON, resources

| Godot 3 | Godot 4 |
|---|---|
| `var f = File.new(); f.open(p, File.WRITE); f.store_string(s); f.close()` | `FileAccess.open(p, FileAccess.WRITE).store_string(s)` |
| `File.new().file_exists(p)`, `Directory.new().dir_exists(p)` | `FileAccess.file_exists(p)`, `DirAccess.dir_exists_absolute(p)` |
| `var d = Directory.new(); d.open(p); d.list_dir_begin(true, true); var n = d.get_next(); ... d.list_dir_end()` | `DirAccess.open(p)`, `list_dir_begin()` (no skip args), `get_files()` |
| `JSON.print(v, "\t")`; `var r = JSON.parse(s)` -> `r.error`, `r.error_string`, `r.result` | `JSON.stringify`, `JSON.parse_string` / `JSON.new().parse()` |
| `ResourceLoader.load_interactive(p)` | `ResourceLoader.load_threaded_request(p)` |
| `res.take_over_path(p)`, `res.duplicate(true)`, `ResourceSaver.save(path, res)` | `take_over_path`; `ResourceSaver.save(res, path)` (args swapped) |
| `ProjectSettings.load_resource_pack(path, replace_files := true)` | same |

## Project and scene file formats

| Godot 3 | Godot 4 |
|---|---|
| `project.godot`: `config_version=4` | `config_version=5` |
| `.tscn`/`.tres`: `[gd_scene load_steps=3 format=2]`, `ExtResource( 1 )` | `format=3`, `ExtResource("1_abcd")`, `uid://` |
| Imported files in `res://.import/` (`*.stex`, `*.sample`, `*.oggstr`) + `<file>.import` | `res://.godot/imported/` (`*.ctex`), UIDs |
| Exported scripts: `*.gdc` bytecode or `*.gde` encrypted; `*.gd.remap` | binary tokens `*.gdc` (different format) |
| Global classes in `project.godot` `_global_script_classes` | `.godot/global_script_class_cache.cfg` |
