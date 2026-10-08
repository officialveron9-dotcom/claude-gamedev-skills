# Audits, all-to-all hashes, quorum, responses, run integrity

Godot 3 GDScript. Audits run on **clients against the host** (and on the host against clients for the few things
clients own). Everything is scored and logged; nothing acts automatically except packet drops and clamps.

## 1. Audit framework

```gdscript
# audit_log.gd  (autoload-like node under the mod's net node)
extends Node

signal warn(subject, kind)
signal run_unverified(subject)
signal vote_requested(subject)

enum Sev { MINOR = 1, MAJOR = 5, HARD = 10 }
const WARN_AT := 5
const UNVERIFIED_AT := 10
const VOTE_AT := 20

var score := {}          # steam_id -> int
var findings := []       # [{wave, tick, subject, kind, expected, got, sev}]
var baseline_wave := 0   # audits ignored up to and including this wave (late join, resync)
var run_unverified := false

func record(subject: int, kind: String, expected, got, sev: int) -> void:
	if RunData.current_wave <= baseline_wave:
		return
	findings.append({"wave": RunData.current_wave, "tick": OS.get_ticks_msec(), "subject": subject,
		"kind": kind, "expected": str(expected), "got": str(got), "sev": sev})
	score[subject] = score.get(subject, 0) + sev
	if score[subject] >= UNVERIFIED_AT and not run_unverified:
		run_unverified = true
		emit_signal("run_unverified", subject)
	elif score[subject] >= WARN_AT:
		emit_signal("warn", subject, kind)
	if score[subject] >= VOTE_AT:
		emit_signal("vote_requested", subject)

func reset_baseline() -> void:          # call on every resync payload and on late join
	baseline_wave = RunData.current_wave

func save() -> void:
	var f := File.new()
	if f.open("user://%s/audit_%d.json" % [MOD_ID, OS.get_unix_time()], File.WRITE) == OK:
		f.store_string(JSON.print({"score": score, "findings": findings}, "\t"))
		f.close()
```

Thresholds that avoid false positives from legitimate desync (floats, pooling, late packets):
- Audit **reliable events and phase states** only. Never snapshots, never interpolated positions, never anything
  within 1 s of a scene change or resync.
- Bounds get a tolerance (table below) **and** a repeat rule: minor findings count only from the second wave in a
  row; a single one is logged with `sev = 0`.
- Exact checks (re-derived rolls, commit hashes, item ledger) are `HARD` on the first miss, because loss or timing
  cannot produce them.
- Reset on resync. Skip the first wave after a join.

## 2. Bounds table (client audits the host; "hook" = Brotato member, verify per patch)

| Check | Source data | Bound | Tolerance | Sev |
|---|---|---|---|---|
| Shop offers | `SHOP_OFFERS{slot, wave, reroll_n, ctx, offers}` | `== pick_weighted(derived_rng(...), ctx.candidates, n)` | exact | HARD |
| Level-up choices, crate loot | same pattern | exact re-derivation | exact | HARD |
| Item/weapon ledger | `ITEMS_FULL` at wave start (sibling: full set every wave) vs previous + purchase/loot/level-up events | sets equal | exact (sort `my_id`, count duplicates) | HARD |
| Gold per player | `GOLD` reliable on change; pickup events carry value | `Δgold ≤ Σ pickup values + wave bonus + sales − purchases − rerolls` | +10 %, 2 waves in a row | MAJOR |
| Enemy HP at spawn | spawn event carries `max_hp`; local type table `base_hp[type]` × scaling for `(wave, difficulty, zone, elite)` (hook: enemy stats scaling in the decompiled spawner) | equality with the table | ±1 after rounding | MAJOR |
| Spawn count per wave | count of spawn events | inside a per-zone/difficulty band measured from honest runs | ±25 % | MINOR |
| Wave timer | `WAVE_TIMER` 2-5 Hz | monotonic non-increasing; `abs(Δtimer − Δgame_time) ≤ 2 s per 30 s` between shared-pause events | 2 s | MINOR |
| Damage numbers (cosmetic events) | per hit `dmg`, `weapon_id`, `crit` | `dmg ≤ weapon.max_damage × (1 + crit_mult) × (1 + %damage/100) × 1.5` from the host-sent stat set | ×1.5 | MINOR |
| Kills per second | death events | `≤ 40/s` sustained for 10 s (tune to the build) | | MINOR |
| XP / level | `XP` on change | level consistent with Brotato's XP curve (hook) for that XP | exact | MAJOR |
| Player stats | host-sent stat set vs stats recomputed from the item ledger with the mod's own stat summation (if the mod implements it; else skip) | equal | exact for ints | MAJOR |

