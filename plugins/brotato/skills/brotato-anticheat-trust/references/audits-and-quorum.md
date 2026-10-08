# Audits, all-to-all hashes, diagnostic quorum, run state, run integrity

Godot 3 GDScript. Audits run on **clients against the host** (and on the host against clients for the few things
clients own). Everything is scored and logged locally; the only consequence is `run_state.invalidate()`. No kick,
no vote, no name in the UI ([optional-moderation.md](optional-moderation.md) is off by default).

## 1. Audit framework

```gdscript
# audit_log.gd  (node under the mod's net node)
extends Node

signal invalidated(reason)

enum Sev { MINOR = 1, MAJOR = 5, HARD = 10 }
const INVALID_AT := 10

var score := {}          # steam_id -> int  (diagnostic only; never shown)
var findings := []       # [{wave, tick, subject, kind, expected, got, sev}]
var baseline_wave := 0   # audits ignored up to and including this wave (late join, resync)

func record(subject: int, kind: String, expected, got, sev: int) -> void:
	if RunData.current_wave <= baseline_wave:
		return
	findings.append({"wave": RunData.current_wave, "tick": OS.get_ticks_msec(), "subject": subject,
		"kind": kind, "expected": str(expected), "got": str(got), "sev": sev})
	score[subject] = score.get(subject, 0) + sev
	if score[subject] >= INVALID_AT:
		emit_signal("invalidated", "audit")        # run_state.invalidate("audit"); UI text is neutral

func reset_baseline() -> void:          # call on every resync payload and on late join
	baseline_wave = RunData.current_wave

func save() -> void:
	var f := File.new()
	if f.open("user://%s/audit_%d.json" % [MOD_ID, OS.get_unix_time()], File.WRITE) == OK:
		f.store_string(JSON.print({"score": score, "findings": findings}, "\t"))
		f.close()
```

Thresholds that avoid false positives from legitimate desync (floats, pooling, late packets). A false positive
now costs a ranked run, so err on the side of silence:
- Audit **reliable events and phase states** only. Never snapshots, never interpolated positions, never anything
  within 1 s of a scene change or resync.
- Bounds get a tolerance (table below) **and** a repeat rule: minor findings count only from the second wave in a
  row; a single one is logged with `sev = 0`.
- Exact checks (re-derived rolls, commit hashes, item ledger) are `HARD` on the first miss, because loss or timing
  cannot produce them.
- Reset on resync. Skip the first wave after a join.
- `subject` stays in the local file for debugging. The toast and the end screen show only the reason category.

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
with `max_speed` from host-side stats including dashes (clamp, don't flag; sustained violation over 3 s →
`MAJOR`); intents per slot ≤ 30/s (drop); unknown message types → log the sender.

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

- Send when leaving the shop (state is final, no gameplay running). Collect for up to 5 s over **connected**
  peers; a peer whose hash never arrives counts as a disconnect (`invalid: disconnect`), not as a mismatch.
- Decision: `seen.size() > 1` → `run_state.invalidate("state_mismatch")` (SKILL.md §5). That is all.
- Diagnostic only (local file): the majority/minority split below. With 2 peers there is no majority; with 3+
  a lone outlier is usually the desynced one, but it is still not shown in the UI.

```gdscript
func diag_quorum(hashes: Dictionary) -> Dictionary:    # steam_id -> PoolByteArray; written to the audit file
	var groups := {}
	for id in hashes:
		var key: String = hashes[id].hex_encode()
		groups[key] = groups.get(key, 0) + 1
	var best := ""
	for key in groups:
		if best == "" or groups[key] > groups[best]:
			best = key
	var minority := []
	for id in hashes:
		if hashes[id].hex_encode() != best:
			minority.append(id)
	return {"n": hashes.size(), "groups": groups.size(), "majority_size": groups.get(best, 0), "minority": minority}
```

- Disagreement is usually a **desync bug**, not a cheat. The sibling's resync (host → that slot) still runs so
  the game stays playable; the run stays invalid for the rest of the run.

## 5. Run state (the single response)

`run_state` (SKILL.md §7) is sticky and additive. Reasons: `seed` (round failed twice / reveal mismatch),
`state_mismatch` (any wave-hash difference), `auth` (any auth-ticket result other than OK, at join or later),
`audit` (score ≥ 10), `disconnect` (a peer left mid-wave, or its hash never arrived), `version` (mod/game/DLC
mismatch found after lobby lock). On the first reason: neutral toast, badge, `MSG_RUN_INVALID` to all peers, and
`invalid` + `reasons` ride along in every phase message and the resync payload so late joiners and peers that
missed the message agree. The invalid flag never clears during a run.

UI text rules: "Run not verified: state mismatch" / "Run not verified: seed" / "Run not verified: auth". No Steam
ID, no slot, no colour on a player. Players keep playing; nothing is disabled except the ranked upload.

## 6. Run integrity (peer-verified run log)

The log is small: per wave `{wave, hash, audit_score_delta, purchases: [...], levelups: [...], deaths: [...]}`
plus the seed round (`round`, `commits`, `reveals`), the member list, the mod/game versions and `reasons`.

```gdscript
func finish_run(won: bool) -> void:
	var log_bytes := canon([ "brotato-run-v1", run_seed, members, won, waves_summary ])   # ints/strings only
	var run_hash := SeedRound.sha256(log_bytes)
	var sig := PoolByteArray()
	if crypto != null:
		sig = crypto.sign(HashingContext.HASH_SHA256, run_hash, my_key)
	net.broadcast_reliable(MSG_RUN_SIGN, {"hash": run_hash, "sig": sig})
	# collect for 10 s; then
	var verified := not run_state.invalid and seed_round.done \
		and _all_slots_that_played_signed_same_hash(run_hash)
	_save_run_file(run_hash, verified, run_state.reasons)   # user://<mod>/runs/<hex>.json: log, hashes, pubkeys, sigs
```

Badge rules: "peer-verified" only if `run_state.invalid` is false at the end, the seed round completed with all
commits verified, and every slot that played signed the same `run_hash`. Anything else is "not verified" with the
reasons listed. A reader of the file re-checks signatures against the embedded public keys and the Steam IDs; it
cannot prove the peers did not collude. Ranked boards additionally need [ranked-backend.md](ranked-backend.md).
