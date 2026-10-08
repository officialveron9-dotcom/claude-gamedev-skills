# Ranking without a server: the witness model

Godot 3 GDScript. No server, no Web API, no Steam leaderboard (SKILL.md §9 says why). Everything below runs on the
players' machines and is shown only to people who are in the lobby right now.

## 1. What a viewer may trust

| Record source | Label | Rule |
|---|---|---|
| Own history, `verified == true` | **verified** | The viewer was a participant and all peers confirmed the final state at run end |
| Own history, `verified == false` | **unverified** (+ reasons) | Played, but the run was invalidated (SKILL.md §7) |
| Received from a present peer `W` | **verified by W** | `W` is in `players`, `W`'s auth ticket is `ok` on this machine, every `sigs[p]` verifies against the pinned key of `p`, and `W` signed `sha256(hash ‖ session_nonce)` now |
| Received, any check fails | **unverified** | Shown greyed; never counted as a best |
| Received, a `players` entry has a pinned key that differs from `pubs[p]` | **mismatch** | Reinstall or impersonation; both mean "cannot verify". Keep the old pin |
| Received from a peer not in `players` | dropped | Forwarding is not vouching |

A colluding group can still forge records among themselves (SKILL.md §8). A single player cannot forge the other
participants' signatures, and nobody can show a viewer a record without a participant present to vouch for it.

## 2. Run record

```gdscript
# One JSON object per line in user://<mod>/history.jsonl. Ints that can exceed 2^53 (Steam IDs, seeds) are
# strings: Godot 3 JSON parses every number as float. canon(log) is hashed; the JSON is only storage.
func build_record(won: bool) -> Dictionary:
	var players := []
	for id in members:                                  # sorted Steam IDs (ints) from lobby lock
		players.append(str(id))
	var log := ["brotato-run-v1", run_seed, members, 1 if won else 0, RunData.current_wave,
		int(run_duration_sec), difficulty_id, zone_id, versions_list(), char_list()]   # ints/strings only
	var h := SeedRound.sha256(Canon.canon(log))
	return {"v": 1, "hash": h.hex_encode(), "seed": str(run_seed), "players": players,
		"char": char_dict(), "wave": RunData.current_wave, "won": won, "duration": int(run_duration_sec),
		"difficulty": difficulty_id, "zone": zone_id, "versions": versions_dict(),
		"verified": not run_state.invalid, "reasons": run_state.reasons.duplicate(),
		"sigs": {}, "pubs": {}}                           # filled by §4
```

`canon(log)` must be rebuilt from the record's fields by a verifier (`record_to_log(r)`), so every value that
goes into `log` is also stored in the record, in a fixed order. Bump `v` when the order or the fields change.

## 3. Keys: persistence and pinning

```gdscript
# keys.gd
const KEY_PATH := "user://%s/peer_key.key"
const PINS_PATH := "user://%s/pinned_keys.json"      # "steam_id" -> PEM
var crypto = null
var my_key: CryptoKey = null
var pins := {}

func init(mod_id: String) -> bool:
	if not ClassDB.class_exists("Crypto"):
		return false
	crypto = Crypto.new()
	if crypto == null:                                 # engine without mbedtls: no signatures, no verified history
		return false
	var path := KEY_PATH % mod_id
	my_key = CryptoKey.new()
	if my_key.load(path) != OK:
		my_key = crypto.generate_rsa(2048)             # once, at the main menu; measure, it takes a moment
		_save_key(path)
	_load_pins(PINS_PATH % mod_id)
	return true

func _save_key(path: String) -> void:                  # tmp + rename, as brotato-ui-qol prescribes
	var dir := Directory.new()
	dir.make_dir_recursive(path.get_base_dir())
	if my_key.save(path + ".tmp") == OK:
		dir.rename(path + ".tmp", path)               # Windows removes the old file first; .tmp left on crash

func my_pub_pem() -> String:
	return my_key.save_to_string(true).replace("\r", "")

func pin(steam_id: int, pem: String) -> String:        # call only after validate_auth_ticket_response == OK
	var k := str(steam_id)
	if pem == "":
		return "missing"
	if pins.has(k) and pins[k] != pem:
		return "mismatch"                              # keep the old pin; label all their records mismatch
	if not pins.has(k):
		pins[k] = pem
		_save_pins()
	return "ok"

func key_of(steam_id_str: String) -> CryptoKey:
	if not pins.has(steam_id_str):
		return null
	var k := CryptoKey.new()
	return k if k.load_from_string(pins[steam_id_str], true) == OK else null
```

