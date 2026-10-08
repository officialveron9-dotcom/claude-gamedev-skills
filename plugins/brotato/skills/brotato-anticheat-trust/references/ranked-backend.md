# Ranked submissions: what a backend must do (and cannot do)

Peer signatures prove that the peers agreed, not that they were honest. A ranked leaderboard needs a server that
binds each signature to a Steam account and re-checks the consistency evidence. It does **not** re-simulate the run:
Brotato's native RNG (shared with cosmetics), node pooling and frame-timed physics are not reproducible outside
the game (`brotato-online-multiplayer` §2). The server verifies identity, agreement and plausibility. Nothing more.

## 1. Blocker to settle first: the Web API key

`ISteamUserAuth/AuthenticateUserTicket/v1` requires a **publisher** Web API key registered to the group that owns
app 1942280 (verify: partner docs were unreachable; from memory of the Steamworks Web API reference). A mod author
cannot create one; only the game's developer can issue it. Options:
1. Ask the developer for a key or for a validation endpoint they host (cleanest).
2. Steam OpenID (`https://steamcommunity.com/openid`) in a browser to bind a Steam ID to an upload token. Works
   without a publisher key, but needs a browser round trip (`OS.shell_open`) and a return URL.
3. No identity binding: accept peer public keys as pseudonymous identities. Boards are then "per key", and a
   cheater can mint keys. Only acceptable for unranked sharing.

