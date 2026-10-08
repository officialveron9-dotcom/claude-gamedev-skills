# Optional moderation: kick, ban list, votes (NOT used by default)

The decided posture is fail-closed: inconsistencies invalidate the run and nothing else happens (SKILL.md §7).
This file keeps the moderation patterns in case the posture changes. Reasons they are off:

- Every check has false positives (desync bugs, loss, late packets). A wrong kick ends the session for a friend;
  a wrong "not verified" badge costs one ranked upload.
- The host cannot be kicked: the simulation lives there. Votes against the host can only end the run.
- Steam lobbies have no kick API. A "kicked" member stays in the member list, and when the lobby owner leaves,
  Steam promotes another member, possibly the kicked one. Every peer must enforce the decision locally.
- Naming a culprit from a hash split is unsafe: with 2 players there is no majority, with 3 a 2-1 split can be two
  desynced peers and one honest one.

## Kick (host executes; BrotatoOnline pattern from a shipped mod)

1. Send `KICKED` reliable to the target, remove it from the slot table, stop accepting its sessions and packets.
2. Wait 1 s so the reliable message flushes (`get_tree().create_timer(1.0, true)` on a PROCESS node).
3. `closeSessionWithUser(id)` / `closeP2PSessionWithUser(id)`, `endAuthSession(id)`, `cancelAuthTicket(...)`.
4. Set lobby data `banned = "<id>,<id>"`; peers read it on `lobby_data_update` and ignore those IDs. If the lobby
   owner later equals a banned ID, peers leave the lobby.

## Local ban list

```gdscript
const BAN_PATH := "user://%s/banlist.json"
var bans := {}        # "7656119..." -> {"when": unix, "why": "...", "run": "<run_hash hex>"}

func is_banned(steam_id: int) -> bool:
	return bans.has(str(steam_id))            # strings: JSON would turn the int into a float

func on_lobby_members_changed(member_ids: Array) -> void:
	for id in member_ids:
		if is_banned(id):
			if net.is_host():
				net.kick(id)
			else:
				net.leave_lobby("banned peer present")
```

Only from an explicit user action in the player list (BrotatoOnline has a kick dialog there). Never from a check.

## Votes

| Vote | Who votes | Needs | Timeout default |
|---|---|---|---|
| Host is the hash outlier | all clients | majority of connected clients | continue, run invalid |
| Kick peer X | all connected peers except X | majority, host must agree | no kick |
| End run | everyone | majority | continue |

`VOTE_OPEN{vote_id, kind, target, deadline_ms}` to all; `VOTE_CAST{vote_id, yes}` to all (everyone counts
locally); the host executes kicks. Count connected peers only, or the vote never resolves.
