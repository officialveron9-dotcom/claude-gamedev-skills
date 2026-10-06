# StateTree and Behavior Tree: setup and traps

## StateTree on an AI (checklist)

- [ ] Plugins: StateTree and GameplayStateTree (AI tasks such as `Move To` and `Run Env Query` live in the GameplayStateTree module).
- [ ] The AIController has a `StateTreeAIComponent`. The asset uses the **StateTree AI Component Schema** with `AIControllerClass` (and the context actor class) set to **your** classes, or property binding cannot see your variables.
- [ ] Logic starts after possession: `Start Logic Automatically`, or `StartLogic()` in `OnPossess`.
- [ ] Global tasks or evaluators expose shared data (a match-state reference, the current `FShotPlan`). Tasks bind inputs to them instead of fetching actors themselves.
- [ ] Every task finishes: Blueprint tasks call **Finish Task** (Succeeded/Failed), and C++ tasks return `Succeeded`/`Failed` from `EnterState` or `Tick`. A task that never finishes keeps the state alive forever unless a transition fires.
- [ ] Transitions: prefer **On Event** (gameplay-tag events sent with `SendStateTreeEvent`) and On State Completed over per-tick condition polling.
- [ ] Each event-waiting state has a fallback timeout transition (a Delay task plus a transition on completion).

Built-in tasks seen in the API: `FStateTreeMoveToTask` (AITask_MoveTo-based; succeeds at the destination, fails if the move is impossible), `FStateTreeRunEnvQueryTask` (async EQS that outputs an actor or vector), plus Delay and Debug Text. Write tiny custom tasks for everything game-specific (play the shot montage, wait for balls at rest).

### StateTree traps

| Trap | Effect | Fix |
|---|---|---|
| Find and Claim Smart Object in the **same** state, or a parent whose selection descends straight into the Claim child | Claim runs before Find has a result | Put Find and Claim in separate states and transition to Claim on Find's completion. The forum fix: set Selection Behavior to `Try Enter` (not a select-children behavior) on the Find state |
| BP task with `Tick` logic but ticking disabled | Tick never runs (also reported when executed through *Use Smart Object with Gameplay Interaction*) | Check the task's tick setting (`bShouldCallTick`). Prefer event-driven tasks |
| State completion waits for *all* tasks while a background task (look-at) never finishes | The state never completes | Mark which tasks count toward completion (newer versions have per-task completion settings, so check the state's details) or move the forever-task to a parent or global task |
| Polling conditions every tick on 30 NPCs | Steady CPU cost | Events plus custom or scheduled tick rates (`FStateTreeScheduledTick`; states can request a custom tick rate) |
| Writing the same evaluator variable from tasks | Data races and confusion. Evaluators are meant as read-only data providers | Put the writable state in the AIController or a component and bind to it |
| Large monolithic tree for every NPC type | Hard to debug | Linked subtrees or linked assets per activity (bar, watch, play) |
| Changing the schema or context class after authoring | Bindings break silently | Fix the bindings, which the compiler flags in the StateTree editor |

Debugging: the StateTree debugger (StateTree editor and Rewind Debugger trace) records active states, transitions, task status and values in PIE, standalone or remote sessions. Turn on auto-record per PIE in the editor settings.

### StateTree for the pool hall (skeleton)

```
Root
├─ Global tasks: GetMatchContext (binds MatchState, MyTableId)
├─ [Opponent] MyTurn  (enter on event Match.TurnBegan.Self)
│   ├─ PlanShot           task: request ShotPlanner, wait event AI.ShotPlanned (timeout 3 s → Safety)
│   ├─ WalkToApproach     MoveTo(Plan.ApproachPoint, acceptance 10 cm)
│   ├─ GetDown            PlayShotMontage(Enter) → wait event Anim.StanceReached
│   ├─ Aim                Delay(Plan.ThinkTime) + practice strokes
│   ├─ Shoot              StartStroke → wait event Shot.StrokeFinished
│   └─ WatchBalls         LookAt cue ball → wait event Match.BallsAtRest → React
├─ [Opponent] NotMyTurn   SitOrStand smart object, watch the table
└─ [Ambient] Activities   Find → Claim → Use (see ambient-npcs.md)
```

## Behavior Tree (if used)

Checklist:
- [ ] `OnPossess` calls `Run Behavior Tree`, which sets up the blackboard from the BT's asset. Use `Use Blackboard` only when you need the blackboard before the tree runs.
- [ ] Blueprint tasks: `Event Receive Execute AI` → … → **`Finish Execute`** on **every** path. Implement `Event Receive Abort AI` → `Finish Abort`.
- [ ] Decorators that must interrupt running branches set **Observer Aborts** (`Self`, `Lower Priority`, `Both`). With `None` a change only applies on the next re-evaluation.
- [ ] Blackboard key types match (an Object key with a Base Class set, a Vector key for locations). A selector with the wrong key type stays empty in the details panel and the task fails.
- [ ] Services update blackboard data at an interval. Do not do it in task Tick.
- [ ] Use `Move To` acceptance radius > 0, and `Allow Partial Path` if the goal may be off the navmesh.

BT traps:

| Trap | Effect | Fix |
|---|---|---|
| Missing `Finish Execute` | Tree hangs on the task | Finish on all branches, including failure |
| Blackboard decorator without aborts | Reaction is delayed until the branch ends | Set Observer Aborts |
| Using BT for turn flow with long waits | Many "Wait" or "Is turn" decorators | A StateTree with events fits better. BT only if the team already uses it |
| Shot math in a BT service | Hitches, unreadable logic | ShotPlanner in C++, with the result in the blackboard |
| Mixing focus from BT and gameplay | NPC snaps between targets | One owner for `SetFocus`. Clear it when the branch exits |

## When to stay with plain Blueprint or C++

A bartender who loops "wipe counter → serve if the player is at the bar" can be a 3-state StateTree. Don't build BT, Blackboard and EQS for it. Spectators with two states (seated idle, react) need no tree at all: an event handler that plays a Chooser-selected montage is enough.
