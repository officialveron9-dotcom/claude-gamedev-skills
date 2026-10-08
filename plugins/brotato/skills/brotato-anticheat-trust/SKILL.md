---
name: brotato-anticheat-trust
description: Makes an online co-op Brotato mod (Godot 3 GDScript, Steam P2P, host-authoritative) resistant to cheating by clients and by the host - threat model, commit-reveal combined run seed, derived RNG every peer can re-derive, client audits of host decisions (shop, drops, gold, damage, wave timer) with bounds, wave-end hashes to all peers with quorum, Steam auth tickets, seq, nonces, HashingContext/HMAC/Crypto signing, verified-run logs, vote-kick, ban lists. Use for Brotato cheat, host cheating, trust, verify host, commit-reveal seed, state hash, audit, vote kick, Steam auth ticket, verified run, or German "Cheat", "Host überwachen", "Betrug", "Anti-Cheat", "Vertrauen", "gegenseitig prüfen", "Kick".
---

# Brotato online co-op: mutual trust and anti-cheat (host included)

Builds on `brotato-online-multiplayer` (host authority, intents vs state, per-purpose RNG, wave-end hash,
epochs, stable slots) and `brotato-modding` / `godot3-gdscript-pitfalls` (Godot 3.x syntax, Mod Loader 6.x).
This skill adds only what makes the host and the clients **checkable by each other**.

## 1. Facts to design around (verified 2026-10-08)

| Fact | Consequence |
|---|---|
| Godot 3.6 source has `HashingContext` (MD5/SHA1/SHA256), `HMACContext`, `Crypto` (`generate_random_bytes`, `generate_rsa`, `sign`, `verify`, `encrypt`, `decrypt`, `hmac_digest`, `constant_time_compare`), `CryptoKey` (`save_to_string`, `load_from_string`), `String.sha256_text()/sha256_buffer()`, `PoolByteArray.hex_encode()` | Everything needed for commitments, HMAC and RSA signatures exists. `Crypto`/`HMACContext` need the mbedtls module: `Crypto.new()` returns `null` without it, so feature-detect. `HashingContext` and `sha256_*` always work |
| GDScript `hash()` is 32-bit: ints hash to themselves (truncated), strings via djb2, floats via their double bits, Dictionaries in insertion order | Fine for seeding private RNGs. For anything compared across peers or signed, hash **canonical bytes** (ints and strings only, sorted) with SHA-256 |
| GodotSteam 3.x (v3.29 source): `getAuthSessionTicket(remote_steam_id = 0) -> {id, buffer, size}`, `beginAuthSession(ticket, ticket_size, steam_id) -> int`, `endAuthSession(steam_id)`, `cancelAuthTicket(id)`, `userHasLicenseForApp(steam_id, app_id)`, `getSteamID()`, signals `get_auth_session_ticket_response(auth_ticket, result)` and `validate_auth_ticket_response(auth_id, response, owner_id)`; enums as `Steam.AUTH_SESSION_RESPONSE_OK` etc. | A peer can prove "this Steam ID is online, owns the game, is not banned" to any other peer. Brotato's exact GodotSteam build is unpublished: log the ticket Dictionary once and check the key names (verify) |
| Steam Networking Messages / Sockets authenticate the remote identity; relays hide IPs; traffic is encrypted and rate-limited (Valve docs, search snippets). Old `sendP2PPacket` also hands you `remote_steam_id` from Steam's session, not from the packet (weaker, verify). ENet has **no** identity | Take the sender from the transport, never from the payload. Spoofing a Steam ID needs the victim's machine. Only ENet needs app-level MACs |
| No VAC, no Valve anti-cheat for mods; Steam lobbies have no kick; Steam promotes another member to lobby owner when the owner leaves | Everything is detection plus social response. A kicked peer may still sit in the lobby and can even inherit ownership |
| No shipped Brotato online mod (Brotatogether, BrotatoOnline, BroTangto) validates the host; Valheim/Lethal Company "anti-cheat" mods only let hosts police clients and admit self-reported plugin lists are spoofable | There is no prior art to copy. Keep the goal modest: **detect, inform, mark the run unverified**. False flags ruin co-op faster than cheats do |

## 2. Threat model (short; full table: [references/threat-model.md](references/threat-model.md))

| Who | How | Caught by | Response |
|---|---|---|---|
| Host | Edits enemy HP, spawn counts, wave timer, own gold/items/stats, damage | Clients: bounds checks, item ledger, timer monotonicity, shop/drop re-derivation | Audit score → warn → run unverified → leave |
| Host | Controls RNG (shop, drops, crits) | Combined commit-reveal seed; clients re-derive mod-owned rolls | Mismatch = evidence; run unverified |
| Host | Sends different states to different clients | All-to-all wave hashes, quorum | Host outlier → vote |
| Client | Speed/teleport, intent spam, fake pickups, memory edits of own process | Host clamps, host owns pickups/gold, rate limits | Host clamps silently; repeated → kick |
| Client | Forges hash/commit, refuses reveal, floods | Quorum, commit verification, per-peer budgets | Flag; abort seed round; drop packets |
| Anyone | Spoofed mod list / version in lobby data | Not detectable (self-reported) | Accept; mark run unverified if hashes disagree |

