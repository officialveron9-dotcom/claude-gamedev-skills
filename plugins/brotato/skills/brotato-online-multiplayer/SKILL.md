---
name: brotato-online-multiplayer
description: Builds and debugs online co-op mods for Brotato (Godot 3.x with GodotSteam compiled in) - host-authoritative netcode, Steam lobbies, P2P and Networking Messages, ENet fallback, hooking Brotato's local co-op (CoopService fake devices), enemy/projectile snapshots and interpolation, RNG, shop and level-up sync, pause, disconnects, desync detection and QoL such as ready checks and ping. Use when code touches Brotato online, co-op, multiplayer, GodotSteam, Steam lobby, P2P, rpc, desync, netcode or host authority, or the user writes German like "Online Mod", "Mehrspieler", "Koop", "Desync", "Synchronisierung", "Lobby".
---

# Brotato online co-op: netcode pitfalls and patterns

Baseline (verified 2026-10-06; re-check after every game patch):
- Brotato 1.1.x runs on **Godot 3.x**. Sources disagree on the minor version:
  - 3.5 in docs from before 1.1;
  - 3.6 in the current Steam modding guide (GodotSteam v3.28);
  - a custom 3.7-dev build according to a 2026 log cited in `brotato-modding`.

  The networking API is the same across 3.5-3.7. Write Godot 3 GDScript only. The newest patch seen in mods is
  1.1.15.4, with ModLoader 6.2.0/6.3.0.
- **GodotSteam is compiled into the game executable.** Any mod can call the `Steam` singleton directly
  (Brotatogether does). Do not bundle the GDNative/GDExtension GodotSteam build in a mod.
- For Mod Loader, script extensions, decompiling and finding hook names, see `brotato-modding`. For Godot 3 vs 4
  syntax, see `godot3-gdscript-pitfalls`. This skill covers only netcode.

## 1. Godot 4 networking code is wrong here

| Godot 4 (does not exist in Brotato) | Godot 3 equivalent |
|---|---|
| `@rpc("any_peer", "unreliable")` | `remote func f()` (+ `master`/`puppet`/`remotesync`), then `rpc_unreliable("f")` |
| `ENetMultiplayerPeer`, `multiplayer.multiplayer_peer = p` | `NetworkedMultiplayerENet`, `get_tree().network_peer = p` |
| `multiplayer.get_unique_id()`, `multiplayer.is_server()` | `get_tree().get_network_unique_id()`, `get_tree().is_network_server()` |
| `multiplayer.get_remote_sender_id()` | `get_tree().get_rpc_sender_id()` |
| `set_multiplayer_authority()`, `is_multiplayer_authority()` | `set_network_master()`, `is_network_master()` |
| `MultiplayerSpawner`, `MultiplayerSynchronizer` | Not available. Write your own snapshot and spawn messages |
| `var_to_bytes`, `PackedByteArray`, `await`, `Callable` | `var2bytes`, `PoolByteArray`, `yield(obj, "sig")`, `connect("sig", self, "_m")` |
| `process_mode = PROCESS_MODE_ALWAYS` | `pause_mode = Node.PAUSE_MODE_PROCESS` |
| `pos.lerp(target, t)` (Vector2) | `pos.linear_interpolate(target, t)` |

## 2. Architecture (decided; don't re-litigate)

- **The host is authoritative over the simulation.** Only the host runs enemy AI, spawning, damage, deaths, drops,
  pickups, gold, XP, level-ups, shop rolls, wave timer and every gameplay RNG call. Clients are **mirrors**: they
  send intents and render snapshots.
- **Each client is authoritative over its own player's movement** (trusted co-op), sent at 20-30 Hz on an
  unreliable channel. The host clamps the reported position to the arena and to the player's max speed. Pure
  input forwarding (BroTangto) is simpler, but the client then feels the full RTT on its own character.
- **No lockstep.** Brotato's gameplay and cosmetic code share the global RNG (sound and sprite variants come from
  `Utils.get_rand_element`/`Utils.randi`), physics overlaps are frame-timed, and nodes are pooled. A deterministic
  replay is not achievable from a mod.
- **Reuse Brotato's local co-op.** Register each remote player as a fake input device in `CoopService` so the
  native co-op scenes create 2-4 players. Then feed remote movement through an override of
  `PlayerMovementBehavior.get_movement()`. Hook list: [references/brotato-hooks.md](references/brotato-hooks.md).
