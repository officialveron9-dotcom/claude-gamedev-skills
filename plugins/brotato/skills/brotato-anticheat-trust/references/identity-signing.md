# Identity, auth tickets, replay protection, signing

Godot 3 GDScript, GodotSteam 3.x compiled into Brotato (`Steam` singleton). Names verified in GodotSteam v3.29
source unless marked (verify). Brotato's exact build is unpublished; feature-detect with `Steam.has_method()`.

## 1. Where the sender identity comes from

| Transport | Identity | Trust | Do |
|---|---|---|---|
| Networking Messages `receiveMessagesOnChannel` | `m["identity"]` (int Steam ID in v3.29) | Authenticated by Steam (Sockets/Messages: "if a Steam ID is authenticated, someone with access to that account authorized the connection"; impersonation needs the victim's machine) | Use it as `sender`; log its type once |
| Old P2P `readP2PPacket` | `p["remote_steam_id"]` | Provided by Steam's session, not by the packet; weaker documentation (verify) | Use it; accept sessions only from lobby members |
| ENet RPC | `get_tree().get_rpc_sender_id()` (peer int) | None: anyone on the port can claim anything | Development only, or add HMAC (§5) |
| Lobby data / member data | `getLobbyMemberData(lobby, steam_id, key)` | Steam attributes it to the member; content is self-reported | Fine for public keys and flags |

Rules:
- The `slot`, `steam_id` or `player_index` **inside** a payload is never trusted. Map `sender → slot` on the host
  and `sender == host_id` for host-only message types on clients. Drop and log the rest.
- Keep the host identity from the lobby data key `host` (set at creation), not from `getLobbyOwner()`.
- Never send to or accept from a Steam ID that is not in the current member set and not banned.

## 2. Steam auth session tickets (mutual, at join)

What a validated ticket proves: this Steam ID is online right now, owns the app (or borrows it: `owner_id !=
auth_id`), is not VAC- or publisher-banned, and the ticket was issued for you (identity-bound tickets) and not
reused. It proves nothing about mod files.

Flow (every peer validates every other peer; with 4 players that is 3 tickets each):

```gdscript
var _my_tickets := {}      # remote_id -> ticket Dictionary {id, buffer, size}
var _auth_state := {}      # remote_id -> "pending" | "ok" | "fail:<n>" | "shared" | "offline"

func _ready() -> void:
	Steam.connect("get_auth_session_ticket_response", self, "_on_my_ticket")
	Steam.connect("validate_auth_ticket_response", self, "_on_peer_validated")

func send_ticket_to(remote_id: int) -> void:
	# v3.29: getAuthSessionTicket(remote_steam_id = 0). Passing the remote ID binds the ticket to that peer
	# (SDK: "if a Steam ID is passed Steam will only allow the ticket to be used by that Steam ID").
	# Older 3.x builds take no argument: call() with no args keeps the script parsing everywhere.
	var t: Dictionary = Steam.call("getAuthSessionTicket")
	if t.empty() or int(t.get("size", 0)) == 0:
		push_warning("no auth ticket (Steam offline?)")
		return
	_my_tickets[remote_id] = t
	# wait for _on_my_ticket before sending: the buffer is final only after the callback

func _on_my_ticket(handle: int, result: int) -> void:
	if result != Steam.RESULT_OK:                       # k_EResultOK == 1
		push_warning("auth ticket failed: %d" % result)
		return
	for remote_id in _my_tickets:
		var t: Dictionary = _my_tickets[remote_id]
		if int(t.get("id", t.get("handle", -1))) == handle:  # key is "id" in v3.29 (verify on Brotato's build)
			var buf: PoolByteArray = t["buffer"].subarray(0, int(t["size"]) - 1)   # trim the 1024 B buffer
			net.send_reliable(remote_id, MSG_AUTH_TICKET, {"buf": buf, "size": buf.size()})

func _on_auth_ticket_msg(sender: int, msg: Dictionary) -> void:
	if _auth_state.has(sender):
		Steam.endAuthSession(sender)                    # else BEGIN_AUTH_SESSION_RESULT_DUPLICATE_REQUEST (2)
	var r: int = Steam.beginAuthSession(msg["buf"], int(msg["size"]), sender)
	_auth_state[sender] = "pending" if r == Steam.BEGIN_AUTH_SESSION_RESULT_OK else "fail:%d" % r

func _on_peer_validated(auth_id: int, response: int, owner_id: int) -> void:
	# (Godot 3 `match` also accepts `Steam.X` patterns; if/elif keeps the multi-code branches readable)
	if response == Steam.AUTH_SESSION_RESPONSE_OK:
		_auth_state[auth_id] = "shared" if owner_id != auth_id else "ok"
	elif response == Steam.AUTH_SESSION_RESPONSE_USER_NOT_CONNECTED_TO_STEAM \
			or response == Steam.AUTH_SESSION_RESPONSE_AUTH_TICKET_CANCELED:
		_auth_state[auth_id] = "offline"                 # fires LATER too: grace 30 s, then treat as disconnected
	elif response == Steam.AUTH_SESSION_RESPONSE_VAC_BANNED \
			or response == Steam.AUTH_SESSION_RESPONSE_PUBLISHER_ISSUED_BAN:
		_auth_state[auth_id] = "fail:%d" % response      # host: refuse the slot; clients: toast
	else:
		_auth_state[auth_id] = "fail:%d" % response

func on_peer_left(remote_id: int) -> void:
	Steam.endAuthSession(remote_id)
	if _my_tickets.has(remote_id):
		Steam.cancelAuthTicket(int(_my_tickets[remote_id].get("id", 0)))
		_my_tickets.erase(remote_id)
```

Response codes (`EAuthSessionResponse`, SDK comments): 0 OK; 1 user not connected to Steam; 2 no license or
expired; 3 VAC banned; 4 logged in elsewhere; 5 VAC check timed out; 6 ticket cancelled by issuer; 7 ticket already
used; 8 ticket not from a connected user instance; 9 publisher-issued ban; 10 network identity in the ticket does not
match the validator. `beginAuthSession` results: 0 OK, 1 invalid ticket, 2 duplicate request, 3 invalid version,
4 game mismatch, 5 expired.

DLC: after a successful validation, `Steam.userHasLicenseForApp(auth_id, DLC_APP_ID)` returns
`USER_HAS_LICENSE_RESULT_HAS_LICENSE` (0), `DOES_NOT_HAVE_LICENSE` (1) or `NO_AUTH` (2, no session). Use it instead of
the self-reported `dlc` lobby key for Abyssal Terrors gating (DLC app ID: look it up on SteamDB; verify how borrowed
copies report).

Pitfalls: nothing works in the editor or without `Steam.run_callbacks()`; one ticket per remote peer, cancel it on
leave; a ticket bound to peer A fails for peer B with response 10; `getAuthSessionTicket` with an argument on a
build that doesn't take one is a **parse error** that kills the script, so use `Steam.call()`.

## 3. Replay protection

Envelope (sibling: `u8 type, u8 epoch, u16 seq`) plus a **session nonce**:

- At lobby lock the host draws `session_nonce` (8 random bytes) and sends it with `SEED_ROUND`. Every reliable
  control message carries `u32 nonce_low` (or the full 8 bytes when size doesn't matter). Drop messages with a
  foreign nonce: packets recorded from a previous session cannot be replayed into this one.
- `seq` is per sender and per type; keep the last seen value per `(sender, type)` and drop `seq <= last` for
  "latest wins" state, and duplicates for events. Reset on epoch change.
- Events carry an event ID (`sender, type, seq`) and are idempotent, so a reliable retransmit after a reconnect is
  harmless (sibling rule).

## 4. Signing (RSA) for wave hashes and the run log

Keys are per installation, self-generated, exchanged through lobby member data (limit `k_cubChatMetadataMax` =
8192 bytes; a 2048-bit public key PEM is ~450 bytes). They bind to the Steam ID only through the transport that
delivered them. Enough for "the same peer who sat in this lobby signed this".

```gdscript
var crypto = null
var my_key: CryptoKey = null

func crypto_init() -> bool:
	if not ClassDB.class_exists("Crypto"):
		return false
	crypto = Crypto.new()
	if crypto == null:                                  # engine built without mbedtls
		return false
	my_key = CryptoKey.new()
	var path := "user://%s/peer_key.key" % MOD_ID
	if my_key.load(path) != OK:
		my_key = crypto.generate_rsa(2048)              # slow: do it once, at the main menu, not in the lobby
		my_key.save(path)
	return true

func publish_pubkey(lobby_id: int) -> void:
	var pem: String = my_key.save_to_string(true).replace("\r", "")   # public_only = true
	Steam.setLobbyMemberData(lobby_id, "pub", pem)

func peer_pubkey(lobby_id: int, steam_id: int) -> CryptoKey:
	var k := CryptoKey.new()
	var pem: String = Steam.getLobbyMemberData(lobby_id, steam_id, "pub")
	return k if pem != "" and k.load_from_string(pem, true) == OK else null

func sign_digest(digest: PoolByteArray) -> PoolByteArray:
	return crypto.sign(HashingContext.HASH_SHA256, digest, my_key)

func verify_digest(digest: PoolByteArray, sig: PoolByteArray, key: CryptoKey) -> bool:
	return key != null and crypto.verify(HashingContext.HASH_SHA256, digest, sig, key)
```

Sign **digests of canonical bytes** (`sha256(canon(parts))`), never JSON text: `JSON.print` float formatting,
`\r\n` and locale differences are why "valid on Windows, invalid on Linux" happens. Snapshot the public keys at
lobby lock; a peer that changes its `pub` mid-run is a finding.

## 5. HMAC for ENet or extra-cheap per-message MACs (optional)

```gdscript
# pairwise key: 32 random bytes encrypted to the peer's RSA public key (Crypto.encrypt / Crypto.decrypt)
func mac(key: PoolByteArray, msg: PoolByteArray) -> PoolByteArray:
	return crypto.hmac_digest(HashingContext.HASH_SHA256, key, msg)   # or HMACContext.start/update/finish

func check_mac(key: PoolByteArray, msg: PoolByteArray, received: PoolByteArray) -> bool:
	return crypto.constant_time_compare(mac(key, msg), received)
```

Skip it on Steam transports: identity is already authenticated and traffic encrypted. On ENet, MAC the control
channel only (32 B per message); snapshots stay unauthenticated.

## 6. What not to bother with

- Per-packet RSA signatures (256 B + ms each), encrypting payloads (Steam does), obfuscating the mod, process or
  window-name scans, reading other processes' memory, Steam Web API calls from the client (needs a publisher key),
  trusting `mods`/`dlc` lobby data as proof, and any "verified" claim that was not computed from peer signatures.
