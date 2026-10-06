# Architecture: authority, message classes, snapshots, phases

All code below is Godot 3 GDScript, written for Brotato 1.1.x. Names marked "(hook)" are Brotato members used by
existing mods. Verify them in your decompiled copy after every patch (see `brotato-modding`).

## 1. What to sync, and who owns it

| Data | Owner | Message class | Rate | Notes |
|---|---|---|---|---|
| Own player position, movement vector, sprite facing | that client | state, unreliable | 20-30 Hz | Host clamps to arena and max speed, then relays it in its snapshot |
| Host player position | host | snapshot | 20 Hz | |
| Enemy and boss positions (+ movement vector for animation) | host | snapshot, unreliable | 10-20 Hz | Quantize to i16 and interpolate |
| Enemy spawn markers and enemy spawns (type, ID, position, elite flag) | host | event, reliable | on change | Brotato shows a birth marker before the enemy appears. Sync both |
| Enemy deaths | host | event, reliable, batched per tick | per tick | Client plays the death animation only: no drops, no XP |
| Player and enemy projectiles | host | spawn event (ID, type, position, velocity) + despawn event | on change | Client moves straight shots itself. Snapshot only homing or bouncing ones |
| Materials, consumables, crates on the ground | host | spawn and despawn events | on change | The magnet/attract animation runs locally. The pickup decision belongs to the host |
| Turrets/structures, pets, trees/neutrals | host | spawn event + low-rate snapshot | 5-10 Hz | |
| HP, max HP, gold, XP, level, pending upgrade count per player | host | snapshot (HP), reliable on change (gold, level) | 5-10 Hz | Client never computes these |
| Wave number, wave timer | host | phase message + snapshot | timer 2-5 Hz | Client never ends a wave itself |
| Items, weapons (tier, cursed), stats/effects per player | host | reliable, on change | shop and level-up | Full set at every wave start |
| Shop offers, locks, reroll price, ready (Go) flags | host | reliable, per player | on change | |
| Level-up choices, crate/loot items | host | reliable | when a menu opens | |
| Hit flashes, hit particles, damage numbers, sounds, explosions | host | batched cosmetic events inside the snapshot | per tick | Losing some is acceptable. Send short IDs, not resource paths |
| Other players' shop or menu cursor | owning client | state, unreliable | 5-10 Hz | QoL only |
| Camera, screen shake, volume, damage-number visibility, own UI focus | local | never | | |

Brotatogether sends almost all of this as one string-keyed Dictionary at 30 Hz: `var2bytes` + gzip, reliable
P2P, one channel per message type. That works for two players. It costs host CPU, and it rubber-bands under
packet loss (head-of-line blocking). Use the split above instead.

## 2. Message envelope and channels

```
u8  type     # message kind
u8  epoch    # scene/phase counter, wraps at 256
u16 seq      # per type: drop duplicates and older "latest wins" states
...          # payload
```

- Use **two channels**: 0 = reliable control and events, 1 = unreliable state. Reliable messages are ordered
  only **within a channel**. Brotatogether's channel-per-message-type design lets "leave shop" overtake
  "buy item". Put everything whose order matters on the same channel.
- Make events idempotent (event ID, or entity ID + kind). Reliable delivery can still repeat after a reconnect.
- Never put Objects, Resources, NodePaths to scene nodes, or `resource_path` strings of pooled scenes in
  packets. Use `my_id`, a u16 type index, or a network ID.
- Build a **type table** at lobby start: a sorted list of enemy, projectile and item IDs. Hash it, and check
  the hash on join. A different mod set gives different tables and wrong spawns.

## 3. Binary snapshots that fit 1200 bytes (Godot 3)

