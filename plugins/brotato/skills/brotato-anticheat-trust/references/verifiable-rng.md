# Verifiable randomness: combined seed and derived RNG

Godot 3 GDScript. Builds on `brotato-online-multiplayer` §6 (host rolls, private seeded RNG per purpose).

## 1. Why commit-reveal

- A host-chosen seed lets the host pick good shops. A client-chosen seed does the same for that client.
- Commit-reveal: everyone first publishes `sha256(id || round || secret)`, then the secret. The hash binds each
  peer to one secret before anyone sees the others. The run seed is a hash over all secrets, so changing it needs
  every peer's cooperation.
- Remaining weakness: the **last revealer** sees all other secrets and can abort instead of revealing (one bit of
  bias per abort). Counter: an abort restarts the round with fresh secrets for everyone, and a second failure
  makes the run invalid (unranked) from wave 1. Re-rolling then has nothing to gain. In co-op that is enough.
- Lockstep-style per-action commitments (hash now, reveal next tick) are not needed: clients don't make hidden
  decisions that need protection, and they cost a round trip per tick.

## 2. Messages (all reliable, control channel, carry the epoch)

| Type | Sender → receiver | Payload | Rule |
|---|---|---|---|
| `SEED_ROUND` | host → all | `round` (u32, increments per attempt), `members` (sorted Steam IDs) | Starts a round; everyone discards older rounds |
| `SEED_COMMIT` | every peer → every peer | `round`, `commit` (32 B) | First commit per (peer, round) wins; later ones logged |
| `SEED_REVEAL` | every peer → every peer | `round`, `secret` (32 B) | Only after the peer has all commits; verify against commit |
| `SEED_ABORT` | host → all | `round`, `reason`, `missing` IDs | Starts a new round; counts a strike for `missing` |
| `SEED_FINAL` | host → all | `round`, `run_seed` | Optional cross-check; every peer must have computed the same |

Timeouts: commits 5 s, reveals 5 s. On timeout the host sends `SEED_ABORT` and starts one fresh round. If the
second round fails too, the host starts the run with its own seed and every peer calls
`run_state.invalidate("seed")`: the run is playable but never verified. Nobody is named. Late joiners (between waves) receive `round`, all commits and all reveals in the resync payload
and verify them; the seed never changes during a run.

## 3. Code

```gdscript
# seed_round.gd - one instance per lobby lock attempt (Godot 3)
extends Reference

const COMMIT_TIMEOUT := 5.0
const REVEAL_TIMEOUT := 5.0

var round_id: int
var members := []            # sorted Steam IDs incl. self
var my_secret: PoolByteArray
var commits := {}            # steam_id -> PoolByteArray(32)
var reveals := {}            # steam_id -> PoolByteArray(32)
var run_seed: int = 0
var done := false

static func u64_bytes(v: int) -> PoolByteArray:
	var b := StreamPeerBuffer.new()
	b.put_64(v)
	return b.data_array

static func sha256(data: PoolByteArray) -> PoolByteArray:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(data)
	return ctx.finish()

static func seed_from(digest: PoolByteArray) -> int:
	var b := StreamPeerBuffer.new()
	b.data_array = digest
	return b.get_64()                     # first 8 bytes; RandomNumberGenerator.seed is 64-bit

static func random_bytes(n: int) -> PoolByteArray:
	if ClassDB.class_exists("Crypto"):
		var c = Crypto.new()              # null when the engine lacks mbedtls
		if c != null:
			return c.generate_random_bytes(n)
	var rng := RandomNumberGenerator.new()
	rng.randomize()                       # fallback: not cryptographic, still unpredictable enough for co-op
	var out := PoolByteArray()
	for _i in n:
		out.append(rng.randi() & 0xFF)
	return out

func commitment(steam_id: int, secret: PoolByteArray) -> PoolByteArray:
	return sha256(u64_bytes(steam_id) + u64_bytes(round_id) + secret)

func start(p_round: int, p_members: Array, my_id: int) -> Dictionary:
	round_id = p_round
	members = p_members.duplicate()
	members.sort()
	my_secret = random_bytes(32)
	commits[my_id] = commitment(my_id, my_secret)
	return {"round": round_id, "commit": commits[my_id]}      # broadcast as SEED_COMMIT to every member

func on_commit(sender: int, msg: Dictionary) -> bool:         # true when it is time to reveal
	if done or int(msg.get("round", -1)) != round_id or not sender in members:
		return false
	if commits.has(sender):
		return false                                           # second commit: ignore, log
	var c = msg.get("commit")
	if typeof(c) != TYPE_RAW_ARRAY or c.size() != 32:
		return false
	commits[sender] = c
	return commits.size() == members.size()

func on_reveal(sender: int, msg: Dictionary) -> String:       # "", "done" or an error for the audit log
	if done or int(msg.get("round", -1)) != round_id or not commits.has(sender):
		return "reveal without commit from %d" % sender
	var s = msg.get("secret")
	if typeof(s) != TYPE_RAW_ARRAY or s.size() != 32:
		return "bad reveal size from %d" % sender
	if commitment(sender, s) != commits[sender]:
		return "commit mismatch from %d" % sender               # hard evidence; keep both values
	reveals[sender] = s
	if reveals.size() == members.size():
		run_seed = compute_run_seed()
		done = true
		return "done"
	return ""

func compute_run_seed() -> int:
	var buf := u64_bytes(round_id)
	for id in members:                                         # sorted; same on every peer
		buf.append_array(u64_bytes(id))
		buf.append_array(reveals[id])
	return seed_from(sha256(buf))
```

