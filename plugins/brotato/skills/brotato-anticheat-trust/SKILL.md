---
name: brotato-anticheat-trust
description: Makes an online co-op Brotato mod (Godot 3 GDScript, Steam P2P, host-authoritative, no server ever) resistant to cheating by clients and by the host - threat model, commit-reveal run seed, derived RNG every peer can re-derive, client audits of the host, wave-end hashes to all peers, Steam auth tickets, Crypto signing, fail-closed "run not verified" rule (no kicks, no votes), witness-model verified-run histories instead of a global leaderboard. Use for Brotato cheat, host cheating, trust, verify host, commit-reveal, state hash, audit, auth ticket, verified run, leaderboard, or German "Cheat", "Host überwachen", "Betrug", "Anti-Cheat", "Vertrauen", "gegenseitig prüfen", "Bestenliste".
---

# Brotato online co-op: mutual trust and anti-cheat (host included)

Builds on `brotato-online-multiplayer` (host authority, intents vs state, per-purpose RNG, wave-end hash,
epochs, stable slots) and `brotato-modding` / `godot3-gdscript-pitfalls` (Godot 3.x syntax, Mod Loader 6.x).
This skill adds only what makes the host and the clients **checkable by each other**.

**Decided posture (don't re-litigate):** every inconsistency has exactly one consequence: the run is marked
**invalid / not verified** and never enters a verified history. Players keep playing. No kicks, no bans, no votes,
no culprit named. **No server of any kind, ever**: no backend, no Web API, no Steam leaderboard upload (§9).

## 1. Facts to design around (verified 2026-10-08)

| Fact | Consequence |
|---|---|
| Godot 3.6 source has `HashingContext` (MD5/SHA1/SHA256), `HMACContext`, `Crypto` (`generate_random_bytes`, `generate_rsa`, `sign`, `verify`, `encrypt`, `decrypt`, `hmac_digest`, `constant_time_compare`), `CryptoKey` (`save`, `load`, `save_to_string`, `load_from_string`), `String.sha256_text()/sha256_buffer()`, `PoolByteArray.hex_encode()`, `Directory.rename()` | Everything needed for commitments, signatures and crash-safe files exists. `Crypto`/`HMACContext` need the mbedtls module: `Crypto.new()` returns `null` without it, so feature-detect. `HashingContext` and `sha256_*` always work |
| GDScript `hash()` is 32-bit: ints hash to themselves (truncated), strings via djb2, floats via their double bits, Dictionaries in insertion order | Fine for seeding private RNGs. For anything compared across peers or signed, hash **canonical bytes** (ints and strings only, sorted) with SHA-256 |
| GodotSteam 3.x (v3.29 source): `getAuthSessionTicket(remote_steam_id = 0) -> {id, buffer, size}`, `beginAuthSession(ticket, ticket_size, steam_id) -> int`, `endAuthSession(steam_id)`, `cancelAuthTicket(id)`, `userHasLicenseForApp(steam_id, app_id)`, `getSteamID()`, `get/setLobbyMemberData` (≤ 8192 B per value), signals `get_auth_session_ticket_response(auth_ticket, result)`, `validate_auth_ticket_response(auth_id, response, owner_id)`; enums as `Steam.AUTH_SESSION_RESPONSE_OK` etc. | A peer can prove "this Steam ID is online, owns the game, is not banned" to any other peer, which is what binds a self-generated signing key to a Steam ID. Brotato's exact GodotSteam build is unpublished: log the ticket Dictionary once and check the key names (verify) |
| Steam Networking Messages / Sockets authenticate the remote identity; relays hide IPs; traffic is encrypted and rate-limited (Valve docs, search snippets). Old `sendP2PPacket` also hands you `remote_steam_id` from Steam's session, not from the packet (weaker, verify). ENet has **no** identity | Take the sender from the transport, never from the payload. Spoofing a Steam ID needs the victim's machine. Only ENet needs app-level MACs |
| No VAC, no Valve anti-cheat for mods, no server. No shipped Brotato online mod (Brotatogether, BrotatoOnline, BroTangto) validates the host; Valheim/Lethal Company "anti-cheat" mods only let hosts police clients and admit self-reported plugin lists are spoofable | Everything is detection; the only response is "run not verified"; ranking is the witness model (§9). No prior art to copy. False flags ruin co-op faster than cheats do, so every check has a tolerance and the response is always the same mild one |

## 2. Threat model (short; full table: [references/threat-model.md](references/threat-model.md))

| Who | How | Caught by | Consequence |
|---|---|---|---|
| Host | Edits enemy HP, spawn counts, wave timer, own gold/items/stats, damage | Clients: bounds checks, item ledger, timer monotonicity, shop/drop re-derivation | Run invalid |
| Host | Controls RNG (shop, drops, crits) | Combined commit-reveal seed; clients re-derive mod-owned rolls | Run invalid (hard evidence in the local log) |
| Host | Sends different states to different clients | All-to-all wave hashes | Run invalid |
| Client | Speed/teleport, intent spam, fake pickups, memory edits of own process | Host clamps, host owns pickups/gold, rate limits | Clamped silently; beyond tolerance: run invalid |
| Client | Forges hash/commit, refuses reveal, floods | Commit verification, hash comparison, per-peer budgets | Seed round aborted once, then run invalid; floods dropped |
| Anyone | Forged run records, spoofed mod list / version in lobby data | Signatures of all participants + witness rule; lobby data not detectable | Record labelled mismatch / unverified; hashes disagree later → run invalid |

## 3. Trust architecture: pick this stack

1. **Host authority** (sibling skill) stays. Clients send intents only.
2. **Combined seed** by commit-reveal before the run, so nobody chooses the RNG.
3. **Mod-owned rolls** (shop offers, level-up choices, crate loot, mod drops) come from the derived RNG, so every
   peer can re-derive them. Whatever still uses Brotato's global RNG (spawns, native crits) gets bounds checks only.
4. **Client audits** of host decisions, batched at wave end, scored, logged with evidence (local file only).
5. **All-to-all wave-end hashes**: any disagreement invalidates the run; who differs is a diagnostic.
6. **Steam auth tickets** at join, transport identity for every packet, seq + session nonce against replay.
7. **Signed run records** at run end, kept locally, shown to co-players through the witness model (§9).

Rejected: split authority (each peer owns its gold/items: invites client cheating, host audits everyone); full
lockstep with cross-hash (impossible from a mod: shared global RNG, pooling, frame-timed physics, see
`brotato-online-multiplayer`); any server or Steam leaderboard (§9). Trade-offs: [references/threat-model.md](references/threat-model.md).

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
```
Per roll: `rng.seed = seed_from(sha256(run_seed || wave || purpose || counter))`, then `randi_range()` only.

- A missing or mismatching reveal **aborts the round once** (fresh secrets for everyone). A second failure starts
  the run anyway with the host's seed and the run is invalid from wave 1. Never finish a round with a subset.
  The run seed is public: it stops seed *choice*, not knowledge (peers can predict shops). Fine in co-op.

## 5. Audits and hash comparison (code and thresholds: [references/audits-and-quorum.md](references/audits-and-quorum.md))

```gdscript
# All peers broadcast the wave-end hash to all peers. Decision: any difference -> run invalid.
# Who differs is only written to the local diagnostic log (never shown as an accusation).
func check_wave_hashes(hashes: Dictionary) -> void:          # steam_id -> PoolByteArray (sha256), connected peers only
	var seen := {}
	for id in hashes:
		seen[hashes[id].hex_encode()] = true
	if seen.size() > 1:
		run_state.invalidate("state_mismatch")                 # neutral UI text: "Run not verified: state mismatch"
		diag.log_outliers(hashes)                              # majority/minority split, local file only
```

- Hash only ints and strings, sorted, through canonical bytes (`canon()` in the reference): floats, Dictionary
  order and interpolated positions cause false mismatches, and a false mismatch now costs a verified run.
- Audit score per run: minor 1, major 5, re-derivation mismatch 10; at 10 the run is invalid, below that nothing
  is shown. Reset the baseline after every resync; skip the first wave after a late join. Mismatch is usually a
  **desync bug**: the sibling's resync still runs; invalidation is additive and sticky.

## 6. Identity and message authenticity (full: [references/identity-signing.md](references/identity-signing.md))

```gdscript
func _on_auth_ticket_msg(sender: int, buf: PoolByteArray, size: int) -> void:
	if _auth_state.has(sender):
		Steam.endAuthSession(sender)                           # else BEGIN_AUTH_SESSION_RESULT_DUPLICATE_REQUEST
	var r: int = Steam.beginAuthSession(buf, size, sender)     # sender = transport identity, not payload
	if r != Steam.BEGIN_AUTH_SESSION_RESULT_OK:
		run_state.invalidate("auth")                           # fail closed; the player still plays

func _on_peer_validated(auth_id: int, response: int, owner_id: int) -> void:   # fires again later (offline, cancelled, banned)
	if response == Steam.AUTH_SESSION_RESPONSE_OK:
		keys.pin(auth_id, Steam.getLobbyMemberData(lobby_id, auth_id, "pub"))   # key bound to a verified Steam ID
	else:
		run_state.invalidate("auth")
```

- Sender = transport (`identity` / `remote_steam_id` / `get_rpc_sender_id()`), never a `slot` or `steam_id` field.
- Replay: per-sender, per-type `seq` plus a per-session nonce chosen at lobby lock and the scene epoch.
- Sign only wave-end hashes and the final run record (RSA via `Crypto.sign`, per-install keys, public PEM in
  lobby member data). Don't sign snapshots. Don't encrypt (Steam does). Don't scan processes or memory.

## 7. The one response: fail closed

```gdscript
var invalid := false                       # run_state.gd: sticky, additive, broadcast so every peer shows the same badge
var reasons := []          # "seed", "state_mismatch", "auth", "audit", "disconnect", "version"

func invalidate(reason: String) -> void:
	if not reason in reasons:
		reasons.append(reason)
	if not invalid:
		invalid = true
		hud.toast(tr("RUN_NOT_VERIFIED"))          # "Run not verified: state mismatch" - never a name, never a slot
		net.broadcast_reliable(MSG_RUN_INVALID, {"reason": reason})   # peers invalidate too; no ack needed
```

Triggers: any wave-hash difference; a seed round that failed twice or a reveal that doesn't match its commit; any
auth-ticket result other than OK (join or later); audit score ≥ 10; a peer disconnecting mid-wave; a version/mod
hash mismatch after lobby lock. Consequences: badge in HUD and end screen, record written with `verified = false`
and the reasons, never enters a verified history. No kick, no vote, no name. Details: [references/audits-and-quorum.md](references/audits-and-quorum.md).

## 8. What this cannot detect

- **Collusion of all peers**, so anything in a 2-player run where both agree (the other player is the only
  auditor). Peer-verified means "these peers agreed", never "nobody cheated".
- **Purely local cheats**: auto-dodge/aim bots, slow-motion tools, info cheats (enemy HP, future shops from the
  public seed), macros. They produce valid, in-bounds state.
- **A rebuilt client that reports expected values** (correct hashes, commits, signatures) is indistinguishable.
  Checks catch sloppy edits, not a rewritten protocol participant.
- **Host cheats inside the tolerances**, cosmetic-only edits, spoofed `mods`/`dlc`/version lobby data until
  behaviour diverges.

## 9. Ranking without a server: the witness model (full: [references/witness-ranking.md](references/witness-ranking.md))

**Why a global leaderboard cannot be secured without a server (never propose one):** any client can forge an
entry, because nothing outside the players' own machines checks it. Steam leaderboards belong to the game's app
and accept whatever any client uploads under app 1942280, so a one-line script posts any score. Encrypted app
tickets and `AuthenticateUserTicket` need the publisher's Web API key, which a mod author does not have. Peer
signatures without a trusted reader prove only that some keys signed something. So: no global board, ever.

What works instead: every client keeps a **local history of runs it played in** whose final state all peers
confirmed. A record is worth showing to a viewer only if the viewer played in it, or a **present, ticket-verified
participant vouches for it now** (the witness). Values are always "vouched by someone you are playing with".

```gdscript
# run record (user://<mod>/history.jsonl, one JSON object per line, appended crash-safe)
{"v": 1, "hash": "<sha256 hex of canon(log)>", "seed": "<int as string>", "players": ["7656...","7656..."],
 "char": {"7656...": "character_x"}, "wave": 20, "won": true, "duration": 1312, "difficulty": 3, "zone": 0,
 "versions": {"game": "1.1.15.4", "mod": "1.0.0", "proto": 3}, "verified": true, "reasons": [],
 "sigs": {"7656...": "<hex RSA sig over hash>", "7656...": "<hex>"}, "pubs": {"7656...": "<PEM>"}}
```

- Keys: one RSA-2048 key per install (`user://<mod>/peer_key.key`); public PEM in lobby member data; pinned per
  Steam ID only after that peer's auth ticket validated OK here. A different key for a known ID later = label
  **mismatch** (reinstall or impersonation; both are "cannot verify").
- Witness rule for a received record `R`: all `sigs` verify against pinned keys of `players`; the sender is in
  `players`, in the lobby now with auth state `ok`, and signed `sha256(R.hash || session_nonce)` for this session
  (fresh vouch, no forwarding). Then `R` is "verified by <sender>"; otherwise "unverified".
- Exchange: in the lobby only, each peer sends its **bests** (per character/difficulty, ≤ 20 records, ≤ 2 KB each)
  as reliable chunks ≤ 32 KB. Show "verified bests of present players" labelled **verified / unverified / mismatch**.
- History: JSON lines, append with `File.READ_WRITE` + `seek_end`, skip an unparsable last line on load; key file
  written tmp + `Directory.rename` (rules: `brotato-ui-qol`). Never write into `ProgressData`.

## 10. Performance and privacy

- Audits run in the shop/upgrade phase, time-sliced (≤ 2 ms per frame). Nothing per enemy per tick. SHA-256 of
  a few KB is microseconds; RSA-2048 keygen is slow (measure) → once on first launch, cached in `user://`.
- Packet budgets, heartbeats, per-peer caps: `brotato-stability-performance`. Rate-limit per peer (intents ≤ 30/s,
  chat ≤ 2/s, audit messages ≤ 1/wave, history ≤ 1 batch per lobby join); drop silently when exceeded.
- Share only what others already see in-game: records carry Steam IDs, characters and scores, not persona names
  or IPs. The local diagnostic log (who differed) stays on disk and is never sent.

## 11. Checklist: every new synced feature

- [ ] Who decides (host) and what does the decider **commit** (ID, wave, counter) so others can check later?
- [ ] Is the roll mod-owned (derived RNG, re-derivable) or native (bounds only)? Write the bound and its tolerance.
- [ ] What goes into the wave-end hash (ints/strings, sorted)? What is deliberately left out (floats, cosmetics)?
- [ ] Which intents can a client spam? Rate limit and idempotency key.
- [ ] Evidence recorded on mismatch (expected, got, wave, tick)? Score weight? Does it invalidate, or only log?
- [ ] Late join / resync: baseline reset so the feature doesn't invalidate an honest run. New record fields → bump `v`.
- [ ] Test: 3 peers, one patched to lie, plus 2 peers with simulated loss. Expect: lie → invalid, loss → still valid.

## 12. Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Honest run invalidated right after a resync or late join | Audit baseline not reset; events applied twice | Reset ledger on resync; skip the first wave after join |
| Hashes differ only on the host | Host hashes before applying its own deferred events, or includes host-only fields | Hash the exact state that was broadcast; ints only |
| Commit check fails for one peer | Different byte encoding (`str(id)` vs `put_64`) | One shared `canon()`/`u64_bytes()` helper |
| `beginAuthSession` returns 2 | Session for that Steam ID still open | `endAuthSession` first |
| Signature valid on Windows, invalid on Linux | Signed text with `\r\n` or JSON floats | Sign `sha256(canon(...))`, strip `\r` from PEM |
| Friend's best shows "unverified" although you played that run | Record not in your own history, or sender's vouch signature missing | Write your own record at run end; vouch over `hash ‖ session_nonce` |

## References (read when needed)

- [references/threat-model.md](references/threat-model.md): full threat table, architecture options with cost,
  what other co-op mod scenes do, what a mod cannot do. Read before deciding scope.
- [references/verifiable-rng.md](references/verifiable-rng.md): commit-reveal messages and code, derivation,
  purpose table, failure handling, late join, pitfalls. Read when touching seeds or rolls.
- [references/audits-and-quorum.md](references/audits-and-quorum.md): audit framework, bounds table, re-derivation,
  all-to-all hashes, diagnostic quorum, run state, run record and badge rules. Read when writing any check.
- [references/identity-signing.md](references/identity-signing.md): transport identity, auth tickets, replay
  protection, RSA/HMAC signing, canonical bytes, what to skip. Read when touching join or message handling.
- [references/witness-ranking.md](references/witness-ranking.md): run record, key persistence and pinning,
  signing/verifying, history exchange over Steam P2P with size limits, witness rule, lobby display. Read before
  building any score display.
- [references/optional-moderation.md](references/optional-moderation.md) (kick/ban/vote, **not used**) and
  [references/optional-backend.md](references/optional-backend.md) (server design, **not possible here**).
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix. [references/sources.md](references/sources.md): what was verified where.