- The public PEM goes into lobby member data at lobby lock: `Steam.setLobbyMemberData(lobby, "pub", my_pub_pem())`
  (value ≤ 8192 B; a 2048-bit PEM is ~450 B).
- Pinning happens in `_on_peer_validated` (SKILL.md §6): the ticket proves the Steam ID, the lobby member data
  binds the key to that member, so the pin is "this Steam ID presented this key while provably logged in".
- Key loss (reinstall) is a new identity for ranking purposes. Say so in the UI; don't offer a key import.

## 4. Signing and verifying records

```gdscript
func sign_record(r: Dictionary) -> void:               # every participant, at run end
	var digest := hex_to_bytes(r.hash)
	var sig := crypto.sign(HashingContext.HASH_SHA256, digest, my_key)
	r.sigs[str(my_id)] = sig.hex_encode()
	r.pubs[str(my_id)] = my_pub_pem()
	net.broadcast_reliable(MSG_RUN_SIGN, {"hash": r.hash, "sig": sig, "pub": r.pubs[str(my_id)]})

func on_run_sign(sender: int, msg: Dictionary, r: Dictionary) -> void:
	if str(msg.hash) != r.hash or not str(sender) in r.players:
		return
	var key := keys.key_of(str(sender))                # pinned during the lobby; null → cannot verify
	if key != null and crypto.verify(HashingContext.HASH_SHA256, hex_to_bytes(r.hash), msg.sig, key):
		r.sigs[str(sender)] = msg.sig.hex_encode()
		r.pubs[str(sender)] = keys.pins[str(sender)]
	# after 10 s: complete = every entry of r.players has a sig; else verified = false, reason "signatures"

func verify_record(r: Dictionary) -> String:           # "ok" | "hash" | "sig:<id>" | "mismatch:<id>" | "nokey:<id>"
	var log := record_to_log(r)
	if SeedRound.sha256(Canon.canon(log)).hex_encode() != r.hash:
		return "hash"
	var digest := hex_to_bytes(r.hash)
	for p in r.players:
		var pinned = keys.pins.get(p, "")
		if pinned == "":
			return "nokey:%s" % p
		if r.pubs.get(p, "") != pinned:
			return "mismatch:%s" % p
		var key := keys.key_of(p)
		if not r.sigs.has(p) or key == null \
				or not crypto.verify(HashingContext.HASH_SHA256, digest, hex_to_bytes(r.sigs[p]), key):
			return "sig:%s" % p
	return "ok"

static func hex_to_bytes(hex: String) -> PoolByteArray:
	var out := PoolByteArray()
	for i in range(0, hex.length(), 2):
		out.append(("0x" + hex.substr(i, 2)).hex_to_int())
	return out
```

Verification order matters: pins first (a `nokey` participant means the viewer never played with that person;
the record can still be vouched by a present participant, but the missing signature keeps it **unverified**).

## 5. Crash-safe history file (JSON lines)

```gdscript
const HIST_PATH := "user://%s/history.jsonl"

func append_record(r: Dictionary) -> void:
	var f := File.new()
	var path := HIST_PATH % MOD_ID
	var mode := File.READ_WRITE if f.file_exists(path) else File.WRITE
	if f.open(path, mode) != OK:
		return
	f.seek_end()
	f.store_line(JSON.print(r))                          # one line; a crash mid-write truncates only this line
	f.close()

func load_history() -> Array:
	var out := []
	var f := File.new()
	if f.open(HIST_PATH % MOD_ID, File.READ) != OK:
		return out
	while not f.eof_reached():
		var line := f.get_line()
		if line == "":
			continue
		var p := JSON.parse(line)
		if p.error == OK and typeof(p.result) == TYPE_DICTIONARY and int(p.result.get("v", 0)) == 1:
			out.append(p.result)                         # unparsable (truncated) last line is skipped
	f.close()
	return out
```

