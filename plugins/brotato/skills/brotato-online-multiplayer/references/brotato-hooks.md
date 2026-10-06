# Brotato hook points for online co-op

These are the classes and members that Brotatogether (HEAD 2026-05) and BroTangto 0.3.0 (for Brotato 1.1.15.4)
extend through ModLoader script extensions. They are names, not guarantees: patches rename private members
(`_foo`), so check every one in your decompiled copy after an update. How to install extensions, call `.parent()`
and decompile is covered in `brotato-modding`.

Pattern for every override: **offline → call the parent unchanged; host → parent + broadcast; client → send
intent / ignore**.

```gdscript
extends "res://ui/menus/shop/coop_shop.gd"

func fill_shop_items(player_locked_items: Array, player_index: int, just_entered_shop: bool = false) -> void:
	if not Net.online or Net.is_host:
		.fill_shop_items(player_locked_items, player_index, just_entered_shop)   # only the host rolls
	# client: shop contents arrive from the host as my_id lists
```

## 1. Registering remote players (local co-op reuse)

| Hook | Use | Pitfall |
|---|---|---|
| `CoopService._add_player(device, player_type)`, `is_device_assigned(device)`, `clear_coop_players()` | Add one fake device per remote slot during character select, so native co-op scenes build 2-4 players | Brotatogether uses device `0` for self and `100 + lobby_index` for the others, with a custom player type `10`. BroTangto uses devices `8`/`9` with `KEYBOARD_AND_MOUSE`. Real joypad IDs start at 0, so pick a high range (≥ 100) and one `is_remote_device()` helper |
| `CoopService.get_remapped_player_device(player_index)`, `is_player_using_gamepad(player_index)` | Return `false` (keyboard/mouse UI) for remote devices | Without this, the UI shows gamepad prompts or waits for a gamepad |
| `CoopService.listening_for_inputs` | Set `false` after selection completes | Otherwise a local key press "joins" a phantom player |
| `PlayerMovementBehavior.get_movement()` + `device` | For remote devices, return the network-fed `get_parent()._current_movement` | Return `Vector2.ZERO` when no update arrived within 150 ms (BroTangto watchdog). Otherwise a lagging player runs forever in the last direction |
| `Utils.is_player_action_released(event, player_index, action)` (and the pressed variants) | Return `false` for remote devices | Otherwise the host's keyboard also drives the remote slot |
| `FocusEmulator._handle_input(event)`, `_get_focus_neighbour_for_event(...)`, `_device` | Ignore events for remote devices. Return `false` when a `LineEdit` (chat) has focus | Otherwise typing in chat moves the shop cursor or presses buttons |
| `Utils.get_focus_emulator(player_index).focused_control` | Read or set a remote player's cursor in shop and upgrade menus | Send the focus as a stable key (`my_id`), not a node path |

## 2. Main scene (wave)

| Hook | Use | Pitfall |
|---|---|---|
| `main.gd`: `_players`, `_wave_timer`, `_entity_spawner`, `_entities_container`, `_coop_upgrades_ui`, `_things_to_process_player_containers` | The host reads state for snapshots. The client applies HP, XP and level UI | Private, so names change between patches |
| `main.gd`: `_on_WaveTimer_timeout()`, `_on_EndWaveTimer_timeout()` | Client: no-op, because only the host ends the wave | Otherwise a client leaves for the shop on its own clock, a few frames early |
| `main.gd`: `_check_for_pause()`; `pause_menu.gd`: `on_game_lost_focus()` | Skip the native auto-pause while online | Otherwise one alt-tab or controller unplug freezes the whole session |
| `main.gd`: `add_node_to_pool(node, id)`, `_pool` | Client mirrors: `queue_free()` instead of pooling them | A pooled mirror is later reused by native code with its behaviors stubbed |
| `main.gd`: `connect_visual_effects(unit)` | The host also connects `took_damage` to batch floating text and hit effects for clients | Batch per tick. Don't send one reliable message per hit |
| `EntitySpawner.spawn(queue_from, player_index)`; `enemies`, `bosses` | Client: pop the queue and return (no native spawns) | If the client spawns too, you get duplicate enemies that don't move with the host's |
| `EntityBirth` (`entities/birth/entity_birth.gd`) | Mirror the spawn markers on clients by ID | Markers that are never despawned stay on the floor |
| `Unit.take_damage(value, args)`, `_on_Hurtbox_area_entered(hitbox)` | Client: return early (`[]`) | Otherwise clients deal and take damage locally, and HP flickers against the snapshots |
| `Unit.flash()`, `Unit.die(args)` | Host: record the network ID in the batched flash/death lists, then call the parent | Client `die()` must not drop materials, give XP or start death effects twice |
| Enemy `MovementBehavior` / `AttackBehavior` child nodes, `_current_movement_behavior`, `_current_attack_behavior` | Client: replace them with stubs (`get_movement()` returns `Vector2.ZERO`) | Leaving native AI running on mirrors is the #1 cause of "enemies in different places" |
| `Unit._current_movement`, `update_animation(movement)`, `sprite.self_modulate` | Feed them from the snapshot for walk animation, facing and tint | |
| Projectiles, `player_explosion.gd`, `turret.gd` | The host spawns and resolves hits. The client gets visual copies with hitboxes disabled | A client-side hitbox applies damage twice, or kills mirrors early |

