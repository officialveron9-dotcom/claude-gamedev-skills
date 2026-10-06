# AI Perception and EQS: pool-hall usage and traps

## Perception: only where it adds value

| NPC | Sense | Purpose |
|---|---|---|
| Bartender | Sight (short radius, wide angle) | Notice the player at the bar and greet or serve |
| Nearby spectators | Hearing | Turn heads toward loud events (a break shot, a ball dropping off the table) |
| Opponent | None | It knows the match state from game code. Perception adds nothing |
| Background spectators | None | Use game-event broadcasts |

Setup:
- Put the `AIPerceptionComponent` on the **AIController** (not the pawn). Add `AISenseConfig_Sight` (Sight Radius, Lose Sight Radius > Sight Radius, Peripheral Vision Half Angle Degrees, Max Age, Detection by Affiliation) and/or `AISenseConfig_Hearing` (Hearing Range).
- Hearing needs someone to emit noise: call `Report Noise Event` (Location, Loudness, Instigator, Max Range, Tag) from game code on events such as a break shot or a ball hitting the floor.
- For sources that aren't auto-registered, or for non-sight senses, add an `AIPerceptionStimuliSourceComponent` with `Auto Register as Source` and the senses listed. Pawns register for sight by default.
- Bind `OnTargetPerceptionUpdated` (per actor, gives the stimulus with `WasSuccessfullySensed`). `OnTargetPerceptionForgotten` only fires when forgetting stale actors is enabled in the AI System settings.

Traps:

| Trap | Effect | Fix |
|---|---|---|
| Detection by Affiliation with only "Enemies" checked in a Blueprint-only project | Nothing is ever perceived, because without a team interface everyone is Neutral | Implement `IGenericTeamAgentInterface` (C++: `GetGenericTeamId`, optionally override `GetTeamAttitudeTowards` or set `FGenericTeamId::SetAttitudeSolver`), or check *Detect Neutrals* and filter by tag or class |
| Team ID never set | `AAIController` already implements the interface, but its team defaults to NoTeam and `SetGenericTeamId` is not Blueprint-exposed | Set the team in C++ (controller constructor or OnPossess), and give the perceived actors (player pawn or controller) a team as well |
| Sight on every spectator | Line traces per listener per target scale badly | Sight only on the bartender. Others use hearing or events |
| Lose Sight Radius ≤ Sight Radius | Flickering perceived/lost | Lose radius should be clearly larger |
| Expecting Perception to report "great shot" | It only senses stimuli | Game events from the match manager |

## EQS: dynamic spot picking

Use EQS when positions are not authored, for example "find a spot to watch the active table". Prefer **Smart Object slots** when positions are known (stools, rail lean spots), because they are cheaper, deterministic and reservable.

Example query `EQS_WatchSpot`:
- Generator: `Points: Donut` around a context = the active table (custom `EnvQueryContext` Blueprint that provides the table actor). Inner radius just outside the table and rail, outer radius about 3 m.
- Tests:
  1. `Pathfinding` (filter: reachable from the querier).
  2. `Trace` to the table center (filter out points with blocked line of sight).
  3. `Distance` to the **stance keep-out context** (filter: greater than the keep-out radius, so spectators don't stand where the shooter needs to be).
  4. `Distance` to other spectators (custom context, score higher when farther) to spread them out.
  5. `Dot` facing toward the table (score).
- Run it from StateTree (`Run Env Query` task, actor or vector output), from BT (`Run EQS Query` task into a Blackboard key), or from Blueprint (`Run EQS Query` → `On Query Finished` → `Get Query Results as Locations`).

Traps:

| Trap | Fix |
|---|---|
| Query returns nothing | Check each test's filter in the **EQS Testing Pawn** (place it, assign the query, inspect the spheres: green to red is the score, blue means it failed the filter) |
| Points off the navmesh | Set the generator's projection to navigation, or add a Pathfinding test |
| Querying every tick | Run on events (turn change, the spectator's current spot became invalid) and cache the result |
| Using EQS for exact seat positions | Use Smart Object slots |
| Expensive Trace or Pathfinding tests run first | Order cheap filters (Distance) before expensive ones (Trace, Pathfinding) |
