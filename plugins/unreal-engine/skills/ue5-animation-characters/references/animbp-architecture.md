# AnimBP architecture: traps and correct setups (UE 5.4–5.8)

## Graph order (player / opponent)

```
Locomotion            State Machine (or Motion Matching fed by Pose History)
Linked Anim Layer     ContextLayer (ALI_PoolCharacter: Idle, TableStance, Seated, BarLean)
Slot FullBody         shot / stance / sit montages
Layered blend/bone    + Slot UpperBody from spine_01 (chalk, drink, gesture)
Apply Additive        Slot Additive (breath, flinch)
Look At / aim         (LOD Threshold 1)
Control Rig           CR_ShotIK (LOD Threshold 0-1), active only during a shot
Foot IK               (LOD Threshold 1), hero characters only
Output Pose
```

Order traps:
- A slot placed **after** Control Rig or IK means the montage overwrites the IK result, so the hands leave the cue during shot montages.
- Layered blend per bone without `Mesh Space Rotation Blend` makes the upper body twist with the pelvis while walking. Enable it for upper-body actions.
- An additive slot fed with a non-additive animation explodes the pose. The asset's Additive Anim Type must be set (Local Space, with the correct base pose).

## Thread safety

| Wrong | Right |
|---|---|
| Logic in `Event Blueprint Update Animation`: Cast To Character → Get Velocity → Set vars | `BlueprintThreadSafeUpdateAnimation` with **Property Access** to the owner's movement data, and helper functions marked *Thread Safe* |
| Ignoring "non thread-safe" compiler warnings | Treat them as errors. Turn on `Warn About Blueprint Usage` (Class Settings) to see Blueprint VM calls in the AnimGraph |
| Calling `GetOwningActor()->SomeFunc()` in `NativeThreadSafeUpdateAnimation` | Copy the data in `NativeUpdateAnimation` (game thread) into members, then read the members in the thread-safe update. Use a custom `FAnimInstanceProxy` only for heavy work |
| Expecting a value set by gameplay this frame to apply this frame | Property Access copies in batches, so expect one frame of latency. Anything frame-exact (cue contact) stays in game code |
| Event Graph flags to "init" a state | Anim Node Functions on the node: `On Initial Update`, `On Become Relevant`, `On Update` (the Lyra pattern) |

Settings: *Project Settings → Engine → General Settings → Anim Blueprints → Allow Multi Threaded Animation Update* (on by default) and the per-AnimBP class setting `Use Multi Threaded Animation Update`.

C++ minimal pattern:
```cpp
// Game thread: gather
void UPoolAnimInstance::NativeUpdateAnimation(float Dt)
{
    Super::NativeUpdateAnimation(Dt);
    if (const APoolCharacter* C = Cast<APoolCharacter>(TryGetPawnOwner()))
    {
        GroundSpeed  = C->GetVelocity().Size2D();
        ShotIKAlpha  = C->GetShotIKAlpha();          // set by gameplay
        GripTargetCS = C->GetGripTargetComponentSpace();
    }
}
// Worker thread: compute (no UObject access here)
void UPoolAnimInstance::NativeThreadSafeUpdateAnimation(float Dt)
{
    Super::NativeThreadSafeUpdateAnimation(Dt);
    bIsMoving = GroundSpeed > 3.f;
}
```

## Linked anim layers: traps

- `Link Anim Class Layers` reinitializes the linked instances. Calling it every tick, or on every shot, resets state machines and causes pops. Link only on a context change (sit down or stand up, approach the table).
- Ungrouped layers each get their own instance, so state is not shared and memory grows. Group layers that should share variables.
- Notifies fired in a linked instance can miss handlers in the main instance. Check `Receive Notifies from Linked Instances` and `Propagate Notifies to Linked Instances` on the `Linked Anim Layer` node.
- Unlinking leaves the default implementation of the interface in the main AnimBP. Make that default a sane idle, not an empty pose (T-pose).

## State machine vs Motion Matching vs Chooser

| Need | Pick | Trap to avoid |
|---|---|---|
| Short walks to a precise stance point | State machine + start/stop with `DistanceMatchToTarget` + Stride/Orientation warping (Animation Locomotion Library and Animation Warping plugins) | MM overshoots precise stops unless the database has stop clips at many distances. Distance matching is exact |
| Premium locomotion for 1–2 hero characters | GASP Motion Matching (production since 5.4) | Copying the 5.4-era setup (Character Trajectory component). Copy the trajectory code from the **current** GASP. Database size and search cost are per character, so don't give MM to spectators |
| Selecting shot or reaction montages | **Chooser table** (enum, float-range, bool, gameplay-tag columns) | Hard-coded `Select` nodes spread across the Event Graph |
| Spectator idles | Tiny state machine or Animation Sharing | Giving each spectator the hero AnimBP |

Motion Matching traps:
- **Capsule and root desync, foot sliding on turns:** use `Offset Root Bone` as GASP does (Experimental). It ignores moving bases.
- **Popping between clips:** schema weights or channels are wrong, or the database has gaps. Inspect the chosen poses and costs in the **Rewind Debugger** (enable the Animation Insights and Pose Search plugins, then Tools → Debug → Rewind Debugger and Rewind Debugger Details).
- **Mirrored clips selected wrongly:** set the Mirror Data Table in the database and check the mirror option per sequence.
- **Distance matching does nothing:** the clip has no baked root-distance curve, or the curve name differs from the one the node reads.

## GASP: what to copy, what to skip

- **Copy:** thread-safe AnimBP structure, Chooser-driven database selection, the trajectory generation code, the `Offset Root Bone` usage, debug widgets, and (5.8, Experimental) the **additive Look-At POI Control Rig** for watching rolling balls.
- **Copy carefully:** 5.8 Pose Search Interaction Assets and `Motion Match Multi` (multi-character interactions such as a handshake or racking the balls together). They are new in 5.8, so expect API changes.
- **Skip for this project:** the Mover-based character (Mover is Experimental), and the UAF character reported in 5.8 (UAF is Experimental and the report is unverified).
- **MetaHuman in GASP:** `CBP_SandboxCharacter_Metahuman_Kellan` uses runtime retargeting. Bake offline for shipping (see retargeting-metahuman.md).