Keep the file small: cap at 2000 lines, rewrite (tmp + rename) when exceeded, bests cached in memory. Never put
this into `ProgressData` (the game's save; `brotato-ui-qol` §persistence).

## 6. Exchanging bests in the lobby (Steam P2P, size limits)

| Message | Direction | Payload | Limits |
|---|---|---|---|
| `HIST_OFFER` | each peer → all, once after lobby lock | `count`, `session_nonce` echo | tiny |
| `HIST_BATCH` | each peer → all | `vouch` (sig over `sha256(batch_hash ‖ session_nonce)`), `records: [...]` | ≤ 20 records, each ≤ 2 KB (4 sigs × 256 B + 4 PEMs × ~450 B is the bulk; send `pubs` only for IDs the receiver lacks, see below), whole batch ≤ 32 KB per reliable message; old P2P reliable allows 1 MB, Messages 512 KB, but a 32 KB chunk survives loss retries better |
| `HIST_NEED_PUB` | receiver → sender | list of Steam IDs whose PEM is missing | tiny; answer `HIST_PUB{id: PEM}` |

```gdscript
func send_bests(session_nonce: PoolByteArray) -> void:
	var bests := pick_bests(load_history(), _bests_cap) # verified == true only; per (char, difficulty) top wave/time; _bests_cap starts at 20
	var strip := []
	for r in bests:
		var c: Dictionary = r.duplicate(true)
		c.erase("pubs")                                  # receiver asks for missing PEMs separately
		strip.append(c)
	var batch_hash := SeedRound.sha256(Canon.canon([hashes_of(strip)]))
	var vouch := crypto.sign(HashingContext.HASH_SHA256, SeedRound.sha256(batch_hash + session_nonce), my_key)
	var bytes := var2bytes({"records": strip, "vouch": vouch})
	if bytes.size() > 32 * 1024:
		_bests_cap = max(1, _bests_cap / 2)              # halve and retry next call; bests are small anyway
		send_bests(session_nonce)
		return
	net.broadcast_reliable(MSG_HIST_BATCH, {"records": strip, "vouch": vouch})

func on_hist_batch(sender: int, msg: Dictionary, session_nonce: PoolByteArray) -> void:
	if _hist_received.has(sender) or not auth_state_ok(sender):
		return                                           # one batch per peer per lobby; ticket must be ok
	_hist_received[sender] = true
	var key := keys.key_of(str(sender))
	var batch_hash := SeedRound.sha256(Canon.canon([hashes_of(msg.records)]))
	if key == null or not crypto.verify(HashingContext.HASH_SHA256, SeedRound.sha256(batch_hash + session_nonce), msg.vouch, key):
		return                                           # no fresh vouch: ignore the whole batch
	for r in msg.records:
		if not str(sender) in r.players:
			continue                                     # forwarding is not vouching
		r["pubs"] = pubs_from_pins(r.players)            # fill from pins; ask HIST_NEED_PUB for the rest
		r["label"] = "verified by %d" % sender if verify_record(r) == "ok" else "unverified"
		_lobby_bests.append(r)
```

- Send only after lobby lock, never during a wave; one batch per peer per lobby; drop oversize batches.
- `var2bytes` with `full_objects = false`; decode with `bytes2var(bytes, false)` (never allow objects).
- The sender's own record of the run is also in the receiver's history when both played it: prefer the local
  copy, use the received one only to confirm.

## 7. Lobby display

For each present player: best wave / fastest win per character at the lobby's difficulty, from (own history ∪
received batches), each with its label. Rules:
- Count a record once per `hash`.
- A number without a label is a bug. Labels: **verified** (own), **verified by <name>** (witness present),
  **unverified**, **mismatch**.
- When the witness leaves the lobby, drop their vouched records from the display (they can no longer vouch).
- Nothing persists from received batches except PEMs asked via `HIST_NEED_PUB` (pinned only through tickets, so
  received PEMs are cached unpinned and used only for records the same sender vouches).
