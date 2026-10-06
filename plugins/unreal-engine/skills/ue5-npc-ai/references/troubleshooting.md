# NPC AI troubleshooting: symptom → cause → fix

## Controller and logic

| Symptom | Cause | Fix |
|---|---|---|
| Spawned NPC does nothing, placed one works | `Auto Possess AI` = Placed in World | *Placed in World or Spawned*, or `SpawnDefaultController()` after spawning |
| No logic although possessed | Logic started in pawn BeginPlay before possession, or the StateTree component doesn't auto-start | Start in `OnPossess`, or enable *Start Logic Automatically* |
| StateTree bindings show nothing from my controller | Schema `AIControllerClass` / context class left at the defaults | Set them to your classes and fix the bindings |
| StateTree stuck in a state | Task never finishes, or the state waits for a never-ending task | `Finish Task` on all paths, set the completion settings, add a timeout transition |
| BT stuck on a task | Missing `Finish Execute` (or `Finish Abort` on abort) | Finish on every path |
| BT reacts late | Blackboard decorator with Observer Aborts = None | `Self` / `Lower Priority` / `Both` |
| Events sent but no transition | Wrong gameplay tag, event sent before the state was active, or the transition is on another state | Check the tag hierarchy, use a "wait for event" state that is already active, and inspect the StateTree debugger |
| NPC logic runs while far away or hidden | No significance gating | `StopLogic` / restart via Significance Manager |

## Movement and navigation

| Symptom | Cause | Fix |
|---|---|---|
| `MoveTo` fails immediately | No navmesh at the start or goal | `P` to visualize, project the goal, acceptance radius > 0 |
| No navmesh in the level | No bounds volume, the floor doesn't affect navigation, auto-update off, broken RecastNavMesh actor | See navigation.md "not building" |
| Navmesh fine in the editor, missing in the packaged build | Static nav data not saved or not built for the sublevel | Rebuild, save all, check the sublevel nav data |
| Constant navmesh rebuilds and hitches | Dynamic generation and moving physics props (balls) affect navigation | `Can Ever Affect Navigation` off on props. Use `Dynamic Modifiers Only` |
| Keep-out modifier ignored | Runtime Generation = Static | `Dynamic Modifiers Only` |
| NPC slides or turns instantly | No acceleration for paths, rotation settings | `Use Acceleration for Paths`, rotation rate, Orient Rotation to Movement |
| NPC stuck at table corners | Agent radius smaller than the capsule, or the navmesh hugs geometry | Match the agent radius to the capsule, check the cell size |
| NPC pushed off the navmesh and stuck | RVO avoidance | Detour Crowd instead, never both |
| Move aborted when a montage starts | Root motion overrides path following | Sequence them: move, then montage |
| NPC jitters at the destination | Tiny acceptance radius for final alignment | Larger radius plus a Motion Warping montage for the exact pose |
| Seated NPC blocks the aisle | Capsule still blocks pawns | Shrink or ignore the capsule against pawns while seated |

## Smart Objects

| Symptom | Cause | Fix |
|---|---|---|
| `FindSmartObjects` returns nothing | Search box too small, tag filter mismatch, definition unset, slots disabled, (5.0/5.1) collection not built | Verify the request box and filters, the component definition, slot enabled state |
| Claim fails though slots look free | Previously leaked claims, or slot user tags don't match the NPC | Release on all exits, check user tag requirements |
| NPC sits floating or offset | Slot transform wrong or not used for alignment | Fix the slot transform in the definition, Motion Warp to the slot |
| Claim runs before Find (StateTree) | Same state, or wrong selection behavior | Separate states, `Try Enter` |
| Gameplay Interaction StateTree tasks don't tick | Reported issue | Event-driven tasks, check the tick flags |

## Perception and EQS

| Symptom | Cause | Fix |
|---|---|---|
| Nothing perceived with "Detect Enemies" | No team interface or team IDs (C++) | `IGenericTeamAgentInterface`, `SetGenericTeamId` in C++, or Detect Neutrals plus tags |
| Hearing never triggers | No `Report Noise Event` calls, range 0, or the listener lacks hearing config | Emit noise from game code, set Hearing Range |
| `OnTargetPerceptionForgotten` never fires | Forgetting stale actors disabled | Enable it in the AI System settings, set Max Age |
| Perceived and lost flicker | Lose Sight Radius ≈ Sight Radius | Make the lose radius clearly larger |
| EQS returns no items | A filter rejects everything | EQS Testing Pawn, then relax one test at a time |
| EQS points off the navmesh | No navigation projection | Projection on the generator, or a Pathfinding test |
| EQS costs spike | Trace or Pathfinding tests on many points every tick | Cheap tests first, run on events, cache results |

## Opponent flow

| Symptom | Cause | Fix |
|---|---|---|
| Match soft-locks on the AI turn | Waiting forever for a montage or notify event | Timeouts on every wait state |
| Hitch when the AI plans | Synchronous full search on the game thread | Time-slice or async over copied state |
| AI shot result differs after the player skipped the animation | Planning or error sampling re-ran on skip | Sample once into `FShotPlan`. Skip just jumps to Stroke |
| Visible cue direction ≠ ball direction | Error applied after presentation | Apply the error in the plan before the stance and IK solve |
| AI uses impossible stances | Planner ignores reachability | Include stance-variant feasibility in scoring |

## Performance

| Symptom | Cause | Fix |
|---|---|---|
| AI cost grows linearly with spectators | Each spectator runs a tree, perception or EQS | Event-handler spectators, no perception, significance gating |
| Periodic spikes | Many NPCs re-plan or re-query on the same frame | Stagger with random delays, time-slice |
| CMC cost for idle NPCs | Movement ticking while seated or idle | Movement mode None while seated, larger tick intervals for far NPCs |
