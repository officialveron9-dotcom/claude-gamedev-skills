# Brotato internals map (1.1.15.x)

Every name below appears in public mods that target Brotato 1.1.15.0-1.1.15.4 (extension targets, overrides or calls). It is a map, not the API: before overriding or calling anything, open the decompiled script of the **installed** game version and copy the exact signature. Private members (`_x`) change between patches.

## Contents
- Hash keys and per-player model
- Global singletons (autoload names -> script)
- Battle scene (main.gd) and spawner
- Units, weapons, projectiles, effects
- Shop, menus, UI
- Co-op specifics
- DLC and content
- Scene/node paths
- Defensive access patterns
- Version history that broke mods

## Hash keys and per-player model

- Since the early-2026 "console performance" refactor (Brotato ~1.1.14, shipped around Paws & Claws) ids and stat/effect keys are `int` hashes: `Keys.generate_hash("stat_max_hp")`, constants like `Keys.stat_armor_hash`, `Keys.stat_max_hp_hash`, `Keys.stat_luck_hash`, `Keys.stat_range_hash`, `Keys.stat_curse_hash`, `Keys.stat_dodge_hash`, `Keys.stat_percent_damage_hash`, `Keys.stat_engineering_hash`, `Keys.stat_elemental_damage_hash`, `Keys.stat_hp_regeneration_hash`, `Keys.stat_lifesteal_hash`, item/consumable constants like `Keys.item_hourglass_hash`, `Keys.consumable_item_box_hash`, `Keys.empty_hash`. Reverse for logging: `Keys.hash_to_string(h)`.
- Resources carry both: `my_id` (`"item_helmet"`, `"weapon_knife"`, `"character_creature"`) and `my_id_hash`; effects carry `key` and `key_hash`.
- Since 1.1.0 (co-op, Aug 2024) almost every API takes `player_index` (0..player_count-1). Code written for 1.0 (`RunData.effects["x"]`, `RunData.gold`, `RunData.items`) is wrong.

## Global singletons (autoload names -> script to extend)

| Global | Script | Members seen in mods |
|---|---|---|
| `RunData` | `res://singletons/run_data.gd` | `get_player_count()`, `players_data[i]` (`items`, `weapons`, `gold`, `current_health`, `current_xp`, `current_level`, `banned_items`, `selected_weapon`, `selected_item`, `appearances`), `current_wave`, `current_zone`, `current_difficulty`, `get_current_difficulty()`, `nb_of_waves`, `is_coop_run`, `is_endless_run`, `retries`, `enabled_dlcs`, `get_player_gold(i)`, `add_gold(v, i)`, `get_player_currency(i)`, `get_player_items(i)`, `get_player_weapons(i)`, `get_player_weapons_ref(i)`, `add_item(item_data, i)`, `remove_item(...)`, `add_weapon(weapon_data, i, ...)`, `add_stat(stat_hash, v, i)`, `get_player_effect(key_hash, i)`, `get_player_effect_bool(key_hash, i)`, `get_player_effects(i)`, `sum_all_player_effects(...)`, `get_player_character(i)`, `get_player_max_health(i)`, `get_nb_item(id_hash, i, ...)`, `add_tracked_value(i, key_hash, v)`, `tracked_item_effects`, `get_shop_scene_path()`, `reset(restart: bool = false) -> void`, `add_starting_items_and_weapons() -> void`, `get_state()`, `resume_from_state(state)`, `set_player_count(n, ...)`, `set_coop_run(bool)`. Signals emitted by mods: `gold_changed`, `stat_added(stat_hash, value, ?, player_index)`, `stat_removed`, `xp_added`, `levelled_up`, `healing_effect` |
| (per-player data class) | `res://singletons/player_run_data.gd` | entries of `RunData.players_data` |
| `ProgressData` | `res://singletons/progress_data.gd` | `settings` (Dictionary, e.g. `manual_aim`, `pause_on_focus_lost`), `get_dlc_data("abyssal_terrors")`, `is_dlc_available("abyssal_terrors")`, `is_dlc_available_and_active("abyssal_terrors")`, `check_for_available_dlcs() -> void`, `load_game_file(try_fallback := true)`, `save()`, `saved_run_state` |
| `ItemService` | `res://singletons/item_service.gd` | `items`, `weapons`, `characters`, `consumables`, `upgrades`, `difficulties`, `_tiers_data`, `get_element(list, id_hash)`, `get_element_safe(list, id)`, `get_item_from_id(id)`, `get_color_from_tier(tier)`, `get_icon(hash)`, `get_value(...)`, `init_unlocked_pool()`, `get_player_shop_items(wave: int, player_index: int, args) -> Array`, `get_rand_item_for_wave(wave, player_index)`, `process_item_box(consumable_data, wave, player_index)`, `get_consumable_to_drop(unit, item_chance)` |
| `WeaponService` | `res://singletons/weapon_service.gd` | `init_ranged_stats(stats, player_index, ...)` |
| `Utils` | `res://singletons/utils.gd` | `get_stat(stat_hash, player_index)`, `reset_stat_cache(player_index)`, `get_focus_emulator(player_index)`, `focus_player_control(...)`, `get_scene_node()`, `get_rand_element(arr)`, `get_chance_success(chance)`, `default_die_args`, `on_console`, `deep_copy_config(...)` |
| `Keys` | (see above) | `generate_hash`, `hash_to_string`, `*_hash` constants |
| `CoopService` | `res://singletons/coop_service.gd` | `connected_players`, `get_max_players()`, `get_player_color(i)`, `get_remapped_player_device(i)`, `is_device_assigned(device)`, `is_player_using_gamepad(i)`, `listening_for_inputs`, signal `connected_players_updated(players)` |
| `TempStats` | `res://singletons/temp_stats.gd` | `get_stat(hash, i)`, `add_stat(hash, v, i)`, `reset()` |
| `LinkedStats` | `res://singletons/linked_stats.gd` | `reset()`, `reset_player(i)` |
| `ZoneService` | `res://singletons/zone_service.gd` | `zones`, `current_zone_rect`, `get_zone_data(zone_id)` |
| `SoundManager`, `SoundManager2D` | `res://singletons/sound_manager.gd`, `sound_manager_2d.gd` | `play(...)` |
| `InputService` | `res://singletons/input_service.gd` | `hide_mouse` |
| `DebugService` | `res://singletons/debug_service.gd` | debug flags |
| `Text` | - | `text("KEY", [args])`, `keys_needing_percent`, `keys_needing_operator`, `get_formatted_number(...)` |
| `ChallengeService` | - | `challenges` |

