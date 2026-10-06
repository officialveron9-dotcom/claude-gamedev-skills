# Ambient NPCs: Smart Objects, spectators, cheap crowds

## Smart Objects in the pool hall

Plugins: **Smart Objects**, plus **Gameplay Behaviors** and **Gameplay Behavior Smart Objects** for the Gameplay Behavior route. Gameplay Interactions is the StateTree-based interaction route; check its maturity label in the Plugins browser of your version.

Assets per activity:

| Object | Slots | Activity / user tags | Behavior |
|---|---|---|---|
| Bar stool | 1 seat slot (transform = the pelvis-aligned seat) | `Activity.Sit`, user requires `NPC.Patron` | Sit-down montage → seated loop (linked layer) → stand-up |
| Bar counter spot | 1 lean slot | `Activity.Drink` | Lean, sip montages picked by a Chooser |
| Table rail watch spot | 2–4 slots per side, facing the table | `Activity.Watch` | Stand/lean idle, react on match events |
| Bartender station | 1 slot, user requires `NPC.Bartender` | `Activity.Work` | Wipe or serve loop |
| Neighbor pool table | 2 player slots | `Activity.PlayPool` | Fake match loop (canned shot montages, no physics) |

Wiring options:
- **Blueprint/BT route:** `Move to and Use Smart Object with Gameplay Behavior` (AITask helper), or the BT task that finds and uses a Gameplay Behavior Smart Object. The slot's Behavior Definition is a `GameplayBehaviorSmartObjectBehaviorDefinition` that references a `GameplayBehavior` Blueprint (play the montage, wait, end).
- **StateTree route:** separate states Find → Claim → MoveTo slot → Use → Release, or Gameplay Interactions (*Use Smart Object with Gameplay Interaction*) where the slot runs its own StateTree.
- **Subsystem API (C++/BP):** `USmartObjectSubsystem::FindSmartObjects(Request, Results)` → claim a slot → use it (the slot goes from Claimed to Occupied) → free it. The method names changed across 5.x: `MarkSlotAsClaimed`/`MarkSlotAsOccupied`/`MarkSlotAsFree` in recent versions versus `Claim`/`Use`/`Release` earlier. Check the header of your engine version instead of trusting tutorials.

Checklist:
- [ ] The actor has a `SmartObjectComponent` with its Definition asset set. Slots carry the correct transform (show slots in the definition preview).
- [ ] The search box in `FSmartObjectRequest` covers the object. The filter's activity and user tags match. Disabled slots are skipped.
- [ ] Slot positions sit on the navmesh, or the approach point is reachable. The final alignment is done by a Motion Warping montage to the slot transform.
- [ ] **The claim handle is stored and released on every exit:** behavior end, abort, StateTree state exit, `EndPlay`, NPC despawn.
- [ ] Older engine versions (5.0/5.1) needed a built Smart Object Collection in the level. If `FindSmartObjects` returns nothing on an old project, check that first.
- [ ] Slots near the active shooter are disabled while a shot is being set up (see the keep-out in navigation.md).

Traps:

| Trap | Effect | Fix |
|---|---|---|
| Find and Claim in one StateTree state | Claim runs with no result | Separate states (see statetree-and-behavior-trees.md) |
| Claim not released after interruption | Stool permanently "occupied" | Release in exit paths, and use a periodic sanity sweep in debug builds |
| NPC teleported or snapped onto the seat | Visible pop | Approach point, then a sit montage with a Motion Warping target = slot transform |
| Seated NPC keeps a full CMC tick and blocking capsule | Wasted CPU, blocked aisles | Movement mode None while seated, shrink or ignore the capsule against pawns |
| StateTree tasks don't tick under Gameplay Interactions | Reported on the forum | Event-driven tasks, check the tick flags |

## Spectator design (cheap and alive)

- **No per-spectator perception or EQS.** The match manager broadcasts `MatchEvent(Type, Table, Intensity)`. Spectators within the event's radius pick a reaction from a Chooser (Type × Intensity × Mood) and play it on `UpperBody` or as an additive layer.
- **Stagger:** add a random reaction delay of 0.1–0.6 s per spectator, so a crowd that reacts on the same frame doesn't look robotic and doesn't spike the CPU.
- **Head tracking:** a cheap Look At on the cue ball for near spectators only (a distance tier).
- **Idle variety:** 3–6 idle variants, each started at a random time (feed a random value into the sequence player's `Start Position`), prevent synchronized breathing.
- **Logic tick:** seated spectators need no tree at all, just an event handler. Use StateTree only for those who move between activities.

## Cost ladder for many NPCs

| Tier | Technique | Status | Trap |
|---|---|---|---|
| 1 | Normal Character + simplified AnimBP + URO/Budget Allocator + MetaHuman Forced LOD | Production | Hero AnimBP on everyone |
| 2 | **Leader Pose** groups (one animated mesh, followers copy) for identical seated rows | Production | Followers must share the skeleton. Everyone moves identically, so offset the start times |
| 3 | **Animation Sharing plugin**: `AnimationSharingSetup` asset (per skeleton: state enum → animation permutations), a State Processor class (`ProcessActorState` returns the state), a manager created at runtime from the setup, actors registered with it. Scalability settings use **significance** (e.g. a Tick Significance Value above which actors don't tick) | Production per the plugin listing. The docs are dated 4.2x/5.0 | Needs a significance source (Significance Manager). States must map cleanly to an enum, which suits seated or standing crowds and not interactive NPCs |
| 4 | **Vertex Animation Textures** (AnimToTexture plugin) on instanced static meshes, as City Sample does | Experimental plugin | Fine only for distant silhouettes. A photoreal close-up shows no deformation quality, no IK and no blending |
| 5 | **MetaHuman Collections** (5.8): modular MetaHuman crowds that switch between full Actors near the camera and Instanced Skinned Meshes far away, orchestrated with Mass | Experimental | For an arena with hundreds of spectators only. Not for a 20-person hall |
| 6 | Mass Entity / MassCrowd (ZoneGraph lanes, City Sample) | MassEntity Beta (5.1+), MassCrowd built for City Sample with sparse docs | Overkill here. Learning cost is high and replication is not production-ready |

## Significance Manager (drives tiers)

- Enable the plugin and add the `SignificanceManager` module to Build.cs. It is C++-centric.
- Register each NPC with a significance function (distance to camera, on-screen, is near the active table) and a post-significance function that applies the tier: animation tier, StateTree on or off, tick intervals, groom and LOD settings.
- Call `Update` with the viewpoints once per frame from a game-specific place.
- **Unregister on EndPlay.** Dangling registrations crash after GC.
- Feed the same significance to the Animation Budget Allocator (budgeted components) and to Animation Sharing scalability so the systems agree.
