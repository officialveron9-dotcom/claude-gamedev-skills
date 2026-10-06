# Online stability: disconnects, net lag, desync (summary)

Protocol design, transports, lobbies, snapshots and desync hashing are in **`brotato-online-multiplayer`**.
This page lists only what makes an online session lag, freeze or drop, and how to test for it.

## Causes → fixes

| Problem | Cause | Fix |
|---|---|---|
| Everyone times out when the host pauses, opens the menu or alt-tabs | Network node inherits pause (`PAUSE_MODE_INHERIT` under `/root` = stop); Brotato's `pause_on_focus_lost` pauses the tree | `pause_mode = Node.PAUSE_MODE_PROCESS` on every net node (heartbeat, receive loop); override native auto-pause online |
| Client drops after a long load, save or big JSON parse | Main thread blocked; no packets read or acked. ENet defaults: timeout limit 32, min 5000 ms, max 30000 ms (`NetworkedMultiplayerENet.set_peer_timeout(id, limit, min, max)`) | Keep every main-thread stall well under the timeout; spread heavy work over frames; app-level timeout longer than the worst expected stall |
| "Disconnected" with no reason after N minutes | No app-level heartbeat: frozen or dead peers are noticed only through transport timeouts, late and differently per transport | Heartbeat every 1-2 s on its own channel, timeout ~8-15 s, show "waiting for player" before dropping |
| Host leaves → clients stuck in a dead run | No host-gone handling | On host loss: stop simulation, show a message, return to main menu safely (free run state, clear caches) |
| Rubber-banding grows with enemy count | Snapshots too big or on a reliable channel (head-of-line blocking) | Unreliable snapshots within the transport limit, delta/binary encoding, reliable only for events |
| Reliable messages pile up, latency climbs to seconds | Sending reliable data every frame; large payloads; send buffer full | Rate-limit, coalesce, chunk large payloads and send a few chunks per frame; retry later when the transport refuses |
| Frame-time spikes from networking at high FPS | Polling transport and running GDScript per message every frame | Cap messages handled per frame; time-based poll throttle (e.g. ~120 Hz) when FPS is uncapped |
| Freeze when the host opens the shop | Host builds and sends one huge reliable state blob in one frame, or clients wait for a reply that was dropped by a scene change | Chunk + spread over frames; tag with scene epoch; ack and resend phase messages |
| Players see different results after a while | Desync: client ran gameplay code or RNG, or a value is outside the state hash | Host authority, state hash per wave/shop, resync on mismatch (`brotato-online-multiplayer`) |
| Client errors right after a scene change | Messages for the old scene touching freed nodes | Scene epoch on every message; drop stale ones; `alive()` checks in handlers |
| Numbers wrong after receiving JSON | JSON parses all numbers as float; big ints lose precision | `int()` at the boundary; Steam IDs as strings or 64-bit binary |

## Reference numbers from a shipped mod (BrotatoOnline, Brotato 1.1.15.4, ModLoader 6.2.0)

Not official limits; a working baseline to compare against:
- Heartbeat every 2000 ms, peer timeout 8000 ms, status poll every 250 ms; heartbeat node `PAUSE_MODE_PROCESS`.
- Battle snapshot every 120 ms, own-player state every 80 ms, wave-timer sync every 160 ms.
- At most 32 (menu) / 64 (battle) messages handled per frame; Steam callback and battle polling throttled to ~120 Hz,
  menu polling 25 Hz (comment: uncapped FPS cost several ms per frame otherwise).
- Large JSON payloads chunked: 44 000 raw bytes per chunk on Steam, 32 000 on ENet, one chunk sent per frame,
  retry after 100 ms when the send buffer is full, chunk TTL 15 s; "latest state" packets dropped after 750 ms.
- Diagnostics logged only above thresholds: packet handling > 10 ms, packets > 64 KB, batches > 128 KB,
  send queue > 4 entries or older than 500 ms.
- Risky sync paths behind `ENABLE_*` constants (several shipped disabled), event caps per snapshot (64) and per
  reliable send (96-160 entries).

## Testing (every release)

- 2, 3 and 4 players on separate machines/accounts (not only two windows on one PC).
- Simulated conditions: 100-150 ms latency with 20 ms jitter, 2-5 % loss; then a 10 s full outage.
  Tools: clumsy (Windows, WinDivert, works for any UDP), `tc qdisc ... netem delay/loss` (Linux), Steam's
  fake-lag config values for the SteamNetworkingSockets stack (see `brotato-online-multiplayer`).
- Scripted disruptions: host alt-tab, host opens pause menu, client opens pause menu, client quits mid-wave,
  host quits in the shop, client reconnects, everyone ready-up at once.
- Max-enemy wave (wave 20+ or endless, all players alive) while watching frame time on host **and** client.
- Leave a session running 30+ minutes (heartbeat drift, queue growth, memory growth).