## Battle scene (main.gd) and spawner

- Scene `res://main.tscn`, script `res://main.gd`, root node `/root/Main` while in a wave. Detect it with `get_tree().current_scene.filename == "res://main.tscn"`; it is replaced via `change_scene` between battle, shop and menus.
- Members: `_players`, `_entity_spawner`, `_wave_timer`, `_cleaning_up` (true once the wave is being cleaned up), `_is_run_won`, `_is_run_lost`, `_is_wave_failed`, `_is_elite_wave`, `_is_horde_wave`, `_consumables`, `_consumables_container`, `_active_golds`, `_items_container`, `_player_projectiles`, `_enemy_projectiles`, `_upgrades_to_process`, `_pool`, `_effects_manager`, `_floating_text_manager`.
- Overridable (signatures as in 1.1.15.x mods): `_on_WaveTimer_timeout() -> void`, `_on_EndWaveTimer_timeout() -> void`, `_on_HalfWaveTimer_timeout()`, `_on_EntitySpawner_players_spawned(players: Array) -> void`, `on_gold_picked_up(gold: Node, player_index: int) -> void`, `on_consumable_picked_up(consumable: Node, player_index: int)`, `spawn_consumables(unit: Unit)`, `spawn_loot(unit: Unit, entity_type: int, args: Entity.DieArgs)`, `_on_neutral_died(neutral: Neutral, args: Entity.DieArgs)`, `_check_for_pause()`, `clean_up_room()`.
- Child nodes: `EntitySpawner` (`res://global/entity_spawner.gd`; members `enemies`, `structures`, `players`/`_players`; signals `enemy_spawned`, `enemy_respawned`, `neutral_spawned`, `neutral_respawned`, `players_spawned`; methods `init(zone_min_pos: Vector2, zone_max_pos: Vector2, current_wave_data: WaveData, wave_timer: Timer) -> void`, `spawn_entity(scene: PackedScene, args: SpawnEntityArgs, data: Resource = null, source = null, charmed_by: int = -1)`, `on_group_spawn_timing_reached(group_data: WaveGroupData)`), `Camera` (`res://global/my_camera.gd`), `UI/HUD`, `UI/UpgradesUI`.
- Wave manager: `res://zones/wave_manager.gd` `init(p_wave_timer: Timer, zone_data: ZoneData, wave_data: Resource)`.
- Other globals in the battle: `res://global/effects_manager.gd`, `res://global/stats_manager.gd`, `res://visual_effects/floating_text/floating_text_manager.gd`.

## Units, weapons, projectiles, effects

