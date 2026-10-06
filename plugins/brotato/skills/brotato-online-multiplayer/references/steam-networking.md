# Steam and transport

## 1. GodotSteam inside Brotato

- The game executable has GodotSteam compiled in. `Steam` is a global singleton, and mods call it directly
  (Brotatogether uses `Steam.createLobby`, `Steam.sendP2PPacket` and the rest with no loader). This is also why a
  decompiled Brotato project only runs in the GodotSteam editor build.
- The exact build is not published. The current Steam modding guide points to GodotSteam **v3.28** for Godot 3.6.
  A third-party mod plan names `win64-g36-s161-gs328`, meaning Godot 3.6, Steamworks SDK 1.61, GodotSteam 3.28
  (unverified). **Feature-detect** instead of assuming:
  ```gdscript
  var has_messages: bool = Steam.has_method("sendMessageToUser")
  # Call optional APIs through call(): the Godot 3 parser rejects a missing method at load time with
  # 'The method "sendMessageToUser" isn't declared on base "Steam".' and the whole script fails.
  Steam.call("sendMessageToUser", remote_id, bytes, flags, channel)
  ```
- Don't call `Steam.steamInit()`, because the game has already initialized Steam. Its signature and return type
  changed in GodotSteam 3.29: it now returns a bool and the first argument was removed; earlier versions return a
  Dictionary. Before networking, check `Steam.loggedOn()`.
- `Steam.run_callbacks()` must run every frame, or `lobby_created`, `lobby_joined` and the session signals never
  fire. Call it from your PROCESS-mode network node. A second call per frame is harmless.
- Non-Steam builds (Game Pass/Xbox PC, consoles, mobile) have no `Steam`. A script that names `Steam` there fails
  with `The identifier "Steam" isn't declared in the current scope.` Isolate the Steam code in its own script,
  load it only when `Engine.has_singleton("Steam")` is true, and fall back to ENet or disable online play.
- GodotSteam moved from GitHub to Codeberg in 2026. The GitHub repo is archived and old release links are dead.
  Look for builds at codeberg.org/godotsteam.

## 2. Old P2P vs Networking Messages (GodotSteam 3.x bindings)

| | ISteamNetworking: `sendP2PPacket` | ISteamNetworkingMessages: `sendMessageToUser` |
|---|---|---|
| Status | **Deprecated** by Valve ("may be removed in a future release"). Brotatogether uses it | Valve's recommended replacement |
| Send | `sendP2PPacket(steam_id, data, send_type, channel)` → bool | `sendMessageToUser(steam_id, data, flags, channel)` → EResult int (`1` = OK) |
| Receive | `getAvailableP2PPacketSize(ch)` then `readP2PPacket(size, ch)` → `{data, remote_steam_id}`, empty Dictionary if nothing | `receiveMessagesOnChannel(ch, max)` → Array of `{payload, identity, channel, size, ...}` |
| Unreliable size | **1200 bytes maximum** (`P2P_SEND_UNRELIABLE`, `P2P_SEND_UNRELIABLE_NO_DELAY`) | Up to 512 KB, fragmented. One lost fragment drops the whole message |
| Reliable size | 1 MB (`P2P_SEND_RELIABLE`, `P2P_SEND_RELIABLE_WITH_BUFFERING`) | 512 KB (`k_cbMaxSteamNetworkingSocketsMessageSizeSend`) |
| Session request | signal `p2p_session_request(remote_steam_id)` → `acceptP2PSessionWithUser(id)` | signal `network_messages_session_request(remote_steam_id)` → `acceptSessionWithUser(id)` |
| Failure | `p2p_session_connect_fail(remote_steam_id, session_error)` | `network_messages_session_failed(reason, remote_steam_id, connection_state, debug_message)` |
| Diagnostics | `getP2PSessionState(id)` → `connection_active`, `using_relay`, `bytes_queued_for_send`, ... | `getSessionConnectionInfo(id, true, true)` → `ping`, `local_quality`, `remote_quality`, `bytes_out_per_second`, ... |
| Close | `closeP2PSessionWithUser(id)` | `closeSessionWithUser(id)` |

Rules:
- **Flags (Networking Messages):** define them yourself from the SDK values: Unreliable `0`, NoNagle `1`,
  NoDelay `4`, Reliable `8`, AutoRestartBrokenSession `32`. GodotSteam 3.29 binds a misspelled constant
  (`NETWORKING_SEND_URELIABLE_NO_NAGLE`), and the names differ between builds.
- **Nagle:** both plain Unreliable and Reliable use Nagle, which adds up to a few ms of batching. Send state with
  `Unreliable|NoNagle`. For many small reliable events per tick, send them normally and flag the last one with
  NoNagle.
- **Ordering:** reliable messages are ordered within one channel only. Unreliable messages can arrive out of
  order or twice, so carry a tick or sequence number.
- **First packets:** the first sends to a new peer may be delayed while NAT traversal runs. Exchange a hello in
  the lobby, before the run starts.
- **Session accept:** accept sessions only from current lobby members. Sending to a peer implicitly accepts that
  peer.
