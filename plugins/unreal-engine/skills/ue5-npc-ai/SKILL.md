---
name: ue5-npc-ai
description: Pitfalls and fixes for NPC and opponent AI in Unreal Engine 5 (current 5.8) for a pool-hall billiards game. Covers StateTree vs Behavior Tree traps, AIController/Blackboard setup, EQS, AI Perception (sight, hearing, teams), NavMesh setup and agents that do not move, Detour Crowd, Smart Objects for ambient behaviors (bar stools, drinking, watching a match), cheap spectators (Animation Sharing, VAT, Significance Manager, Mass/MetaHuman Collections status), an opponent billiards AI that keeps shot decisions out of BT/StateTree and animation, NPC budgets, and debugging (Gameplay Debugger, Visual Logger). Use it for AIController, Behavior Tree, StateTree, EQS, NavMesh, Smart Objects or Mass questions and AI bugs. German triggers: NPC, KI, KI-Gegner, Gegner-KI, Zuschauer, Barkeeper, Navigation, NavMesh, Verhaltensbaum.
---

# UE5 NPC and opponent AI: pitfalls and fixes (pool hall)

Scope: the billiards opponent, the bartender, players at other tables, and spectators. Animation is in `ue5-animation-characters`, ball and shot physics in `billiards-game-dev`, generic C++ and replication in the other `ue5-*` skills.

**Version (checked 2026-10-06):** UE 5.8 is current. **StateTree and Smart Objects** have been production-ready since 5.1. Behavior Trees still ship and work but get no new features (forum guidance points new work to StateTree; a formal deprecation is not confirmed). **MassEntity** has been Beta since 5.1 and was overhauled in 5.8 (Mass Signals in core, sparse fragments, entity creation off the game thread). Mass Entity Builder is Experimental (5.8), Mass replication is not production-ready, MetaHuman Collections are Experimental (5.8, built on Mass), and Mover is Experimental.

## Top traps (read first)

1. **Shot selection in a Behavior Tree, StateTree or EQS.** Shot choice is a search over geometry and physics. **Right:** a plain C++ `ShotPlanner` (time-sliced) returns a `FShotPlan`. StateTree only sequences presentation (walk, get down, aim, stroke, watch, react). See [references/billiards-opponent-ai.md](references/billiards-opponent-ai.md).
2. **AI waits on animation state ("is the montage at frame X?").** **Right:** the explicit events `StanceReached`, `StrokeFinished` and `BallsAtRest` are sent to the StateTree (`SendStateTreeEvent` with a gameplay tag), each with a timeout fallback.
3. **Using Mass for 20 pool-hall NPCs.** Mass pays off at hundreds to thousands of agents and is Beta or Experimental. **Right:** use ordinary Characters with StateTree, Smart Objects and animation LOD tiers.
4. **Balls, cues and glasses affecting navigation.** Physics props with `Can Ever Affect Navigation` on dirty the navmesh constantly (Dynamic) or carve holes (Static). Turn it off on every small or moving prop.
5. **Spectators standing in the shooter's cue path.** **Right:** a Nav Modifier (NavArea_Null or a high-cost area) around the active stance, with Runtime Generation = `Dynamic Modifiers Only`, plus Smart Object slots that a keep-out tag disables.
6. **StateTree ticking every frame on every NPC.** With default settings the component ticks every frame unless the active states or tasks request otherwise, and community benchmarks disagree on StateTree vs BT cost. Don't assume it's free. Use event-driven transitions, scheduled or custom tick rates (`FStateTreeScheduledTick`), and stop logic on insignificant NPCs. Profile.
7. **Smart Object claims never released** (NPC destroyed or interrupted). Slots stay "Claimed" forever, so bar stools look full while no one sits on them. Release in every exit path, including EndPlay.
8. **Perception teams in Blueprint.** Detection by Affiliation needs `IGenericTeamAgentInterface` (C++). Blueprint-only projects get "Neutral" for everyone. Use `Detect Neutrals` and filter by tag, or add the small C++ interface.
9. **`AI MoveTo` from a pawn with no controller.** `Auto Possess AI` defaults to *Placed in World*, so spawned NPCs have no AIController. Set it to *Placed in World or Spawned*.
10. **Robotic NPC locomotion.** Path following sets velocity directly, so locomotion animations see no acceleration. Enable `Use Acceleration for Paths` on the CMC (Nav Movement) and use `Orient Rotation to Movement`, or controller desired rotation with a sane rotation rate.

