# Symptom → cause → fix

Versions: Brotato 1.1.15.x (custom Godot 3.6/3.7-dev build), GodotSteam 3.2x compiled in, Mod Loader 6.x.
Posture: the only in-game response is "run not verified". Rows below never lead to a kick.

| Symptom | Cause | Fix |
|---|---|---|
| Honest run invalidated right after a resync, late join or reconnect | Ledger/baseline still holds pre-resync values; events applied twice | `audit.reset_baseline()` on every resync payload; skip audits for the first wave after a join |
| Every run invalidated after the host alt-tabbed or opened the menu | Wave-timer check compared against wall clock across a shared pause | Treat shared pause as an event; compare game time only between pause events |
| Runs invalidated under packet loss or high ping | Audits based on unreliable snapshots or on event order | Audit only reliable events and phase states; never positions from snapshots |
| Hash mismatch although values look equal | Floats, Dictionary insertion order, unsorted arrays, interpolated values | `canon()` over ints/strings only, lists sorted |
| Hashes differ only on the host, all clients agree | Host hashes before `call_deferred` events apply, or includes host-only fields (timer float, pool IDs) | Hash the exact state that was broadcast, after applying deferred events |
| Hash differs only on one client every wave | Client-side mod (another mod) changes RunData, or a stale zip | Check `mods` hash; show the diff in the local log; it is a desync bug until proven otherwise |
| "Run not verified" shown on one peer only | `MSG_RUN_INVALID` not broadcast, or dropped on epoch change | Broadcast reliable on first finding; include `invalid` + `reasons` in every phase message and the resync payload |
| Commit verification fails for exactly one peer | Different byte encoding (`str(id)` vs `put_64`, utf8 vs ascii) or a different round id | One shared `u64_bytes()`/`canon()`; include `round` in commit and reveal |
| Run seed differs between peers | Reveals iterated in Dictionary order | `ids.sort()` before concatenation |
| Reveal missing after a disconnect during lobby lock | Peer left mid-round | Abort the round, re-commit with the remaining members; never compute with a subset |
| Seed round aborts twice, run starts invalid | Loss on the control channel, or a peer never reveals | Reliable channel + 5 s timeouts; after the second abort the run runs on the host seed and is invalid by design |
| Peer sends a second, different commit | Attempt to re-roll after seeing others | Keep the first commit per peer per round; log the second |
| Shop re-derivation mismatches for every peer every time | Picker uses `randf`/float weights or iterates an unsorted candidate list | `randi_range`, integer weights, candidates sorted by `my_id`, same `ctx` as the host |
| Shop re-derivation mismatches only after rerolls | Reroll counter or lock state not part of the derivation | `counter = slot * 1000 + reroll_n`; locked items excluded on both sides |
| `beginAuthSession` returns 2 (`DUPLICATE_REQUEST`) | A session for that Steam ID is still open (rejoin) | `endAuthSession(id)` before `beginAuthSession` |
| `beginAuthSession` returns 1 (`INVALID_TICKET`) | Buffer not trimmed to `size`, ticket for another peer (identity-bound), or stale ticket | `buffer.subarray(0, size - 1)`; fresh ticket per peer; send only after `get_auth_session_ticket_response` with result `RESULT_OK` |
| `validate_auth_ticket_response` never fires | No `Steam.run_callbacks()` on a PROCESS node, editor run, not launched through Steam | PROCESS-mode net node; test in the packaged game with two accounts |
| `validate_auth_ticket_response` with 1 or 6 mid-run | Peer lost Steam connection or cancelled the ticket (left) | Run invalid (`auth`), player keeps playing; it is also a disconnect signal, so combine with the heartbeat |
| Response 2 (`NO_LICENSE_OR_EXPIRED`) for a Family Sharing user | `owner_id != auth_id`; borrowed game | Policy: allow but unranked, or treat as OK; DLC checks with `userHasLicenseForApp` may need the owner (verify) |
| `getAuthSessionTicket()` raises a parse error on load | Wrong argument count for that build | `Steam.call("getAuthSessionTicket")`; feature-detect with `Steam.has_method()` |
| Ticket Dictionary has no `id` key | Older GodotSteam build names it differently | Log the Dictionary once; read `t.get("id", t.get("handle", 0))` |
| Signature verifies on Windows, fails on Linux (or vice versa) | Signed a text (`JSON.print` float formatting, `\r\n` in PEM, locale) | Sign `sha256(canon(...))`; PEM via `save_to_string(true)` with `\r` stripped |
| `Crypto.new()` is `null`, "Crypto is not available when the mbedtls module is disabled" | Custom engine build without mbedtls | Feature-detect; hash-only mode (no signatures, badge "unsigned", never ranked) |
| `The identifier "Crypto" isn't declared` | Non-Steam/console build or stripped engine | `ClassDB.class_exists("Crypto")` and `load()` the crypto script lazily |
| Audit batch stutters the shop | All audits in one frame, string-keyed Dictionaries per enemy | Time-slice ≤ 2 ms per frame; audit ledgers, not entities |
| "Verified" badge shown although a peer disconnected mid-run | Missing signature not treated as failure | Badge only if every slot that played signed the same run hash; disconnect mid-wave → `invalid: disconnect` |
| Honest client's run invalidated for speed | Host clamps with base speed, not host-side stats (speed items, dash, slow effects) | Compute the cap from host-side stats per tick, tolerance ×1.3, clamp silently, invalidate only on sustained violations |
| Gold ledger drifts by small amounts | Material value rounding, bonus gold items, selling | Integer ledger from host events (pickup value, sale value); tolerance +10 % and ≥ 2 waves in a row before a finding |
| Backend rejects every ticket (`result != OK`) | Session ticket instead of Web API ticket, wrong identity string, user key instead of publisher key | `getAuthTicketForWebApi("<identity>")`, same identity on the server, publisher key (see ranked-backend.md) |
| Upload never starts (`ERR_BUSY`) | One `HTTPRequest` reused while a request runs | Queue uploads; one node per in-flight request |