Host audits of clients (only what clients own): position inside the arena and `distance ≤ max_speed × dt × 1.3`
with `max_speed` from host-side stats including dashes (clamp, don't flag); intents per slot ≤ 30/s; unknown
message types → log the sender.

## 3. Re-derivation at wave end (time-sliced)

```gdscript
var _queue := []       # audit jobs: {"kind": "shop", "msg": {...}}

func _process(_delta: float) -> void:
	if get_tree().paused or not _in_shop_phase or _queue.empty():
		return
	var t0 := OS.get_ticks_usec()
	while not _queue.empty() and OS.get_ticks_usec() - t0 < 2000:     # 2 ms per frame
		var job: Dictionary = _queue.pop_front()
		if job.kind == "shop":
			var m: Dictionary = job.msg
			var rng := Rng.derived_rng(run_seed, m.wave, Rng.Purpose.SHOP, m.slot * 1000 + m.reroll_n)
			var expect := Rng.pick_weighted(rng, m.ctx.candidates, m.offers.size())
			if expect != m.offers:
				audit.record(host_id, "shop_mismatch", expect, m.offers, audit.Sev.HARD)
```

## 4. All-to-all wave-end hashes

```gdscript
static func canon(parts: Array) -> PoolByteArray:      # ints, strings, nested arrays only
	var b := StreamPeerBuffer.new()
	for p in parts:
		match typeof(p):
			TYPE_INT:
				b.put_u8(1)
				b.put_64(p)
			TYPE_STRING:
				b.put_u8(2)
				b.put_utf8_string(p)
			TYPE_ARRAY:
				b.put_u8(3)
				b.put_32(p.size())
				b.put_data(canon(p))
			_:
				push_error("canon(): unsupported type %d" % typeof(p))
	return b.data_array

func wave_hash_parts() -> Array:
	var parts := [RunData.current_wave, run_seed]
	for i in RunData.get_player_count():
		var pd = RunData.players_data[i]
		var items := []
		for it in pd.items:                           # (hook) verify the member name per patch
			items.append(it.my_id)
		items.sort()
		var weapons := []
		for w in RunData.get_player_weapons(i):
			weapons.append(w.my_id)
		weapons.sort()
		parts.append([i, int(pd.gold), int(pd.current_xp), int(pd.current_level), items, weapons])
	return parts

func broadcast_wave_hash() -> void:
	var h := SeedRound.sha256(canon(wave_hash_parts()))
	_hashes[my_id] = h
	net.broadcast_reliable(MSG_WAVE_HASH, {"wave": RunData.current_wave, "hash": h})   # to ALL peers
```

- Send when leaving the shop (state is final, no gameplay running). Collect for up to 5 s, then resolve with
  `resolve_quorum()` (SKILL.md §5) over **connected** peers only.
- `status == "outliers"`: each outlier gets a `MAJOR` finding on every peer; if the outlier is the host, open a vote.
- `status == "undecided"` (2 players or a tie): show both players a diff of `wave_hash_parts()` (exchange the parts,
  ≤ 1 KB) and mark the run unverified. Nobody is accused.
- Disagreement is usually a **desync bug**, not a cheat. The sibling's resync (host → that slot) still runs; the
  audit only records.

## 5. Votes (host mismatch, kick)

| Vote | Who votes | Needs | Timeout default |
|---|---|---|---|
| Host is the outlier | all clients | majority of connected clients | continue, run unverified |
| Kick peer X | all connected peers except X | majority, and host must agree if host is a voter | no kick |
| End run | everyone | majority | continue |

Message: `VOTE_OPEN{vote_id, kind, target, deadline_ms}` from the initiator to all; `VOTE_CAST{vote_id, yes}` to all
(not only to the host, so everyone can count); each peer counts locally; the host executes kicks. A vote the host
refuses to execute is itself a finding (`MAJOR`), shown to all clients.

Kick execution (BrotatoOnline pattern, proven in a shipped mod): send `KICKED` reliable to the target, remove it from
the slot table, stop accepting its sessions and packets, wait 1 s so the reliable message flushes, then
`closeSessionWithUser`/`closeP2PSessionWithUser`, and set lobby data `banned = "<id>,<id>"`. Every peer reads
`banned` on `lobby_data_update` and ignores those IDs. If the lobby owner later becomes a banned ID, peers leave.

## 6. Local ban list

```gdscript
const BAN_PATH := "user://%s/banlist.json"
var bans := {}        # "7656119..." -> {"when": unix, "why": "...", "run": "<run_hash>"}

func is_banned(steam_id: int) -> bool:
	return bans.has(str(steam_id))            # strings: JSON would turn the int into a float

func on_lobby_members_changed(member_ids: Array) -> void:
	for id in member_ids:
		if is_banned(id):
			if net.is_host():
				net.kick(id)                  # host: don't let them play
			else:
				net.leave_lobby("banned peer present")
```

Ban only after a vote or an explicit user action in the player list (BrotatoOnline has a kick dialog there; add
"kick and ban"). A single mismatch never bans. Show the ban reason and allow unbanning in the mod settings.

## 7. Run integrity (verified-run log)

The log is small: per wave `{wave, hash, outliers, audit_score_delta, purchases: [...], levelups: [...], deaths: [...]}`
plus the seed round (`round`, `commits`, `reveals`), the member list and the mod/game versions.

```gdscript
func finish_run(won: bool) -> void:
	var log_bytes := canon([ "brotato-run-v1", run_seed, members, won, waves_summary ])   # ints/strings only
	var run_hash := SeedRound.sha256(log_bytes)
	var sig := crypto.sign(HashingContext.HASH_SHA256, run_hash, my_key)                 # null-safe: skip if no Crypto
	net.broadcast_reliable(MSG_RUN_SIGN, {"hash": run_hash, "sig": sig})
	# collect for 10 s; then
	var verified := _all_connected_slots_signed_same_hash(run_hash) and not audit.run_unverified \
		and seed_round.done and _no_mid_run_disconnects
	_save_run_file(run_hash, verified)      # user://<mod>/runs/<hex>.json: log, hashes, pubkeys, signatures
```

Badge rules: "peer-verified" only if every slot that played signed the same `run_hash`, the seed round completed
with all commits verified, no peer crossed `UNVERIFIED_AT`, no quorum result was "outliers" or "undecided", and no
one disconnected mid-wave. Anything else is "unverified" with the reason listed. A reader of the file re-checks
signatures against the embedded public keys and the Steam IDs; it cannot prove the peers did not collude.