## 3. Trust architecture: pick this stack

1. **Host authority** (sibling skill) stays. Clients send intents only.
2. **Combined seed** by commit-reveal before the run, so nobody chooses the RNG.
3. **Mod-owned rolls** (shop offers, level-up choices, crate loot, mod drops) come from the derived RNG, so every
   peer can re-derive them. Whatever still uses Brotato's global RNG (spawns, native crits) gets bounds checks only.
4. **Client audits** of host decisions, batched at wave end, scored, logged with evidence.
5. **All-to-all wave-end hashes** with quorum, not host-only.
6. **Steam auth tickets** at join, transport identity for every packet, seq + session nonce against replay.
7. **Signed run log** at run end: "verified" only when every peer agrees.

Alternatives and why not: split authority (each peer owns its gold/items) invites client cheating and makes the host
the auditor of everyone; full lockstep with cross-hash is impossible from a mod (shared global RNG, pooling,
frame-timed physics, see `brotato-online-multiplayer`); a verification server would need hosting, Web API
`AuthenticateUserTicket` and a re-simulation of Brotato, none of which a mod can ship. Trade-offs:
[references/threat-model.md](references/threat-model.md).

## 4. Verifiable randomness (protocol: [references/verifiable-rng.md](references/verifiable-rng.md))

```gdscript
# 1. lobby locked: every peer commits  sha256(steam_id || round || secret)  to EVERY peer
# 2. all commits present: every peer reveals its secret
# 3. everyone checks each reveal against its commit, then
func compute_run_seed(round_id: int, reveals: Dictionary) -> int:   # steam_id -> PoolByteArray(32)
	var ids := reveals.keys()
	ids.sort()                                                        # same order on every peer
	var buf := u64_bytes(round_id)
	for id in ids:
		buf.append_array(u64_bytes(id))
		buf.append_array(reveals[id])
	return seed_from(sha256(buf))

func derived_rng(run_seed: int, wave: int, purpose: int, counter: int) -> RandomNumberGenerator:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_from(sha256(u64_bytes(run_seed) + u64_bytes(wave) + u64_bytes(purpose) + u64_bytes(counter)))
	return rng
```

- A missing reveal **aborts the round** (re-commit with everyone). Never "continue without them": a peer that may
  withhold can choose between two seeds.
- Use `rng.randi_range()` and integer math for audited rolls. Never `seed()` the global RNG.
- The run seed is public. It stops seed *choice*, not knowledge: peers can predict shops. Acceptable in co-op.

## 5. Audits and quorum (code and thresholds: [references/audits-and-quorum.md](references/audits-and-quorum.md))

```gdscript
# All peers broadcast the wave-end hash to all peers; each peer resolves locally.
func resolve_quorum(hashes: Dictionary) -> Dictionary:   # steam_id -> PoolByteArray (sha256)
	var votes := {}
	for id in hashes:
		var key: String = hashes[id].hex_encode()
		votes[key] = votes.get(key, 0) + 1
	var n := hashes.size()
	if votes.size() == 1:
		return {"status": "agree"}
	if n <= 2:
		return {"status": "undecided"}                          # 2 players: show both the diff, nobody is "wrong"
	var best := ""
	for key in votes:
		if best == "" or votes[key] > votes[best]:
			best = key
	if votes[best] * 2 <= n:
		return {"status": "undecided"}                          # no majority (e.g. 2-2)
	var outliers := []
	for id in hashes:
		if hashes[id].hex_encode() != best:
			outliers.append(id)
	return {"status": "outliers", "ids": outliers}
```

- Hash only ints and strings, sorted, through canonical bytes (`canon()` in the reference). Floats, Dictionary
  order and interpolated positions cause false mismatches.
- Audit score per peer per run: minor finding 1, major 5, re-derivation mismatch 10. Warn at 5, mark the run
  unverified at 10, open a vote at 20. Reset the baseline after every resync; skip the first wave after a late join.
- Host is the outlier → vote among the others: continue (unverified) / end run. The host cannot be kicked.

## 6. Identity and message authenticity (full: [references/identity-signing.md](references/identity-signing.md))