The session tickets from `getAuthSessionTicket` are rejected by the Web API ("not to be used for
ISteamUserAuth\AuthenticateUserTicket - it will fail", SDK comment). Use `getAuthTicketForWebApi`.

## 2. Protocol

```
client (each peer)                         server
  POST /runs/{run_hash}/begin  ─────────▶  create or load run; return {nonce, expires_in}
  (one peer is enough; idempotent)
  getAuthTicketForWebApi("brotato-ranked")  (identity string must equal the server's expected identity)
  sig = sign(sha256(run_hash || nonce))
  POST /runs/{run_hash}/peers  ─────────▶  { steamid, ticket_hex, pubkey_pem, sig, run_log? }
                                           validate ticket → steamid must equal claimed
                                           store (run_hash, steamid) upsert
  ...all peers listed in the log...        when all present (or window expires): verify, score, publish
  GET  /runs/{run_hash}        ◀─────────  {status: pending|verified|invalid, reasons: [...]}
```

Upload content (one copy of the run log is enough; every peer sends its own signature):

| Field | Content | Server check |
|---|---|---|
| `run_hash` | `sha256(canon(log))`, hex | recompute from the uploaded log; must match the URL and every signature |
| `log` | version strings, member Steam IDs (sorted), seed round (`round`, commits, reveals), per wave: hash, purchases, level-ups, deaths, gold/XP per slot, duration, audit score, `verified` flag from the game | commits == `sha256(id ‖ round ‖ secret)`; run seed recomputed equals the logged one; all per-wave hashes identical across peers' signed copies; `verified == true`; versions on the allow-list |
| `ticket_hex` | Web API ticket (`ticket_buffer.hex_encode()`) | `AuthenticateUserTicket` → `result == "OK"`, `steamid` equals the claimed one and is in the member list, `vacbanned`/`publisherbanned` false, `ownersteamid` recorded (borrowed copies allowed or not: policy) |
| `pubkey_pem`, `sig` | RSA public key, `sign(SHA256, sha256(run_hash ‖ nonce))` | signature verifies; key pinned per Steam ID after first use (a changed key = manual review) |
| `wave_sigs` (optional) | per-wave hash signatures from the game | lets the server reject a log edited after the run |

Plausibility bounds the server applies (same spirit as the client audits, coarser): waves × minimum wave time ≤
duration ≤ waves × maximum; total gold ≤ f(waves, difficulty); items ≤ purchases + loot events; level ≤ XP curve;
version/mod allow-list; one run per `run_hash`; at most N uploads per Steam ID per hour.

Idempotency and replay:
- `run_hash` is the primary key; `(run_hash, steamid)` upserts; re-uploads of an identical payload return the
  stored status. A different `log` for the same `run_hash` is impossible (hash mismatch) and is rejected.
- The nonce expires (10 min) and is bound to the signature, so a captured upload cannot be replayed later.
- Web API tickets are short-lived and tied to the identity string; a ticket from another service name fails.
- The server never trusts the game's own `verified` flag alone; it is one input among the checks above.

## 3. Client side (Godot 3)

```gdscript
var _http: HTTPRequest
var _web_ticket := PoolByteArray()

func _ready() -> void:
	_http = HTTPRequest.new()
	_http.use_threads = true
	_http.timeout = 15
	add_child(_http)
	_http.connect("request_completed", self, "_on_http_done")
	Steam.connect("get_ticket_for_web_api", self, "_on_web_ticket")

func request_web_ticket() -> void:
	Steam.call("getAuthTicketForWebApi", "brotato-ranked")        # call(): keeps the script parsing on builds without it

func _on_web_ticket(auth_ticket: int, result: int, ticket_size: int, ticket_buffer: Array) -> void:
	if result != Steam.RESULT_OK:
		return
	_web_ticket = PoolByteArray(ticket_buffer).subarray(0, ticket_size - 1)   # signal delivers an Array (v3.29)
	_upload()

func _upload() -> void:
	var body := JSON.print({
		"steamid": str(Steam.getSteamID()),                       # String: JSON floats corrupt 64-bit ints
		"ticket_hex": _web_ticket.hex_encode(),
		"pubkey_pem": my_key.save_to_string(true).replace("\r", ""),
		"sig": sign_digest(SeedRound.sha256(run_hash + nonce_bytes)).hex_encode(),
		"log": run_log,                                            # ints and strings only
	})
	var headers := PoolStringArray(["Content-Type: application/json"])
	var err := _http.request(BASE_URL + "/runs/%s/peers" % run_hash.hex_encode(), headers, true,
		HTTPClient.METHOD_POST, body)
	if err != OK:
		push_warning("upload not started: %d" % err)              # ERR_BUSY: previous request still running

func _on_http_done(result: int, code: int, _headers: PoolStringArray, body: PoolByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		return                                                     # retry later with backoff; keep the run file
	var parsed := JSON.parse(body.get_string_from_utf8())
	if parsed.error == OK:
		hud.set_rank_status(parsed.result.get("status", "pending"))
```

Notes: `HTTPRequest.request(url, custom_headers, ssl_validate_domain, method, request_data: String)`; `request_raw`
takes a `PoolByteArray` body (3.6 source). HTTPS needs the mbedtls module, the same one `Crypto` needs, so one
feature check covers both. One `HTTPRequest` handles one request at a time (`ERR_BUSY`). Keep uploads off the
gameplay path (end screen) and never block on them. The publisher key, if any, lives on the server only.

## 4. Server-side notes

- Store the full upload (evidence) and the decision with reasons; expose `GET /runs/{hash}` for the badge.
- Rate-limit per Steam ID and per IP; reject logs larger than ~64 KB.
- Validate tickets server-to-Valve over HTTPS with the key in an environment variable; log Valve's raw response.
- A run with any peer missing after the window is `invalid: incomplete`, not pending forever.

## 5. Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Valve returns `result != OK` for every ticket | Session ticket uploaded, wrong `identity`, or user key instead of publisher key | `getAuthTicketForWebApi` with the server's identity string; publisher key |
| Ticket valid but `steamid` ≠ claimed | Client uploaded another peer's ticket or a stale one | Reject; each peer uploads its own |
| Signature fails only for some peers | PEM with `\r\n`, or signature over text instead of the digest | `replace("\r", "")`; sign `sha256(run_hash ‖ nonce)` bytes |
| Same run uploaded twice with different outcomes | `verified` computed per upload | Decide once per `run_hash`; later uploads only add peers |
| Everyone's upload "pending" forever | Window never closes when a peer disconnected | Expire with `invalid: incomplete` |
| `HTTPRequest` returns `RESULT_SSL_HANDSHAKE_ERROR` | Engine without mbedtls or missing system CA on Linux | Feature-detect; set `ssl_validate_domain` true and test on Linux |