- **Transport:** use Steam lobbies plus Steam P2P (relayed, no port forwarding). Prefer Networking Messages
  (`sendMessageToUser`) when the game's GodotSteam build has it. Otherwise use the deprecated `sendP2PPacket`.
  Use ENet only for LAN, VPN or development. Details: [references/steam-networking.md](references/steam-networking.md).

Data flow, rates, encoding and interpolation are in [references/architecture.md](references/architecture.md).

## 3. Rules that prevent most bugs

1. **Never let a client run gameplay code on mirrored entities.** On clients, make `EntitySpawner.spawn()` a
   no-op. Replace enemy movement and attack behaviors with stubs, and return early from `take_damage()` and
   `_on_Hurtbox_area_entered()`. Never run native drop or pickup code. Otherwise you get double deaths, duplicated
   materials and crates, and "already dead" warnings.
2. **Never roll gameplay RNG on a client.** The host fills the shops (`fill_shop_items` runs only on the host),
   picks the level-up choices, resolves random characters and weapons, and sends the results as stable IDs.
3. **Identify entities by host-assigned network IDs.** Never use `get_instance_id()` (it's local to the
   process), node names (Godot auto-renames to `@Enemy@123`) or array order. Brotato pools nodes: assign a fresh
   ID every time the host spawns or reuses a pooled node, not only in `_ready()`.
4. **Identify content by `my_id`**, never by `resource_path` or index. Serialize items, weapons and characters as
   `my_id` strings (plus `is_cursed` for Abyssal Terrors). Send a compact u16 type index when bandwidth matters.
5. **Never send Objects or Resources.** `bytes2var` decodes objects only with `allow_objects=true`, and RPC only
   with `allow_object_decoding`. Leave both off, because they allow remote code execution.
6. **Give the network node `pause_mode = Node.PAUSE_MODE_PROCESS`**, and call `Steam.run_callbacks()` every
   frame. Otherwise a paused tree stops packet reads, timeouts fire and reliable queues back up.
7. **Disable Brotato's auto-pause in online play.** Override `on_game_lost_focus()` in the pause menu and
   `_check_for_pause()` in `main.gd`. Otherwise an alt-tab on the host freezes everyone.
8. **Apply snapshots outside physics callbacks.** Use `call_deferred`/`set_deferred` when adding or removing
   Area2D or collision nodes. The engine error is `Can't change this state while flushing queries. Use
   call_deferred() or set_deferred() to change monitoring state instead.`
9. **Tag every message with the scene epoch** (incremented on every host scene change). Drop stale messages,
   because a packet for the old scene that arrives after `change_scene()` touches freed nodes.
10. **Use stable player slots.** The host keeps a `steam_id -> slot` table and broadcasts it. Never use the
    lobby member index, because it shifts when someone leaves (Brotatogether indexes by it).
11. **Keep snapshots small and unreliable.** Old P2P allows at most 1200 bytes per unreliable packet.
    Networking Messages can send more, but if any fragment is lost the whole message is dropped. Send spawns,
    despawns, purchases and phase changes reliably, and positions unreliably.
12. **Version-gate the lobby.** Put the protocol version, game version, hash of the sorted mod list and DLC
    ownership in the lobby data, filter on them, and re-check on join.

## 4. Wrong vs right

```gdscript
# WRONG: default pause_mode INHERIT under /root behaves as STOP, so packets stop when the host pauses
var net = NetNode.new()
get_tree().root.call_deferred("add_child", net)
# RIGHT
var net = NetNode.new()
net.name = "MyModNet"                       # fixed name: RPC/NodePath must match on every peer
net.pause_mode = Node.PAUSE_MODE_PROCESS
get_tree().root.call_deferred("add_child", net)
# inside NetNode
func _physics_process(_delta):
	Steam.run_callbacks()                   # harmless if the game also calls it
	_drain_packets()
```

```gdscript
# WRONG: "sync" randomness by seeding the global RNG on both machines
seed(run_seed)                      # the first cosmetic randi() call on one side diverges the sequence
# RIGHT: host decides, clients receive results; mod-only rolls use a private seeded RNG
var rng := RandomNumberGenerator.new()
rng.seed = hash([run_seed, RunData.current_wave, purpose_id])  # same inputs on every peer
```

```gdscript
# WRONG: client-side purchase executes locally, then tells the host
.on_shop_item_bought(shop_item, player_index); net.send_buy(index)
# RIGHT: the client only sends an intent; the host validates (item still in that slot? gold?) and replies with state
net.send_reliable(MSG_SHOP_BUY, {"slot": player_slot, "id": shop_item.item_data.my_id, "epoch": epoch})
```