`PoolByteArray == PoolByteArray` compares contents in Godot 3. `TYPE_RAW_ARRAY` is the `typeof()` value of
`PoolByteArray`. Keep the secret out of logs until the round is done.

## 4. Derived RNG per purpose

```gdscript
const SeedRound = preload("res://mods-unpacked/<Namespace-Mod>/seed_round.gd")   # static helpers above

enum Purpose { SHOP = 1, LEVEL_UP = 2, CRATE = 3, MOD_DROP = 4, ARENA_DECOR = 5, TIEBREAK = 6 }

static func derived_rng(run_seed: int, wave: int, purpose: int, counter: int) -> RandomNumberGenerator:
	var buf := SeedRound.u64_bytes(run_seed)
	buf.append_array(SeedRound.u64_bytes(wave))
	buf.append_array(SeedRound.u64_bytes(purpose))
	buf.append_array(SeedRound.u64_bytes(counter))
	var rng := RandomNumberGenerator.new()
	rng.seed = SeedRound.seed_from(SeedRound.sha256(buf))
	return rng
```

| Purpose | `counter` | Who rolls | Who re-derives |
|---|---|---|---|
| Shop offers | `slot * 1000 + reroll_n` | host, when the shop opens or on reroll | that client at wave end (own shop) and optionally one other peer |
| Level-up choices | `slot * 1000 + levelup_index` | host | that client |
| Crate / loot contents | `crate_net_id` | host | the opener |
| Mod-added drops (not native) | `enemy_net_id` | host | any client, sampled |
| Tie-breaks (shared shop claims) | `0` | host | all |

Rules:
- One fresh `RandomNumberGenerator` per roll. Never carry one across rolls, or a missed message shifts the stream.
- Use `randi_range(a, b)` and integer weights. `randf()` is deterministic too, but float weight sums and
  `int(randf() * n)` invite rounding differences in your own code. `randfn` is out.
- The candidate list is the input of the roll. Sort it by `my_id` and include everything that filters it (wave,
  tier weights, luck, DLC flags, locked slots, excluded items) in a `ctx` Dictionary the host sends with the
  result. Clients re-derive from `ctx`, not from their own view of the player.
- Brotato's native rolls (enemy spawns, native drops, crits, dodges) use the global RNG and are **not**
  re-derivable. Don't try to seed them (sibling skill §6). Audit them with bounds only.
- The sibling's `hash([lobby_seed, wave, purpose])` is fine for cosmetic client-side RNG; for audited rolls use the
  SHA-256 derivation above (64-bit seed, no 32-bit collisions, same code path on every peer).

## 5. Mod-owned picker that clients can re-derive

```gdscript
# Weighted pick without replacement; ints only; identical on every peer
static func pick_weighted(rng: RandomNumberGenerator, candidates: Array, count: int) -> Array:
	# candidates: [{"id": "item_x", "w": 120}, ...] already sorted by id, w > 0
	var pool := candidates.duplicate()
	var out := []
	while out.size() < count and not pool.empty():
		var total := 0
		for c in pool:
			total += int(c.w)
		var r := rng.randi_range(0, total - 1)
		for i in pool.size():
			r -= int(pool[i].w)
			if r < 0:
				out.append(pool[i].id)
				pool.remove(i)
				break
	return out
```

The host fills `ShopItem`s from `out` (see `fill_shop_items` (hook) in `brotato-online-multiplayer`) and sends
`{"slot", "wave", "reroll_n", "ctx", "offers": out}`. The client stores it and re-derives at wave end.

## 6. Refusals and edge cases

| Case | Do |
|---|---|
| A peer never commits | Abort after 5 s, one new round (could be loss); second failure → run invalid (`seed`) |
| A peer commits but never reveals | Abort, same rule. Never finish with a subset |
| A peer reveals a secret that doesn't match | Run invalid (`seed`) immediately; keep commit + secret in the local log; no UI name |
| Host disconnects during the round | Session ends anyway (no host migration) |
| Two players only | Still worth it: neither can pick the seed alone. Audits of the other are symmetric |
| Peer joins between waves | Send round, commits, reveals; it verifies and uses the same `run_seed` |
| Reroll spam on the host side to find a good roll | Impossible: reroll_n is in the derivation and each costs gold the client ledger sees |
| Endless mode | Same seed; wave number keeps the streams apart |

## 7. Tests

- Three peers, one with a patched `on_reveal` that sends a different secret → the other two log a commit mismatch
  and the run is marked invalid on all three (the badge must appear on the cheater's screen too).
- Simulated 30 % loss on the control channel → rounds complete after retries (reliable channel), no strikes.
- Same `run_seed` printed on all peers; same shop offers re-derived on the client; a one-byte change in `ctx`
  makes the re-derivation fail (so `ctx` is complete).