- **Sender identity:** in v3.29, `identity` in received messages is the sender's Steam ID as an int. Log one
  message to confirm the type on Brotato's build before relying on it.

## 3. Transport skeleton (Godot 3)

```gdscript
extends Node                 # added under /root; pause_mode = PAUSE_MODE_PROCESS

const CH_CONTROL := 0        # reliable, ordered: events, phases, shop, chat
const CH_STATE := 1          # unreliable: snapshots, own-player movement, ping
const F_UNRELIABLE := 0
const F_NO_NAGLE := 1
const F_RELIABLE := 8
var use_messages := false
var members := []            # steam ids from the lobby, excluding self

func _ready() -> void:
	pause_mode = Node.PAUSE_MODE_PROCESS
	if not Steam.loggedOn():
		return
	use_messages = Steam.has_method("sendMessageToUser")
	if use_messages:
		Steam.connect("network_messages_session_request", self, "_on_session_request")
	else:
		Steam.connect("p2p_session_request", self, "_on_session_request")

func send(to: int, bytes: PoolByteArray, reliable: bool) -> void:
	var ch := CH_CONTROL if reliable else CH_STATE
	if use_messages:
		var flags := F_RELIABLE if reliable else (F_UNRELIABLE | F_NO_NAGLE)
		var res: int = Steam.call("sendMessageToUser", to, bytes, flags, ch)
		if res != 1:
			push_warning("sendMessageToUser EResult %d" % res)
	elif not reliable and bytes.size() > 1200:
		push_error("unreliable P2P packet of %d B exceeds 1200 B; chunk it" % bytes.size())
	else:
		Steam.sendP2PPacket(to, bytes, Steam.P2P_SEND_RELIABLE if reliable else Steam.P2P_SEND_UNRELIABLE, ch)

func _physics_process(_delta: float) -> void:
	Steam.run_callbacks()
	for ch in [CH_CONTROL, CH_STATE]:
		if use_messages:
			for m in Steam.call("receiveMessagesOnChannel", ch, 128):
				_dispatch(int(m["identity"]), m["payload"], ch)
		else:
			var size: int = Steam.getAvailableP2PPacketSize(ch)
			while size > 0:
				var p: Dictionary = Steam.readP2PPacket(size, ch)
				if p.empty():
					break
				_dispatch(p["remote_steam_id"], p["data"], ch)
				size = Steam.getAvailableP2PPacketSize(ch)

func _on_session_request(remote_id: int) -> void:
	if remote_id in members:                       # ignore strangers
		if use_messages:
			Steam.call("acceptSessionWithUser", remote_id)
		else:
			Steam.acceptP2PSessionWithUser(remote_id)

func _dispatch(sender: int, bytes: PoolByteArray, ch: int) -> void:
	if not sender in members:
		return
	# decode header (type, epoch, seq), reject host-only types unless sender == host_id, route by type
```

- Drain packets every frame, including during scene changes. Unread packets pile up in Steam's queue.
- Don't poll 30+ channels per frame (Brotatogether polls one channel per message type). Put a type byte in the
  header instead.
- Never send to your own Steam ID. Brotatogether warns "Attempting to send data to myself". When the local
  player is the host, handle loopback in code.

## 4. Lobbies

- Create the lobby with `Steam.createLobby(Steam.LOBBY_TYPE_FRIENDS_ONLY, 4)`. Brotato's co-op has 4 slots
  (Brotatogether uses `LOBBY_TYPE_PUBLIC` plus a lobby browser). In `lobby_created(connect, lobby_id)`, continue
  only if `connect == 1`.
- Set these lobby data keys right after creation:

  | Key | Value |
  |---|---|
  | `mod` | your unique mod tag |
  | `proto` | protocol int |
  | `game_ver` | game version |
  | `mods` | hash of the sorted `id@version` mod list |
  | `dlc` | DLC flags |
  | `host` | host Steam ID as a String |
  | `state` | `lobby` or `in_run` |

  Every Brotato mod shares App ID 1942280, so the lobby list contains other mods' lobbies too.
- `requestLobbyList()` filters are cleared after each request. Re-add `addRequestLobbyListStringFilter("mod", ...)`,
  the `proto` filter and `addRequestLobbyListDistanceFilter(Steam.LOBBY_DISTANCE_FILTER_WORLDWIDE)` before every
  call. Without the worldwide filter, friends in other regions don't show up.
- In `lobby_joined(lobby, permissions, locked, response)`, continue only if
  `response == Steam.CHAT_ROOM_ENTER_RESPONSE_SUCCESS`. Then compare `proto`, `mods` and `dlc` before
  changing scene. Brotatogether jumps straight to character selection.
- Use `setLobbyMemberData(lobby, key, value)` for per-member info (mod hash, DLC ownership, ready flag). It is
  readable before any P2P session exists.
- In `lobby_chat_update(lobby_id, changed_id, making_change_id, chat_state)`, treat `CHAT_MEMBER_STATE_CHANGE_LEFT`,
  `_DISCONNECTED`, `_KICKED` and `_BANNED` all as "gone". Brotatogether reacts only to LEFT, and only when the host
  leaves.