## StateTree vs Behavior Tree (decide once)

| Situation | Pick | Why |
|---|---|---|
| New project, ambient NPCs, opponent turn flow | **StateTree** (`StateTreeAIComponent` on the AIController, schema `StateTree AI Component Schema` with your AIController class set) | Explicit states and transitions, Smart Object and Mass integration, property binding, debugger |
| Existing BT team knowledge, highly reactive combat-style AI | BT + Blackboard | Mature, but no new features. Not needed for a pool hall |
| Need a BT feature inside StateTree, or the reverse | `Run StateTree` BT task | Migration path |

Details, setup checklists and both systems' traps: [references/statetree-and-behavior-trees.md](references/statetree-and-behavior-trees.md). Read it before you author any AI logic asset.

## AIController setup checklist

- [ ] Pawn: `AI Controller Class` set, and `Auto Possess AI` = *Placed in World or Spawned*.
- [ ] Logic starts in `OnPossess`: `Run Behavior Tree`, or a StateTree AI component with `Start Logic Automatically`, or a manual `StartLogic`. Logic started in the pawn's BeginPlay before possession finds no controller.
- [ ] Movement: CMC in Walking mode, `Use Acceleration for Paths` on, nav agent radius ≥ capsule radius (see navigation).
- [ ] Focus: `SetFocus` or `SetFocalPoint` for looking at the table or the shooter, and `ClearFocus` when leaving. Focus overrides rotation if the pawn uses controller desired rotation.
- [ ] Logic stops (`StopLogic` / `BrainComponent->StopLogic`) on NPCs that become insignificant or hidden. Restart on demand.

## NavMesh checklist (pool hall)

- [ ] One `NavMeshBoundsVolume` covers the walkable floor. Press `P` in the viewport to see the green mesh. Build with Build → Build Paths or the `RebuildNavigation` console command.
- [ ] Runtime Generation: `Static` if nothing changes. Use `Dynamic Modifiers Only` for keep-out zones and doors (it modifies costs and blocking without regenerating geometry). Use `Dynamic` only if geometry moves.
- [ ] The tables carve the navmesh (their collision is too high to step on), with chairs and stools as obstacles or nav areas. Balls, cues, glasses and racks have `Can Ever Affect Navigation` off.
- [ ] Agent radius and height fit the gaps between tables and stools. Too large produces islands, too small makes NPCs clip into tables.
- [ ] Narrow aisles between tables: Detour Crowd (`UCrowdFollowingComponent` or `ADetourCrowdAIController`) or CMC RVO, **never both**. RVO can push agents off the navmesh.

Details, plus "nav not building" and "agents not moving" playbooks: [references/navigation.md](references/navigation.md).

## Ambient NPCs (bartender, drinkers, spectators)

- Model each activity as a **Smart Object** slot: stool seat, bar lean spot, watch spot at a table rail, darts lane. The NPC loop is find → claim → move → use → release, driven by StateTree (or the BT task / AITask *Move to and Use Smart Object with Gameplay Behavior*).
- Spectators react to **game events** (`GreatShot`, `Foul`, `FrameWon`) broadcast by the match. Do not route these through AI Perception.
- Cost ladder: Smart Object loop + Chooser reaction montages for near NPCs. Animation Sharing or Forced LOD for background NPCs. VAT (AnimToTexture, Experimental) or MetaHuman Collections (Experimental) only for arena-sized crowds.

Smart Object recipes, spectator design and crowd options: [references/ambient-npcs.md](references/ambient-npcs.md). Read it before you build any bar, stool or spectator behavior.

## EQS and Perception (short)

