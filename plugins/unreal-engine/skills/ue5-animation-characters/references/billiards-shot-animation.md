# Billiards shot animation: stance, cue, bridge, stroke

Principle: **the aim data is the truth.** Game code owns the cue transform, stroke curve and impulse. Animation and IK make the body agree with them. Physics and shot simulation are in `billiards-game-dev`.

## Data contract (game → animation)

```cpp
USTRUCT(BlueprintType)
struct FShotPresentation
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FTransform StanceWS;        // where the root/capsule must end
    UPROPERTY(BlueprintReadOnly) FVector    CueTipWS;        // tip at address (just behind the cue ball)
    UPROPERTY(BlueprintReadOnly) FVector    AimDirWS;        // unit, includes cue elevation
    UPROPERTY(BlueprintReadOnly) FVector    BridgeHandWS;    // on the cloth/rail, under the cue
    UPROPERTY(BlueprintReadOnly) FVector    GripWS;          // on the cue butt
    UPROPERTY(BlueprintReadOnly) EBridgeType Bridge;         // Open, Closed, Rail, MechanicalRest, SitOnRail
    UPROPERTY(BlueprintReadOnly) bool       bLeftHanded = false;
    UPROPERTY(BlueprintReadOnly) float      StrokeDuration = 0.f; // backswing+forward, from game
};
```
The AnimBP reads the component-space versions through Property Access (or the gather pattern in animbp-architecture.md). Convert with the mesh component transform **on the game thread**. Doing it in the thread-safe update by reading the component directly is a race.

## Stance solve (game code, not AnimBP)

1. Compute the bridge point: the cue ball minus `AimDir2D × BridgeLength` (tune per variant; a typical bridge sits a hand-span behind the ball).
2. Compute the grip point along the cue from the cue length and the grip offset.
3. Derive `StanceWS` from the grip and bridge points plus the handedness offset, and project it to the floor.
4. **If `StanceWS` lies inside the table footprint inflated by the body radius:** do not clamp-and-stretch. Choose a variant through a Chooser: Rail bridge (cue ball near the cushion), `SitOnRail` (one leg on the rail), or MechanicalRest (too far). Each variant has its own montage and IK target rules.
5. Check the stance against other actors (the opponent or spectators). Spectators get a dynamic nav keep-out zone (see `ue5-npc-ai`).

Trap: computing the stance from the animated hand position. That creates a feedback loop, and the stance creeps between shots.

## Getting into the stance (Motion Warping)

```
// BP order matters
MotionWarping->AddOrUpdateWarpTargetFromLocationAndRotation("Stance", Stance.GetLocation(), Stance.Rotator());
PlayAnimMontage(GetDownMontage);   // montage has root motion + Motion Warping notify-state, Warp Target Name = "Stance"
```
- The montage must contain **root motion**, and that root motion must be enabled on the source sequences. Motion Warping only reshapes root motion.
- `Skew Warp` puts the root at the target transform at the end of the window. Make the window end where the feet are planted.
- Approach with `MoveTo` to a point about one step away **before** playing the montage. Root motion overrides path following, so a move in progress gets aborted.
- Trap: the warp target is never set, or its name differs from the notify's Warp Target Name. Nothing errors, and the warp simply does not happen.
- Trap: a capsule blocked by the table edge shoves the character back. Shrink the capsule or ignore the table channel during the window, then restore it.

## Aim loop and stroke

| Wrong | Right |
|---|---|
| A cue attached to `hand_r`, with the stroke animated and the impulse fired by notify | The cue is its own actor or component, positioned by game code: `Tip = CueTipWS + AimDir × s(t)`, where `s(t)` is the stroke curve (backswing, pause, accelerate, contact, follow-through) |
| Montage length decides the contact time | Montage play rate = authored stroke clip duration ÷ `StrokeDuration`. IK covers the residual difference |
| `AnimNotify_Strike` calls `AddImpulse` | Game code detects `s(t)` crossing the contact distance (sub-step accurate) and applies the impulse. A `CueContact` Branching Point notify (or the gameplay event) drives SFX and VFX only |
| Practice strokes faked with montage loops while the cue stays still | The same stroke curve with a small amplitude and no contact (AI personality decides how many) |

