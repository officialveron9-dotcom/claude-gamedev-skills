# Symptom → cause → fix (Brotato online co-op, Godot 3.x)

Engine error strings are quoted from the Godot 3.6 source. GodotSteam behavior is from v3.29 bindings.
"(reported)" marks symptoms seen in user reports of existing mods.

## Desync and simulation

| Symptom | Cause | Fix |
|---|---|---|
| Enemies stand in different places on host and client | Native AI still runs on client mirrors, or the client matches enemies by name or order | Replace `MovementBehavior`/`AttackBehavior` with stubs on clients, and map by host network ID |
| Client has extra enemies, or enemies that never move | Client spawner or `EntityBirth` completes natively | `EntitySpawner.spawn()` is a no-op on clients. Mirror births and spawns from host events |
| An enemy occasionally "teleports" across the map | A pooled node was reused with its old network ID (ID assigned in `_ready()`) | Assign a new ID on every host spawn or pool reuse |
| Dead enemies stay on the client screen | The death event was sent unreliably, or despawn relies on "absent from snapshot" with chunked or throttled snapshots | Reliable, batched death and despawn events. Reconcile the full ID set once per second |
| `die()` twice, "already dead" warnings, double death effects | Client `take_damage()` or hurtbox still active | Return early in `take_damage()` and `_on_Hurtbox_area_entered()` on clients |
| Materials, crates or heals multiply, then a crash (reported: Brotatogether, after a non-host player dies) | Client runs native drop or pickup code, or mirrors go back into the game's `_pool` | Drops and pickups are host events only. `queue_free()` mirrors in the `add_node_to_pool` override |
| Shop offers differ between host and client | The client ran `fill_shop_items` (RNG) itself | Run it on the host only, and send each player's offers as `my_id` lists |
| Buying gives a different item than the one clicked | Buy by index after the lists diverged | Send `my_id` + index. The host rejects mismatches, and the client shows "pending" until it confirms |
| Level-up choices or reroll results differ | Client rolled the options | The host rolls them and sends IDs |
| Gold, XP or level differ after a wave | Client applies pickups or purchases locally, or applies an event twice | Host-authoritative values in snapshots, idempotent events, a wave-end state hash |
| Wave number off by one on a client | Both sides do `current_wave += 1` on different paths | Set the wave from the phase message payload |
| Random character or weapon differs | `Utils.get_rand_element` ran on every peer | The host resolves it and broadcasts the concrete `my_id` |
| Desync within seconds even though both sides seeded the RNG | Cosmetic code (sound variants, sprite picks) consumes the global RNG at frame-dependent times | No lockstep. Host authority. Mod-only rolls use a private seeded `RandomNumberGenerator` |
| State hash mismatches although values look equal | Floats or unsorted Dictionary/Array order in the hash | Hash ints and strings only, and sort lists first |
| A client's stats are doubled after a purchase | Client ran the native purchase **and** received the host's inventory | The client sends an intent and never calls the parent purchase method |

## Latency, smoothness, bandwidth

| Symptom | Cause | Fix |
|---|---|---|
| Rubber-banding in bursts, worse with many enemies | Reliable snapshots: one lost packet stalls all later ones (head-of-line blocking) | Unreliable snapshots with tick numbers. Reliable only for events and phases |
| Unreliable packets silently never arrive | Old P2P unreliable packet over **1200 bytes** (hard limit) | Chunks of 1100 bytes or less, binary encoding, check the size before sending |
| Large unreliable Networking Message never arrives under loss | Message fragmented, and one lost fragment drops it | Keep state messages around one MTU, or chunk them |
| Full resync or reconnect payload fails | Over 1 MB (old P2P reliable) or 512 KB (Messages reliable) | Split and compress (`PoolByteArray.compress(File.COMPRESSION_GZIP)`) |
| Remote players and enemies jitter | Positions snapped at 20-30 Hz on a 60+ Hz display | Interpolate in `_process` (`linear_interpolate`), snap only beyond a teleport threshold |
| Own player snaps back every few frames | Client applies the host snapshot to its own player | Skip the local slot when applying snapshots |
| Remote player keeps running after a lag spike | Last movement vector stays applied | Host watchdog: zero the movement after about 150 ms without an update |
| Host FPS drops in late waves only when online | Per-tick string-keyed Dictionary per entity, plus gzip, in GDScript | `StreamPeerBuffer` binary, entity registry, 10-15 Hz plus round-robin above about 250 enemies. Profile send time |
| First seconds of a match laggy, or the first messages lost | NAT traversal on the first send. `NoDelay` sends are dropped while connecting | Exchange a hello during the lobby phase, so the session is up before the run |

## Pause and scene flow