```gdscript
const MSG_ENEMY_SNAPSHOT := 10
const MAX_DATAGRAM := 1100           # old Steam P2P unreliable hard limit is 1200 B; keep headroom
const HEADER := 8                    # u8 type, u8 epoch, u32 tick, u8 chunk, u8 chunk_count
const ENTRY := 7                     # u16 net_id, i16 x, i16 y, u8 flags
const PER_CHUNK := (MAX_DATAGRAM - HEADER) / ENTRY   # 156 enemies per datagram

func encode_enemy_chunks(tick: int, epoch: int, enemies: Array) -> Array:
	var out := []
	var total := enemies.size()
	var chunk_count := int(max(1, ceil(float(total) / PER_CHUNK)))
	for c in chunk_count:
		var buf := StreamPeerBuffer.new()
		buf.put_u8(MSG_ENEMY_SNAPSHOT)
		buf.put_u8(epoch & 0xFF)
		buf.put_u32(tick)
		buf.put_u8(c)
		buf.put_u8(chunk_count)
		for i in range(c * PER_CHUNK, int(min((c + 1) * PER_CHUNK, total))):
			var e = enemies[i]
			buf.put_u16(e.net_id)                        # set by your entity extension on host spawn
			buf.put_16(int(round(e.global_position.x)))  # assumes arena within +-32767 px
			buf.put_16(int(round(e.global_position.y)))
			buf.put_u8(_flags(e))                        # e.g. facing, elite, charging
		out.append(buf.data_array)
	return out

func decode_enemy_chunk(bytes: PoolByteArray) -> void:
	var buf := StreamPeerBuffer.new()
	buf.data_array = bytes
	if buf.get_u8() != MSG_ENEMY_SNAPSHOT or buf.get_u8() != (epoch & 0xFF):
		return                                           # wrong type or stale scene
	var tick := buf.get_u32()
	buf.get_u8(); buf.get_u8()                           # chunk index/count (unused when despawns are events)
	if tick < _latest_enemy_tick:
		return                                           # out-of-order datagram, a newer one was applied
	_latest_enemy_tick = tick
	while buf.get_available_bytes() >= ENTRY:
		var id := buf.get_u16()
		var pos := Vector2(buf.get_16(), buf.get_16())
		var flags := buf.get_u8()
		var mirror = _mirrors.get(id)
		if mirror != null:
			mirror.net_update(pos, flags)                # unknown ID: spawn event not here yet, ignore
```

Budget: 300 enemies × 7 B is about 2.1 KB per snapshot, or 2 datagrams. At 20 Hz that is about 42 KB/s per
client, and about 130 KB/s host upload with 3 clients. Gzipped string-keyed Dictionaries are many times
larger and cost milliseconds of GDScript time per tick on the host.

Late-wave load:
- send enemies at 10-15 Hz;
- round-robin (half of the enemies per tick) above about 250 enemies;
- skip enemies that moved less than 1 px since the last send. Re-send everything at least once per second.

## 4. Interpolation of mirrored units (client)

```gdscript
# Component on each mirrored enemy (and on remote players on every peer)
const SNAP_DT := 1.0 / 20.0
const TELEPORT := 160.0          # spawn, knockback spike, respawn: snap instead of sliding
var _from := Vector2.ZERO
var _to := Vector2.ZERO
var _t := 1.0

func net_update(pos: Vector2, _flags: int) -> void:
	var unit: Node2D = get_parent()
	if unit.global_position.distance_to(pos) > TELEPORT:
		unit.global_position = pos
		_from = pos
		_to = pos
		_t = 1.0
		return
	_from = unit.global_position
	_to = pos
	_t = 0.0

func _process(delta: float) -> void:     # _process, not _physics_process: smooth on high-refresh displays
	if _t < 1.0:
		_t = min(_t + delta / SNAP_DT, 1.0)
		get_parent().global_position = _from.linear_interpolate(_to, _t)
```

- Brotatogether sets the position directly on every snapshot. That jitters at 30 Hz on a 60+ Hz display.
- For even smoother results, buffer snapshots with their tick and render about 100 ms (2 snapshots) behind the
  newest one.
- Pass the movement vector to the unit's animation code (Brotatogether calls `update_animation(_current_movement)`
  (hook)) so walk cycles and facing match.
- Never interpolate the local player. Its own movement runs natively from input.

## 5. Entity IDs, pooling, despawn

- The host assigns IDs from a counter at spawn time: u16 with wrap-around, or u32. Keep the `id -> node` maps on
  both sides and remove entries on despawn.
- Brotato pools nodes (`add_node_to_pool(node, id)` and `_pool` in `main.gd` (hook)). A pooled node's `_ready()`
  runs once. If you assign the ID in `_ready()`, as Brotatogether's `entity.gd` extension does, a reused node keeps
  its old ID, and the client sees an entity "teleporting" across the map. Assign the ID in the spawn path instead.
- On clients, **free mirrors** (`queue_free()`). Never hand them to the game's pool, because the pool would later
  give a mirror (with its behaviors stubbed) to native code. Brotatogether marks mirrors with
  `set_meta("btg_ghost_enemy", true)` and frees them in its `add_node_to_pool` override.
- Despawn by explicit reliable event. "Absent from the snapshot means despawn" only works with full,
  unchunked, unthrottled snapshots.
- A spawn that arrives after its first position update is normal (different channels). Ignore unknown IDs in
  snapshots. Don't create mirrors from snapshots without the type info.

## 6. RNG

- The host makes every gameplay roll: enemy spawns, drops, crits and dodges, item procs, shop offers, level-up
  choices, crate contents, random character/weapon picks. Clients receive the outcome.