## 3. Menus, shop, run data

| Hook | Use | Pitfall |
|---|---|---|
| `character_selection.gd`, `weapon_selection.gd`, `difficulty_selection.gd` | Clients send focus and selection intents. The host resolves random picks (`Utils.get_rand_element`) and broadcasts the concrete `my_id` | Commit the selections to the client's `RunData` before the scene change (BroTangto). Clients must not run the native "selection complete → change scene" path |
| `coop_shop.gd`: `fill_shop_items(...)`, `on_shop_item_bought(shop_item, player_index)`, `_on_item_combine_button_pressed`, `_on_item_discard_button_pressed`, `_on_GoButton_pressed(player_index)`, `_player_pressed_go_button`, `_shop_items` | Client actions become intents. The host executes and broadcasts that player's shop and inventory | Buy by `my_id` plus slot index. The host rejects a mismatch instead of buying the wrong item (BroTangto) |
| `RunData.lock_player_shop_item(item_data, wave_value, player_index)`, `unlock_player_shop_item(...)`, `RunData.locked_shop_items` | Host-side locking, mirrored to clients | Locks carry `wave_value` |
| `RunData.players_data[i]`: `gold`, `current_xp`, `current_level`, `effects`, `active_sets`; `RunData.get_player_count()`, `get_player_weapons(i)`, `get_next_level_xp_needed(i)`, `current_wave`, `bonus_gold` | Values for snapshots, resync and the state hash | The client also has to emit the matching UI signals (`gold_changed`, `xp_added`) after writing, or the HUD stays stale |
| `ItemService.items`, `.weapons`, `.characters`, `ItemService.get_icon(...)`; `.my_id`, `.is_cursed` | Map IDs back to resources | The same `my_id` can appear twice in an inventory (two identical weapons, cursed vs. normal). Identify by (`my_id`, index, `is_cursed`) |
| `ProgressData.get_dlc_data("abyssal_terrors")` | DLC ownership check | DLC content lives in a separate pack. A client without the DLC can't `load()` DLC characters, items or zones, so the host must disable DLC content when any member lacks it |
| `MenuData.character_selection_scene`, `MenuData.game_scene`, `RunData.get_shop_scene_path()` | Phase targets for host-driven `change_scene` | Send the scene key in the phase message, not a path built on the client |

## 4. Order-of-operations traps

- Install the extensions in the mod's `_init()`, and add root nodes deferred in `_ready()`. Brotatogether adds
  `SteamConnection` and `BrotogetherOptions` under `/root` with `call_deferred("add_child", ...)`. Extensions
  read them in their own `_ready()` with `$"/root/..."`, which fails if your extension's `_ready()` runs first.
  Use `get_node_or_null` and lazy lookups.
- Godot 3 runs `_ready`, `_enter_tree`, `_exit_tree`, `_process` and `_physics_process` on **every** script
  in the extension chain automatically (multilevel call, verified in the 3.6 source). Don't call `._ready()`, or
  the parent's code runs twice. You **cannot** stop the native per-frame logic on a client by overriding
  `_physics_process`. Override the methods it calls, or use `set_physics_process(false)` on the mirror.
  Details: `godot3-gdscript-pitfalls`.
- `get_tree().change_scene()` takes effect at the end of the frame. Bump the epoch before calling it (see
  [architecture.md](architecture.md)).