| Symptom | Cause | Fix |
|---|---|---|
| Everyone freezes when the host opens the pause menu | Tree paused, and the network node has the default `pause_mode` (behaves as STOP under `/root`) | `pause_mode = Node.PAUSE_MODE_PROCESS` on the network node. Use a shared pause message |
| Game pauses when the host alt-tabs or unplugs a controller | Brotato's native auto-pause (`on_game_lost_focus`, `_check_for_pause`) | Override both while online |
| Clients time out during a pause | `Steam.run_callbacks()` and heartbeats stop with the paused tree | Same as above. Pause-aware timeouts |
| Client jumps to the shop early or late | Client's wave or end-wave timer runs the native transition | No-op `_on_WaveTimer_timeout` and `_on_EndWaveTimer_timeout` on clients. Change scene only on a host phase message |
| Client takes invisible damage at wave start, or starts mid-wave | The host started the wave before the client finished loading | Load barrier: `LOADED(epoch)` from every slot before the host starts `_wave_timer` |
| `Attempt to call function '...' in base 'previously freed instance' on a null instance.` after a scene change | Packets for the old scene processed after `change_scene()` | Epoch in every message, drop stale ones, `is_instance_valid()` on cached nodes |
| `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead.` | Adding or removing Area2D/collision nodes while applying a snapshot inside a physics callback | `call_deferred("add_child", ...)`, `set_deferred("monitoring", false)` |
| Client misses a phase change and stays in the old scene | The one-shot transition message was lost or arrived out of order | Reliable phase on the control channel, plus the desired scene and epoch in every snapshot |

## Connection, lobby, transport

| Symptom | Cause | Fix |
|---|---|---|
| Crash when a client leaves mid-wave: `Invalid get index '2' (on base: 'Array').` | Slot = lobby member index; the member array shrank | Host-owned `steam_id -> slot` map. Keep the slot and mark it disconnected |
| Clients stuck when the host quits | No handling for host loss. Steam gives the lobby to another member | Compare against the `host` lobby key, end the session, clean up `CoopService` and lobby |
| Lobby browser empty for friends abroad | Default distance filter; filters reset after each request | Add `LOBBY_DISTANCE_FILTER_WORLDWIDE` and your string filters before every `requestLobbyList()` |
| Joined a lobby of another mod or version, then a crash | All Brotato mods share App ID 1942280 | Filter on `mod` and `proto`, and verify the `mods` hash and DLC on join |
| `lobby_created`/`lobby_joined` signals never fire | `Steam.run_callbacks()` is not called, or its node is paused | Call it every frame from the PROCESS-mode node |
| Accepting an invite while the game is closed does nothing | `+connect_lobby <id>` launch argument not handled | Parse `OS.get_cmdline_args()` after the main menu is ready. Also handle `join_requested` |
| Works on LAN, not over the internet (ENet) | ENet has no NAT traversal | Use Steam P2P, or forward the UDP port, or use a VPN (BroTangto: Radmin, UDP 9000) |
| `create_server` returns `ERR_CANT_CREATE` | Port in use (second instance) or blocked | Other port, check the firewall, close the old peer (`close_connection()`) |
| `RPC 'f' is not allowed on node /root/X from: N. Mode is 0, master is 1.` | Function lacks the `remote`/`puppet`/`master` keyword (Godot 3) | Add the keyword, and validate `get_tree().get_rpc_sender_id()` |
| `Invalid packet received. Requested node was not found.` / `Failed to get path from RPC` | NodePath differs between peers (auto-renamed `@Name@2`, created later) | Fixed unique names under `/root`. Create the node before connecting |
| `Trying to call an RPC while no network peer is active.` | RPC after a disconnect or before connecting | Guard with `get_tree().has_network_peer()` and the connection status |
| RPC argument arrives as null / `Invalid packet received. Unable to decode RPC argument.` | An Object or Resource was sent | Send `my_id` or network IDs. Keep `allow_object_decoding` off |
| Steam IDs or lobby IDs end in `...000` / wrong user | 64-bit ID passed through JSON (float) | Keep IDs as int (`put_64`) or as a String |
| Script fails to load: `The method "sendMessageToUser" isn't declared on base "Steam".` | The game's GodotSteam build lacks the API (parse-time check) | `Steam.has_method(...)` plus `Steam.call(...)`, with a fallback to `sendP2PPacket` |
| `The identifier "Steam" isn't declared in the current scope.` | Non-Steam build, or the editor is not the GodotSteam build | Isolate Steam code behind `Engine.has_singleton("Steam")`. Use the GodotSteam editor |
| Mod behaves differently on two PCs | Different zip versions, or a stale zip still in the Workshop folder | Lobby `mods` hash, identical zips (BroTangto ships a SHA256) |
| Client without Abyssal Terrors crashes when the host picks DLC content | DLC resources missing on the client | DLC flags in member data. The host disables DLC content if anyone lacks it |
| Typing in chat moves the shop cursor or the player | Focus emulator and gameplay input still active | Return `false` from the focus emulator while a `LineEdit` has focus |
| The next solo run has phantom players | Fake co-op devices not cleared after leaving | `CoopService.clear_coop_players()` and reset the co-op flags on session end |
| Host's keyboard also moves a remote player | Remote device not filtered in `Utils.is_player_action_*` / `CoopService` | Return `false` for remote devices in the input hooks |
