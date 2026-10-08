# Threat model, architecture options, cost

Scope: a co-op mod where cheating ruins fun, not ranked play. Goal order: (1) don't invalidate honest runs,
(2) detect, (3) mark the run invalid and keep playing, (4) keep the evidence locally. Prevention only where it
is free (host clamps, host-owned decisions). The consequence column is always the same by design.

## 1. Who can cheat how

| Actor | Attack | Effect | Detectable by | Detection method | Consequence |
|---|---|---|---|---|---|
| Host | Edits enemy HP/damage/speed (own process) | Trivial waves for all | Clients | Enemy HP at spawn vs type table × wave/difficulty scaling; kills per second plausibility | Run invalid |
| Host | Edits spawn counts / wave length | Shorter or easier run | Clients | Spawn count per wave inside a per-zone/difficulty band; wave timer monotonic and ≈ wall clock outside shared pause | Run invalid |
| Host | Gives itself gold / items / stats | Unfair run, shared board pollution | Clients | Gold ledger (Δgold ≤ materials picked + wave bonus + sales); item ledger (items = purchases + loot + level-ups); stats re-derived from items where the mod computes them | Run invalid |
| Host | Chooses or re-rolls the seed | Perfect shops, drops | Everyone | Combined commit-reveal seed; re-derive mod-owned rolls | Run invalid (hard evidence in the local log) |
| Host | Sends inconsistent state to different clients (equivocation) | One client sees a different game | Clients | All-to-all wave hash: any difference | Run invalid |
| Host | Drops or delays a client's intents | Griefing | That client | Intent ack timeout statistics | Local diagnostic only |
| Host | Fakes the "verified" badge in a shared run file | Board fraud | File readers, backend | Signatures of every peer over the run hash; missing/invalid = unverified | File rejected |
| Client | Speed/teleport, wall clip | Unfair survival | Host (then everyone via host) | Host clamps position to arena and max speed from host-side stats (incl. dashes) | Clamped silently; beyond tolerance: run invalid |
| Client | Intent spam (buy/reroll/level-up loops) | Dupes if host code has races | Host | Idempotent intents, per-slot rate limits, "pending" state | Dropped |
| Client | Claims pickups, damage, XP | None if host owns them | Host | Host ignores such messages: they are not in the protocol | Logged |
| Client | Memory edits of its own process | Only own display and movement | Host | Same as speed/teleport; everything else is a mirror | Clamped |
| Client | Forged wave hash / commit, refusing to reveal | Blocks verification, grief | Everyone | Commit check; hash comparison; reveal timeout | Seed round aborted once, then run invalid |
| Client | Floods packets | Host CPU/bandwidth | Host, Steam relay (rate-limited) | Per-peer messages per second | Dropped |
| Anyone | Spoofs lobby `mods`/`proto`/`dlc` data | Joins with altered mod | Nobody (self-reported) | None. Auth tickets prove account and app, not file integrity | Accepted; later hash differences invalidate |
| Anyone | Impersonates a Steam ID | Framing | Steam | Transport identity (Messages/Sockets authenticated; needs the victim's machine); auth ticket bound to Steam ID | Nothing beyond "sender from transport" |
| Anyone (ENet/LAN) | Spoofed sender, replay | Full control | Nobody without app-level MACs | HMAC with pairwise key + seq + nonce | Use ENet only for development |

Facts behind the table: Valve's networking docs say an authenticated Steam ID means someone with access to that
account authorized the connection and impersonation requires access to the target's computer; `BeginAuthSession`
"authenticates the ticket from the entity's Steam ID to be sure it is valid and isn't reused" and registers
callbacks when the entity goes offline or cancels the ticket (SDK comments, see sources). No Brotato online mod
checked (Brotatogether, BrotatoOnline, BroTangto) does any of this.

## 2. Architecture options

| Option | Catches | Misses | Cost | Verdict |
|---|---|---|---|---|
| Host authority only (sibling skill baseline) | Client gameplay cheats (host simulates everything) | Everything the host does | 0 | Baseline, keep |
| + combined seed + client audits + all-to-all hashes, fail-closed (this skill) | Host RNG choice, host equivocation, most host value edits (within bounds), mod-set drift | Host cheats inside tolerance; cosmetic-only edits; collusion; local-only cheats (SKILL.md §8) | 1 reliable round at lobby lock; 1 hash + ≤ 1 audit batch per wave per peer; ~400 lines | **Recommended** |
| Split authority (each peer owns its player's gold/items/stats; host owns enemies/waves; everyone validates) | Host edits to other players | Every client can now edit itself; host must audit N peers; conflicts on shared shop | Protocol rewrite, more races | No |
| Full deterministic lockstep + cross-hash | Everything except equal-input cheats | Not reachable: Brotato's global RNG is shared with cosmetics, nodes are pooled, physics is frame-timed (`brotato-online-multiplayer` §2) | Rewrite of the game | No |
| Witness-model histories ([witness-ranking.md](witness-ranking.md)) | Forged records shown to non-participants, edited records, key swaps | Collusion of all participants; nothing for people who never play together | ~250 lines, one batch per lobby | **Recommended** for scores |
| Any server / global board ([optional-backend.md](optional-backend.md)) | - | - | Owner's rule: no server, ever; a global board without one is forgeable by anyone | **Never** |
| Witness peer (one client re-runs host logic for a sample of events) | Same as audits, finer | Same as audits | Pick a random client per wave as auditor to spread CPU; only when 3+ peers | Optional extension |

## 3. What a mod cannot do (don't promise it)

- No VAC, no kernel driver, no memory scanning of other processes, no file-integrity proof of other peers' mods.
  A modified mod can report any `mods` hash it likes. Valheim's CatosAntiCheat README says the same about plugin
  lists; koumodgp's process/window-name signatures kick on any match (false positives). Don't copy that.
- No proof that a run was honest: peer signatures prove that these peers agreed, not that none of them lied.
  Call the badge "peer-verified"; there is no "server-verified" (no server, ever).
- No enforcement: kicks and bans are deliberately off ([optional-moderation.md](optional-moderation.md)).

## 4. Cost and complexity budget

| Piece | Messages | CPU | Code |
|---|---|---|---|
| Commit-reveal | 2 reliable broadcasts per peer at lobby lock (≤ 64 B each) | nil | ~80 lines |
| Derived RNG + mod-owned shop/loot picker | none extra; offers already sent | nil | picker: 60-150 lines, the bulk of the work |
| Wave-end hash all-to-all | (n-1) × 40 B per peer per wave | µs | ~60 lines |
| Audits | host adds roll context (≤ 200 B) to shop/loot messages | ≤ 2 ms per frame in shop phase | ~200 lines |
| Auth tickets | 1 ticket (≤ 1 KB) per peer pair at join | nil | ~60 lines |
| Run state + run log + signatures | one `RUN_INVALID` on first finding; one ≤ 1 KB message per peer at run end | RSA sign ms; keygen once | ~100 lines |

Do it in this order: hashes all-to-all (cheap, catches desync bugs too) → run state badge → commit-reveal → shop
re-derivation → gold/item ledgers → auth tickets → run records → witness exchange. Stop where the fun/benefit
ratio drops.