| Script | Notes |
|---|---|
| `res://entities/entity.gd` | base; `Entity.DieArgs` |
| `res://entities/units/unit/unit.gd` | base of player/enemies/neutrals. Signals `took_damage(unit, value, knockback, is_crit, is_dodge, is_protected, armor_did_something, args, hit_type, is_one_shot)` and `health_updated(unit, current, max_value)` (emitted before `took_damage`). Extending this reloads every subclass - prefer signals |
| `res://entities/units/enemies/enemy.gd`, `.../enemies/boss/boss.gd` | `enemy_id`, `is_elite`, `take_damage(value: int, args: TakeDamageArgs) -> Array`, `_on_hurt(hitbox: Hitbox)`. Pooled: listen to `enemy_respawned` |
| `res://entities/units/player/player.gd` (`class_name Player`) | `player_index`, `current_weapons`, `take_damage(value: int, args: TakeDamageArgs) -> Array`, `on_healing_effect(value: int, tracking_key: int = Keys.empty_hash, from_torture: bool = false) -> int`, `on_health_regen(...)`, `on_lifesteal_effect(...)`, `die(args = Utils.default_die_args)`, `_dodge_damage_args` |
| `res://entities/units/movement_behaviors/player_movement_behavior.gd` | player movement input |
| `res://entities/units/pet/...` | pets (Paws & Claws, 1.1.14+) |
| `res://entities/structures/turret/turret.gd`, `.../landmine/landmine.gd` | structures |
| `res://weapons/weapon.gd` | `weapon_id`, `tier`, `_hitbox`, `effects`, `on_weapon_hit_something(_thing_hit: Node, damage_dealt: int, hitbox: Hitbox)` |
| `res://weapons/weapon_stats/weapon_stats.gd` | stats resources (`RangedWeaponStats` class exists) |
| `res://projectiles/player_projectile.gd`, `player_explosion.gd` | `Hitbox`: `from`, `damage_tracking_key_hash`, `scaling_stats`, signal `hit_something` |
| `res://items/global/item.gd`, `effect.gd`; `res://effects/items/*.gd`, `res://effects/weapons/*.gd` | effect behaviours |
| Data | `res://weapons/{melee,ranged}/<name>/<tier>/<name>_data.tres`, `res://items/all/<name>/<name>_data.tres`, sets `res://items/sets/<set>/<set>_set_data.tres` |

Vanilla global classes usable as type hints: `Unit`, `Entity`, `Player`, `Weapon`, `TakeDamageArgs`, `Hitbox`, `WeaponData`, `ItemData`, `ItemParentData`, `CharacterData`, `ConsumableData`, `ShopItem`, `InventoryElement`, `WaveData`, `WaveGroupData`, `SpawnEntityArgs`, `ZoneData`, `Neutral`, `RangedWeaponStats`.

## Shop, menus, UI

| Script | Notes |
|---|---|
| `res://ui/menus/shop/base_shop.gd` | shared base |
| `res://ui/menus/shop/shop.gd` + `shop.tscn` | solo shop |
| `res://ui/menus/shop/coop_shop.gd` + `coop_shop.tscn` | co-op shop: `fill_shop_items(player_locked_items: Array, player_index: int, just_entered_shop: bool = false) -> void`, `on_shop_item_bought(shop_item: ShopItem, player_index: int)`, `buy_item(item_data: ItemData, player_index: int)`, `_on_GoButton_pressed(player_index: int)`, `_on_RerollButton_pressed(player_index: int)` |
| `res://ui/menus/shop/coop_shop_player_container.gd`, `shop_item.gd`, `player_gear_container.gd`, `reroll_button.gd`, `item_description.gd` | per-player panels; shop state `_reroll_price`, `_reroll_count`, `_free_rerolls`; nodes `%ShopItemsContainer`, `%GearContainer`, `%RerollButton`, `%GoButton`, `%ItemPopup` |
| `res://ui/menus/run/character_selection.gd`, `weapon_selection.gd`, `difficulty_selection/difficulty_selection.gd`, `base_selection.gd` | run setup; difficulty page root `/root/DifficultySelection` |
| `res://ui/menus/run/coop_end_run.gd` (+ `end_run.gd`) | end screen `/root/EndRun` |
| `res://ui/menus/ingame/pause_menu.gd`, `upgrades_ui.gd`, `upgrades_ui_player_container.gd`, `coop_upgrades_ui_player_container.gd`, `coop_player_selector.gd` | in-run menus; level-up UI at `/root/Main/UI/UpgradesUI` |
| `res://ui/menus/pages/main_menu.gd`, `menu_options.gd` | title + options |
| `res://ui/menus/global/focus_emulator.gd`, `popup_manager.gd` | per-player focus handling |
| `res://ui/hud/ui_wave_timer.gd` | HUD |
| Fonts | `res://resources/fonts/actual/base/font_22.tres`, `font_26.tres`, `font_26_outline.tres`, `font_30_outline.tres`, `font_40_outline.tres` |

