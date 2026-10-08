# Threat model, architecture options, cost

Scope: a co-op mod where cheating ruins fun, not ranked play. Goal order: (1) don't flag honest players,
(2) detect, (3) inform and let players decide, (4) keep the evidence. Prevention only where it is free
(host clamps, host-owned decisions).

## 1. Who can cheat how

| Actor | Attack | Effect | Detectable by | Detection method | Response |
|---|---|---|---|---|---|
| Host | Edits enemy HP/damage/speed (own process) | Trivial waves for all | Clients | Enemy HP at spawn vs type table × wave/difficulty scaling; kills per second plausibility | Score; run unverified |
| Host | Edits spawn counts / wave length | Shorter or easier run | Clients | Spawn count per wave inside a per-zone/difficulty band; wave timer monotonic and ≈ wall clock outside shared pause | Score; unverified |
| Host | Gives itself gold / items / stats | Unfair run, shared leaderboard pollution | Clients | Gold ledger (Δgold ≤ materials picked + wave bonus + sales); item ledger (items = purchases + loot + level-ups); stats re-derived from items where the mod computes them | Score; unverified; vote |
| Host | Chooses or re-rolls the seed | Perfect shops, drops | Everyone | Combined commit-reveal seed; re-derive mod-owned rolls | Mismatch is hard evidence |
| Host | Sends inconsistent state to different clients (equivocation) | One client sees a different game | Clients | All-to-all wave hash: host becomes the outlier | Vote: continue unverified / end |
| Host | Drops or delays a client's intents | Griefing | That client | Intent ack timeout statistics | Toast; no automated action |
| Host | Fakes the "verified" badge in a shared run file | Leaderboard fraud | File readers | Signatures of every peer over the run hash; missing/invalid = unverified | Reject file |
| Client | Speed/teleport, wall clip | Unfair survival | Host (then everyone via host) | Host clamps position to arena and max speed from host-side stats (incl. dashes) | Clamp silently; repeated → kick |
| Client | Intent spam (buy/reroll/level-up loops) | Dupes if host code has races | Host | Idempotent intents, per-slot rate limits, "pending" state | Drop; kick on flood |
| Client | Claims pickups, damage, XP | None if host owns them | Host | Host ignores such messages: they are not in the protocol | Log unknown message types |
| Client | Memory edits of its own process | Only own display and movement | Host | Same as speed/teleport; everything else is a mirror | Clamp |
| Client | Forged wave hash / commit, refusing to reveal | Blocks verification, grief | Everyone | Commit check; quorum; reveal timeout | Abort seed round; flag; kick on repeat |
| Client | Floods packets | Host CPU/bandwidth | Host, Steam relay (rate-limited) | Per-peer messages per second | Drop; kick |
| Anyone | Spoofs lobby `mods`/`proto`/`dlc` data | Joins with altered mod | Nobody (self-reported) | None. Auth tickets prove account and app, not file integrity | Accept; hashes will disagree if behaviour differs |
| Anyone | Impersonates a Steam ID | Ban evasion, framing | Steam | Transport identity (Messages/Sockets authenticated; needs the victim's machine); auth ticket bound to Steam ID | Nothing to do beyond "sender from transport" |
| Anyone (ENet/LAN) | Spoofed sender, replay | Full control | Nobody without app-level MACs | HMAC with pairwise key + seq + nonce | Use ENet only for development |

Facts behind the table: Valve's networking docs say an authenticated Steam ID means someone with access to that
account authorized the connection and impersonation requires access to the target's computer; `BeginAuthSession`
"authenticates the ticket from the entity's Steam ID to be sure it is valid and isn't reused" and registers
callbacks when the entity goes offline or cancels the ticket (SDK comments, see sources). No Brotato online mod
checked (Brotatogether, BrotatoOnline, BroTangto) does any of this; BrotatoOnline implements a kick (`player_kicked`
message, 1 s flush, close connection, kicked-set) and nothing else.

## 2. Architecture options

| Option | Catches | Misses | Cost | Verdict |
|---|---|---|---|---|
| Host authority only (sibling skill baseline) | Client gameplay cheats (host simulates everything) | Everything the host does | 0 | Baseline, keep |
| + combined seed + client audits + all-to-all hashes (this skill) | Host RNG choice, host equivocation, most host value edits (within bounds), mod-set drift | Host cheats inside tolerance; cosmetic-only edits; collusion of all peers | 1 reliable round at lobby lock; 1 hash + ≤ 1 audit batch per wave per peer; ~400 lines | **Recommended** |
| Split authority (each peer owns its player's gold/items/stats; host owns enemies/waves; everyone validates) | Host edits to other players | Every client can now edit itself; host must audit N peers; conflicts on shared shop | Protocol rewrite, more races | No |
| Full deterministic lockstep + cross-hash | Everything except equal-input cheats | Not reachable: Brotato's global RNG is shared with cosmetics, nodes are pooled, physics is frame-timed (`brotato-online-multiplayer` §2) | Rewrite of the game | No |
| Relay/verification server | Host and clients, if it re-simulates | Needs hosting, a Brotato re-simulator or trusted logic, Web API `AuthenticateUserTicket` with a publisher key, uptime | Not a mod any more | No |
| Witness peer (one client re-runs host logic for a sample of events) | Same as audits, finer | Same as audits | Pick a random client per wave as auditor to spread CPU; only when 3+ peers | Optional extension |

## 3. What a mod cannot do (don't promise it)

- No VAC, no kernel driver, no memory scanning of other processes, no file-integrity proof of other peers' mods.
  A modified mod can report any `mods` hash it likes. Valheim's CatosAntiCheat README says the same about plugin
  lists; koumodgp's process/window-name signatures kick on any match (false positives). Don't copy that.
- No kick from a Steam lobby. Steam picks a new lobby owner when the owner leaves; it can be the person you
  "kicked". Compare against the `host` lobby data key and your ban list, not against `getLobbyOwner()`.
- No proof that a run was honest: peer signatures prove that these peers agreed, not that none of them lied.
  Call the badge "peer-verified".

## 4. Cost and complexity budget

| Piece | Messages | CPU | Code |
|---|---|---|---|
| Commit-reveal | 2 reliable broadcasts per peer at lobby lock (≤ 64 B each) | nil | ~80 lines |
| Derived RNG + mod-owned shop/loot picker | none extra; offers already sent | nil | picker: 60-150 lines, the bulk of the work |
| Wave-end hash all-to-all | (n-1) × 40 B per peer per wave | µs | ~60 lines |
| Audits | host adds roll context (≤ 200 B) to shop/loot messages | ≤ 2 ms per frame in shop phase | ~200 lines |
| Auth tickets | 1 ticket (≤ 1 KB) per peer pair at join | nil | ~60 lines |
| Run log + signatures | one ≤ 1 KB message per peer at run end | RSA sign ms; keygen once | ~100 lines |

Do it in this order: hashes all-to-all (cheap, catches desync bugs too) → commit-reveal → shop re-derivation →
gold/item ledgers → auth tickets → run log. Stop where the fun/benefit ratio drops.