Montage sections for the shot montage: `Enter` (root motion, warped) → `AimLoop` (loops to itself) → `Backswing` → `Stroke` → `FollowThrough` → `Exit` (root motion). Use Branching Point notifies where game code must react exactly (for example `StanceReached`). Author the AimLoop and Stroke sequences in place (or set `Force Root Lock`) so the root cannot drift.

## Control Rig: CR_ShotIK

Inputs (exposed variables → pins on the AnimBP `Control Rig` node): `GripTargetCS`, `BridgeTargetCS`, `CueAxisCS` (point and direction), `HeadAimPointCS`, `LeanAlpha`, `IKAlpha`.

Forwards Solve, in order:
1. **Bridge hand:** rotation from the cloth normal (or rail normal) and the aim direction. Finger shapes come from the authored bridge pose (open/closed), not from IK.
2. **Full Body IK** (`Hierarchy > Full Body IK`): effectors on `hand_l` (bridge) and `hand_r` (grip), plus foot effectors pinned to their animated transforms so the feet stay planted. Set the FBIK root to the pelvis. Raise stiffness on the pelvis and spine so the lean spreads naturally, and add elbow and knee limits so joints do not invert. Use a pole/preferred angle on the elbow of the grip arm so it hangs vertically above the cue (the classic "pendulum" arm).
3. **Head and spine:** aim the head at `HeadAimPointCS` (a point on the cue line ahead of the cue ball). Weight it more on the head and less on spine_03.
4. Blend everything by `IKAlpha` (0 outside a shot).

Traps:
- World-space targets fed into the rig make the hands fly off when the actor rotates. Feed component space.
- FBIK without pinned feet slides the whole body toward the hand targets.
- Do not rely on `IKAlpha = 0` alone to make the rig free, because the node and its inputs still update. Put the Control Rig node behind `Blend Poses by bool` (`bInShot`) so the branch is not evaluated when unused, and set `LOD Threshold` 0 or 1.
- Body clipping into the table during long reaches: add a pelvis/chest offset effector pushed outward along the table edge normal, or switch variants. Do not rely on IK alone for extreme reaches.
- Opponent seen from far away: replace FBIK with two `Two Bone IK` nodes (AnimGraph) plus a spine aim. The difference is invisible at a distance.
- The `IK Rig` AnimGraph node is cheaper to author when you only need goals. Turn on *Expose Position/Rotation* on the goals in the IK Rig asset or no pins appear.

## Feet

- The floor is flat, so foot IK only matters for keeping feet planted during the lean and for the `SitOnRail` leg. Use FBIK foot effectors in CR_ShotIK. Spectators need no foot IK.
- `Foot Placement` (Animation Warping plugin) is Experimental. If you use it, keep the pelvis settings conservative, because aggressive pelvis interpolation looks like bobbing while standing at the table.

## Reacting and watching

- Look-at during ball roll: the `Look At` node (cheap), or the GASP 5.8 additive Look-At POI Control Rig (Experimental, better layering).
- Reactions (made it, missed, foul): a Chooser picks a montage on `UpperBody` or `FullBody` depending on whether the character is still in the stance. Play the stand-up `Exit` section first if a full-body reaction needs locomotion.

## Opponent-specific

- The opponent uses the same `FShotPresentation` path as the player. Only the source of the aim data differs (the AI planner).
- Exempt the opponent from the Budget Allocator and URO while it is the active shooter. Re-enable them afterwards.
- If the opponent shoots while the camera looks at the player, keep `AlwaysTickPose` or the montage stalls and the game waits for it forever.