- Use EQS for dynamic spot picking, such as a viewing spot with line of sight to the active table, outside the keep-out zone and not too close to the shooter. Prefer authored Smart Object slots when the positions are known.
- Use Perception for the bartender noticing the player at the bar (sight) and NPCs turning toward loud events (hearing via `Report Noise Event`). It is optional, so don't run sight on 30 spectators.

Details: [references/perception-eqs.md](references/perception-eqs.md).

## Performance budget for many NPCs

| Item | Rule |
|---|---|
| Logic tick | StateTree is event-driven where possible. Use a custom or scheduled tick rate for slow states (sitting: about 0.5–2 Hz) |
| Perception | Few senses and few listeners. Sight is the costliest, so limit it to the NPCs that need it |
| Movement | Only a handful of walkers at once. Seated NPCs have movement disabled and no CMC tick |
| Animation | Tiers from `ue5-animation-characters` (URO or Budget Allocator, Forced LOD, Animation Sharing) |
| Significance | Significance Manager (C++) drives tick rates, logic on/off and animation tier from distance and visibility |
| Starting target (60 fps) | AI game-thread under ~1 ms for the whole hall. An assumption, so profile with Insights |

## Debugging

- **Gameplay Debugger:** the `'` (apostrophe) key in PIE, numpad keys toggle categories (NavMesh, Basic, Behavior Tree, EQS, Perception). Point at an NPC to select it. The `EnableGDT` cheat also works.
- **Visual Logger** (Tools → Debug → Visual Logger): record a session and scrub through per-actor logs, paths, EQS and perception. Add your own entries with `UE_VLOG` and `UE_VLOG_LOCATION`.
- **StateTree debugger:** in the StateTree editor or Rewind Debugger, it records active states, transitions and task values. It works with PIE, standalone and remote sessions.
- `P` / `show Navigation` for the navmesh. The EQS Testing Pawn previews queries in the editor.

## Symptom → cause → fix (most common)

| Symptom | Cause | Fix |
|---|---|---|
| NPC stands still, no logic | No controller (Auto Possess AI), or logic not started | *Placed in World or Spawned*. Start the logic in OnPossess |
| `MoveTo` fails instantly | No navmesh at the start or goal, or the goal is off the mesh | Check with `P`, use `ProjectPointToNavigation`, raise the acceptance radius |
| `MoveTo` aborts mid-way | A root-motion montage started, or a new move request replaced it | Sequence moves and montages, check the move result |
| NPCs ice-skate or turn instantly | No acceleration for paths, bad rotation settings | `Use Acceleration for Paths`, set the rotation rate |
| All bar stools "taken" with nobody sitting | Claims not released | Release on abort, EndPlay and death |
| StateTree stuck in a state | A task never calls Finish Task, or transitions wait for "all tasks" | Finish every task and check the completion settings |
| Spectators block the player's stance | No keep-out | Dynamic nav modifier plus disabling slots near the shot |
| AI perceives nobody as hostile | No team interface (C++) | `IGenericTeamAgentInterface`, or Detect Neutrals plus tags |

Full table: [references/troubleshooting.md](references/troubleshooting.md).

## References

- [references/statetree-and-behavior-trees.md](references/statetree-and-behavior-trees.md): setup, task authoring, tick control and traps for StateTree and BT.
- [references/navigation.md](references/navigation.md): NavMesh generation modes, agents, modifiers, crowds, failure playbooks.
- [references/perception-eqs.md](references/perception-eqs.md): sight and hearing config, teams, EQS generators and tests for spot picking.
- [references/ambient-npcs.md](references/ambient-npcs.md): Smart Objects in the pool hall, spectator design, Animation Sharing, VAT, Mass and MetaHuman Collections status.
- [references/billiards-opponent-ai.md](references/billiards-opponent-ai.md): shot planner, difficulty model, turn flow StateTree, decision/animation contract.
- [references/troubleshooting.md](references/troubleshooting.md): extended symptom → cause → fix.
- [references/sources.md](references/sources.md): URLs and what each one supports (accessed 2026-10-06).
