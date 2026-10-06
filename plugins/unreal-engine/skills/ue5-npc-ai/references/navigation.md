# Navigation (NavMesh) for a pool hall

## Generation mode: pick deliberately

| Mode (Project Settings → Navigation Mesh → Runtime Generation, or on the RecastNavMesh actor) | Behavior | Use here |
|---|---|---|
| `Static` | Built in the editor, saved, never changes | Hall layout is fixed and you need no runtime keep-outs |
| `Dynamic Modifiers Only` | Built in the editor. At runtime only modifiers (nav areas, links, dynamic obstacles) change costs or blocking. No new surfaces. Cached collision makes affected-tile updates cheaper (up to ~50%) | **Default recommendation:** keep-out zone around the shooter, doors, "reserved" areas |
| `Dynamic` | Tiles regenerate from changed geometry | Only if furniture moves at runtime (it shouldn't) |

Navigation Invokers ("Generate Navigation Only Around Navigation Invokers") are for open worlds. Don't use them in a single hall.

## Setup checklist

- [ ] A `NavMeshBoundsVolume` encloses the floor, slightly above and below it. Press `P` in the viewport to show the green navmesh.
- [ ] Build via Build → Build Paths, or the console `RebuildNavigation`. If the editor never updates, check *Editor Preferences → Level Editor → Miscellaneous → Update Navigation Automatically*.
- [ ] Supported Agents (Project Settings → Navigation System): one agent whose radius and height match the NPC capsule. Several agents each get their own navmesh, and a pawn whose capsule doesn't fit any agent may use an unexpected one.
- [ ] Pool tables and the bar carve the mesh. Stools: decide whether they are obstacles (carve) or NavArea_Obstacle (high cost) so NPCs can path close to them for sitting.
- [ ] **`Can Ever Affect Navigation` = false** on balls, cues, chalk, glasses, bottles, racks, the scoreboard and all small decorative meshes. Physics-simulating balls on a Dynamic navmesh cause constant tile rebuilds.
- [ ] The cell size fits the narrowest aisle. Too coarse a mesh closes gaps between tables.
- [ ] Smart Object slot locations are on the navmesh (or reachable within the acceptance radius). Project them with `ProjectPointToNavigation` at design time.

## Keep-out zone around the shooter

1. Use a `NavModifierComponent` (or a Nav Modifier Volume) on a small actor spawned at the stance. `Area Class` = `NavArea_Null` (blocked) or a custom high-cost `NavArea`.
2. Runtime Generation must be `Dynamic Modifiers Only` or `Dynamic`. **With `Static`, the modifier does nothing at runtime.**
3. NPCs already inside the zone: send them a "make room" event that re-paths them to a free slot. Modifiers don't push agents.
4. Disable spectator Smart Object slots that overlap the stance (slot enable/disable or a blocking tag) so nobody claims them.

## Crowd and avoidance in aisles

| Option | Setup | Trap |
|---|---|---|
| Detour Crowd | `ADetourCrowdAIController`, or `SetDefaultSubobjectClass<UCrowdFollowingComponent>(TEXT("PathFollowingComponent"))` in the AIController constructor | Tune `CollisionQueryRange`, separation weight and avoidance quality. The global config is in `UCrowdManager` (`FCrowdAvoidanceConfig`) |
| RVO (CMC `Use RVOAvoidance`) | Checkbox on the CMC | Force-based, it can push agents **off** the navmesh and leave them stuck. Never combine it with Detour |
| None | Few walkers at a time | Often fine in a pool hall. Stagger NPC moves instead |

Mover 5.8 added NavWalking support for Detour Crowd, but Mover itself is Experimental. Stay on the CMC.

## Playbook: navmesh not building

1. No bounds volume, or the volume does not intersect the floor collision → fix the volume.
2. The floor mesh has no collision or `Can Ever Affect Navigation` is off → enable collision on the floor.
3. Auto-update is disabled → Build Paths or turn on *Update Navigation Automatically*.
4. A RecastNavMesh actor is left over with odd settings → delete it and rebuild (it is recreated). The forum also reports a `Runtime → Can Be Main Nav Data` flag turned off.
5. World Partition levels need the world-partitioned navmesh workflow (see Epic's "World Partitioned Navigation Mesh"). Avoid World Partition for a single hall.
6. The mesh builds in the editor but is missing in a packaged game: the Static navmesh was not saved with the level, or the streaming sublevel lacks nav data → rebuild and save all levels.

## Playbook: agent not moving

1. **Controller?** Use `Auto Possess AI` = *Placed in World or Spawned*, and check with the Gameplay Debugger (`'`) that the NPC has a controller.
2. **Navmesh under the start and the goal?** Press `P`. Project the goal with `ProjectPointToNavigation`. Set an acceptance radius > 0.
3. **Move result:** read the `AI MoveTo` result or the `MoveTo` return value (`Failed`, `AlreadyAtGoal`, `RequestSuccessful`). Visual Logger shows the path request.
4. **Movement mode:** CMC must be Walking. A Flying or None mode, or a disabled movement component (seated NPC), ignores paths.
5. **Root motion montage playing:** it overrides path following.
6. **Agent radius:** a capsule larger than the agent radius in a tight aisle gets stuck at corners. Match them.
7. **Blocked by other NPCs:** RVO and Detour tuning, or a seated NPC whose capsule collision still blocks the aisle (shrink it or switch it to no-pawn-blocking while seated).
8. **Focus or rotation:** the NPC moves but faces wrong, because `SetFocus` is still active. Clear it.

## Navigation and animation contract

- Enable `Use Acceleration for Paths` on the CMC so locomotion animations (and Motion Matching trajectories) get believable starts and stops.
- Stop distance: the final positioning to a stance or seat is done by a Motion Warping montage, not by path following with a tiny acceptance radius (which jitters).
- Seated NPCs: disable movement or set the movement mode to None while seated, so no CMC tick runs. Re-enable it before the stand-up montage ends.
