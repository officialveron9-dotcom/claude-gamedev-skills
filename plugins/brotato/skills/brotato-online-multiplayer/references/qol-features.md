# QoL features for online play: pitfalls only

The host owns the authoritative state of every feature. Clients send intents and receive the result. Message
classes are defined in [architecture.md](architecture.md).

## Pause and pause voting

- Clients must not pause the tree on their own. Choose one model: the host pauses, a vote (all or a majority, with
  a 10-15 s timeout), or any player pauses plus a host-side cooldown.
- Unpause with a host-timed countdown (e.g. 3 s) that is broadcast once. Every peer resumes on the host's
  signal, not on its local timer.
- Send the pause state reliably **and** include it in every snapshot, so a client that missed the event
  recovers.
- Reject pause requests during scene changes and the end-of-wave transition. A pause there makes a client
  miss the phase change. The shop has no timer, so don't offer a pause there at all.
- A local options or volume menu is an overlay that does not pause anything. Warn the player that their
  character keeps taking hits, or turn opening it into a pause request.

## Ready checks (shop "Go", lobby start)

- Send the desired state (`ready = true/false`), not "toggle". A duplicated or replayed toggle flips it back.
  Brotatogether sends the new state.
- The host advances when every **connected** slot is ready. Treat disconnected slots as ready, and offer a host
  "force start" with a short countdown.
- Before sending the phase change to the next wave, the host sends the final shop and inventory state, so
  clients enter the wave with the same build.
- If a player buys or rerolls after readying, either clear their ready flag or block shop input while ready.
  Pick one rule and enforce it on the host.

## Shops

- Brotato's co-op shop is already per player (separate offers and gold). The host rolls each player's shop
  (`fill_shop_items` runs on the host only) and sends `my_id` lists.
- Don't let the client update optimistically: show the item as "pending" until the host confirms. With a
  shared shop or gifting, two players can claim the same item in the same RTT window. The host processes
  claims in arrival order and rejects the second.
- The reroll price, item prices (luck, stats, discounts) and lock state are host values. Display them; never
  recompute them on the client.
- Gifting or trading: the host validates both sides and sends **both** players' updated inventories in one
  reliable message, so the change is never half applied.
- Combining weapons and discarding: identify the weapon by (`my_id`, inventory index, `is_cursed`). Two
  identical weapons share a `my_id`.

## Level-up choices, crates, loot

- The host rolls the choices and the reroll results. The client renders them from IDs and sends
  choose/reroll/take/discard intents. BroTangto adds a one-second per-slot gate against double presses.
- Players finish their menus at different times. Keep each slot's menu state separate, and don't let one
  player's "done" close the others' menus.
- Optional AFK rule: the host auto-picks after N seconds. Show the countdown on every peer from the host's time.

## Ping and connection display

- With Networking Messages, `Steam.getSessionConnectionInfo(id, false, true)` returns `ping`, `local_quality`
  and `remote_quality`. Otherwise, run an app-level ping on the **unreliable** channel that echoes a sender
  timestamp, and smooth it (EMA). Pings over the reliable channel include retransmits and Nagle delay.
- Only compare times taken on the same machine (RTT). Clocks of different PCs are not synchronized.
- Also show the snapshot age (ms since the last host snapshot). That is what players perceive as lag, and it
  exposes host frame drops that ping can't show.
- The topology is a star: show each client's ping to the host. Client-to-client ping is meaningless.

## Spectating after death

- A dead slot stops sending movement, and the host ignores movement for dead players (Brotatogether returns
  early on `player.dead`). Brotatogether users report duplicated items and crashes after a client dies. Check
  that no pickup, magnet or drop code runs for a dead client player.
- The spectator camera is local only: follow a living player and cycle with input. Brotato's local co-op camera
  frames all players on one screen. Online, each client wants a camera on its own player or the spectated one.
  Override the camera target locally without touching anything the host simulates.

## Chat and player names

- Send text with Steam lobby chat (`sendLobbyChatMsg`, signal `lobby_message`). Never send game data through it.
- While a chat `LineEdit` has focus, consume input. Brotatogether's focus-emulator extension returns `false` for
  that case. Release focus on Enter/Esc, or the player can't move afterwards.
- `Steam.getFriendPersonaName(id)` can be empty or "[unknown]" for non-friends until their persona data loads.
  Refresh on `persona_state_change(steam_id, flags)`.
- Escape `[` in names shown in a `RichTextLabel` with BBCode enabled, or names can inject markup.
- Send IDs, never translated strings. Players may run different languages.

## Disconnects, reconnects, kicks

- When a client drops mid-wave, keep the slot. Freeze the player (zero movement, immune or downed), auto-ready
  it in the shop, and allow a rejoin by `steam_id` between waves. Removing it from `RunData.players_data` breaks
  every native array indexed by `player_index`.
- When the host drops, the session ends: show the reason, return to the menu and clean up. Call
  `CoopService.clear_coop_players()`, reset the co-op flags in `RunData`, call `leaveLobby` and close the P2P
  sessions. Otherwise the next solo run has phantom players.
- Kick: the Steamworks lobby API has no kick for members. Send a kick message, stop accepting that ID's sessions
  and packets, and update a `banned` list in the lobby data.
- Disconnect detection: combine lobby `LEFT`/`DISCONNECTED` events, session-failed signals and a heartbeat timeout
  (e.g. no packet for 5 s). Each one alone misses some cases.

## Settings sync

- The host's run settings (difficulty, endless, zone, DLC usage, gameplay-affecting mod configs) travel in
  `run_config` and are applied before the scene loads.
- Local preferences (volume, screen shake, damage-number visibility, language, keybinds) never sync.
- If you temporarily apply the host's gameplay mod configs on a client, restore the client's own values when the
  session ends.

## End of run, stats, damage meter

- The host decides victory or defeat and sends a phase message with the summary. Run the client's native
  run-end screen only after its `RunData` is fully synced. Unlocks and achievements are computed locally from
  `RunData` and `ProgressData`, and mirror data gives wrong results (e.g. 0 kills).
- Damage meters and per-weapon stats must be counted on the host, because that is where damage happens. Send
  them at wave end, not per hit.
- Emotes and map pings: small reliable events, rate-limited per slot on the host.
