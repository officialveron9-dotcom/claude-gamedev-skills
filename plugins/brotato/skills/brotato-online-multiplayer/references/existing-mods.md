# Existing online multiplayer projects for Brotato (checked 2026-10-06)

| Project | License | Status | Transport | Players |
|---|---|---|---|---|
| Brotatogether, https://github.com/boardengineer/Brotatogether (mod `Pasha-Brotatogether`, also on the Steam Workshop) | **MIT** (© 2023 boardengineer) | Maintained: last commit 2026-05-20, about 44 stars and 14 forks. Workshop users report crashes after a few minutes and duplicated items after a client dies (search snippets) | Steam lobbies + old Steam P2P (`sendP2PPacket`, all reliable) | Lobby created with max 4 |
| BroTangto, https://github.com/SellenChen/brotangto-mod | **None declared**, so all rights reserved: read it, don't copy it | Alpha 0.3.0 (2026-09-10) for Brotato 1.1.15.4 / ModLoader 6.2.0-6.3.0. Its own status file says "PARTIALLY_COMPLETED / NEEDS_RUNTIME_VERIFICATION" | Godot 3 ENet, UDP 9000, over Radmin VPN | Exactly 2 |
| brotato-couch-online, https://github.com/inwf/brotato-couch-online | none checked | 2026-09 | Streams an HTML5 build of the game over WebRTC with virtual gamepads | n/a |
| Steam Remote Play Together (official) | n/a | Supported by the game | Streams the host's local co-op session | up to 4 |

Avoid brotato-couch-online as a model or dependency: the repository contains the game's exported `.pck` split into
parts, which is redistribution of game files. It is streaming, not netcode. Remote Play Together is the baseline
an online mod must beat: lower input latency, one camera per player, playable over weak upload.

## Brotatogether: how it works

- `mod_main.gd` installs about 25 script extensions (unit, entity, entity_birth, player_movement_behavior,
  entity_spawner, item, main, player_explosion, coop_service, run_data, sound managers, utils, pause menu,
  menus, shops, focus emulator). It adds `/root/SteamConnection` and `/root/BrotogetherOptions`, and calls
  `Steam.steamInit()` in `_init()`.
- **Lobbies:** public game lobbies tagged with the lobby data `lobby_type=BROTATOGETHER_GAME_LOBBY` and
  `lobby_status=OPEN/CLOSED`, plus an invisible 250-member "global chat" lobby (it joins the lowest lobby ID).
- **Transport:**
  - every message uses `P2P_SEND_RELIABLE`, on a channel equal to the message type (35 channels, all
    polled every physics frame);
  - the payload is `var2bytes(dict).compress(File.COMPRESSION_GZIP)`;
  - ping goes client → host, and the host broadcasts latencies every 2 s.
- **Slots:** the player index is the position in the lobby member list. The local player is device `0`, remote
  players are `100 + index` with player type `10`, and hooks test `device >= 50`.
- **Wave sync:** the host sends one Dictionary at 30 Hz containing:
  - wave time and bonus gold;
  - all players (position, movement, weapons, HP, gold, XP, level);
  - enemies, bosses, births, projectiles, items, consumables, neutrals, structures and pets;
  - batched deaths, flashes, hit effects, particles, floating text, sounds and explosions;
  - the upgrade-menu status.
- **Clients:**
  - spawn mirrors from `load(filename).instance()`;
  - swap `MovementBehavior`/`AttackBehavior` for stubs;
  - disable `take_damage` and hurtboxes;
  - make the spawner a no-op;
  - snap positions with `set_deferred`;
  - free mirrors instead of pooling them.

  Each client sends its own player position and weapon state (client-authoritative movement).
- **Shop:** host-rolled. Clients send focus, buy, reroll, lock, combine, discard and go intents keyed by `my_id`.
  The host sends the per-player shop, locks, weapons, effects and sets, and handles the Abyssal Terrors cursed flag.
- **Testing:** `is_solo_test` replays the host's own snapshots after 100 ms onto collision-less ghosts.
- A legacy ENet `DirectConnection` with Godot 3 `remote`/`remotesync` RPCs is still in `networking/`.

Learn from it: the hook list, client behavior stubs, batched cosmetic events, the solo ghost test, host-rolled
shops keyed by `my_id`, and disabling auto-pause on focus loss.

Don't repeat:
- reliable full-state snapshots (head-of-line blocking, and CPU cost grows with entity count);
- string-keyed Dictionaries per entity;
- lobby index as the player slot;
- ignoring clients that leave;
- assigning network IDs in `_ready()` on pooled nodes;
- no interpolation;
- a stale `manifest.json` (it still declares game `0.8.0.3` and ModLoader `6.0.0` while the code targets 1.1).

## BroTangto: how it works

- Two-player ENet host/client:
  - host peer ID is `1`;
  - every RPC checks the sender (`_is_host_sender`, `_is_tracked_client_sender`), and the client-provided slot
    is overwritten on the server;
  - 8 s connect timeout.
- The host snapshots at 20 Hz with unreliable RPC. Each snapshot carries the desired `scene` and a primitive
  `run_config` (zone, wave, difficulty, endless/co-op flags, player count), which the client applies before
  loading `Main`.
- Clients forward intents (`player_move`, selection, post-wave upgrade/reroll/take/discard, shop buy/reroll/go).
  The host gates post-wave actions to one per second per slot. Shop buys carry index plus item ID, and the host
  refuses a mismatch.
- Remote slots are fake devices `8`/`9` with `KEYBOARD_AND_MOUSE`. The movement extension returns
  `_current_movement` for `device >= 8`, and a 150 ms host watchdog clears stale movement.
- Known gaps, from its own docs:
  - enemies are matched by node name and then by order (fragile);
  - spawns, deaths, projectiles and drops are not synced;
  - the shop snapshot is incomplete;
  - an abnormal disconnect can leave the session active;
  - no NAT traversal, encryption or authentication.

Learn from it: strict RPC sender validation, the desired scene in every snapshot, applying `run_config` before the
scene load, and a decision log (`docs/DECISIONS.md`) that rejects lockstep for the same reasons as this skill.

## Other search hits

The GitHub search for "brotato multiplayer" also returns TypeScript and Node backends "inspired by Brotato".
These are standalone clones, not mods, and are irrelevant to modding the shipped game.
