---
name: brotato-anticheat-trust
description: Makes an online co-op Brotato mod (Godot 3 GDScript, Steam P2P, host-authoritative) resistant to cheating by clients and by the host - threat model, commit-reveal run seed, derived RNG every peer can re-derive, client audits of host decisions with bounds, wave-end hashes to all peers, Steam auth tickets, replay protection, Crypto signing, fail-closed "run not verified" rule (no kicks, no votes), ranked backend via Valve Web API. Use for Brotato cheat, host cheating, trust, verify host, commit-reveal, state hash, audit, auth ticket, verified run, ranked, or German "Cheat", "Host überwachen", "Betrug", "Anti-Cheat", "Vertrauen", "gegenseitig prüfen", "ungültiger Run".
---

# Brotato online co-op: mutual trust and anti-cheat (host included)

Builds on `brotato-online-multiplayer` (host authority, intents vs state, per-purpose RNG, wave-end hash,
epochs, stable slots) and `brotato-modding` / `godot3-gdscript-pitfalls` (Godot 3.x syntax, Mod Loader 6.x).
This skill adds only what makes the host and the clients **checkable by each other**.

**Decided posture (don't re-litigate):** every inconsistency has exactly one consequence: the run is marked
**invalid / not verified** and is never ranked. Players keep playing. No kicks, no bans, no votes, no culprit
named. Moderation features exist only as an opt-in note: [references/optional-moderation.md](references/optional-moderation.md).

## 1. Facts to design around (verified 2026-10-08)

| Fact | Consequence |
|---|---|
| Godot 3.6 source has `HashingContext` (MD5/SHA1/SHA256), `HMACContext`, `Crypto` (`generate_random_bytes`, `generate_rsa`, `sign`, `verify`, `encrypt`, `decrypt`, `hmac_digest`, `constant_time_compare`), `CryptoKey` (`save_to_string`, `load_from_string`), `String.sha256_text()/sha256_buffer()`, `PoolByteArray.hex_encode()` | Everything needed for commitments, HMAC and RSA signatures exists. `Crypto`/`HMACContext` need the mbedtls module: `Crypto.new()` returns `null` without it, so feature-detect. `HashingContext` and `sha256_*` always work |
| GDScript `hash()` is 32-bit: ints hash to themselves (truncated), strings via djb2, floats via their double bits, Dictionaries in insertion order | Fine for seeding private RNGs. For anything compared across peers or signed, hash **canonical bytes** (ints and strings only, sorted) with SHA-256 |
| GodotSteam 3.x (v3.29 source): `getAuthSessionTicket(remote_steam_id = 0) -> {id, buffer, size}`, `beginAuthSession(ticket, ticket_size, steam_id) -> int`, `endAuthSession(steam_id)`, `cancelAuthTicket(id)`, `getAuthTicketForWebApi(service_identity)`, `userHasLicenseForApp(steam_id, app_id)`, `getSteamID()`, signals `get_auth_session_ticket_response(auth_ticket, result)`, `validate_auth_ticket_response(auth_id, response, owner_id)`, `get_ticket_for_web_api(auth_ticket, result, ticket_size, ticket_buffer)`; enums as `Steam.AUTH_SESSION_RESPONSE_OK` etc. | A peer can prove "this Steam ID is online, owns the game, is not banned" to any other peer, and a backend can check a Web API ticket. Brotato's exact GodotSteam build is unpublished: log the ticket Dictionary once and check the key names (verify) |
| Steam Networking Messages / Sockets authenticate the remote identity; relays hide IPs; traffic is encrypted and rate-limited (Valve docs, search snippets). Old `sendP2PPacket` also hands you `remote_steam_id` from Steam's session, not from the packet (weaker, verify). ENet has **no** identity | Take the sender from the transport, never from the payload. Spoofing a Steam ID needs the victim's machine. Only ENet needs app-level MACs |
| No VAC, no Valve anti-cheat for mods, no server inside a mod | Everything in-game is detection. The only in-game response is "run not verified" |
| No shipped Brotato online mod (Brotatogether, BrotatoOnline, BroTangto) validates the host; Valheim/Lethal Company "anti-cheat" mods only let hosts police clients and admit self-reported plugin lists are spoofable | No prior art to copy. False flags ruin co-op faster than cheats do, so every check has a tolerance and the response is always the same mild one |

## 2. Threat model (short; full table: [references/threat-model.md](references/threat-model.md))

| Who | How | Caught by | Consequence |
|---|---|---|---|
| Host | Edits enemy HP, spawn counts, wave timer, own gold/items/stats, damage | Clients: bounds checks, item ledger, timer monotonicity, shop/drop re-derivation | Run invalid |
| Host | Controls RNG (shop, drops, crits) | Combined commit-reveal seed; clients re-derive mod-owned rolls | Run invalid (hard evidence in the local log) |
| Host | Sends different states to different clients | All-to-all wave hashes | Run invalid |
| Client | Speed/teleport, intent spam, fake pickups, memory edits of own process | Host clamps, host owns pickups/gold, rate limits | Clamped silently; beyond tolerance: run invalid |
| Client | Forges hash/commit, refuses reveal, floods | Commit verification, hash comparison, per-peer budgets | Seed round aborted once, then run invalid; floods dropped |
| Anyone | Spoofed mod list / version in lobby data | Not detectable (self-reported) | Accepted; hashes disagree later → run invalid |

## 3. Trust architecture: pick this stack

1. **Host authority** (sibling skill) stays. Clients send intents only.
2. **Combined seed** by commit-reveal before the run, so nobody chooses the RNG.
3. **Mod-owned rolls** (shop offers, level-up choices, crate loot, mod drops) come from the derived RNG, so every
   peer can re-derive them. Whatever still uses Brotato's global RNG (spawns, native crits) gets bounds checks only.
4. **Client audits** of host decisions, batched at wave end, scored, logged with evidence (local file only).
5. **All-to-all wave-end hashes**: any disagreement invalidates the run; who differs is a diagnostic.
6. **Steam auth tickets** at join, transport identity for every packet, seq + session nonce against replay.
7. **Signed run log** at run end: "peer-verified" only when every peer agrees; ranking needs the backend (§9).

Rejected: split authority (each peer owns its gold/items: invites client cheating, host audits everyone); full
lockstep with cross-hash (impossible from a mod: shared global RNG, pooling, frame-timed physics, see
`brotato-online-multiplayer`); an in-mod verification server (none exists; even an external one cannot re-simulate
Brotato, §9). Trade-offs: [references/threat-model.md](references/threat-model.md).

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

- A missing or mismatching reveal **aborts the round once** (fresh secrets for everyone). A second failure starts
  the run anyway with the host's seed and the run is invalid from wave 1. Never finish a round with a subset.
- Use `rng.randi_range()` and integer math for audited rolls. Never `seed()` the global RNG.
- The run seed is public. It stops seed *choice*, not knowledge: peers can predict shops. Acceptable in co-op.

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

- Hash only ints and strings, sorted, through canonical bytes (`canon()` in the reference). Floats, Dictionary
  order and interpolated positions cause false mismatches, and a false mismatch now costs a ranked run.
- Audit score per run: minor finding 1, major 5, re-derivation mismatch 10. At 10 the run is invalid. Below that
  nothing is shown. Reset the baseline after every resync; skip the first wave after a late join.
- Mismatch is usually a **desync bug**. The sibling's resync still runs; invalidation is additive and sticky.

## 6. Identity and message authenticity (full: [references/identity-signing.md](references/identity-signing.md))

```gdscript
func _ready() -> void:
	Steam.connect("get_auth_session_ticket_response", self, "_on_my_ticket")
	Steam.connect("validate_auth_ticket_response", self, "_on_peer_validated")

func _on_auth_ticket_msg(sender: int, buf: PoolByteArray, size: int) -> void:
	if _auth_state.has(sender):
		Steam.endAuthSession(sender)                           # else BEGIN_AUTH_SESSION_RESULT_DUPLICATE_REQUEST
	var r: int = Steam.beginAuthSession(buf, size, sender)     # sender = transport identity, not payload
	if r != Steam.BEGIN_AUTH_SESSION_RESULT_OK:
		run_state.invalidate("auth")                           # fail closed; the player still plays

func _on_peer_validated(auth_id: int, response: int, owner_id: int) -> void:
	if response != Steam.AUTH_SESSION_RESPONSE_OK:             # fires again later (offline, cancelled, banned)
		run_state.invalidate("auth")
```

- Sender = transport (`identity` / `remote_steam_id` / `get_rpc_sender_id()`), never a `slot` or `steam_id` field.
- Replay: per-sender, per-type `seq` plus a per-session nonce chosen at lobby lock and the scene epoch.
- Sign only wave-end hashes and the final run log (RSA via `Crypto.sign`, keys exchanged as PEM in lobby member
  data, ≤ 8192 bytes). Don't sign snapshots. Don't encrypt (Steam does). Don't scan processes or memory.

## 7. The one response: fail closed

```gdscript
# run_state.gd - sticky, additive, broadcast so every peer shows the same badge
var invalid := false
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
hash mismatch discovered after lobby lock. Consequences: badge in the HUD and the end screen, the run file is
written with `verified = false` and the reasons, no ranked upload. Nothing else happens: no kick, no vote, no
message that names a player. Details and the badge rules: [references/audits-and-quorum.md](references/audits-and-quorum.md).

## 8. What this cannot detect

- **Collusion of all peers**, and therefore anything in a 2-player run where both agree (the other player is the
  only auditor). Peer-verified means "these peers agreed", never "nobody cheated".
- **Purely local cheats**: auto-dodge or aim bots, pause/slow-motion tools, info cheats (showing enemy HP, future
  shops from the public seed), rebinding, macro input. They produce valid, in-bounds state.
- **A rebuilt client that reports expected values**: a modified mod that recomputes exactly what honest peers
  expect (correct hashes, commits, signatures) is indistinguishable. Checks catch sloppy edits, not a rewritten
  protocol participant.
- **Host cheats inside the tolerances** (small gold bumps, a few extra HP) and cosmetic-only edits.
- Spoofed `mods`/`dlc`/version lobby data until behaviour diverges.

## 9. Ranked submissions need a backend (protocol: [references/ranked-backend.md](references/ranked-backend.md))

Peers can only vouch for each other. A ranked board needs a server that, per run: validates **every** peer's
Web API ticket (`getAuthTicketForWebApi` → `ISteamUserAuth/AuthenticateUserTicket/v1` with `key`, `appid`,
`ticket`, optional `identity` (verify); session tickets from `getAuthSessionTicket` fail there per the SDK
comment); requires a signature from every listed peer over `sha256(run_hash || server_nonce)`; recomputes the
seed commitments and run seed from the uploaded commits/reveals; checks that all per-wave hashes are equal and
signed; applies plausibility bounds (waves vs duration, gold vs materials, items vs purchases); stores the run
under `run_hash` idempotently. **It cannot re-simulate the run** (native RNG, pooling, physics): consistency and
plausibility only. Blocker: `AuthenticateUserTicket` needs a **publisher** Web API key for app 1942280, which only
the game's developer can issue (verify); without it, bind identities via Steam OpenID or trust the in-game mutual
ticket checks. Client: Godot 3 `HTTPRequest.request(url, headers, true, HTTPClient.METHOD_POST, body)` and
`request_completed(result, response_code, headers, body)`; HTTPS needs the mbedtls module (same as `Crypto`).

## 10. Performance and privacy

- Audits run in the shop/upgrade phase, time-sliced (≤ 2 ms per frame). Nothing per enemy per tick.
- SHA-256 of a few KB is microseconds; RSA-2048 keygen is slow (measure) → generate once on first launch, cache
  in `user://`. One signature per wave is nothing; per packet is not.
- Packet budgets, heartbeats, per-peer caps: `brotato-stability-performance`. Rate-limit per peer (intents ≤ 30/s,
  chat ≤ 2/s, audit messages ≤ 1/wave); drop silently when exceeded.
- Share only what others already see in-game. Run files carry Steam IDs and item lists, not persona names or
  IPs. The local diagnostic log (who differed) stays on disk and is never broadcast.

## 11. Checklist: every new synced feature

- [ ] Who decides (host) and what does the decider **commit** (ID, wave, counter) so others can check later?
- [ ] Is the roll mod-owned (derived RNG, re-derivable) or native (bounds only)? Write the bound and its tolerance.
- [ ] What goes into the wave-end hash (ints/strings, sorted)? What is deliberately left out (floats, cosmetics)?
- [ ] Which intents can a client spam? Rate limit and idempotency key.
- [ ] Evidence recorded on mismatch (expected, got, wave, tick)? Score weight? Does it invalidate, or only log?
- [ ] Late join / resync: baseline reset so the feature doesn't invalidate an honest run.
- [ ] Test: 3 peers, one patched to lie, plus 2 peers with simulated loss. Expect: lie → invalid, loss → still valid.

## 12. Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Honest run invalidated right after a resync or late join | Audit baseline not reset; events applied twice | Reset ledger on resync; skip the first wave after join |
| Hashes differ only on the host | Host hashes before applying its own deferred events, or includes host-only fields | Hash the exact state that was broadcast; ints only |
| Commit check fails for one peer | Different byte encoding (`str(id)` vs `put_64`) | One shared `canon()`/`u64_bytes()` helper |
| `beginAuthSession` returns 2 | Session for that Steam ID still open | `endAuthSession` first |
| `validate_auth_ticket_response` never fires | No `Steam.run_callbacks()`, editor run, wrong app | PROCESS-mode net node; test in the packaged game |
| Signature valid on Windows, invalid on Linux | Signed text with `\r\n` or JSON floats | Sign `sha256(canon(...))`, strip `\r` from PEM |
| Backend rejects every ticket | Session ticket sent instead of a Web API ticket, or no publisher key | `getAuthTicketForWebApi`; publisher key on the server only |

## References (read when needed)

- [references/threat-model.md](references/threat-model.md): full threat table, architecture options with cost,
  what other co-op mod scenes do, what a mod cannot do. Read before deciding scope.
- [references/verifiable-rng.md](references/verifiable-rng.md): commit-reveal messages and code, derivation,
  purpose table, failure handling, late join, pitfalls. Read when touching seeds or rolls.
- [references/audits-and-quorum.md](references/audits-and-quorum.md): audit framework, bounds table, re-derivation,
  all-to-all hashes, diagnostic quorum, run state, run log and badge rules. Read when writing any check.
- [references/identity-signing.md](references/identity-signing.md): transport identity, auth tickets, replay
  protection, RSA/HMAC signing, canonical bytes, what to skip. Read when touching join or message handling.
- [references/ranked-backend.md](references/ranked-backend.md): upload protocol, server checks, Web API ticket
  validation, idempotency, GDScript 3 `HTTPRequest`. Read before building a leaderboard.
- [references/optional-moderation.md](references/optional-moderation.md): kick/ban/vote patterns, **not used by
  default**. Read only if the posture changes.
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix.
- [references/sources.md](references/sources.md): what was verified where.