- Don't call `seed()` or `randomize()` on the global RNG from the mod. That changes Brotato's (and other mods')
  randomness, and it still won't stay in sync: cosmetic calls such as sound variants
  (`Utils.get_rand_element(hurt_sounds)`) and sprite picks (`Utils.randi()`) consume the same sequence at
  frame-dependent times.
- Rolls that the mod itself makes and that every peer must reproduce: use a private RNG seeded from shared
  values, advanced only by host-ordered events.
  ```gdscript
  var rng := RandomNumberGenerator.new()
  rng.seed = hash([lobby_seed, RunData.current_wave, PURPOSE_ARENA_DECOR])
  ```
- Purely cosmetic client randomness (particle spread, which hurt sound plays) can stay local.

## 7. Phases, epochs, scene changes

Typical flow: Lobby → CharacterSelection → WeaponSelection → DifficultySelection → Main (load barrier →
running → end of wave) → upgrades/loot menu → CoopShop → Main ... → run end.

```gdscript
func host_go_to(scene_path: String, run_config: Dictionary) -> void:
	epoch = (epoch + 1) & 0xFF                     # bump BEFORE changing scene
	net.broadcast_reliable(MSG_PHASE, {"epoch": epoch, "scene": scene_path,
		"wave": RunData.current_wave, "cfg": run_config})
	get_tree().change_scene(scene_path)            # deferred: this frame still runs on the old scene
```

- Clients change scene **only** on `MSG_PHASE`. Suppress native transitions on clients: the wave timer
  timeout, the end-of-wave timer, the shop "Go" handler and the scene change after the difficulty pick.
  Brotatogether overrides `_on_WaveTimer_timeout` and `_on_EndWaveTimer_timeout` (hook).
- **Set** `RunData.current_wave` from the phase payload. Never `+= 1` on both sides, because an extra or
  missing transition gives off-by-one waves.
- Apply `run_config` (zone, difficulty, endless, DLC flags, player count) **before** loading the scene
  (BroTangto does this). Character and weapon choices must be committed to `RunData` on the client too.
- Load barrier: clients send `LOADED(epoch)`. The host keeps `_wave_timer` paused until every connected slot has
  reported, or a 10-15 s timeout marks the missing ones as disconnected (Brotatogether pattern:
  `waiting_to_start_round` + `player_in_scene`).
- Put the desired scene and epoch in every snapshot as well (BroTangto). A client that missed a phase message
  then recovers.

## 8. Pause

- Online, the local Esc menu (options, volume) must **not** set `get_tree().paused`. Show it as an overlay.
- A shared pause (host decision or vote) is a reliable message. Every peer sets `get_tree().paused = true`. The
  network node keeps running because of `PAUSE_MODE_PROCESS`, so heartbeats, ping and chat continue.
- Godot timers under the paused tree stop by themselves, including the wave timer. `get_tree().create_timer(t)`
  keeps running during a pause because its second argument defaults to `true`. Pass `false` for gameplay timeouts.
- Native auto-pause triggers (focus loss, controller disconnect) must be overridden online (see
  [brotato-hooks.md](brotato-hooks.md)).

## 9. Late join and reconnect

- Accept joins and rejoins only in the lobby or between waves (upgrade or shop phase). A mid-wave join needs
  a full entity sync plus spawning a player into a running wave. Not worth it.
- Reconnect by `steam_id` to the same slot. Keep the slot's `RunData.players_data[i]` on the host while the
  player is away.
- The resync payload is one reliable message (old P2P: up to 1 MB; Messages: up to 512 KB). It contains:
  - character;
  - weapons (`my_id`, tier, cursed);
  - items with counts;
  - effects/stats (Brotatogether sends `players_data[i]._serialize_effects(effects)` and `active_sets`);
  - gold, XP, level;
  - locked shop items;
  - wave, zone, difficulty, endless and DLC flags.

  Prefer reusing Brotato's own continue-run save serialization over a hand-picked field list. Find it in the
  decompiled save code.

## 10. Desync detection

```gdscript
func state_hash() -> int:
	var parts := [RunData.current_wave]
	for i in RunData.get_player_count():
		var pd = RunData.players_data[i]
		var weapons := []
		for w in RunData.get_player_weapons(i):
			weapons.append(w.my_id)
		weapons.sort()                                  # Dictionary/array order differs between peers; sort
		parts.append([i, pd.gold, pd.current_xp, pd.current_level, weapons])
	return hash(parts)                                  # ints/strings only: floats print differently after math
```

- Exchange the hash at wave start and when leaving the shop. On a mismatch, the host sends that slot the full
  resync payload, and both sides write their state to `user://` for diffing.
- Add every new synchronized value (items, stats, locks) to the hash. A feature outside the hash will drift
  silently.

## 11. Host CPU budget

- Brotatogether wraps its send and apply code in microsecond timers (`BTPROF` logs). Do the same, because GDScript
  serialization of hundreds of entities shows up as host frame drops in late waves.
- Keep an entity registry updated on spawn and despawn instead of iterating `_entity_spawner.enemies` (hook) with
  `is_instance_valid()` every tick.
- Pre-allocate one `StreamPeerBuffer` per chunk and use `clear()`. Don't build one Dictionary per entity per tick.