```gdscript
# WRONG: Steam ID through JSON (float, loses precision above 2^53) or a 32-bit field
var id = parse_json(text)["owner"]
# RIGHT: keep Steam IDs as int in var2bytes/StreamPeerBuffer.put_64, or as a String in lobby data
var owner_id: int = Steam.getLobbyOwner(lobby_id)
```

## 5. Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Enemies in different places on host and client | Client runs native AI or spawning, or matches enemies by name/order | Client spawner no-op, stub behaviors, host network IDs |
| Materials/crates multiply (Brotatogether reports: after a client dies), then crash | Client runs native drop/pickup, or reuses mirrored nodes from `_pool` | Drops are host events only; `queue_free()` mirrors, never pool them |
| Shop/upgrades differ between players | Client rolled its own shop or upgrade options | `fill_shop_items` and upgrade rolls run on the host only; send `my_id` lists |
| Rubber-banding in bursts, worse with more enemies | Snapshots on a reliable channel (head-of-line blocking) or over 1200 B | Unreliable snapshots, chunks of 1100 B or less, binary encoding |
| Everyone freezes when the host opens the menu or alt-tabs | Tree paused, network node not PROCESS, native auto-pause | Section 3 rules 6-7, plus a shared pause state |
| Crash when a client leaves mid-wave: `Invalid get index '2' (on base: 'Array')` | Arrays indexed by lobby member index | Stable slots; keep the slot and mark it disconnected |
| Works on LAN, not over the internet (ENet) | No NAT traversal in ENet | Steam P2P relay, or port-forward UDP, or a VPN |
| `RPC 'x' is not allowed on node ... Mode is 0` | Missing `remote`/`master`/`puppet` keyword (Godot 3) | Add the keyword, and check `get_rpc_sender_id()` |

## 6. Checklist: adding any synchronized feature

- [ ] Write down who owns the state (normally the host) and who may request changes. Clients send intents only.
- [ ] Choose the message class: **state** (unreliable, latest wins, carries a tick), **event** (reliable,
      idempotent, has an ID) or **phase** (reliable, carries the epoch, needs an ack).
- [ ] Use host-assigned network IDs for entities and `my_id` or a type index for content, never Objects or paths.
- [ ] Gate the native code path on clients: `if net.is_client(): return` before any RNG, spawn, damage, gold
      or XP change. Call the parent (`.method()`) only on the host or offline.
- [ ] Handle the epoch: drop stale messages, and buffer or ignore messages that arrive during a scene change.
- [ ] Late join and reconnect: make sure the feature's full state is included in the resync payload.
- [ ] Disconnect: decide what happens to that slot's pending state (auto-ready, refund, freeze the player).
- [ ] Pause: does the feature run while the tree is paused? If so, set `pause_mode` and use `create_timer(t, true)`.
- [ ] Size: estimate bytes × rate × players. Over 1100 B unreliable means chunk or delta-encode.
- [ ] Add the feature's values to the wave-end state hash (desync check).
- [ ] Test with two real Steam accounts, plus loss and lag simulation, plus a host alt-tab, a client
      disconnect mid-wave and a reconnect in the shop.

## References (read when needed)

- [references/architecture.md](references/architecture.md): what to sync, rates, binary snapshot code,
  interpolation, entity IDs and pooling, RNG, phases and epochs, pause, late join, desync hashing. Read before
  designing or changing the protocol.
- [references/steam-networking.md](references/steam-networking.md): GodotSteam inside Brotato, the P2P vs
  Networking Messages APIs and limits, lobbies, invites (`+connect_lobby`), NAT, the ENet fallback, testing with
  two accounts and fake lag. Read when touching transport or lobby code.
- [references/brotato-hooks.md](references/brotato-hooks.md): Brotato classes and methods that online mods
  extend (CoopService, movement, focus emulator, main, spawner, unit, coop shop, RunData), with their pitfalls.
  Read before writing script extensions.
- [references/qol-features.md](references/qol-features.md): pitfalls for pause voting, ready checks, shops,
  ping display, spectating, chat, reconnect, kicks and settings sync.
- [references/existing-mods.md](references/existing-mods.md): Brotatogether (MIT) and BroTangto (no license):
  what they do, what to learn from them, and licensing limits on reusing their code.
- [references/common-issues.md](references/common-issues.md): the full symptom → cause → fix table, with engine
  error strings.
- [references/sources.md](references/sources.md): URLs, and what was read directly vs. seen only in search snippets.