```gdscript
func _ready() -> void:
	Steam.connect("get_auth_session_ticket_response", self, "_on_my_ticket")
	Steam.connect("validate_auth_ticket_response", self, "_on_peer_validated")

func request_ticket_for(peer_id: int) -> void:
	var t: Dictionary = Steam.getAuthSessionTicket()          # no args works on every 3.x build (verify keys)
	_my_tickets[peer_id] = t                                   # keep t["id"] for cancelAuthTicket
	_waiting_ticket_peer = peer_id                             # send after _on_my_ticket(result == Steam.RESULT_OK)

func _on_auth_ticket_msg(sender: int, buf: PoolByteArray, size: int) -> void:
	if _auth_state.has(sender):
		Steam.endAuthSession(sender)                           # else BEGIN_AUTH_SESSION_RESULT_DUPLICATE_REQUEST
	var r: int = Steam.beginAuthSession(buf, size, sender)     # sender = transport identity, not payload
	_auth_state[sender] = "pending" if r == Steam.BEGIN_AUTH_SESSION_RESULT_OK else "rejected:%d" % r

func _on_peer_validated(auth_id: int, response: int, owner_id: int) -> void:
	_auth_state[auth_id] = "ok" if response == Steam.AUTH_SESSION_RESPONSE_OK else "fail:%d" % response
	# fires again later: USER_NOT_CONNECTED_TO_STEAM, AUTH_TICKET_CANCELED, PUBLISHER_ISSUED_BAN ... grace, don't insta-kick
```

- Sender = transport (`identity` / `remote_steam_id` / `get_rpc_sender_id()`), never a `slot` or `steam_id` field.
- Replay: per-sender, per-type `seq` plus a per-session nonce chosen at lobby lock and the scene epoch.
- Sign only wave-end hashes and the final run log (RSA via `Crypto.sign`, keys exchanged as PEM in lobby member
  data, ≤ 8192 bytes). Don't sign snapshots. Don't encrypt (Steam does). Don't scan processes or memory.

## 7. Responses (ladder; never skip steps on one finding)

log with evidence → toast to all peers → run marked unverified (badge, no leaderboard export) → vote-kick
(majority of connected non-target peers, host executes: send `KICKED`, 1 s flush, close session, ignore ID,
`banned` lobby data) → local ban list by Steam ID in `user://` (auto-leave if a banned ID is in the lobby) →
never auto-ban on a single mismatch. Details: [references/audits-and-quorum.md](references/audits-and-quorum.md).

## 8. Performance and privacy

- Audits run in the shop/upgrade phase, time-sliced (≤ 2 ms per frame). Nothing per enemy per tick.
- SHA-256 of a few KB is microseconds; RSA-2048 keygen is slow (measure, likely hundreds of ms) → generate once on
  first launch, cache in `user://`. One signature per wave is nothing; per packet is not.
- Packet budgets, heartbeats and per-peer message caps: `brotato-stability-performance`. Add per-peer rate limits
  (intents ≤ 30/s, chat ≤ 2/s, audit messages ≤ 1/wave) and drop silently when exceeded.
- Share only what others already see in-game. Run files carry Steam IDs and item lists, not persona names or IPs.

## 9. Checklist: every new synced feature

- [ ] Who decides (host) and what does the decider **commit** (ID, wave, counter) so others can check later?
- [ ] Is the roll mod-owned (derived RNG, re-derivable) or native (bounds only)? Write the bound and its tolerance.
- [ ] What goes into the wave-end hash (ints/strings, sorted)? What is deliberately left out (floats, cosmetics)?
- [ ] Which intents can a client spam? Rate limit and idempotency key.
- [ ] Evidence recorded on mismatch (expected, got, wave, tick, sender)? Score weight?
- [ ] Late join / resync: baseline reset so the feature doesn't flag an honest peer.
- [ ] Test: 3 peers, one patched to lie, plus 2 peers with simulated loss. Expect: lie detected, loss not flagged.

## 10. Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Honest peer flagged right after a resync or late join | Audit baseline not reset; events applied twice | Reset ledger on resync; skip the first wave after join |
| Hashes differ only on the host | Host hashes before applying its own deferred events, or includes host-only fields | Hash the exact state that was broadcast; ints only |
| Commit check fails for one peer | Different byte encoding (`str(id)` vs `put_64`) | One shared `canon()`/`u64_bytes()` helper |
| `beginAuthSession` returns 2 | Session for that Steam ID still open | `endAuthSession` first |
| `validate_auth_ticket_response` never fires | No `Steam.run_callbacks()`, editor run, wrong app | PROCESS-mode net node; test in the packaged game |
| Signature valid on Windows, invalid on Linux | Signed text with `\r\n` or JSON floats | Sign `sha256(canon(...))`, strip `\r` from PEM |
| `Crypto.new()` is null | Engine built without mbedtls | Feature-detect; fall back to hash-only mode |

## References (read when needed)

- [references/threat-model.md](references/threat-model.md): full threat table, architecture options with cost,
  what other co-op mod scenes do, what a mod cannot do. Read before deciding scope.
- [references/verifiable-rng.md](references/verifiable-rng.md): commit-reveal messages and code, derivation,
  purpose table, refusal handling, late join, pitfalls. Read when touching seeds or rolls.
- [references/audits-and-quorum.md](references/audits-and-quorum.md): audit framework, bounds table, re-derivation,
  all-to-all hashes, votes, kick/ban, run log and verified badge. Read when writing any check or response.
- [references/identity-signing.md](references/identity-signing.md): transport identity, auth tickets, replay
  protection, RSA/HMAC signing, canonical bytes, what to skip. Read when touching join or message handling.
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix.
- [references/sources.md](references/sources.md): what was verified where.