UI traps (from mods with working overlays):
- Godot 3 picks the control under the mouse by tree order, not `CanvasLayer.layer`; a full-screen game container can eat clicks. Put your `CanvasLayer` last under `/root` (re-move it after every scene change) or dispatch mouse input yourself in `_input`.
- In multiplayer the `FocusEmulator` marks mouse events handled in `_input`; your buttons may never see them.
- `Button`/`LineEdit` grab keyboard/gamepad focus and break the game's focus navigation: set `focus_mode = Control.FOCUS_NONE` on overlay controls, or integrate with `Utils.get_focus_emulator(player_index)`.
- Hide overlays while paused or during the level-up/shop screens, or they cover and steal input from those menus.

## Co-op specifics

- Local co-op up to `CoopService.get_max_players()` (4 in vanilla; a mod overrides it to 8). Devices are remapped per player (`CoopService.get_remapped_player_device(i)`); per-device actions are named like `ui_accept_<device>`, `ui_pause_<device>`.
- `CoopService.connected_players[i]` is an array per joined player: the **index `i` is the player slot**; element `[1]` is the controller *type* (keyboard/Xbox/PlayStation/Switch), not the slot (a mod shipped this bug and cross-mapped inputs).
- Solo uses `shop.gd`/`upgrades_ui_player_container.gd`, co-op uses `coop_shop.gd`/`coop_upgrades_ui_player_container.gd`: test both.
- Online play is not part of vanilla; it comes from mods (e.g. BrotatoOnline). Its public mod API (node group `brotato_online_api`, `is_online`, `owns_player`, `broadcast(...)`, signal `mod_message_received`) is documented by the Combat Tracker mod. See the `brotato-online-multiplayer` skill for networking.

## DLC and content

- DLC id `"abyssal_terrors"`, files under `res://dlcs/dlc_1/` (`dlc_data.tres`, `dlc_1_data.gd`). They exist only if the DLC is installed.
- Never install an extension of a DLC script unconditionally. Pattern used by two content mods:

```gdscript
# extensions/singletons/progress_data.gd
extends "res://singletons/progress_data.gd"

func check_for_available_dlcs() -> void:
	if File.new().file_exists("res://dlcs/dlc_1/dlc_data.tres"):
		ModLoaderMod.install_script_extension("res://mods-unpacked/YourName-QoLPack/extensions/dlcs/dlc_1/dlc_1_data.gd")
	.check_for_available_dlcs()
	if ProgressData.is_dlc_available("abyssal_terrors"):
		pass  # adjust DLC data here
```

- Adding items/weapons/characters: use a content framework instead of appending to `ItemService.items` yourself (pools, unlocks, DLC merge, removal). Current options: `Yoko-NewContentLoader` (targets 1.1.15.4, restricted-source license) or `Darkly77-ContentLoader` + `Darkly77-Brotils` (last tested on 1.1.13.1).

## Scene/node paths

`/root/ModLoader/<ModId>` (mod mains), `/root/Main` (battle), `/root/Main/EntitySpawner`, `/root/Main/Camera`, `/root/Main/UI/HUD`, `/root/Main/UI/UpgradesUI`, `/root/DifficultySelection`, `/root/EndRun`. Shop and menus are their own scenes; use `get_tree().current_scene` plus `%UniqueName` lookups with `get_node_or_null`.

## Defensive access patterns

Brotato renames private members between patches and pools entities. Mods that survive updates do this:

```gdscript
var main = get_tree().current_scene
if main == null or main.filename != "res://main.tscn":
	return
var spawner = main.get_node_or_null("EntitySpawner")
if spawner and spawner.has_signal("enemy_spawned") and not spawner.is_connected("enemy_spawned", self, "_on_enemy_spawned"):
	spawner.connect("enemy_spawned", self, "_on_enemy_spawned")
var cleaning = main.get("_cleaning_up") == true          # get() returns null instead of erroring
if RunData.has_method("get_player_effects"):
	var effects = RunData.get_player_effects(0)
```

Use these guards for optional hooks into private state; for core logic prefer failing loudly in testing (a silently dead feature is worse). Re-check the guarded list after every game update.

## Version history that broke mods

| Version (date) | Change |
|---|---|
| 1.0.1.3 | many 1.0 mods broke (ContentLoader GDScript) |
| 1.1.0.0 (Aug 2024, co-op + Abyssal Terrors) | per-player APIs; mods older than Oct 2024 generally broken |
| 1.1.7.1 | menu node paths moved |
| 1.1.13.0 "New Dawn" (Oct 2025, Evil Empire) | bans, save profiles, codex; native Linux/macOS |
| ~1.1.14 "Paws & Claws" (Jan/Feb 2026) | pets, Godot 3.7-dev engine, int-hash keys refactor, code style changes |
| 1.1.15.0 "All Pain No Gain" (Apr 2026) | Nightmare difficulty; balance changes |
| 1.1.15.4 (current, Sep 2026) | baseline of most maintained mods; e.g. `main.gd clean_up_room()` takes no args here, older builds had `clean_up_room(is_last_wave, is_run_lost, is_run_won)` |