- When the run starts, call `setLobbyJoinable(lobby_id, false)` and set `state=in_run`. Reopen in the shop only
  if you support rejoining.
- **Steam lobby ownership is not your game host.** When the owner leaves, Steam promotes another member to lobby
  owner. The simulation state left with the host, so end the session for everyone (no host migration). Compare
  against the `host` lobby data key, not `getLobbyOwner()`.
- Use `sendLobbyChatMsg` for chat text only. It goes through Steam's servers and is rate-limited, so never send
  game data through it.

## 5. Invites and joining from Steam

- In-game invite button: `Steam.activateGameOverlayInviteDialog(lobby_id)` opens the overlay, or
  `Steam.inviteUserToLobby(lobby_id, friend_id)`. The overlay requires the game to be launched through Steam.
- When the game is already running and the player accepts an invite or clicks "Join Game", the signal
  `join_requested(lobby_id, steam_id)` fires. Call `Steam.joinLobby(lobby_id)`. Connect this signal in your
  autoload so it works from every menu.
- When the game is not running, Steam launches it with `+connect_lobby <64-bit lobby id>`. Read
  `OS.get_cmdline_args()` once the main menu is ready, not during Mod Loader init. If the local player is in a
  solo run, ask before abandoning it.
- With rich presence, `Steam.setRichPresence("connect", "+connect_lobby %d" % lobby_id)` makes "Join Game" work
  from the friends list. Joins through that path arrive as `join_game_requested(user, connect)`.
- Keep the lobby ID as an int, or as a String in lobby data. It is 64-bit: JSON parses it into a float and
  corrupts it.

## 6. NAT, relay, ENet fallback

- Steam P2P traverses NAT and falls back to Valve's relays automatically. No port forwarding is needed.
  `getP2PSessionState(id)["using_relay"]` shows when a relay is in use (expect more latency).
- Godot 3 ENet has **no NAT traversal**: direct IP works on LAN, and over the internet only with a UDP port
  forward or a VPN. BroTangto requires Radmin VPN and UDP 9000.

```gdscript
# Godot 3 ENet host/client (dev, LAN, VPN)
var peer := NetworkedMultiplayerENet.new()
var err := peer.create_server(9000, 3)          # 3 clients + host = 4 slots
# client: peer.create_client(ip, 9000)
if err != OK:
	push_error("ENet create failed: %d" % err)      # ERR_CANT_CREATE: port in use or blocked
get_tree().network_peer = peer
peer.refuse_new_connections = true              # once the run starts
get_tree().connect("network_peer_disconnected", self, "_on_peer_gone")
get_tree().connect("server_disconnected", self, "_on_host_gone")

remote func client_intent(kind: int, payload: Dictionary) -> void:
	var sender := get_tree().get_rpc_sender_id()   # validate: map sender -> slot, never trust payload slot
	...
puppet func host_state(bytes: PoolByteArray) -> void:   # only the master (host, id 1) may call it
	...
```

- The RPC node must have the same NodePath on every peer. Mod nodes under `/root` need a fixed, unique name
  set before `add_child`. If two nodes share a name, Godot renames one (`@Name@2`), and the result is
  `Invalid packet received. Requested node was not found.` / `Failed to get path from RPC`.
- Call RPCs only while connected. Otherwise you get `Trying to call an RPC while no network peer is active.`
  or `... via a network peer which is not connected.`
- `rpc_unreliable` with a large Dictionary is fragmented by ENet. One lost fragment drops the whole packet.

## 7. Development and testing

- **Editor runs:** a decompiled project run from the GodotSteam editor needs the App ID 1942280 for Steam to
  initialize. Use `steam_appid.txt` in the project root (GodotSteam convention). A third-party note says Brotato
  ships a `steam_data.json` that you copy to the project root (unverified). The shipped game is always launched
  through Steam, and a mod zip cannot provide these files.
- **Two accounts:** Steam P2P cannot connect to your own Steam ID, so you need two accounts on two machines (or a
  VM), each with its own Brotato license. One copy can't be played by two family members at the same time.
- **Solo test mode:** Brotatogether's `is_solo_test` makes the host queue its own snapshots for about 100 ms
  and apply them to "ghost" mirrors in the same process, with collisions disabled. This catches most
  serialization and mirror bugs without a second machine.
- **Fake network conditions (Networking Messages / SteamNetworkingSockets stack):**
  ```gdscript
  Steam.setGlobalConfigValueFloat(Steam.NETWORKING_CONFIG_FAKE_PACKET_LOSS_SEND, 5.0)   # percent
  Steam.setGlobalConfigValueInt32(Steam.NETWORKING_CONFIG_FAKE_PACKET_LAG_SEND, 80)     # ms
  ```
  For old P2P and ENet, use an OS-level tool (e.g. clumsy on Windows).
- **Logs:** `%APPDATA%\Brotato\logs\godot.log`. Prefix your mod's lines (e.g. `[MyMod]`) and log the epoch, tick,
  message type and sender on errors.
- **Mod parity:** both players need byte-identical mod zips. BroTangto publishes a SHA256 for its zip, and stale
  older zips in the Workshop folder also get loaded. Enforce this through the lobby `mods` hash.
